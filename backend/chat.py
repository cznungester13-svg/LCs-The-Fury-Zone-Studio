from fastapi import APIRouter, Depends, HTTPException, status
from database import db
from auth import get_current_admin, get_current_user
from bson import ObjectId

router = APIRouter(prefix="/api/chat", tags=["chat"])

@router.get("/messages")
async def get_messages():
    return await db.chat.find().to_list(length=100)

@router.post("/messages")
async def post_message(data: dict, user: dict = Depends(get_current_user)):
    # Add logic to save message
    return {"status": "posted"}

@router.delete("/messages/{message_id}")
async def delete_message(message_id: str, admin: dict = Depends(get_current_admin)):
    message = await db.chat.find_one({"_id": ObjectId(message_id)})
    if not message:
        raise HTTPException(status_code=404, detail="Message not found")
    await db.chat.delete_one({"_id": ObjectId(message_id)})
    return {"status": "success"}
