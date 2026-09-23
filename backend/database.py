import os
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

load_dotenv()

MONGO_URL = os.getenv("MONGO_URI") or os.getenv("MONGODB_URL") or os.getenv("MONGO_URL")
if not MONGO_URL:
    raise ValueError("❌ MONGO_URI / MONGODB_URL / MONGO_URL is missing in environment variables.")

client = AsyncIOMotorClient(MONGO_URL)

# Prefer an explicit DB_NAME; otherwise fall back to the default DB encoded in the URI.
_db_name = os.getenv("DB_NAME")
if _db_name:
    db = client[_db_name]
else:
    try:
        db = client.get_default_database()
    except Exception:
        db = client["test_database"]
