from dotenv import load_dotenv
from pathlib import Path
load_dotenv(Path(__file__).parent / ".env")

import os
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from database import db, client
import storage
from auth import router as auth_router
from catalog import router as catalog_router
from resale import router as resale_router
from shop import router as shop_router
from engage import router as engage_router
from admin_routes import router as admin_router
from storage import router as files_router
from seed import run_seed
from chat import router as chat_router
logging.basicConfig(level=logging.INFO,
                    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


# Standard Lifespan Context Manager replacing deprecated on_event hooks
@asynccontextmanager
async def lifespan(app: FastAPI):
    # ---- Startup Phase ----
    try:
        storage.init_storage()
        logger.info("Storage initialized")
    except Exception as e:
        logger.error(f"Storage init failed: {e}")
        
    try:
        await run_seed()
        logger.info("Seed complete")
    except Exception as e:
        logger.error(f"Seed failed: {e}")
        
    yield  # Application runs here
    
    # ---- Shutdown Phase ----
    try:
        client.close()
        logger.info("MongoDB connection closed cleanly")
    except Exception as e:
        logger.error(f"Error during database shutdown: {e}")


app = FastAPI(title="LCs The Fury Zone API", lifespan=lifespan)


@app.get("/api/")
async def root():
    return {"message": "LCs The Fury Zone API", "status": "ok"}


@app.get("/api/health")
async def health():
    return {"status": "healthy"}


for r in [auth_router, catalog_router, resale_router, shop_router,
          engage_router, admin_router, files_router]:
    app.include_router(r)

# Safe parsing configuration for cross-origin tracking vectors
raw_cors = os.environ.get("CORS_ORIGINS", "*")
parsed_origins = [origin.strip() for origin in raw_cors.split(",")] if "," in raw_cors else [raw_cors]

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=parsed_origins,
    allow_methods=["*"],
    allow_headers=["*"],
)
