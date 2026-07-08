import uuid
import asyncio
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field
from typing import Optional

from database import db, now_iso, NO_ID
from auth import require_roles
from notify import create_notification

router = APIRouter(prefix="/api/admin", tags=["admin"])

VALID_STATUSES = ["pending", "paid", "shipped", "delivered", "cancelled", "refunded"]


@router.get("/metrics")
async def metrics(admin=Depends(require_roles("admin"))):
    # Optimize Revenue via Native Database Aggregation
    pipeline = [
        {"$match": {"status": {"$nin": ["refunded", "cancelled"]}}},
        {"$group": {"_id": None, "total_revenue": {"$sum": "$total"}}}
    ]
    revenue_cursor = await db.orders.aggregate(pipeline).to_list(1)
    revenue = revenue_cursor[0]["total_revenue"] if revenue_cursor else 0.0

    # Optimize Commissions via Native Database Aggregation
    comm_pipeline = [
        {"$group": {"_id": None, "total_comm": {"$sum": "$commission"}}}
    ]
    comm_cursor = await db.commissions.aggregate(comm_pipeline).to_list(1)
    commission_earned = comm_cursor[0]["total_comm"] if comm_cursor else 0.0

    # Execute all descriptive collection counters concurrently
    counts = await asyncio.gather(
        db.users.count_documents({}),
        db.products.count_documents({"is_active": {"$ne": False}}),
        db.resale_listings.count_documents({"status": "active"}),
        db.resale_listings.count_documents({"status": "sold"}),
        db.orders.count_documents({}),
        db.seller_payouts.count_documents({"status": "pending"})
    )

    return {
        "total_users": counts[0],
        "total_products": counts[1],
        "active_listings": counts[2],
        "sold_listings": counts[3],
        "total_orders": counts[4],
        "revenue": round(revenue, 2),
        "pending_payouts": counts[5],
        "commission_earned": round(commission_earned, 2),
    }


async def _attach_buyer_email(o: dict):
    u = await db.users.find_one({"id": o["user_id"]}, NO_ID)
    o["buyer_email"] = u["email"] if u else None
    return o


@router.get("/orders")
async def all_orders(admin=Depends(require_roles("admin"))):
    orders = await db.orders.find({}, NO_ID).sort("created_at", -1).to_list(500)
    # Fix N+1 loop with concurrent resolution tasks
    await asyncio.gather(*[_attach_buyer_email(o) for o in orders])
    return orders


class StatusUpdate(BaseModel):
    status: str


@router.post("/orders/{order_id}/status")
async def update_status(order_id: str, body: StatusUpdate, admin=Depends(require_roles("admin"))):
    if body.status not in VALID_STATUSES:
        raise HTTPException(status_code=400, detail="Invalid status")
    o = await db.orders.find_one({"id": order_id}, NO_ID)
    if not o:
        raise HTTPException(status_code=404, detail="Order not found")
        
    # Guard: Prevent mutation of finalized orders
    if o.get("status") in ("refunded", "cancelled"):
        raise HTTPException(status_code=400, detail="Cannot alter status of a finalized order")

    history = o.get("status_history", [])
    history.append({"status": body.status, "at": now_iso()})
    await db.orders.update_one({"id": order_id},
                               {"$set": {"status": body.status, "status_history": history}})
    await create_notification(o["user_id"], "Order update",
                              f"Order #{order_id[:8]} is now {body.status}.", "info", "/orders")
    return {"ok": True}


class RefundRequest(BaseModel):
    reason: str = ""


@router.post("/orders/{order_id}/refund")
async def refund_order(order_id: str, body: RefundRequest, admin=Depends(require_roles("admin"))):
    o = await db.orders.find_one({"id": order_id}, NO_ID)
    if not o:
        raise HTTPException(status_code=404, detail="Order not found")
        
    if o.get("status") == "refunded":
         raise HTTPException(status_code=400, detail="Order has already been refunded")

    history = o.get("status_history", [])
    history.append({"status": "refunded", "at": now_iso()})
    await db.orders.update_one({"id": order_id},
                               {"$set": {"status": "refunded", "status_history": history}})
    await db.refunds.insert_one({
        "id": str(uuid.uuid4()), "order_id": order_id, "amount": o["total"],
        "reason": body.reason, "created_at": now_iso(),
    })
    await create_notification(o["user_id"], "Refund processed",
                              f"Order #{order_id[:8]} was refunded ${o['total']:.2f}..", "info", "/orders")
    return {"ok": True}


