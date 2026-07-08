import asyncio
from fastapi import APIRouter, HTTPException, Depends
from database import db, now_iso, NO_ID
from auth import get_current_user

router = APIRouter(prefix="/api", tags=["engage"])


@router.get("/notifications")
async def list_notifications(user: dict = Depends(get_current_user)):
    # Run the query and the count concurrently using asyncio.gather
    items_task = db.notifications.find({"user_id": user["id"]}, NO_ID).sort("created_at", -1).to_list(100)
    unread_task = db.notifications.count_documents({"user_id": user["id"], "read": {"$ne": True}})
    
    items, unread = await asyncio.gather(items_task, unread_task)
    
    return {"items": items, "unread": unread}


@router.post("/notifications/{notification_id}/read")
async def mark_read(notification_id: str, user: dict = Depends(get_current_user)):
    await db.notifications.update_one({"id": notification_id, "user_id": user["id"]},
                                      {"$set": {"read": True}})
    return {"ok": True}


@router.post("/notifications/read-all")
async def mark_all_read(user: dict = Depends(get_current_user)):
    await db.notifications.update_many({"user_id": user["id"]}, {"$set": {"read": True}})
    return {"ok": True}
