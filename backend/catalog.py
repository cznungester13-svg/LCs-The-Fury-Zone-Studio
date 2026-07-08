import uuid
import asyncio  # Added to support concurrent execution
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field
from typing import List, Optional

from database import db, now_iso, NO_ID
from auth import get_current_user, require_roles, ensure_seller_profile
from notify import create_notification

router = APIRouter(prefix="/api", tags=["resale"])

CONDITIONS = ["new", "like_new", "good", "fair"]


class ListingIn(BaseModel):
    title: str
    description: str = ""
    price: float
    condition: str = "good"
    category_id: Optional[str] = None
    brand_id: Optional[str] = None
    images: List[str] = []
    tags: List[str] = []


async def _decorate_listing(l: dict):
    seller = await db.users.find_one({"id": l["seller_id"]}, NO_ID)
    prof = await db.seller_profiles.find_one({"user_id": l["seller_id"]}, NO_ID)
    l["seller_name"] = (prof and prof.get("store_name")) or (seller and seller.get("full_name")) or "Seller"
    reviews = await db.reviews.find({"target_id": l["id"]}, NO_ID).to_list(500)
    l["rating"] = round(sum(r["rating"] for r in reviews) / len(reviews), 1) if reviews else 0
    l["review_count"] = len(reviews)
    return l


@router.get("/listings")
async def list_listings(
    search: Optional[str] = None,
    condition: Optional[str] = None,
    category_id: Optional[str] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    sort: str = "newest",
    limit: int = 60,
):
    q = {"status": "active"}
    if search:
        q["$or"] = [{"title": {"$regex": search, "$options": "i"}},
                    {"description": {"$regex": search, "$options": "i"}}]
    if condition:
        q["condition"] = condition
    if category_id:
        q["category_id"] = category_id
    price_q = {}
    if min_price is not None:
        price_q["$gte"] = min_price
    if max_price is not None:
        price_q["$lte"] = max_price
    if price_q:
        q["price"] = price_q
    sort_map = {"newest": ("created_at", -1), "price_asc": ("price", 1), "price_desc": ("price", -1)}
    field, direction = sort_map.get(sort, ("created_at", -1))
    
    # --- Performance Fix Applied Here ---
    items = await db.resale_listings.find(q, NO_ID).sort(field, direction).to_list(limit)
    
    # Create a list of co-routines (tasks) without awaiting them yet
    tasks = [_decorate_listing(l) for l in items]
    
items = await db.products.find(q, NO_ID).sort(field, direction).to_list(limit)
    
    # Fire all product decoration database calls at the exact same time
    await asyncio.gather(*[_decorate_product(p) for p in items])
    
    return items

@router.get("/listings/{listing_id}")
async def get_listing(listing_id: str):
    l = await db.resale_listings.find_one({"id": listing_id}, NO_ID)
    if not l:
        raise HTTPException(status_code=404, detail="Listing not found")
    return await _decorate_listing(l)


@router.post("/listings")
async def create_listing(body: ListingIn, user: dict = Depends(get_current_user))(=):
    if body.condition not in CONDITIONS:
        raise HTTPException(status_code=400, detail="Invalid condition")
    if "seller" not in user.get("roles", []):
        roles = user.get("roles", []) + ["seller"]
        await db.users.update_one({"id": user["id"]}, {"$set": {"roles": roles}})
        await ensure_seller_profile(user["id"])
    doc = body.model_dump()
    doc.update({
        "id": str(uuid.uuid4()),
        "seller_id": user["id"],
        "status": "active",  # instant go-live
        "created_at": now_iso(),
    })
    await db.resale_listings.insert_one(doc)
    await create_notification(user["id"], "Listing is live",
                              f"'{body.title}' is now live on the marketplace.", "success",
                              f"/listing/{doc['id']}")
    return {k: v for k, v in doc.items() if k != "_id"}


@router.get("/my/listings")
async def my_listings(user: dict = Depends(get_current_user)):
    items = await db.resale_listings.find({"seller_id": user["id"]}, NO_ID).sort("created_at", -1).to_list(500)
    return items


