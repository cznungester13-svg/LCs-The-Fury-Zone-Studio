import os
import uuid
from fastapi import APIRouter, HTTPException, Depends, Request
from pydantic import BaseModel, Field
from typing import List, Optional

from emergentintegrations.payments.stripe.checkout import (
    StripeCheckout, CheckoutSessionRequest, CheckoutStatusResponse,
)

from database import db, now_iso, NO_ID
from auth import get_current_user
from notify import create_notification, log_event
from emailer import send_email, order_confirmation_html

router = APIRouter(prefix="/api", tags=["shop"])

COMMISSION = float(os.environ.get("PLATFORM_COMMISSION_RATE", "0.10"))


# ---------------- Cart ----------------
class CartItemIn(BaseModel):
    item_type: str  # product | listing
    item_id: str
    quantity: int = 1
    variant_id: Optional[str] = None


async def get_or_create_cart(user_id: str) -> dict:
    cart = await db.carts.find_one({"user_id": user_id}, NO_ID)
    if not cart:
        cart = {"id": str(uuid.uuid4()), "user_id": user_id, "items": [], "created_at": now_iso()}
        await db.carts.insert_one(cart)
        cart.pop("_id", None)
    return cart


@router.get("/cart")
async def view_cart(user: dict = Depends(get_current_user)):
    cart = await get_or_create_cart(user["id"])
    total = sum(i["price"] * i["quantity"] for i in cart["items"])
    cart["subtotal"] = round(total, 2)
    return cart


@router.post("/cart/add")
async def add_to_cart(body: CartItemIn, user: dict = Depends(get_current_user)):
    if body.item_type == "product":
        src = await db.products.find_one({"id": body.item_id}, NO_ID)
    else:
        src = await db.resale_listings.find_one({"id": body.item_id, "status": "active"}, NO_ID)
    if not src:
        raise HTTPException(status_code=404, detail="Item not available")
    price = src["price"]
    seller_id = src.get("seller_id")
    if body.variant_id and body.item_type == "product":
        for v in src.get("variants", []):
            if v["id"] == body.variant_id:
                price = v["price"]
    cart = await get_or_create_cart(user["id"])
    items = cart["items"]
    existing = next((i for i in items if i["item_id"] == body.item_id and i.get("variant_id") == body.variant_id), None)
    if existing:
        if body.item_type == "listing":
            raise HTTPException(status_code=400, detail="Item already in cart")
        existing["quantity"] += body.quantity
    else:
        items.append({
            "item_type": body.item_type,
            "item_id": body.item_id,
            "variant_id": body.variant_id,
            "title": src["title"],
            "price": price,
            "image": (src.get("images") or [None])[0],
            "seller_id": seller_id,
            "quantity": 1 if body.item_type == "listing" else body.quantity,
        })
    await db.carts.update_one({"user_id": user["id"]}, {"$set": {"items": items}})
    return await view_cart(user)


@router.post("/cart/update")
async def update_cart_item(body: CartItemIn, user: dict = Depends(get_current_user)):
    cart = await get_or_create_cart(user["id"])
    items = cart["items"]
    for i in items:
        if i["item_id"] == body.item_id and i.get("variant_id") == body.variant_id:
            # Fix: Ensure quantities on resale listings never overflow beyond 1
            if i["item_type"] == "listing":
                i["quantity"] = 1
            else:
                i["quantity"] = max(1, body.quantity)
    await db.carts.update_one({"user_id": user["id"]}, {"$set": {"items": items}})
    return await view_cart(user)


@router.delete("/cart/item/{item_id}")
async def remove_cart_item(item_id: str, user: dict = Depends(get_current_user)):
    cart = await get_or_create_cart(user["id"])
    items = [i for i in cart["items"] if i["item_id"] != item_id]
    await db.carts.update_one({"user_id": user["id"]}, {"$set": {"items": items}})
    return await view_cart(user)


@router.delete("/cart")
async def clear_cart(user: dict = Depends(get_current_user)):
    await db.carts.update_one({"user_id": user["id"]}, {"$set": {"items": []}})
    return {"ok": True}


# ---------------- Wishlist ----------------
@router.get("/wishlist")
async def get_wishlist(user: dict = Depends(get_current_user)):
    items = await db.wishlists.find({"user_id": user["id"]}, NO_ID).sort("created_at", -1).to_list(500)
    return items


