import asyncio
import uuid
from fastapi import APIRouter, HTTPException, Depends
from database import db, now_iso, NO_ID
from auth import get_current_user

router = APIRouter(prefix="", tags=["engage"])


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


# ---------------- Wishlist ----------------
async def _resolve_wish_meta(item_type, item_id, fallback):
    if item_type == "listing":
        src = await db.resale_listings.find_one({"id": item_id}, NO_ID)
    else:
        src = await db.products.find_one({"id": item_id}, NO_ID)
    if src:
        return {
            "title": src.get("title", "Item"),
            "price": src.get("price", 0),
            "image": (src.get("images") or [""])[0],
        }
    return {
        "title": fallback.get("title", "Item"),
        "price": fallback.get("price", 0),
        "image": fallback.get("image", ""),
    }


async def _add_wish(user_id, item_type, item_id, fallback):
    meta = await _resolve_wish_meta(item_type, item_id, fallback)
    doc = {
        "id": str(uuid.uuid4()),
        "user_id": user_id,
        "item_id": item_id,
        "item_type": item_type,
        **meta,
        "created_at": now_iso(),
    }
    await db.wishlists.insert_one(doc)
    return {k: v for k, v in doc.items() if k != "_id"}


@router.get("/wishlist")
async def get_wishlist(user: dict = Depends(get_current_user)):
    return await db.wishlists.find({"user_id": user["id"]}, NO_ID).sort("created_at", -1).to_list(500)


@router.get("/wishlist/check/{item_id}")
async def check_wishlist(item_id: str, user: dict = Depends(get_current_user)):
    existing = await db.wishlists.find_one({"user_id": user["id"], "item_id": item_id}, NO_ID)
    return {"in_wishlist": bool(existing)}


@router.post("/wishlist")
async def add_wishlist(body: dict, user: dict = Depends(get_current_user)):
    item_id = body.get("item_id") or body.get("product_id")
    item_type = body.get("item_type", "product")
    if not item_id:
        raise HTTPException(status_code=400, detail="item_id is required")
    existing = await db.wishlists.find_one({"user_id": user["id"], "item_id": item_id}, NO_ID)
    if existing:
        return {"in_wishlist": True, **existing}
    doc = await _add_wish(user["id"], item_type, item_id, body)
    return {"in_wishlist": True, **doc}


@router.post("/wishlist/toggle")
async def toggle_wishlist(body: dict, user: dict = Depends(get_current_user)):
    item_id = body.get("item_id") or body.get("product_id")
    item_type = body.get("item_type", "product")
    if not item_id:
        raise HTTPException(status_code=400, detail="item_id is required")
    existing = await db.wishlists.find_one({"user_id": user["id"], "item_id": item_id}, NO_ID)
    if existing:
        await db.wishlists.delete_one({"user_id": user["id"], "item_id": item_id})
        return {"in_wishlist": False}
    doc = await _add_wish(user["id"], item_type, item_id, body)
    return {"in_wishlist": True, **doc}


@router.delete("/wishlist/{item_id}")
async def remove_wishlist(item_id: str, user: dict = Depends(get_current_user)):
    await db.wishlists.delete_one({"user_id": user["id"], "item_id": item_id})
    return {"ok": True}


# ---------------- Newsletter ----------------
@router.post("/newsletter")
async def subscribe_newsletter(body: dict):
    email = str(body.get("email", "")).strip().lower()
    if not email or "@" not in email:
        raise HTTPException(status_code=400, detail="A valid email is required")
    await db.newsletter.update_one(
        {"email": email},
        {"$set": {"email": email, "subscribed_at": now_iso()}},
        upsert=True,
    )
    return {"ok": True, "message": "You're on the list!"}
