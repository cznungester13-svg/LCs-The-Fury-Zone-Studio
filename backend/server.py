from contextlib import asynccontextmanager
from fastapi import FastAPI, APIRouter
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field, EmailStr
from typing import List, Optional
import uuid
from datetime import datetime, timezone


ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Define the lifespan manager for database cleanup
@asynccontextmanager
async def lifespan(app: FastAPI):
    yield
    client.close()

# Create the main app and pass the lifespan manager
app = FastAPI(lifespan=lifespan)


# ---------------- Models ----------------
class Product(BaseModel):
    id: str
    name: str
    category: str
    price: float
    original_price: Optional[float] = None
    rating: float
    reviews: int
    seller: str
    image: str
    description: str
    badge: Optional[str] = None
    stock: int = 25


class Category(BaseModel):
    id: str
    name: str
    image: str
    count: int


class OrderItem(BaseModel):
    id: str
    name: str
    price: float
    quantity: int
    image: Optional[str] = None


class OrderCreate(BaseModel):
    items: List[OrderItem]
    full_name: str
    email: EmailStr
    address: str
    city: str
    zip_code: str


class Order(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4())[:8].upper())
    items: List[OrderItem]
    full_name: str
    email: EmailStr
    address: str
    city: str
    zip_code: str
    subtotal: float
    shipping: float
    total: float
    status: str = "confirmed"
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class NewsletterSignup(BaseModel):
    email: EmailStr


# ---------------- Seed Data ----------------
CATEGORIES = [
    {"id": "electronics", "name": "Electronics", "image": "https://images.unsplash.com/photo-1615655406736-b37c4fabf923?crop=entropy&cs=srgb&fm=jpg&q=85&w=800", "count": 0},
    {"id": "fashion", "name": "Fashion", "image": "https://images.unsplash.com/photo-1441984904996-e0b6ba687e04?crop=entropy&cs=srgb&fm=jpg&q=85&w=800", "count": 0},
    {"id": "home", "name": "Home & Living", "image": "https://images.unsplash.com/photo-1617806265182-7b3f847f0b75?crop=entropy&cs=srgb&fm=jpg&q=85&w=800", "count": 0},
    {"id": "handmade", "name": "Handmade", "image": "https://images.unsplash.com/photo-1649810617979-16001a60c89c?crop=entropy&cs=srgb&fm=jpg&q=85&w=800", "count": 0},
    {"id": "beauty", "name": "Beauty", "image": "https://images.unsplash.com/photo-1522335789203-aabd1fc54bc9?crop=entropy&cs=srgb&fm=jpg&q=85&w=800", "count": 0},
]