@router.post("/wishlist/toggle")
async def toggle_wishlist(body: CartItemIn, user: dict = Depends(get_current_user)):
    existing = await db.wishlists.find_one({"user_id": user["id"], "item_id": body.item_id}, NO_ID)
    if existing:
        await db.wishlists.delete_one({"user_id": user["id"], "item_id": body.item_id})
        return {"wishlisted": False}
    if body.item_type == "product":
        src = await db.products.find_one({"id": body.item_id}, NO_ID)
    else:
        src = await db.resale_listings.find_one({"id": body.item_id}, NO_ID)
    if not src:
        raise HTTPException(status_code=404, detail="Item not found")
    await db.wishlists.insert_one({
        "id": str(uuid.uuid4()),
        "user_id": user["id"],
        "item_id": body.item_id,
        "item_type": body.item_type,
        "title": src["title"],
        "price": src["price"],
        "image": (src.get("images") or [None])[0],
        "created_at": now_iso(),
    })
    return {"wishlisted": True}


# ---------------- Coupons ----------------
class CouponValidate(BaseModel):
    code: str


@router.post("/coupons/validate")
async def validate_coupon(body: CouponValidate):
    c = await db.coupons.find_one({"code": body.code.upper(), "active": True}, NO_ID)
    if not c:
        raise HTTPException(status_code=404, detail="Invalid coupon code")
    return {"code": c["code"], "percent_off": c.get("percent_off", 0), "description": c.get("description", "")}


# ---------------- Addresses ----------------
class AddressIn(BaseModel):
    label: str = "Home"
    full_name: str
    line1: str
    city: str
    state: str = ""
    postal_code: str
    country: str = "USA"
    phone: str = ""


@router.get("/addresses")
async def list_addresses(user: dict = Depends(get_current_user)):
    return await db.user_addresses.find({"user_id": user["id"]}, NO_ID).to_list(50)


@router.post("/addresses")
async def add_address(body: AddressIn, user: dict = Depends(get_current_user)):
    doc = body.model_dump()
    doc.update({"id": str(uuid.uuid4()), "user_id": user["id"], "created_at": now_iso()})
    await db.user_addresses.insert_one(doc)
    return {k: v for k, v in doc.items() if k != "_id"}


# ---------------- Checkout & Payments ----------------
class CheckoutRequest(BaseModel):
    origin_url: str
    coupon_code: Optional[str] = None
    address_id: Optional[str] = None


def stripe_client(request: Request) -> StripeCheckout:
    host_url = str(request.base_url)
    webhook_url = f"{host_url}api/webhook/stripe"
    return StripeCheckout(api_key=os.environ["STRIPE_API_KEY"], webhook_url=webhook_url)


@router.post("/checkout/session")
async def create_checkout(body: CheckoutRequest, request: Request, user: dict = Depends(get_current_user)):
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

    success_url = f"{body.origin_url}/checkout/success?session_id={{CHECKOUT_SESSION_ID}}"
    cancel_url = f"{body.origin_url}/cart"
    checkout = stripe_client(request)
    session = await checkout.create_checkout_session(CheckoutSessionRequest(
        amount=float(total), currency="usd",
        success_url=success_url, cancel_url=cancel_url,
        metadata={"user_id": user["id"], "type": "cart_checkout"},
    ))

    await db.payment_transactions.insert_one({
        "id": str(uuid.uuid4()),
        "session_id": session.session_id,
        "user_id": user["id"],
        "amount": float(total),
        "currency": "usd",
        "items": cart["items"],
        "subtotal": subtotal,
        "discount": discount,
        "coupon_code": coupon_code,
        "address_id": body.address_id,
        "payment_status": "initiated",
        "order_created": False,
        "metadata": {"user_id": user["id"]},
        "created_at": now_iso(),
    })
    return {{"url": session.url, "session_id": session.session_id}}


@router.get("/checkout/status/{session_id}")
async def checkout_status(session_id: str, request: Request, user: dict = Depends(get_current_user)):
    txn = await db.payment_transactions.find_one({{"session_id": session_id}}, NO_ID)
    if not txn:
        raise HTTPException(status_code=404, detail="Transaction not found")
    checkout = stripe_client(request)
    status: CheckoutStatusResponse = await checkout.get_checkout_status(session_id)
    
    if txn["payment_status"] != "paid":
        # Run atomic updates on transaction document state
        await db.payment_transactions.update_one(
            {{"session_id": session_id}},
            {"$set": {{"payment_status": status.payment_status, "status": status.status}}},
        )
        # Fix: Fetch a fresh, hot-off-the-press state dictionary before checking order limits
        txn = await db.payment_transactions.find_one({{"session_id": session_id}}, NO_ID)
        
        if status.payment_status == "paid" and not txn.get("order_created"):
            order = await _fulfill_order(txn)
            return {{"payment_status": "paid", "status": status.status, "order_id": order["id"]}}
            
    existing_order = await db.orders.find_one({{"session_id": session_id}}, NO_ID)
    return {{"payment_status": status.payment_status, "status": status.status,
            "order_id": existing_order["id"] if existing_order else None}}


