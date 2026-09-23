from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database import client, db

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Verify database connection
    try:
        await client.admin.command('ping')
        print("Successfully connected to MongoDB!")
    except Exception as e:
        print(f"Failed to connect to MongoDB: {e}")
    yield
    # Shutdown: Close database connection cleanly
    client.close()
    print("MongoDB connection closed.")

app = FastAPI(
    title="LCs The Fury Zone Studio API",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust domains in production as needed
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"status": "online", "project": "The Fury Zone Studio"}


@app.get("/api/health")
async def health():
    return {"status": "ok"}


# ---------------- Routers ----------------
# Every router is mounted under /api to match the Kubernetes ingress + Vercel rewrite.
from auth import router as auth_router
from catalog import router as catalog_router
from shop import router as shop_router
from resale import router as resale_router
from raffle import router as raffle_router
from chat import router as chat_router
from engage import router as engage_router
from storage import router as storage_router
from admin_routes import router as admin_router

for _r in (
    auth_router,
    catalog_router,
    shop_router,
    resale_router,
    raffle_router,
    chat_router,
    engage_router,
    storage_router,
    admin_router,
):
    app.include_router(_r, prefix="/api")