PRODUCTS = [
    {"id": "p1", "name": "FuryWave Pro Wireless Headphones", "category": "electronics", "price": 129.99, "original_price": 199.99, "rating": 4.8, "reviews": 2431, "seller": "AudioLab", "image": "https://images.unsplash.com/photo-1618366712010-f4ae9c647dcb?crop=entropy&cs=srgb&fm=jpg&q=85&w=800", "description": "Immersive noise-cancelling over-ear headphones with 40-hour battery life, plush memory-foam cushions and studio-grade sound signature. Bluetooth 5.3 with multipoint pairing.", "badge": "Best Seller", "stock": 40},
    {"id": "p2", "name": "Nimbus Minimalist Watch", "category": "fashion", "price": 89.00, "original_price": None, "rating": 4.6, "reviews": 812, "seller": "Nimbus Co.", "image": "https://images.unsplash.com/photo-1523275335684-37898b6baf30?crop=entropy&cs=srgb&fm=jpg&q=85&w=800", "description": "A clean Scandinavian-inspired timepiece with sapphire glass, stainless steel case and interchangeable leather strap. Water resistant to 50m.", "badge": None, "stock": 30},
    {"id": "p3", "name": "AeroStride Court Sneakers", "category": "fashion", "price": 74.50, "original_price": 110.00, "rating": 4.7, "reviews": 1560, "seller": "StrideWorks", "image": "https://images.unsplash.com/photo-1608231387042-66d1773070a5?crop=entropy&cs=srgb&fm=jpg&q=85&w=800", "description": "Timeless low-top sneakers crafted from premium full-grain leather with cushioned insoles for all-day comfort.", "badge": "Deal", "stock": 55},
    {"id": "p4", "name": "Heritage Leather Backpack", "category": "fashion", "price": 149.00, "original_price": None, "rating": 4.9, "reviews": 640, "seller": "Wanderbound", "image": "https://images.unsplash.com/photo-1622560480605-d83c853bc5c3?crop=entropy&cs=srgb&fm=jpg&q=85&w=800", "description": "Handcrafted full-grain leather backpack with padded 15\" laptop sleeve, brass hardware and a lifetime repair guarantee.", "badge": None, "stock": 18},
    {"id": "p5", "name": "Ember Soy Candle — Cedar & Amber", "category": "home", "price": 28.00, "original_price": None, "rating": 4.8, "reviews": 980, "seller": "Ember Studio", "image": "https://images.unsplash.com/photo-1603905179139-db12ab535ca9?crop=entropy&cs=srgb&fm=jpg&q=85&w=800", "description": "Hand-poured 100% soy wax candle with a wooden crackling wick. 60-hour burn time and notes of cedarwood, amber and vanilla.", "badge": None, "stock": 120},
    {"id": "p6", "name": "Classic Wayfarer Sunglasses", "category": "fashion", "price": 59.99, "original_price": 85.00, "rating": 4.5, "reviews": 2210, "seller": "SunHaus", "image": "https://images.unsplash.com/photo-1572635196237-14b3f281503f?crop=entropy&cs=srgb&fm=jpg&q=85&w=800", "description": "UV400 polarized lenses in a timeless acetate frame. Comes with a hard case and microfiber cleaning cloth.", "badge": "Deal", "stock": 70},
    {"id": "p7", "name": "GlowDrop Vitamin-C Serum", "category": "beauty", "price": 34.00, "original_price": None, "rating": 4.7, "reviews": 3120, "seller": "GlowDrop", "image": "https://images.unsplash.com/photo-1713768704571-6aeb0d0e5105?crop=entropy&cs=srgb&fm=jpg&q=85&w=800", "description": "Brightening 15% vitamin-C serum with hyaluronic acid and ferulic acid. Vegan, cruelty-free and dermatologist tested.", "badge": "New", "stock": 90},
    {"id": "p8", "name": "Artisan Stoneware Mug Set", "category": "handmade", "price": 42.00, "original_price": None, "rating": 4.9, "reviews": 415, "seller": "ClayField", "image": "https://images.unsplash.com/photo-1590422749897-47036da0b0ff?crop=entropy&cs=srgb&fm=jpg&q=85&w=800", "description": "Set of two wheel-thrown stoneware mugs with a reactive glaze. Each piece is unique and microwave-safe.", "badge": None, "stock": 25},
    {"id": "p9", "name": "Hand-Thrown Ceramic Vase", "category": "handmade", "price": 68.00, "original_price": 95.00, "rating": 4.8, "reviews": 302, "seller": "ClayField", "image": "https://images.unsplash.com/photo-1649810617979-16001a60c89c?crop=entropy&cs=srgb&fm=jpg&q=85&w=800", "description": "A sculptural matte-white ceramic vase, hand-thrown by independent artisans. A statement piece for any shelf or table.", "badge": "Deal", "stock": 12},
    {"id": "p10", "name": "Creator's Tech Desk Bundle", "category": "electronics", "price": 219.00, "original_price": 289.00, "rating": 4.6, "reviews": 189, "seller": "AudioLab", "image": "https://images.unsplash.com/photo-1615655406736-b37c4fabf923?crop=entropy&cs=srgb&fm=jpg&q=85&w=800", "description": "Everything a creator needs: USB condenser mic, RGB controller and desk accessories. Plug-and-play on any setup.", "badge": None, "stock": 22},
    {"id": "p11", "name": "Pro Makeup Brush Collection", "category": "beauty", "price": 46.00, "original_price": None, "rating": 4.7, "reviews": 1740, "seller": "GlowDrop", "image": "https://images.unsplash.com/photo-1596462502278-27bfdc403348?crop=entropy&cs=srgb&fm=jpg&q=85&w=800", "description": "12-piece vegan makeup brush set with ultra-soft synthetic bristles and an ergonomic rose-gold handle. Travel pouch included.", "badge": None, "stock": 60},
    {"id": "p12", "name": "Nordic Shelf Decor Set", "category": "home", "price": 96.00, "original_price": 130.00, "rating": 4.5, "reviews": 268, "seller": "Wanderbound", "image": "https://images.unsplash.com/photo-1617806265182-7b3f847f0b75?crop=entropy&cs=srgb&fm=jpg&q=85&w=800", "description": "Curated 6-piece decor set with woven baskets, brass mirror and faux greenery to style any shelf in seconds.", "badge": "Deal", "stock": 15},
]


