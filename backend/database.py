import os
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

load_dotenv()

MONGO_URL = os.getenv("MONGO_URI") or os.getenv("MONGODB_URL")
if not MONGO_URL:
    raise ValueError("❌ MONGO_URI or MONGODB_URL is missing in environment variables.")

client = AsyncIOMotorClient(MONGO_URL)
db = client.get_default_database() # or client["your_database_name"]