@router.put("/listings/{listing_id}")
async def update_listing(listing_id: str, body: ListingIn, user: dict = Depends(get_current_user)):
    l = await db.resale_listings.find_one({"id": listing_id}, NO_ID)
    if not l:
        raise HTTPException(status_code=404, detail="Listing not found")
    if l["seller_id"] != user["id"] and "admin" not in user.get("roles", []):
        raise HTTPException(status_code=403, detail="Not your listing")
    
    # Optimization: Prevent payload mutations overriding "status" fields if listing is removed/sold
    if l.get("status") != "active":
        raise HTTPException(status_code=400, detail="Cannot modify inactive or sold listings")
        
    await db.resale_listings.update_one({"id": listing_id}, {"$set": body.model_dump()})
    return await db.resale_listings.find_one({"id": listing_id}, NO_ID)


@router.delete("/listings/{listing_id}")
async def delete_listing(listing_id: str, user: dict = Depends(get_current_user)):
    l = await db.resale_listings.find_one({"id": listing_id}, NO_ID)
    if not l:
        raise HTTPException(status_code=404, detail="Listing not found")
    if l["seller_id"] != user["id"] and "admin" not in user.get("roles", []):
        raise HTTPException(status_code=403, detail="Not your listing")
    await db.resale_listings.update_one({"id": listing_id}, {"$set": {"status": "removed"}})
    return {"ok": True}


# ---------- Seller dashboard ----------
@router.get("/seller/profile")
async def seller_profile(user: dict = Depends(get_current_user)):
    prof = await db.seller_profiles.find_one({"user_id": user["id"]}, NO_ID)
    if not prof:
        await ensure_seller_profile(user["id"])
        prof = await db.seller_profiles.find_one({"user_id": user["id"]}, NO_ID)
    return prof


@router.get("/seller/balance")
async def seller_balance(user: dict = Depends(get_current_user)):
    bal = await db.seller_balances.find_one({"user_id": user["id"]}, NO_ID)
    if not bal:
        await ensure_seller_profile(user["id"])
        bal = await db.seller_balances.find_one({"user_id": user["id"]}, NO_ID)
    return bal


@router.get("/seller/stats")
async def seller_stats(user: dict = Depends(get_current_user)):
    active = await db.resale_listings.count_documents({"seller_id": user["id"], "status": "active"})
    sold = await db.resale_listings.count_documents({"seller_id": user["id"], "status": "sold"})
    bal = await db.seller_balances.find_one({"user_id": user["id"]}, NO_ID) or {}
    return {
        "active_listings": active,
        "sold_listings": sold,
        "available": bal.get("available", 0),
        "pending": bal.get("pending", 0),
        "total_earned": bal.get("total_earned", 0),
    }


class PayoutRequest(BaseModel):
    amount: float
    method: str = "bank"


@router.get("/seller/payouts")
async def list_payouts(user: dict = Depends(get_current_user)):
    return await db.seller_payouts.find({"user_id": user["id"]}, NO_ID).sort("created_at", -1).to_list(200)


@router.post("/seller/payouts")
async def request_payout(body: PayoutRequest, user: dict = Depends(get_current_user)):
    bal = await db.seller_balances.find_one({"user_id": user["id"]}, NO_ID)
    if not bal or body.amount <= 0 or body.amount > bal.get("available", 0):
        raise HTTPException(status_code=400, detail="Invalid payout amount")
    doc = {
        "id": str(uuid.uuid4()),
        "user_id": user["id"],
        "amount": body.amount,
        "method": body.method,
        "status": "pending",
        "created_at": now_iso(),
    }
    await db.seller_payouts.insert_one(doc)
    await db.seller_balances.update_one(
        {"user_id": user["id"]},
        {"$inc": {"available": -body.amount, "pending": body.amount}, "$set": {"updated_at": now_iso()}},
    )
    await create_notification(user["id"], "Payout requested",
                              f"Your payout of ${body.amount:.2f} is being processed.", "info")
    return {k: v for k, v in doc.items() if k != "_id"}
