import os
from datetime import datetime, timezone
from motor.motor_asyncio import AsyncIOMotorClient

mongo_url = os.environ.get("MONGO_URL", "")

client = AsyncIOMotorClient(mongo_url)

db_name = os.environ.get("DB_NAME", "fury_zone")
db = client[db_name]


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


NO_ID = {"_id": 0}
