nano requirements.txtimport os
import uuid
from fastapi import APIRouter, HTTPException, Depends, Request
from pydantic import BaseModel
from typing import Optional

# REPLACE YOUR STRIPE IMPORT WITH YOUR NEW PAYPAL SERVICE
from emergentintegrations.payments.paypal.checkout import PayPalCheckout

from database import db, now_iso, NO_ID
from auth import get_current_user
from notify import create_notification, log_event
from emailer import send_email, order_confirmation_html
<<<<<<< HEAD

router = APIRouter(prefix="/api", tags=["shop"])
COMMISSION = float(os.environ.get("PLATFORM_COMMISSION_RATE", "0.10"))

# ---------------- Cart & Utils (Kept the same) ----------------
# [Keep all your existing get_or_create_cart, cart routes, wishlist, etc., here]
=======
s
>>>>>>> 8f1abd3 (Manual backup before codespace deletion)

# ---------------- Checkout & Payments (Updated) ----------------
class CheckoutRequest(BaseModel):
    origin_url: str
    coupon_code: Optional[str] = None
    address_id: Optional[str] = None

def paypal_client() -> PayPalCheckout:
    return PayPalCheckout(
        client_id=os.environ["PAYPAL_CLIENT_ID"],
        secret=os.environ["PAYPAL_SECRET"]
    )

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

    # Initialize PayPal checkout
    paypal = paypal_client()
    order_data = await paypal.create_order(amount=float(total), currency="USD")
    order_id = order_data["id"]

    await db.payment_transactions.insert_one({
        "id": str(uuid.uuid4()),
        "session_id": order_id,
        "user_id": user["id"],
        "amount": float(total),
        "payment_status": "initiated",
        "order_created": False,
        "created_at": now_iso(),
    })
    
    # Return approval link to frontend
    approval_url = next(link["href"] for link in order_data["links"] if link["rel"] == "approve")
    return {"url": approval_url, "session_id": order_id}

# [Keep your existing _fulfill_order function, but update webhook logic below]

@router.post("/webhook/paypal")
async def paypal_webhook(request: Request):
    payload = await request.json()
    # Verify event type (e.g., 'CHECKOUT.ORDER.APPROVED')
    if payload.get("event_type") == "CHECKOUT.ORDER.APPROVED":
        order_id = payload["resource"]["id"]
        txn = await db.payment_transactions.find_one({"session_id": order_id}, NO_ID)
        if txn and not txn.get("order_created"):
            await db.payment_transactions.update_one(
                {"session_id": order_id}, {"$set": {"payment_status": "paid"}}
            )
            txn = await db.payment_transactions.find_one({"session_id": order_id}, NO_ID)
            await _fulfill_order(txn)
<<<<<<< HEAD
    return {"received": True}
=======
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
stripe>=10.0.0
>>>>>>> 8f1abd3 (Manual backup before codespace deletion)
