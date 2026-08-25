from dotenv import load_dotenv
from pathlib import Path
import os

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

import logging
import uuid
import math
import asyncio
import random as _random
from datetime import datetime, timezone, timedelta
from typing import List, Optional, Set

import bcrypt
import jwt
import stripe
import requests
from bson import ObjectId
from fastapi import (FastAPI, APIRouter, HTTPException, Request, Response, Depends,
                     UploadFile, File, Form, WebSocket, WebSocketDisconnect)
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
from pydantic import BaseModel, EmailStr, Field

from seed_data import generate_products, department_meta, DEPARTMENTS

# ---------------------------------------------------------------- DB
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

JWT_SECRET = os.environ['JWT_SECRET']
JWT_ALGORITHM = "HS256"

stripe.api_key = os.environ.get("STRIPE_SECRET_KEY") or "sk_test_emergent"
STRIPE_WEBHOOK_SECRET = os.environ.get("STRIPE_WEBHOOK_SECRET", "")

# object storage
STORAGE_BASE = (os.environ.get("INTEGRATION_PROXY_URL") or "").strip() or "https://integrations.emergentagent.com"
STORAGE_URL = STORAGE_BASE.rstrip("/") + "/objstore/api/v1/storage"
EMERGENT_KEY = os.environ.get("EMERGENT_LLM_KEY")
APP_NAME = "lc-fury-marketplace"
_storage_key = None

DEPT_NAMES = {d["slug"]: d["name"] for d in DEPARTMENTS}
RAFFLE_PRIZE = "$25 Store Credit"
TICKET_PER = 20.0

app = FastAPI(title="LC Multi-Dept Resale Marketplace")
api = APIRouter(prefix="/api")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("marketplace")


# ---------------------------------------------------------------- Storage helpers
def init_storage(force: bool = False):
    global _storage_key
    if _storage_key and not force:
        return _storage_key
    resp = requests.post(f"{STORAGE_URL}/init", json={"emergent_key": EMERGENT_KEY}, timeout=30)
    resp.raise_for_status()
    _storage_key = resp.json()["storage_key"]
    return _storage_key


def put_object(path: str, data: bytes, content_type: str) -> dict:
    key = init_storage()
    resp = requests.put(f"{STORAGE_URL}/objects/{path}",
                        headers={"X-Storage-Key": key, "Content-Type": content_type},
                        data=data, timeout=120)
    if resp.status_code == 404:
        key = init_storage(force=True)
        resp = requests.put(f"{STORAGE_URL}/objects/{path}",
                            headers={"X-Storage-Key": key, "Content-Type": content_type},
                            data=data, timeout=120)
    resp.raise_for_status()
    return resp.json()


def get_object(path: str):
    key = init_storage()
    resp = requests.get(f"{STORAGE_URL}/objects/{path}", headers={"X-Storage-Key": key}, timeout=60)
    if resp.status_code == 404:
        key = init_storage(force=True)
        resp = requests.get(f"{STORAGE_URL}/objects/{path}", headers={"X-Storage-Key": key}, timeout=60)
    resp.raise_for_status()
    return resp.content, resp.headers.get("Content-Type", "application/octet-stream")


# ---------------------------------------------------------------- Auth helpers
def hash_password(p: str) -> str:
    return bcrypt.hashpw(p.encode(), bcrypt.gensalt()).decode()


def verify_password(p: str, h: str) -> bool:
    return bcrypt.checkpw(p.encode(), h.encode())


def create_access_token(uid: str, email: str) -> str:
    return jwt.encode({"sub": uid, "email": email, "type": "access",
                       "exp": datetime.now(timezone.utc) + timedelta(hours=12)},
                      JWT_SECRET, algorithm=JWT_ALGORITHM)


def create_refresh_token(uid: str) -> str:
    return jwt.encode({"sub": uid, "type": "refresh",
                       "exp": datetime.now(timezone.utc) + timedelta(days=7)},
                      JWT_SECRET, algorithm=JWT_ALGORITHM)


def set_auth_cookies(response: Response, access: str, refresh: str):
    response.set_cookie("access_token", access, httponly=True, secure=True, samesite="none", max_age=43200, path="/")
    response.set_cookie("refresh_token", refresh, httponly=True, secure=True, samesite="none", max_age=604800, path="/")


