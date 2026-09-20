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