@router.get("/listings")
async def all_listings(admin=Depends(require_roles("admin"))):
    return await db.resale_listings.find({"status": {"$ne": "removed"}}, NO_ID).sort("created_at", -1).to_list(500)


@router.delete("/listings/{listing_id}\")")
@router.delete("/listings/{listing_id}")
async def remove_listing(listing_id: str, admin=Depends(require_roles("admin"))):
    l = await db.resale_listings.find_one({"id": listing_id}, NO_ID)
    if not l:
        raise HTTPException(status_code=404, detail="Listing not found")
    await db.resale_listings.update_one({"id": listing_id}, {"$set": {"status": "removed"}})
    await create_notification(l["seller_id"], "Listing removed",
                              f"Your listing '{l['title']}' was removed by an admin.", "warning")
    return {"ok": True}


@router.get("/users")
async def all_users(admin=Depends(require_roles("admin"))):
    users = await db.users.find({}, {"_id": 0, "password_hash": 0}).sort("created_at", -1).to_list(500)
    return users


async def _attach_seller_email(p: dict):
    u = await db.users.find_one({"id": p["user_id"]}, NO_ID)
    p["seller_email"] = u["email"] if u else None
    return p


@router.get("/payouts")
async def all_payouts(admin=Depends(require_roles("admin"))):
    payouts = await db.seller_payouts.find({}, NO_ID).sort("created_at", -1).to_list(500)
    # Fix N+1 loop with concurrent resolution tasks
    await asyncio.gather(*[_attach_seller_email(p) for p in payouts])
    return payouts


@router.post("/payouts/{payout_id}/approve")
async def approve_payout(payout_id: str, admin=Depends(require_roles("admin"))):
    p = await db.seller_payouts.find_one({"id": payout_id}, NO_ID)
    if not p or p["status"] != "pending":
        raise HTTPException(status_code=400, detail="Invalid payout")
    await db.seller_payouts.update_one({"id": payout_id},
                                       {"$set": {"status": "paid", "paid_at": now_iso()}})
    await db.seller_balances.update_one({"user_id": p["user_id"]},
                                        {"$inc": {"pending": -p["amount"]}, "$set": {"updated_at": now_iso()}})
    await create_notification(p["user_id"], "Payout sent",
                              f"Your payout of ${p['amount']:.2f} has been sent.", "success")
    return {"ok": True}


class CouponIn(BaseModel):
    code: str
    percent_off: int = Field(ge=1, le=90)
    description: str = ""


@router.get("/coupons")
async def list_coupons(admin=Depends(require_roles("admin"))):
    return await db.coupons.find({}, NO_ID).sort("created_at", -1).to_list(200)


@router.post("/coupons")
async def create_coupon(body: CouponIn, admin=Depends(require_roles("admin"))):
    doc = {"id": str(uuid.uuid4()), "code": body.code.upper(), "percent_off": body.percent_off,
           "description": body.description, "active": True, "created_at": now_iso()}
    await db.coupons.insert_one(doc)
    return {k: v for k, v in doc.items() if k != "_id"}


@router.get("/feature-flags")
async def get_flags(admin=Depends(require_roles("admin"))):
    return await db.feature_flags.find({}, NO_ID).to_list(100)


class FlagIn(BaseModel):
    key: str
    enabled: bool


@router.post("/feature-flags")
async def set_flag(body: FlagIn, admin=Depends(require_roles("admin"))):
    await db.feature_flags.update_one({"key": body.key},
                                      {"$set": {"key": body.key, "enabled": body.enabled}}, upsert=True)
    return {"ok": True}
