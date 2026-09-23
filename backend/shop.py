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
    cart.pop("_id", None)
    return cart


@router.get("/cart")
async def get_cart(user: dict = Depends(get_current_user)):
    return await get_or_create_cart(user["id"])


@router.post("/cart/add")
async def add_to_cart(body: dict, user: dict = Depends(get_current_user)):
    item_type = body.get("item_type", "product")
    item_id = body.get("item_id") or body.get("product_id")
    if not item_id:
        raise HTTPException(status_code=400, detail="item_id is required")
    quantity = max(int(body.get("quantity", 1)), 1)
    variant_id = body.get("variant_id")

    if item_type == "listing":
        src = await db.resale_listings.find_one({"id": item_id, "status": "active"}, NO_ID)
        if not src:
            raise HTTPException(status_code=404, detail="Listing not found")
        title = src.get("title", "Listing")
        price = src.get("price", 0)
        quantity = 1  # resale items are one-of-a-kind
    else:
        src = await db.products.find_one({"id": item_id, "is_active": {"$ne": False}}, NO_ID)
        if not src:
            raise HTTPException(status_code=404, detail="Product not found")
        title = src.get("title", "Product")
        price = src.get("price", 0)

    image = (src.get("images") or [""])[0]
    cart = await get_or_create_cart(user["id"])

    def _match(i):
        return i.get("item_id") == item_id and i.get("variant_id") == variant_id

    items = list(cart["items"])
    existing = next((i for i in items if _match(i)), None)
    if existing:
        if item_type != "listing":
            existing["quantity"] = existing.get("quantity", 1) + quantity
    else:
        items.append({
            "item_id": item_id,
            "item_type": item_type,
            "title": title,
            "image": image,
            "price": price,
            "quantity": quantity,
            "variant_id": variant_id,
        })
    await db.carts.update_one({"id": cart["id"]}, {"$set": {"items": items, "updated_at": now_iso()}})
    return {**cart, "items": items}


@router.post("/cart/update")
async def update_cart(body: dict, user: dict = Depends(get_current_user)):
    item_id = body.get("item_id")
    variant_id = body.get("variant_id")
    new_qty = max(int(body.get("quantity", 1)), 1)
    cart = await get_or_create_cart(user["id"])
    items = []
    for i in cart["items"]:
        if i.get("item_id") == item_id and i.get("variant_id") == variant_id:
            items.append({**i, "quantity": new_qty})
        else:
            items.append(i)
    await db.carts.update_one({"id": cart["id"]}, {"$set": {"items": items, "updated_at": now_iso()}})
    return {**cart, "items": items}


@router.delete("/cart/item/{item_id}")
async def remove_from_cart(item_id: str, user: dict = Depends(get_current_user)):
    cart = await get_or_create_cart(user["id"])
    items = [i for i in cart["items"] if i.get("item_id") != item_id]
    await db.carts.update_one({"id": cart["id"]}, {"$set": {"items": items, "updated_at": now_iso()}})
    return {**cart, "items": items}

# ---------------- Orders ----------------
@router.get("/orders")
async def list_orders(user: dict = Depends(get_current_user)):
    return await db.orders.find({"user_id": user["id"]}, NO_ID).sort("created_at", -1).to_list(200)


# ---------------- Coupons ----------------
class CouponIn(BaseModel):
    code: str


@router.post("/coupons/validate")
async def validate_coupon(body: CouponIn):
    c = await db.coupons.find_one({"code": body.code.upper(), "active": True}, NO_ID)
    if not c:
        raise HTTPException(status_code=404, detail="Invalid or expired coupon")
    return {"code": c["code"], "percent_off": c.get("percent_off", 0)}


# ---------------- Addresses ----------------
@router.get("/addresses")
async def list_addresses(user: dict = Depends(get_current_user)):
    return await db.addresses.find({"user_id": user["id"]}, NO_ID).sort("created_at", -1).to_list(100)


@router.post("/addresses")
async def add_address(body: dict, user: dict = Depends(get_current_user)):
    doc = {k: v for k, v in body.items() if k not in ("id", "user_id", "_id")}
    doc.update({"id": str(uuid.uuid4()), "user_id": user["id"], "created_at": now_iso()})
    await db.addresses.insert_one(doc)
    return {k: v for k, v in doc.items() if k != "_id"}


# ---------------- Checkout & Payments (Stripe) ----------------
FREE_SHIP_THRESHOLD = 75.0
FLAT_SHIP = 6.99


def _compute_totals(items, discount_percent=0):
    subtotal = round(sum(i["price"] * i["quantity"] for i in items), 2)
    discount = round(subtotal * (discount_percent / 100.0), 2) if discount_percent else 0.0
    shipping = 0.0 if (subtotal >= FREE_SHIP_THRESHOLD or subtotal == 0) else FLAT_SHIP
    total = max(round(subtotal - discount + shipping, 2), 0.5)
    return subtotal, discount, shipping, total


class CheckoutRequest(BaseModel):
    origin_url: str
    coupon_code: Optional[str] = None
    address_id: Optional[str] = None
    full_name: Optional[str] = None
    email: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    zip_code: Optional[str] = None