def public_user(u: dict) -> dict:
    return {"id": str(u["_id"]), "email": u["email"], "name": u.get("name", ""),
            "role": u.get("role", "user"), "total_spent": round(u.get("total_spent", 0.0), 2)}


async def get_current_user(request: Request) -> dict:
    token = request.cookies.get("access_token")
    if not token:
        auth = request.headers.get("Authorization", "")
        if auth.startswith("Bearer "):
            token = auth[7:]
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        if payload.get("type") != "access":
            raise HTTPException(status_code=401, detail="Invalid token type")
        user = await db.users.find_one({"_id": ObjectId(payload["sub"])})
        if not user:
            raise HTTPException(status_code=401, detail="User not found")
        return user
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")


# ---------------------------------------------------------------- Models
class RegisterBody(BaseModel):
    name: str = Field(min_length=1, max_length=80)
    email: EmailStr
    password: str = Field(min_length=6, max_length=128)


class LoginBody(BaseModel):
    email: EmailStr
    password: str


class CartItemBody(BaseModel):
    product_id: str
    quantity: int = Field(default=1, ge=1, le=99)


class ShippingBody(BaseModel):
    full_name: str = Field(min_length=1)
    address: str = Field(min_length=1)
    city: str = Field(min_length=1)


class CheckoutBody(BaseModel):
    origin_url: str
    shipping: ShippingBody


class ListingBody(BaseModel):
    name: str = Field(min_length=2, max_length=120)
    department: str
    price: float = Field(gt=0, le=999)
    condition: str = Field(min_length=1)
    description: str = Field(min_length=1, max_length=1000)
    image: str = Field(min_length=1)
    stock: int = Field(default=1, ge=1, le=999)


# ---------------------------------------------------------------- Auth routes
@api.post("/auth/register")
async def register(body: RegisterBody, response: Response):
    email = body.email.lower()
    if await db.users.find_one({"email": email}):
        raise HTTPException(status_code=400, detail="Email already registered")
    doc = {"email": email, "name": body.name, "password_hash": hash_password(body.password),
           "role": "user", "total_spent": 0.0, "created_at": datetime.now(timezone.utc).isoformat()}
    res = await db.users.insert_one(doc)
    uid = str(res.inserted_id)
    set_auth_cookies(response, create_access_token(uid, email), create_refresh_token(uid))
    doc["_id"] = res.inserted_id
    return public_user(doc)


@api.post("/auth/login")
async def login(body: LoginBody, request: Request, response: Response):
    email = body.email.lower()
    ip = request.client.host if request.client else "unknown"
    identifier = f"{ip}:{email}"
    rec = await db.login_attempts.find_one({"identifier": identifier})
    now = datetime.now(timezone.utc)
    if rec and rec.get("locked_until") and datetime.fromisoformat(rec["locked_until"]) > now:
        raise HTTPException(status_code=429, detail="Too many failed attempts. Try again later.")
    user = await db.users.find_one({"email": email})
    if not user or not verify_password(body.password, user["password_hash"]):
        attempts = (rec.get("count", 0) if rec else 0) + 1
        update = {"identifier": identifier, "count": attempts}
        if attempts >= 5:
            update["locked_until"] = (now + timedelta(minutes=15)).isoformat()
        await db.login_attempts.update_one({"identifier": identifier}, {"$set": update}, upsert=True)
        raise HTTPException(status_code=401, detail="Invalid email or password")
    await db.login_attempts.delete_one({"identifier": identifier})
    uid = str(user["_id"])
    set_auth_cookies(response, create_access_token(uid, email), create_refresh_token(uid))
    return public_user(user)


@api.post("/auth/logout")
async def logout(response: Response):
    response.delete_cookie("access_token", path="/")
    response.delete_cookie("refresh_token", path="/")
    return {"message": "Logged out"}


@api.get("/auth/me")
async def me(user: dict = Depends(get_current_user)):
    return public_user(user)