async def _fulfill_order(txn: dict) -> dict:
    # idempotency guard
    res = await db.payment_transactions.update_one(
        {{"session_id": txn["session_id"], "order_created": {"$ne": True}}},
        {"$set": {{"order_created": True}}},
    )
    if res.modified_count == 0:
        return await db.orders.find_one({{"session_id": txn["session_id"]}}, NO_ID)

    order_id = str(uuid.uuid4())
    now = now_iso()
    order = {
        "id": order_id,
        "user_id": txn["user_id"],
        "session_id": txn["session_id"],
        "items": txn["items"],
        "subtotal": txn.get("subtotal", txn["amount"]),
        "discount": txn.get("discount", 0),
        "total": txn["amount"],
        "coupon_code": txn.get("coupon_code"),
        "address_id": txn.get("address_id"),
        "status": "paid",
        "status_history": [
            {{"status": "pending", "at": now}},
            {{"status": "paid", "at": now}},
        ],
        "created_at": now,
    }
    await db.orders.insert_one(order)

    # inventory + listing + seller balances
    for it in txn["items"]:
        if it["item_type"] == "product":
            await db.inventory.update_one({{"product_id": it["item_id"]}},
                                          {"$inc": {{"stock": -it["quantity"]}}})
            await db.products.update_one({{"id": it["item_id"]}},
                                         {"$inc": {{"stock": -it["quantity"]}}})
        elif it["item_type"] == "listing":
            await db.resale_listings.update_one({{"id": it["item_id"]}}, {"$set": {{"status": "sold"}}})
            seller_id = it.get("seller_id")
            if seller_id:
                gross = it["price"] * it["quantity"]
                commission = round(gross * COMMISSION, 2)
                net = round(gross - commission, 2)
                await db.seller_balances.update_one(
                    {{"user_id": seller_id}},
                    {"$inc": {{"pending": net, "total_earned": net}}, "$set": {{"updated_at": now}}},
                )
                await db.commissions.insert_one({
                    "id": str(uuid.uuid4()), "order_id": order_id, "seller_id": seller_id,
                    "gross": gross, "commission": commission, "net": net, "created_at": now,
                })
                await create_notification(seller_id, "Item sold!",
                                          f"Your '{it['title']}' sold for ${gross:.2f}. ${net:.2f} added to pending balance.",
                                          "success")

    await db.carts.update_one({{"user_id": txn["user_id"]}}, {"$set": {{"items": []}}})
    await create_notification(txn["user_id"], "Order confirmed",
                              f"Order #{order_id[:8]} confirmed. Total ${txn['amount']:.2f}.",
                              "success", f"/orders")
    await log_event("order_paid", txn["user_id"], {{"order_id": order_id, "total": txn["amount"]}})
    buyer = await db.users.find_one({{"id": txn["user_id"]}}, NO_ID)
    if buyer:
        await send_email(buyer["email"], "Your LCs Fury Zone order is confirmed",
                         order_confirmation_html(order))
    return order


@router.post("/webhook/stripe")
async def stripe_webhook(request: Request):
    body = await request.body()
    sig = request.headers.get("Stripe-Signature")
    checkout = stripe_client(request)
    try:
        event = await checkout.handle_webhook(body, sig)
    except Exception:
        return {{"received": True}}
    if event.payment_status == "paid":
        txn = await db.payment_transactions.find_one({{"session_id": event.session_id}}, NO_ID)
        if txn and not txn.get("order_created"):
            await db.payment_transactions.update_one(
                {{"session_id": event.session_id}},
                {"$set": {{"payment_status": "paid"}}},
            )
            # Fetch a fresh document dictionary here as well to protect webhook tasks
            txn = await db.payment_transactions.find_one({{"session_id": event.session_id}}, NO_ID)
            await _fulfill_order(txn)
    return {{"received": True}}


# ---------------- Orders ----------------
@router.get("/orders")
async def my_orders(user: dict = Depends(get_current_user)):
    return await db.orders.find({{"user_id": user["id"]}}, NO_ID).sort("created_at", -1).to_list(200)


@router.get("/orders/{order_id}")
async def get_order(order_id: str, user: dict = Depends(get_current_user)):
    o = await db.orders.find_one({{"id": order_id}}, NO_ID)
    if not o:
        raise HTTPException(status_code=404, detail="Order not found")
    if o["user_id"] != user["id"] and "admin" not in user.get("roles", []):
        raise HTTPException(status_code=403, detail="Forbidden")
    return o
