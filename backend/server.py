import logging
import os
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import List
import uuid

from dotenv import load_dotenv
from fastapi import APIRouter, FastAPI
from pydantic import BaseModel, ConfigDict, Field
from starlette.middleware.cors import CORSMiddleware

# 1. Import your unified database and auth router
from auth import router as auth_router
from database import client, db

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / ".env")


# 2. Modern Lifespan Manager using our imported database client
@asynccontextmanager
async def lifespan(app: FastAPI):
    yield
    client.close()


# 3. Create main application instance
app = FastAPI(lifespan=lifespan)

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")


# Define Models
class StatusCheck(BaseModel):
    model_config = ConfigDict(extra="ignore")  # Ignore MongoDB's _id field

    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    client_name: str
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )


class StatusCheckCreate(BaseModel):
    client_name: str


# System Status Routes
@api_router.get("/")
async def root():
    return {"message": "Hello World"}


@api_router.post("/status", response_model=StatusCheck)
async def create_status_check(input: StatusCheckCreate):
    status_dict = input.model_dump()
    status_obj = StatusCheck(**status_dict)

    doc = status_obj.model_dump()
    doc["timestamp"] = doc["timestamp"].isoformat()

    await db.status_checks.insert_one(doc)
    return status_obj


@api_router.get("/status", response_model=List[StatusCheck])
async def get_status_checks():
    status_checks = await db.status_checks.find({}, {"_id": 0}).to_list(1000)

    for check in status_checks:
        if isinstance(check["timestamp"], str):
            check["timestamp"] = datetime.fromisoformat(check["timestamp"])

    return status_checks


# 4. Include both your main API paths and your explicit Auth router
app.include_router(api_router)
app.include_router(auth_router)

# 5. Robust CORS settings using your explicit frontend URL fallback
app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=[
        os.environ.get(
            "CORS_ORIGINS",
            "https://marketplace-fury.preview.emergentagent.com",
        )
    ],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)