async def seed_data():
    existing = await db.products.count_documents({})
    if existing == 0:
        await db.products.insert_many([dict(p) for p in PRODUCTS])
    counts = {}
    for p in PRODUCTS:
        counts[p["category"]] = counts.get(p["category"], 0) + 1
    await db.categories.delete_many({})
    cats = [dict(c) for c in CATEGORIES]
    for c in cats:
        c["count"] = counts.get(c["id"], 0)
    await db.categories.insert_many(cats)


# ---------------- Routes ----------------
@api_router.get("/")
async def root():
    return {"message": "LC's The Fury Zone API"}


@api_router.get("/categories", response_model=List[Category])
async def get_categories():
    cats = await db.categories.find({}, {"_id": 0}).to_list(100)
    return cats


@api_router.get("/products", response_model=List[Product])
async def get_products(category: Optional[str] = None, search: Optional[str] = None, sort: Optional[str] = None):
    query = {}
    if category and category != "all":
        query["category"] = category
    if search:
        query["name"] = {"$regex": search, "$options": "i"}
    cursor = db.products.find(query, {"_id": 0})
    products = await cursor.to_list(200)
    if sort == "price_asc":
        products.sort(key=lambda x: x["price"])
    elif sort == "price_desc":
        products.sort(key=lambda x: x["price"], reverse=True)
    elif sort == "rating":
        products.sort(key=lambda x: x["rating"], reverse=True)
    return products


@api_router.get("/products/{product_id}", response_model=Product)
async def get_product(product_id: str):
    product = await db.products.find_one({"id": product_id}, {"_id": 0})
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product


@api_router.post("/orders", response_model=Order)
async def create_order(payload: OrderCreate):
    subtotal = round(sum(item.price * item.quantity for item in payload.items), 2)
    if subtotal == 0:
        raise HTTPException(status_code=400, detail="Cart is empty")
    shipping = 0.0 if subtotal >= 75 else 6.99
    total = round(subtotal + shipping, 2)
    order = Order(
        items=payload.items,
        full_name=payload.full_name,
        email=payload.email,
        address=payload.address,
        city=payload.city,
        zip_code=payload.zip_code,
        subtotal=subtotal,
        shipping=shipping,
        total=total,
    )
    await db.orders.insert_one(order.model_dump())
    return order


@api_router.post("/newsletter")
async def newsletter(payload: NewsletterSignup):
    await db.newsletter.update_one(
        {"email": payload.email},
        {"$setOnInsert": {"email": payload.email, "created_at": datetime.now(timezone.utc).isoformat()}},
        upsert=True,
    )
    return {"message": "Subscribed successfully"}


app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=["https://marketplace-fury.preview.emergentagent.com"],
    allow_methods=["*"],
    allow_headers=["*"],
)

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


@app.on_event("startup")
async def startup_db():
    await seed_data()



