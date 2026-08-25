from dotenv import load_dotenv
from pathlib import Path
import os

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

import logging
import uuid
import secrets
from datetime import datetime, timezone, timedelta
from typing import List, Optional

import bcrypt
import jwt
from bson import ObjectId
from fastapi import FastAPI, APIRouter, HTTPException, Request, Response, Depends
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
from pydantic import BaseModel, EmailStr, Field

from seed_data import generate_products, department_meta

# ---------------------------------------------------------------- DB
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

JWT_SECRET = os.environ['JWT_SECRET']
JWT_ALGORITHM = "HS256"

app = FastAPI(title="LC Multi-Dept Resale Marketplace")
api = APIRouter(prefix="/api")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("marketplace")


# ---------------------------------------------------------------- Auth helpers
def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(plain: str, hashed: str) -> bool:
    return bcrypt.checkpw(plain.encode("utf-8"), hashed.encode("utf-8"))


def create_access_token(user_id: str, email: str) -> str:
    payload = {"sub": user_id, "email": email, "type": "access",
               "exp": datetime.now(timezone.utc) + timedelta(hours=12)}
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)


def create_refresh_token(user_id: str) -> str:
    payload = {"sub": user_id, "type": "refresh",
               "exp": datetime.now(timezone.utc) + timedelta(days=7)}
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)


def set_auth_cookies(response: Response, access: str, refresh: str):
    response.set_cookie("access_token", access, httponly=True, secure=True,
                        samesite="none", max_age=43200, path="/")
    response.set_cookie("refresh_token", refresh, httponly=True, secure=True,
                        samesite="none", max_age=604800, path="/")


def public_user(u: dict) -> dict:
    return {"id": str(u["_id"]), "email": u["email"], "name": u.get("name", ""),
            "role": u.get("role", "user")}


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


class CheckoutBody(BaseModel):
    full_name: str = Field(min_length=1)
    address: str = Field(min_length=1)
    city: str = Field(min_length=1)


# ---------------------------------------------------------------- Auth routes
@api.post("/auth/register")
async def register(body: RegisterBody, response: Response):
    email = body.email.lower()
    if await db.users.find_one({"email": email}):
        raise HTTPException(status_code=400, detail="Email already registered")
    doc = {"email": email, "name": body.name, "password_hash": hash_password(body.password),
           "role": "user", "created_at": datetime.now(timezone.utc).isoformat()}
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
    if rec and rec.get("locked_until"):
        locked_until = datetime.fromisoformat(rec["locked_until"])
        if locked_until > now:
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
                "rating": ("rating", -1), "featured": ("sku", 1)}
    field, direction = sort_map.get(sort, ("sku", 1))
    total = await db.products.count_documents(query)
    skip = max(0, (page - 1) * limit)
    cursor = db.products.find(query, {"_id": 0}).sort(field, direction).skip(skip).limit(limit)
    items = await cursor.to_list(limit)
    return {"items": items, "total": total, "page": page, "limit": limit,
            "pages": (total + limit - 1) // limit}


@api.get("/products/deals")
async def get_deals():
    cursor = db.products.find({}, {"_id": 0}).sort("price", 1).limit(8)
    return await cursor.to_list(8)


@api.get("/products/{product_id}")
async def get_product(product_id: str):
    p = await db.products.find_one({"id": product_id}, {"_id": 0})
    if not p:
        raise HTTPException(status_code=404, detail="Product not found")
    related = await db.products.find(
        {"department": p["department"], "id": {"$ne": product_id}}, {"_id": 0}
    ).limit(4).to_list(4)
    return {"product": p, "related": related}


# ---------------------------------------------------------------- Cart routes
async def _cart_with_products(user_id: str):
    cart = await db.carts.find_one({"user_id": user_id})
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
    if not await db.products.find_one({"id": body.product_id}):
        raise HTTPException(status_code=404, detail="Product not found")
    cart = await db.carts.find_one({"user_id": uid})
    if not cart:
        await db.carts.insert_one({"user_id": uid, "items": [
            {"product_id": body.product_id, "quantity": body.quantity}]})
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
    found = False
    for it in items:
        if it["product_id"] == body.product_id:
            it["quantity"] = body.quantity
            found = True
            break
    if not found and body.quantity > 0:
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


# ---------------------------------------------------------------- Order routes
@api.post("/orders")
async def create_order(body: CheckoutBody, user: dict = Depends(get_current_user)):
    uid = str(user["_id"])
    cart = await _cart_with_products(uid)
    if not cart["items"]:
        raise HTTPException(status_code=400, detail="Cart is empty")
    order = {
        "id": str(uuid.uuid4()),
        "user_id": uid,
        "items": [{"product_id": i["product"]["id"], "name": i["product"]["name"],
                   "image": i["product"]["image"], "price": i["product"]["price"],
                   "quantity": i["quantity"], "line_total": i["line_total"]}
                  for i in cart["items"]],
        "total": cart["total"],
        "shipping": {"full_name": body.full_name, "address": body.address, "city": body.city},
        "status": "confirmed",
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    await db.orders.insert_one(order)
    await db.carts.update_one({"user_id": uid}, {"$set": {"items": []}})
    order.pop("_id", None)
    return order


@api.get("/orders")
async def list_orders(user: dict = Depends(get_current_user)):
    cursor = db.orders.find({"user_id": str(user["_id"])}, {"_id": 0}).sort("created_at", -1)
    return await cursor.to_list(200)


@api.get("/")
async def root():
    return {"status": "ok", "service": "LC Multi-Dept Resale Marketplace"}


@api.get("/health")
async def health():
    count = await db.products.count_documents({})
    return {"status": "healthy", "products": count}


app.include_router(api)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=["*"] if os.environ.get('CORS_ORIGINS', '*') == '*'
    else os.environ['CORS_ORIGINS'].split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------------------------------------------------------- Startup seeding
@app.on_event("startup")
async def startup():
    await db.users.create_index("email", unique=True)
    # admin
    admin_email = os.environ.get("ADMIN_EMAIL", "admin@lcfury.com")
    admin_password = os.environ.get("ADMIN_PASSWORD", "admin123")
    existing = await db.users.find_one({"email": admin_email})
    if not existing:
        await db.users.insert_one({"email": admin_email, "name": "Admin",
                                   "password_hash": hash_password(admin_password),
                                   "role": "admin",
                                   "created_at": datetime.now(timezone.utc).isoformat()})
    elif not verify_password(admin_password, existing["password_hash"]):
        await db.users.update_one({"email": admin_email},
                                  {"$set": {"password_hash": hash_password(admin_password)}})
    # test shopper user
    test_email = "shopper@test.com"
    if not await db.users.find_one({"email": test_email}):
        await db.users.insert_one({"email": test_email, "name": "Shopper",
                                   "password_hash": hash_password("test123"),
                                   "role": "user",
                                   "created_at": datetime.now(timezone.utc).isoformat()})
    # products (self-healing: reseed if not exactly 300)
    if await db.products.count_documents({}) != 300:
        await db.products.delete_many({})
        products = generate_products()
        for p in products:
            p["id"] = str(uuid.uuid4())
        await db.products.insert_many(products)
        logger.info(f"Seeded {len(products)} products")


@app.on_event("shutdown")
async def shutdown():
    client.close()
