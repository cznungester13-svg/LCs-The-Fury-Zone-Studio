import uuid
from fastapi import APIRouter, Depends, HTTPException
from database import db, now_iso, NO_ID
from auth import get_current_admin, get_current_user

router = APIRouter(prefix="/chat", tags=["chat"])
ROOM_NAME = "Chatting with the Peeps"


@router.get("/room")
async def get_room():
    return {"name": ROOM_NAME}

@router.get("/messages")
async def get_messages():
    return await db.chat.find({"room": ROOM_NAME}, NO_ID).sort("created_at", 1).to_list(length=100)

@router.post("/messages")
async def post_message(data: dict, user: dict = Depends(get_current_user)):
    text = str(data.get("text", "")).strip()
    if not text:
        raise HTTPException(status_code=400, detail="Message cannot be empty")
    message = {
        "id": str(uuid.uuid4()), "room": ROOM_NAME, "text": text,
        "user_id": user["id"], "user_name": user.get("full_name", "User"),
        "created_at": now_iso(),
    }
    await db.chat.insert_one(message)
    return {k: v for k, v in message.items() if k != "_id"}

@router.delete("/messages/{message_id}")
async def delete_message(message_id: str, admin: dict = Depends(get_current_admin)):
    message = await db.chat.find_one({"id": message_id})
    if not message:
        raise HTTPException(status_code=404, detail="Message not found")
    await db.chat.delete_one({"id": message_id})
    return {"status": "success"}