@router.post("/checkout/session")
async def create_checkout(body: CheckoutRequest, user: dict = Depends(get_current_user)):
    cart = await get_or_create_cart(user["id"])
    if not cart["items"]:
        raise HTTPException(status_code=400, detail="Cart is empty")

    discount_percent = 0
    coupon_code = None
    if body.coupon_code:
        c = await db.coupons.find_one({"code": body.coupon_code.upper(), "active": True}, NO_ID)
        if c:
            discount_percent = c.get("percent_off", 0)
            coupon_code = c["code"]

    # Amounts computed SERVER-SIDE from the stored cart (never trust the client).
    subtotal, discount, shipping, total = _compute_totals(cart["items"], discount_percent)

    if not stripe or not stripe.api_key:
        raise HTTPException(status_code=503, detail="Stripe is not configured")

    item_count = sum(i["quantity"] for i in cart["items"])
    session = stripe.checkout.Session.create(
        mode="payment",
        line_items=[{
            "price_data": {
                "currency": "usd",
                "product_data": {"name": f"LCs The Fury Zone \u2014 {item_count} item(s)"},
                "unit_amount": round(total * 100),
            },
            "quantity": 1,
        }],
        success_url=f"{body.origin_url}/checkout/success?session_id={{CHECKOUT_SESSION_ID}}",
        cancel_url=f"{body.origin_url}/cart",
        metadata={"user_id": user["id"]},
    )

    order_items = [{
        "item_id": i["item_id"],
        "title": i.get("title", "Item"),
        "price": i["price"],
        "quantity": i["quantity"],
        "image": i.get("image", ""),
    } for i in cart["items"]]

    shipping_address = {
        "full_name": body.full_name,
        "email": body.email,
        "address": body.address,
        "city": body.city,
        "zip_code": body.zip_code,
    }
    if body.address_id:
        saved = await db.addresses.find_one({"id": body.address_id, "user_id": user["id"]}, NO_ID)
        if saved:
            shipping_address = saved

    await db.payment_transactions.insert_one({
        "id": str(uuid.uuid4()),
        "session_id": session.id,
        "user_id": user["id"],
        "items": order_items,
        "subtotal": subtotal,
        "discount": discount,
        "shipping": shipping,
        "amount": float(total),
        "coupon_code": coupon_code,
        "shipping_address": shipping_address,
        "payment_status": "pending",
        "status": "initiated",
        "order_created": False,
        "created_at": now_iso(),
        "updated_at": now_iso(),
    })

    return {"url": session.url, "session_id": session.id}


async def _mark_paid_and_create_order(session_id: str):
    """Idempotent: flips the transaction to paid and creates the order exactly once."""
    tx = await db.payment_transactions.find_one({"session_id": session_id}, NO_ID)
    if not tx:
        return None
    if tx.get("order_created"):
        return tx.get("order_id")

    res = await db.payment_transactions.update_one(
        {"session_id": session_id, "order_created": {"$ne": True}},
        {"$set": {"payment_status": "paid", "status": "completed",
                  "order_created": True, "updated_at": now_iso()}},
    )
    if res.modified_count == 0:
        tx = await db.payment_transactions.find_one({"session_id": session_id}, NO_ID)
        return tx.get("order_id") if tx else None

    order_id = str(uuid.uuid4())
    order = {
        "id": order_id,
        "user_id": tx["user_id"],
        "items": tx.get("items", []),
        "subtotal": tx.get("subtotal", 0),
        "discount": tx.get("discount", 0),
        "shipping": tx.get("shipping", 0),
        "total": tx.get("amount", 0),
        "coupon_code": tx.get("coupon_code"),
        "shipping_address": tx.get("shipping_address"),
        "status": "paid",
        "session_id": session_id,
        "created_at": now_iso(),
    }
    await db.orders.insert_one(order)
    await db.payment_transactions.update_one({"session_id": session_id}, {"$set": {"order_id": order_id}})
    await db.carts.update_one({"user_id": tx["user_id"]}, {"$set": {"items": [], "updated_at": now_iso()}})

    try:
        await create_notification(tx["user_id"], "Order confirmed",
                                  f"Your order #{order_id[:8]} is confirmed and on its way.",
                                  "success", "/orders")
    except Exception:
        pass
    try:
        addr = tx.get("shipping_address") or {}
        if addr.get("email"):
            await send_email(addr["email"], "Your LCs The Fury Zone order", order_confirmation_html(order))
    except Exception:
        pass
    return order_id


@router.get("/checkout/status/{session_id}")
async def checkout_status(session_id: str):
    tx = await db.payment_transactions.find_one({"session_id": session_id}, NO_ID)
    if not tx:
        raise HTTPException(status_code=404, detail="Transaction not found")
    if tx.get("payment_status") != "paid" and stripe and stripe.api_key:
        try:
            s = stripe.checkout.Session.retrieve(session_id)
            if s.payment_status == "paid" or s.status == "complete":
                await _mark_paid_and_create_order(session_id)
                tx = await db.payment_transactions.find_one({"session_id": session_id}, NO_ID)
        except Exception:
            pass
    return {
        "session_id": session_id,
        "status": tx.get("status", "initiated"),
        "payment_status": tx.get("payment_status", "pending"),
        "order_id": tx.get("order_id"),
    }


@router.post("/stripe/webhook")
async def stripe_webhook(request: Request):
    if not stripe:
        raise HTTPException(status_code=503, detail="Stripe dependency is not installed")
    payload = await request.body()
    signature = request.headers.get("stripe-signature", "")
    webhook_secret = os.environ.get("STRIPE_WEBHOOK_SECRET", "")
    try:
        event = stripe.Webhook.construct_event(payload, signature, webhook_secret)
    except Exception as exc:
        raise HTTPException(status_code=400, detail="Invalid Stripe webhook") from exc

    obj = event["data"]["object"]
    etype = event["type"]
    if etype == "checkout.session.completed":
        await _mark_paid_and_create_order(obj["id"])
    elif etype == "checkout.session.async_payment_succeeded":
        await _mark_paid_and_create_order(obj["id"])
    elif etype == "checkout.session.expired":
        await db.payment_transactions.update_one(
            {"session_id": obj["id"], "payment_status": {"$ne": "paid"}},
            {"$set": {"status": "expired", "payment_status": "expired", "updated_at": now_iso()}},
        )
    return {"received": True}
