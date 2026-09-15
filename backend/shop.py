import os
import uuid
from fastapi import APIRouter, HTTPException, Depends, Request
from pydantic import BaseModel
from typing import Optional
try:
    import stripe
except ImportError:
    stripe = None

from database import db, now_iso, NO_ID
from auth import get_current_user
from notify import create_notification, log_event
from emailer import send_email, order_confirmation_html

router = APIRouter(prefix="", tags=["shop"])
COMMISSION = float(os.environ.get("PLATFORM_COMMISSION_RATE", "0.10"))
if stripe:
    stripe.api_key = os.environ.get("STRIPE_SECRET_KEY", "")

async def get_or_create_cart(user_id: str):
    cart = await db.carts.find_one({"user_id": user_id}, NO_ID)
    if cart:
        return cart
    cart = {"id": str(uuid.uuid4()), "user_id": user_id, "items": [], "created_at": now_iso()}
    await db.carts.insert_one(cart)
    return cart


@router.get("/cart")
async def get_cart(user: dict = Depends(get_current_user)):
    return await get_or_create_cart(user["id"])


@router.post("/cart/add")
async def add_to_cart(body: dict, user: dict = Depends(get_current_user)):
    product = await db.products.find_one({"id": body.get("product_id"), "is_active": {"$ne": False}}, NO_ID)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    cart = await get_or_create_cart(user["id"])
    quantity = max(int(body.get("quantity", 1)), 1)
    item = {"id": product["id"], "name": product["title"], "price": product["price"], "quantity": quantity,
            "image": (product.get("images") or [""])[0]}
    items = [i for i in cart["items"] if i["id"] != item["id"]]
    existing = next((i for i in cart["items"] if i["id"] == item["id"]), None)
    if existing:
        item["quantity"] += existing.get("quantity", 0)
    items.append(item)
    await db.carts.update_one({"id": cart["id"]}, {"$set": {"items": items, "updated_at": now_iso()}})
    return {**cart, "items": items}


@router.post("/cart/update")
async def update_cart(body: dict, user: dict = Depends(get_current_user)):
    cart = await get_or_create_cart(user["id"])
    items = [{**i, "quantity": max(int(body.get("quantity", i["quantity"])), 1)} if i["id"] == body.get("item_id") else i for i in cart["items"]]
    await db.carts.update_one({"id": cart["id"]}, {"$set": {"items": items, "updated_at": now_iso()}})
    return {**cart, "items": items}


@router.delete("/cart/item/{item_id}")
async def remove_from_cart(item_id: str, user: dict = Depends(get_current_user)):
    cart = await get_or_create_cart(user["id"])
    items = [i for i in cart["items"] if i["id"] != item_id]
    await db.carts.update_one({"id": cart["id"]}, {"$set": {"items": items, "updated_at": now_iso()}})
    return {**cart, "items": items}

# ---------------- Checkout & Payments (Updated) ----------------
class CheckoutRequest(BaseModel):
    origin_url: str
    coupon_code: Optional[str] = None
    address_id: Optional[str] = None

@router.post("/checkout/session")
async def create_checkout(body: CheckoutRequest, user: dict = Depends(get_current_user)):
    cart = await get_or_create_cart(user["id"])
    if not cart["items"]:
        raise HTTPException(status_code=400, detail="Cart is empty")
    
    subtotal = sum(i["price"] * i["quantity"] for i in cart["items"])
    discount = 0.0
    coupon_code = None
    if body.coupon_code:
        c = await db.coupons.find_one({"code": body.coupon_code.upper(), "active": True}, NO_ID)
        if c:
            discount = round(subtotal * (c.get("percent_off", 0) / 100.0), 2)
            coupon_code = c["code"]
    total = max(round(subtotal - discount, 2), 0.5)

    if not stripe or not stripe.api_key:
        raise HTTPException(status_code=503, detail="Stripe is not configured")
    session = stripe.checkout.Session.create(
        mode="payment", line_items=[{"price_data": {"currency": "usd", "product_data": {"name": "Fury Zone order"}, "unit_amount": round(total * 100)}, "quantity": 1}],
        success_url=f"{body.origin_url}/checkout/success?session_id={{CHECKOUT_SESSION_ID}}",
        cancel_url=f"{body.origin_url}/cart", metadata={"user_id": user["id"]},
    )
    order_id = session.id

    await db.payment_transactions.insert_one({
        "id": str(uuid.uuid4()),
        "session_id": order_id,
        "user_id": user["id"],
        "amount": float(total),
        "payment_status": "initiated",
        "order_created": False,
        "created_at": now_iso(),
    })
    
    return {"url": session.url, "session_id": order_id}

@router.post("/webhook/stripe")
async def stripe_webhook(request: Request):
    if not stripe:
        raise HTTPException(status_code=503, detail="Stripe dependency is not installed")
    payload = await request.body()
    signature = request.headers.get("stripe-signature", "")
    try:
        event = stripe.Webhook.construct_event(payload, signature, os.environ["STRIPE_WEBHOOK_SECRET"])
    except (ValueError, KeyError, stripe.error.SignatureVerificationError) as exc:
        raise HTTPException(status_code=400, detail="Invalid Stripe webhook") from exc
    if event["type"] == "checkout.session.completed":
        session = event["data"]["object"]
        await db.payment_transactions.update_one({"session_id": session["id"]}, {"$set": {"payment_status": "paid"}})
    return {"received": True}