@api.post("/auth/refresh")
async def refresh(request: Request, response: Response):
    token = request.cookies.get("refresh_token")
    if not token:
        raise HTTPException(status_code=401, detail="No refresh token")
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        if payload.get("type") != "refresh":
            raise HTTPException(status_code=401, detail="Invalid token type")
        user = await db.users.find_one({"_id": ObjectId(payload["sub"])})
        if not user:
            raise HTTPException(status_code=401, detail="User not found")
        response.set_cookie("access_token", create_access_token(str(user["_id"]), user["email"]),
                            httponly=True, secure=True, samesite="none", max_age=43200, path="/")
        return public_user(user)
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid refresh token")


# ---------------------------------------------------------------- Catalog routes
@api.get("/departments")
async def get_departments():
    metas = department_meta()
    for m in metas:
        m["count"] = await db.products.count_documents({"department": m["slug"]})
    return metas


@api.get("/products")
async def get_products(department: Optional[str] = None, search: Optional[str] = None,
                       sort: str = "featured", page: int = 1, limit: int = 24):
    query = {}
    if department:
        query["department"] = department
    if search:
        query["name"] = {"$regex": search, "$options": "i"}
    sort_map = {"price_asc": ("price", 1), "price_desc": ("price", -1),
                "rating": ("rating", -1), "newest": ("created_at", -1), "featured": ("sku", 1)}
    field, direction = sort_map.get(sort, ("sku", 1))
    total = await db.products.count_documents(query)
    skip = max(0, (page - 1) * limit)
    # sold-out items sink to the bottom
    cursor = db.products.find(query, {"_id": 0}).sort([("stock", -1), (field, direction)]).skip(skip).limit(limit)
    items = await cursor.to_list(limit)
    return {"items": items, "total": total, "page": page, "limit": limit,
            "pages": (total + limit - 1) // limit}


@api.get("/products/deals")
async def get_deals():
    return await db.products.find({"stock": {"$gt": 0}}, {"_id": 0}).sort("price", 1).limit(8).to_list(8)


@api.get("/products/new")
async def get_new_arrivals():
    return await db.products.find({}, {"_id": 0}).sort("created_at", -1).limit(8).to_list(8)


@api.post("/products")
async def create_listing(body: ListingBody, user: dict = Depends(get_current_user)):
    if body.department not in DEPT_NAMES:
        raise HTTPException(status_code=400, detail="Invalid department")
    doc = {
        "id": str(uuid.uuid4()),
        "name": body.name,
        "department": body.department,
        "department_name": DEPT_NAMES[body.department],
        "category": body.name,
        "condition": body.condition,
        "price": round(body.price, 2),
        "original_price": round(body.price * 2.2, 2),
        "image": body.image,
        "sku": f"USR-{uuid.uuid4().hex[:6].upper()}",
        "description": body.description,
        "stock": body.stock,
        "rating": 5.0,
        "seller_id": str(user["_id"]),
        "seller_name": user.get("name", "Seller"),
        "is_user_listed": True,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    await db.products.insert_one(doc)
    doc.pop("_id", None)
    return doc


@api.get("/products/mine")
async def my_listings(user: dict = Depends(get_current_user)):
    return await db.products.find({"seller_id": str(user["_id"])}, {"_id": 0}).sort("created_at", -1).to_list(200)


@api.get("/products/{product_id}")
async def get_product(product_id: str):
    p = await db.products.find_one({"id": product_id}, {"_id": 0})
    if not p:
        raise HTTPException(status_code=404, detail="Product not found")
    related = await db.products.find(
        {"department": p["department"], "id": {"$ne": product_id}}, {"_id": 0}).limit(4).to_list(4)
    return {"product": p, "related": related}


# ---------------------------------------------------------------- Uploads
@api.post("/upload")
async def upload(file: UploadFile = File(...), user: dict = Depends(get_current_user)):
    ext = file.filename.split(".")[-1].lower() if "." in file.filename else "bin"
    if ext not in ("jpg", "jpeg", "png", "webp", "gif"):
        raise HTTPException(status_code=400, detail="Only image files are allowed")
    data = await file.read()
    if len(data) > 8 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="Image too large (max 8MB)")
    path = f"{APP_NAME}/uploads/{str(user['_id'])}/{uuid.uuid4()}.{ext}"
    result = put_object(path, data, file.content_type or "image/jpeg")
    await db.files.insert_one({"id": str(uuid.uuid4()), "storage_path": result["path"],
                               "content_type": file.content_type or "image/jpeg",
                               "is_deleted": False, "created_at": datetime.now(timezone.utc).isoformat()})
    return {"url": f"/api/files/{result['path']}"}


@api.get("/files/{path:path}")
async def serve_file(path: str):
    rec = await db.files.find_one({"storage_path": path, "is_deleted": False})
    if not rec:
        raise HTTPException(status_code=404, detail="File not found")
    data, ctype = get_object(path)
    return Response(content=data, media_type=rec.get("content_type", ctype))


# ---------------------------------------------------------------- Cart
async def _cart_with_products(uid: str):
    cart = await db.carts.find_one({"user_id": uid})
    if not cart:
        return {"items": [], "total": 0.0}
    detailed, total = [], 0.0
    for it in cart.get("items", []):
        p = await db.products.find_one({"id": it["product_id"]}, {"_id": 0})
        if not p:
            continue
        line = round(p["price"] * it["quantity"], 2)
        total += line
        detailed.append({"product": p, "quantity": it["quantity"], "line_total": line})
    return {"items": detailed, "total": round(total, 2)}


@api.get("/cart")
async def get_cart(user: dict = Depends(get_current_user)):
    return await _cart_with_products(str(user["_id"]))


@api.post("/cart")
async def add_to_cart(body: CartItemBody, user: dict = Depends(get_current_user)):
    uid = str(user["_id"])
    p = await db.products.find_one({"id": body.product_id})
    if not p:
        raise HTTPException(status_code=404, detail="Product not found")
    if p.get("stock", 0) <= 0:
        raise HTTPException(status_code=400, detail="This item is sold out")
    cart = await db.carts.find_one({"user_id": uid})
    if not cart:
        await db.carts.insert_one({"user_id": uid, "items": [{"product_id": body.product_id, "quantity": body.quantity}]})
    else:
        items = cart["items"]
        for it in items:
            if it["product_id"] == body.product_id:
                it["quantity"] += body.quantity
                break
        else:
            items.append({"product_id": body.product_id, "quantity": body.quantity})
        await db.carts.update_one({"user_id": uid}, {"$set": {"items": items}})
    return await _cart_with_products(uid)


@api.put("/cart")
async def update_cart(body: CartItemBody, user: dict = Depends(get_current_user)):
    uid = str(user["_id"])
    cart = await db.carts.find_one({"user_id": uid})
    if not cart:
        raise HTTPException(status_code=404, detail="Cart empty")
    items = cart["items"]
    for it in items:
        if it["product_id"] == body.product_id:
            it["quantity"] = body.quantity
            break
    else:
        items.append({"product_id": body.product_id, "quantity": body.quantity})
    items = [it for it in items if it["quantity"] > 0]
    await db.carts.update_one({"user_id": uid}, {"$set": {"items": items}})
    return await _cart_with_products(uid)


@api.delete("/cart/{product_id}")
async def remove_from_cart(product_id: str, user: dict = Depends(get_current_user)):
    uid = str(user["_id"])
    cart = await db.carts.find_one({"user_id": uid})
    if cart:
        items = [it for it in cart["items"] if it["product_id"] != product_id]
        await db.carts.update_one({"user_id": uid}, {"$set": {"items": items}})
    return await _cart_with_products(uid)


# ---------------------------------------------------------------- Payments (Stripe)
@api.post("/payments/checkout")
async def create_checkout(body: CheckoutBody, user: dict = Depends(get_current_user)):
    uid = str(user["_id"])
    cart = await _cart_with_products(uid)
    if not cart["items"]:
        raise HTTPException(status_code=400, detail="Cart is empty")
    line_items, snapshot = [], []
    for it in cart["items"]:
        p = it["product"]
        if p.get("stock", 0) < it["quantity"]:
            raise HTTPException(status_code=400, detail=f"Not enough stock for {p['name']}")
        pd = {"name": p["name"][:120]}
        if isinstance(p.get("image"), str) and p["image"].startswith("http"):
            pd["images"] = [p["image"]]
        line_items.append({"price_data": {"currency": "usd", "unit_amount": int(round(p["price"] * 100)),
                                           "product_data": pd}, "quantity": it["quantity"]})
        snapshot.append({"product_id": p["id"], "name": p["name"], "image": p["image"],
                         "price": p["price"], "quantity": it["quantity"], "line_total": it["line_total"]})
    origin = body.origin_url.rstrip("/")
    session = stripe.checkout.Session.create(
        line_items=line_items,
        mode="payment",
        success_url=f"{origin}/payment/success?session_id={{CHECKOUT_SESSION_ID}}",
        cancel_url=f"{origin}/payment/cancel",
        metadata={"user_id": uid},
    )
    await db.payment_transactions.insert_one({
        "session_id": session.id, "user_id": uid, "amount": cart["total"], "currency": "usd",
        "status": "initiated", "payment_status": "pending", "fulfilled": False,
        "items": snapshot, "shipping": body.shipping.model_dump(),
        "created_at": datetime.now(timezone.utc).isoformat(),
        "updated_at": datetime.now(timezone.utc).isoformat(),
    })
    return {"checkout_url": session.url, "session_id": session.id}


async def _finalize(session_id: str):
    """Idempotently turn a paid transaction into an order (+ stock, raffle)."""
    txn = await db.payment_transactions.find_one_and_update(
        {"session_id": session_id, "fulfilled": {"$ne": True}},
        {"$set": {"fulfilled": True}})
    if not txn:
        return
    uid = txn["user_id"]
    order = {"id": str(uuid.uuid4()), "user_id": uid, "items": txn["items"], "total": txn["amount"],
             "shipping": txn["shipping"], "status": "confirmed", "payment": "stripe",
             "session_id": session_id, "created_at": datetime.now(timezone.utc).isoformat()}
    await db.orders.insert_one(order)
    for it in txn["items"]:
        await db.products.update_one({"id": it["product_id"]}, {"$inc": {"stock": -it["quantity"]}})
    await db.products.update_many({"stock": {"$lt": 0}}, {"$set": {"stock": 0}})
    await db.carts.update_one({"user_id": uid}, {"$set": {"items": []}})
    await db.users.update_one({"_id": ObjectId(uid)}, {"$inc": {"total_spent": txn["amount"]}})
    await _award_raffle_tickets(uid, txn["amount"])


@api.get("/payments/status/{session_id}")
async def payment_status(session_id: str):
    rec = await db.payment_transactions.find_one({"session_id": session_id})
    if not rec:
        raise HTTPException(status_code=404, detail="Transaction not found")
    if rec.get("payment_status") != "paid":
        try:
            s = stripe.checkout.Session.retrieve(session_id)
            if s.payment_status == "paid" or s.status == "complete":
                await db.payment_transactions.update_one(
                    {"session_id": session_id, "payment_status": {"$ne": "paid"}},
                    {"$set": {"status": "completed", "payment_status": "paid",
                              "updated_at": datetime.now(timezone.utc).isoformat()}})
                await _finalize(session_id)
                rec = await db.payment_transactions.find_one({"session_id": session_id})
        except stripe.error.StripeError:
            pass
    return {"session_id": rec["session_id"], "status": rec["status"], "payment_status": rec["payment_status"]}


@api.post("/stripe/webhook")
async def stripe_webhook(request: Request):
    payload = await request.body()
    sig = request.headers.get("stripe-signature", "")
    try:
        event = stripe.Webhook.construct_event(payload, sig, STRIPE_WEBHOOK_SECRET)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid signature")
    obj, t = event["data"]["object"], event["type"]
    if t == "checkout.session.completed":
        await db.payment_transactions.update_one(
            {"session_id": obj["id"], "payment_status": {"$ne": "paid"}},
            {"$set": {"status": "completed", "payment_status": obj.get("payment_status", "paid"),
                      "updated_at": datetime.now(timezone.utc).isoformat()}})
        await _finalize(obj["id"])
    return {"status": "ok"}


@api.get("/orders")
async def list_orders(user: dict = Depends(get_current_user)):
    return await db.orders.find({"user_id": str(user["_id"])}, {"_id": 0}).sort("created_at", -1).to_list(200)


# ---------------------------------------------------------------- Raffle
async def _ensure_raffle():
    now = datetime.now(timezone.utc)
    raffle = await db.raffles.find_one({"status": "open"})
    if not raffle:
        raffle = {"id": str(uuid.uuid4()), "status": "open",
                  "period_start": now.isoformat(),
                  "period_end": (now + timedelta(days=7)).isoformat()}
        await db.raffles.insert_one(dict(raffle))
        return await db.raffles.find_one({"id": raffle["id"]})
    if datetime.fromisoformat(raffle["period_end"]) <= now:
        await _draw_winner(raffle)
        return await _ensure_raffle()
    return raffle


async def _draw_winner(raffle):
    entries = await db.raffle_entries.find({"raffle_id": raffle["id"]}).to_list(10000)
    pool = []
    for e in entries:
        pool += [(e["user_id"], e.get("user_name", "Shopper"))] * int(e.get("tickets", 0))
    winner_id, winner_name = (None, None)
    if pool:
        winner_id, winner_name = _random.choice(pool)
    await db.raffles.update_one({"id": raffle["id"]}, {"$set": {
        "status": "closed", "winner_user_id": winner_id, "winner_name": winner_name,
        "prize": RAFFLE_PRIZE, "entrants": len({e["user_id"] for e in entries}),
        "total_tickets": len(pool), "drawn_at": datetime.now(timezone.utc).isoformat()}})


async def _award_raffle_tickets(uid: str, amount: float):
    raffle = await _ensure_raffle()
    entry = await db.raffle_entries.find_one({"raffle_id": raffle["id"], "user_id": uid})
    spent = (entry.get("spent", 0.0) if entry else 0.0) + amount
    user = await db.users.find_one({"_id": ObjectId(uid)})
    await db.raffle_entries.update_one(
        {"raffle_id": raffle["id"], "user_id": uid},
        {"$set": {"spent": round(spent, 2), "tickets": int(spent // TICKET_PER),
                  "user_name": user.get("name", "Shopper") if user else "Shopper"}},
        upsert=True)


@api.get("/raffle")
async def raffle_status(request: Request):
    raffle = await _ensure_raffle()
    agg = await db.raffle_entries.aggregate([
        {"$match": {"raffle_id": raffle["id"]}},
        {"$group": {"_id": None, "tickets": {"$sum": "$tickets"}, "entrants": {"$sum": 1}}}
    ]).to_list(1)
    totals = agg[0] if agg else {"tickets": 0, "entrants": 0}
    my_tickets, my_spent = 0, 0.0
    try:
        user = await get_current_user(request)
        entry = await db.raffle_entries.find_one({"raffle_id": raffle["id"], "user_id": str(user["_id"])})
        if entry:
            my_tickets, my_spent = int(entry.get("tickets", 0)), float(entry.get("spent", 0.0))
    except HTTPException:
        pass
    winners = await db.raffles.find({"status": "closed", "winner_name": {"$ne": None}}, {"_id": 0}) \
        .sort("drawn_at", -1).limit(5).to_list(5)
    return {
        "raffle_id": raffle["id"], "period_end": raffle["period_end"], "prize": RAFFLE_PRIZE,
        "ticket_per": TICKET_PER, "total_tickets": totals["tickets"], "entrants": totals["entrants"],
        "my_tickets": my_tickets, "my_spent": round(my_spent, 2),
        "next_ticket_at": round((math.floor(my_spent / TICKET_PER) + 1) * TICKET_PER, 2),
        "past_winners": winners,
    }


async def _user_from_token(token: Optional[str]) -> Optional[dict]:
    if not token:
        return None
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        if payload.get("type") != "access":
            return None
        return await db.users.find_one({"_id": ObjectId(payload["sub"])})
    except jwt.InvalidTokenError:
        return None


# ---------------------------------------------------------------- Chat ("My Peeps")
class ChatManager:
    def __init__(self):
        self.active: Set[WebSocket] = set()

    async def connect(self, ws: WebSocket):
        await ws.accept()
        self.active.add(ws)

    def disconnect(self, ws: WebSocket):
        self.active.discard(ws)

    async def broadcast(self, message: dict):
        dead = []
        for ws in list(self.active):
            try:
                await ws.send_json(message)
            except Exception:
                dead.append(ws)
        for ws in dead:
            self.disconnect(ws)


chat_manager = ChatManager()


@api.get("/chat/messages")
async def chat_history():
    msgs = await db.chat_messages.find({}, {"_id": 0}).sort("created_at", -1).limit(50).to_list(50)
    return list(reversed(msgs))


# ---------------------------------------------------------------- Misc
@api.get("/")
async def root():
    return {"status": "ok", "service": "LC Multi-Dept Resale Marketplace"}


@api.get("/health")
async def health():
    return {"status": "healthy", "products": await db.products.count_documents({})}


app.include_router(api)


@app.websocket("/api/ws/chat")
async def ws_chat(ws: WebSocket):
    token = ws.cookies.get("access_token") or ws.query_params.get("token")
    user = await _user_from_token(token)
    if not user:
        await ws.close(code=1008)
        return
    name = user.get("name", "Shopper")
    uid = str(user["_id"])
    await chat_manager.connect(ws)
    await chat_manager.broadcast({"type": "system", "text": f"{name} joined the chat",
                                  "created_at": datetime.now(timezone.utc).isoformat()})
    try:
        while True:
            data = await ws.receive_json()
            text = (data.get("text") or "").strip()[:500]
            if not text:
                continue
            msg = {"type": "message", "id": str(uuid.uuid4()), "user_id": uid, "name": name,
                   "text": text, "created_at": datetime.now(timezone.utc).isoformat()}
            await db.chat_messages.insert_one(dict(msg))
            await chat_manager.broadcast(msg)
    except WebSocketDisconnect:
        chat_manager.disconnect(ws)
        await chat_manager.broadcast({"type": "system", "text": f"{name} left the chat",
                                      "created_at": datetime.now(timezone.utc).isoformat()})
    except Exception:
        chat_manager.disconnect(ws)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup():
    await db.users.create_index("email", unique=True)
    try:
        init_storage()
        logger.info("Storage initialized")
    except Exception as e:
        logger.error(f"Storage init failed: {e}")
    admin_email = os.environ.get("ADMIN_EMAIL", "admin@lcfury.com")
    admin_password = os.environ.get("ADMIN_PASSWORD", "admin123")
    existing = await db.users.find_one({"email": admin_email})
    if not existing:
        await db.users.insert_one({"email": admin_email, "name": "Admin", "role": "admin",
                                   "total_spent": 0.0, "password_hash": hash_password(admin_password),
                                   "created_at": datetime.now(timezone.utc).isoformat()})
    elif not verify_password(admin_password, existing["password_hash"]):
        await db.users.update_one({"email": admin_email}, {"$set": {"password_hash": hash_password(admin_password)}})
    if not await db.users.find_one({"email": "shopper@test.com"}):
        await db.users.insert_one({"email": "shopper@test.com", "name": "Shopper", "role": "user",
                                   "total_spent": 0.0, "password_hash": hash_password("test123"),
                                   "created_at": datetime.now(timezone.utc).isoformat()})
    # seeded catalog is the 300 base items (exclude user listings from the count check)
    if await db.products.count_documents({"is_user_listed": {"$ne": True}}) != 300:
        await db.products.delete_many({"is_user_listed": {"$ne": True}})
        products = generate_products()
        now = datetime.now(timezone.utc).isoformat()
        for p in products:
            p["id"] = str(uuid.uuid4())
            p["is_user_listed"] = False
            p["created_at"] = now
        await db.products.insert_many(products)
        logger.info(f"Seeded {len(products)} products")
    await _ensure_raffle()
    asyncio.create_task(_raffle_scheduler())


async def _raffle_scheduler():
    """Fully automated weekly draw — runs regardless of traffic."""
    while True:
        try:
            await _ensure_raffle()
        except Exception as e:
            logger.error(f"raffle scheduler error: {e}")
        await asyncio.sleep(300)


@app.on_event("shutdown")
async def shutdown():
    client.close()
