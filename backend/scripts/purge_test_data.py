import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
# Adjust the import below if 'database.py' is in a different location
from database import db 

async def purge_test_messages():
    # Regex targets any message starting with TEST_ or UITest_
    filter_query = {
        "text": {"$regex": "^(TEST_|UITest_)"}
    }
    
    try:
        result = await db.chat_messages.delete_many(filter_query)
        print(f"Success: {result.deleted_count} test messages purged.")
    except Exception as e:
        print(f"Error purging messages: {e}")

if __name__ == "__main__":
    asyncio.run(purge_test_messages())
