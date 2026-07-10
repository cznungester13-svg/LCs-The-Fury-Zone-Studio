from fastapi import APIRouter, Depends, HTTPException, status
from bson import ObjectId
from database import db
from auth import get_current_user, get_current_admin

router = APIRouter(prefix="/api/chat", tags=["chat"])

@router.delete("/messages/{message_id}")
async def delete_message(message_id: str, current_user: dict = Depends(get_current_admin)):
    # 1. Attempt to find the message
    message = await db.messages.find_one({"_id": ObjectId(message_id)})
    
    # 2. If it doesn't exist, return 404
    if not message:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Message not found"
        )
        
    # 3. Proceed with deletion if found
    await db.messages.delete_one({"_id": ObjectId(message_id)})
    return {"status": "success", "message": "Message deleted"}
