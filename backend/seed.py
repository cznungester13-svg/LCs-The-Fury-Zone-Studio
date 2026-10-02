"""
Canonical seeder for LCs The Fury Zone.
15 departments x 50 DISTINCT items, each with its own matching image fetched
from the Pixabay API (keyword search), into MONGO_URL + DB_NAME.

Run: python3 seed.py --wipe
Images are cached in .pixabay_cache.json so reruns are instant.
"""
import os
import sys
import json
import time
import uuid
import random
from pathlib import Path
from datetime import datetime, timezone

import httpx
from dotenv import load_dotenv
from pymongo import MongoClient
from passlib.context import CryptContext

load_dotenv()
MONGO_URL = os.getenv("MONGO_URI") or os.getenv("MONGODB_URL") or os.getenv("MONGO_URL")
DB_NAME = os.getenv("DB_NAME", "test_database")
PIXABAY_KEY = os.getenv("PIXABAY_API_KEY", "")
client = MongoClient(MONGO_URL)
db = client[DB_NAME]
pwd = CryptContext(schemes=["bcrypt"], deprecated="auto")

NEW_SHOPPER_FREE_ITEMS = 3
CACHE_PATH = Path(__file__).parent / ".pixabay_cache.json"
_cache = json.loads(CACHE_PATH.read_text()) if CACHE_PATH.exists() else {}


def now_iso():
    return datetime.now(timezone.utc).isoformat()


def _save_cache():
    CACHE_PATH.write_text(json.dumps(_cache, indent=0))


def fetch_images(query, n=20):
    """Return a list of image URLs for a keyword (cached, throttled)."""
    key = query.lower().strip()
    if key in _cache and _cache[key]:
        return _cache[key]
    urls = []
    try:
        r = httpx.get("https://pixabay.com/api/", params={
            "key": PIXABAY_KEY, "q": query, "image_type": "photo",
            "per_page": max(n, 3), "safesearch": "true", "order": "popular",
        }, timeout=30)
        if r.status_code == 200:
            urls = [h["webformatURL"] for h in r.json().get("hits", [])]
        elif r.status_code == 429:
            time.sleep(30)
            return fetch_images(query, n)
    except Exception as e:
        print(f"  ! image fetch failed for '{query}': {e}")
    _cache[key] = urls
    _save_cache()
    time.sleep(0.7)
    return urls


ADJ = ["Cozy", "Vintage", "Premium", "Deluxe", "Classic", "Retro", "Mini", "Portable",
       "Handmade", "Eco", "Soft", "Ultra", "Compact", "Trendy", "Essential", "Signature",
       "Everyday", "Bold", "Sleek", "Cute"]

# name, slug, (min,max price), subcats, [ (item type, pixabay query), ... ]
DEPARTMENTS = [
    ("Apparel", "apparel", (2.99, 16.99), ["Men's", "Women's", "Kids"], [
        ("Hoodie", "hoodie"), ("Graphic Tee", "t-shirt"), ("Leggings", "leggings"),
        ("Pajama Set", "pajamas"), ("Socks", "socks"), ("Denim Jacket", "denim jacket"),
        ("Flannel Shirt", "flannel shirt"), ("Joggers", "jogger pants"), ("Sweater", "sweater"),
        ("Dress", "dress"), ("Shorts", "shorts clothing"), ("Tank Top", "tank top"),
        ("Cardigan", "cardigan"), ("Beanie", "beanie hat")]),

    ("Shoes, Handbags & Accessories", "shoes-accessories", (3.99, 18.99), ["Men's", "Women's", "Kids"], [
        ("Sneakers", "sneakers"), ("Handbag", "handbag"), ("Tote Bag", "tote bag"),
        ("Slippers", "slippers"), ("Bucket Hat", "bucket hat"), ("Sunglasses", "sunglasses"),
        ("Wallet", "wallet"), ("Boots", "boots shoes"), ("Backpack", "backpack"),
        ("Belt", "leather belt"), ("Scarf", "scarf"), ("Watch", "wristwatch"),
        ("Cap", "baseball cap"), ("Crossbody Bag", "crossbody bag")]),

    ("Health & Beauty", "health-beauty", (1.99, 14.99), None, [
        ("Nail Polish", "nail polish"), ("UV Nail Lamp", "nail lamp"), ("Face Roller", "face roller"),
        ("Makeup Sponge", "makeup sponge"), ("Foot Mask", "foot care"), ("Scalp Massager", "scalp massager"),
        ("Facial Brush", "facial cleansing brush"), ("Lip Balm", "lip balm"), ("Skincare Serum", "skincare serum"),
        ("Hair Clips", "hair clips"), ("Perfume", "perfume bottle"), ("Eyeshadow Palette", "eyeshadow palette"),
        ("Hand Cream", "hand cream"), ("Bath Bomb", "bath bomb")]),

    ("Home & Garden", "home-garden", (2.49, 15.99), None, [
        ("Solar Garden Light", "solar garden light"), ("Plant Mister", "plant mister spray"),
        ("Pruning Shears", "pruning shears"), ("Hanging Planter", "hanging planter"),
        ("Seed Tray", "seedling tray"), ("Wind Chime", "wind chime"), ("Watering Can", "watering can"),
        ("Garden Gloves", "garden gloves"), ("Flower Pot", "flower pot"), ("Bird Feeder", "bird feeder"),
        ("Succulent", "succulent plant"), ("Garden Hose", "garden hose"), ("Outdoor Lantern", "garden lantern"),
        ("Trowel", "garden trowel")]),

    ("Tools, Home Improvement & Office Supplies", "tools-office", (1.49, 16.99), None, [
        ("Screwdriver Set", "screwdriver set"), ("Tape Measure", "tape measure"), ("Headlamp", "headlamp"),
        ("Hammer", "hammer tool"), ("Pliers", "pliers"), ("Sticky Notes", "sticky notes"),
        ("Pen Set", "pens"), ("Stapler", "stapler"), ("Notebook", "notebook"),
        ("Cable Organizer", "cable organizer"), ("Flashlight", "flashlight"), ("Wrench", "wrench"),
        ("Scissors", "scissors"), ("Desk Lamp", "desk lamp")]),

    ("Jewelry", "jewelry", (0.49, 5.99), None, [
        ("Necklace", "necklace"), ("Ring", "ring jewelry"), ("Earrings", "earrings"),
        ("Bracelet", "bracelet"), ("Pendant", "pendant necklace"), ("Anklet", "anklet"),
        ("Brooch", "brooch"), ("Charm", "charm jewelry"), ("Choker", "choker necklace"),
        ("Bangle", "bangle"), ("Nose Ring", "nose ring"), ("Hair Pin", "hair pin"),
        ("Locket", "locket"), ("Stud Earrings", "stud earrings")]),

    ("Electronics & Gadgets", "electronics", (2.99, 19.99), None, [
        ("USB Cable", "usb cable"), ("Phone Holder", "phone holder"), ("Earbuds", "earbuds"),
        ("Power Bank", "power bank"), ("Bluetooth Speaker", "bluetooth speaker"), ("Smart Watch", "smartwatch"),
        ("Webcam", "webcam"), ("Mouse", "computer mouse"), ("Keyboard", "keyboard"),
        ("Phone Tripod", "phone tripod"), ("LED Strip", "led strip lights"), ("Charger", "phone charger"),
        ("Headphones", "headphones"), ("Phone Case", "phone case")]),

    ("Hobbies, Arts & Crafts", "hobbies-crafts", (1.29, 13.99), None, [
        ("Yarn", "yarn"), ("Crochet Hook", "crochet hook"), ("Knitting Needles", "knitting needles"),
        ("Embroidery Kit", "embroidery"), ("Markers", "art markers"), ("Sketchbook", "sketchbook"),
        ("Washi Tape", "washi tape"), ("Beads", "craft beads"), ("Paint Set", "paint set"),
        ("Paint Brushes", "paint brushes"), ("Glue Gun", "glue gun"), ("Stickers", "stickers"),
        ("Canvas", "art canvas"), ("Sewing Kit", "sewing kit")]),

    ("Automotive & E-Bike Accessories", "automotive-ebike", (2.49, 17.99), None, [
        ("Car Phone Mount", "car phone mount"), ("Microfiber Towel", "microfiber towel"),
        ("Bike Handlebar Grips", "bicycle handlebar"), ("Tire Valve Caps", "tire valve"),
        ("Car Seat Cushion", "car seat cushion"), ("Keychain", "keychain"), ("Trunk Organizer", "car trunk organizer"),
        ("Bike Light", "bicycle light"), ("Air Freshener", "car air freshener"), ("Jumper Cables", "jumper cables"),
        ("Bike Helmet", "bike helmet"), ("Car Vacuum", "car vacuum"), ("Floor Mats", "car floor mat"),
        ("Bike Lock", "bike lock")]),

    ("Bed & Bath", "bed-bath", (3.49, 18.99), None, [
        ("Bed Sheets", "bed sheets"), ("Bath Towel", "bath towel"), ("Pillow", "pillow"),
        ("Shower Curtain", "shower curtain"), ("Bath Mat", "bath mat"), ("Blanket", "blanket"),
        ("Bathrobe", "bathrobe"), ("Duvet", "duvet bedding"), ("Washcloth", "washcloth"),
        ("Soap Dispenser", "soap dispenser"), ("Laundry Basket", "laundry basket"),
        ("Toothbrush Holder", "toothbrush holder"), ("Comforter", "comforter"), ("Pillowcase", "pillowcase")]),

    ("Home Decor", "home-decor", (2.49, 16.99), None, [
        ("Faux Plant", "faux plant decor"), ("Wall Art", "wall art"), ("Throw Pillow", "throw pillow"),
        ("Diffuser", "aroma diffuser"), ("Vase", "vase"), ("Candle", "candle"),
        ("String Lights", "string lights"), ("Picture Frame", "picture frame"), ("Wall Clock", "wall clock"),
        ("Mirror", "decorative mirror"), ("Area Rug", "area rug"), ("Decor Figurine", "figurine decor"),
        ("Table Lamp", "table lamp"), ("Wall Shelf", "wall shelf")]),

    ("Wicca & Wiccan Supplies", "wicca", (1.99, 14.99), None, [
        ("Healing Crystal", "healing crystals"), ("Sage Smudge Stick", "sage smudge"),
        ("Mini Cauldron", "cauldron"), ("Altar Cloth", "altar cloth"), ("Incense", "incense"),
        ("Tarot Cards", "tarot cards"), ("Ritual Candle", "ritual candle"), ("Pendulum", "crystal pendulum"),
        ("Crystal Ball", "crystal ball"), ("Amulet", "amulet"), ("Spell Jar", "spell jar"),
        ("Rune Stones", "rune stones"), ("Moon Decor", "moon decor"), ("Dried Herbs", "dried herbs")]),

    ("Camping & Outdoor Entertainment", "camping-outdoor", (3.99, 19.99), None, [
        ("Camping Stove", "camping stove"), ("Lantern", "camping lantern"), ("Dry Bag", "dry bag"),
        ("Cooler", "cooler box"), ("Paracord Bracelet", "paracord bracelet"), ("Camp Chair", "camping chair"),
        ("Hammock", "hammock"), ("Tent", "tent"), ("Sleeping Bag", "sleeping bag"),
        ("Hiking Backpack", "hiking backpack"), ("Water Bottle", "water bottle"), ("Binoculars", "binoculars"),
        ("Compass", "compass"), ("Camp Flashlight", "camping flashlight")]),

    ("Children's Toys & Entertainment", "kids-toys", (2.49, 19.99), None, [
        ("Building Blocks", "building blocks toy"), ("Plush Toy", "plush toy"), ("RC Car", "remote control car toy"),
        ("Jigsaw Puzzle", "jigsaw puzzle"), ("Board Game", "board game"), ("Art Kit", "kids art kit"),
        ("Action Figure", "action figure"), ("Dollhouse", "dollhouse"), ("Slime Kit", "slime toy"),
        ("Kite", "kite"), ("Toy Train", "toy train"), ("Play Kitchen", "toy kitchen"),
        ("Stuffed Animal", "stuffed animal"), ("Toy Robot", "toy robot")]),

    ("Collectibles & Oddities", "collectibles", (0.99, 17.99), None, [
        ("Enamel Pin", "enamel pin"), ("Vinyl Figure", "vinyl figure toy"), ("Trading Cards", "trading cards"),
        ("Figurine", "figurine"), ("Keychain", "keychain collectible"), ("Sticker Pack", "sticker pack"),
        ("Bobblehead", "bobblehead"), ("Fridge Magnet", "fridge magnet"), ("Collector Coin", "coin collection"),
        ("Postage Stamp", "postage stamp"), ("Comic Book", "comic book"), ("Model Kit", "model kit"),
        ("Snow Globe", "snow globe"), ("Postcard", "vintage postcard")]),
]

FALLBACK = "https://images.unsplash.com/photo-1607082348824-0a96f2a4b9da?auto=format&fit=crop&w=800&q=80"


def wipe():
    for c in ["products", "departments", "categories", "brands", "inventory", "carts"]:
        db[c].delete_many({})
    print("Wiped catalog collections.")


def seed():
    print(f"Seeding into DB: {DB_NAME}")
    if not PIXABAY_KEY:
        print("WARNING: PIXABAY_API_KEY not set; images will use fallback.")
    total = 0
    for d_idx, (name, slug, prange, subcats, types) in enumerate(DEPARTMENTS):
        rnd = random.Random(2000 + d_idx)
        dep = db.departments.find_one({"slug": slug}, {"_id": 0})
        if dep:
            dep_id = dep["id"]
        else:
            dep_id = str(uuid.uuid4())
            db.departments.insert_one({"id": dep_id, "name": name, "slug": slug,
                                       "image": "", "order": d_idx, "created_at": now_iso()})
        cat = db.categories.find_one({"department_id": dep_id, "name": name}, {"_id": 0})
        cat_id = cat["id"] if cat else str(uuid.uuid4())
        if not cat:
            db.categories.insert_one({"id": cat_id, "name": name, "department_id": dep_id,
                                      "created_at": now_iso()})

        # Fetch an image pool per item type.
        type_images = {}
        for disp, query in types:
            imgs = fetch_images(query, 20)
            type_images[disp] = imgs or [FALLBACK]
        # Department tile image = first image of the first type.
        db.departments.update_one({"id": dep_id},
                                  {"$set": {"image": type_images[types[0][0]][0]}})

        # Generate 50 items cycling through types; each gets a distinct image.
        type_counter = {t[0]: 0 for t in types}
        for i in range(50):
            disp, query = types[i % len(types)]
            adj = ADJ[i % len(ADJ)]
            base = f"{adj} {disp}"
            title = f"{subcats[i % len(subcats)]} {base}" if subcats else base
            if db.products.find_one({"title": title, "department_id": dep_id}):
                total += 1
                continue
            pool = type_images[disp]
            img_url = pool[type_counter[disp] % len(pool)]
            type_counter[disp] += 1
            price = round(rnd.uniform(*prange), 2)
            original = round(price * rnd.uniform(2.8, 4.8), 2)
            pid = str(uuid.uuid4())
            tags = [w.lower() for w in disp.split()]
            if subcats:
                tags.append(subcats[i % len(subcats)].lower())
            db.products.insert_one({
                "id": pid, "title": title,
                "description": f"{title} \u2014 flash-deal pricing at The Fury Zone. Top-rated pick, unbeatable value while stock lasts.",
                "price": price, "original_price": original,
                "department_id": dep_id, "category_id": cat_id, "brand_id": None,
                "images": [img_url], "tags": tags,
                "subcategory": subcats[i % len(subcats)] if subcats else None,
                "variants": [], "stock": rnd.randint(15, 400),
                "sold_count": rnd.randint(30, 9500), "rating": round(rnd.uniform(4.4, 4.9), 1),
                "featured": i < 2, "is_active": True, "created_at": now_iso(),
            })
            total += 1
        print(f"  [{d_idx+1:>2}] {name}: 50 items")
    print(f"Total products ensured: {total}")

    for code, off in [("FURY10", 10), ("ZONE20", 20)]:
        db.coupons.update_one({"code": code},
                              {"$set": {"code": code, "percent_off": off, "active": True,
                                        "created_at": now_iso()}}, upsert=True)
    print("Coupons: FURY10 (10%), ZONE20 (20%)")
    db.shop_settings.update_one({"setting": "resell_market"},
                                {"$set": {"active": True, "status": "open"}}, upsert=True)

    users = [
        ("admin@furyzone.com", "Admin123!", "Fury Admin", ["customer", "admin", "seller"]),
        ("customer@furyzone.com", "Customer123!", "Zone Customer", ["customer"]),
    ]
    for email, password, name, roles in users:
        existing = db.users.find_one({"email": email})
        if existing:
            update = {"roles": roles}
            if existing.get("free_items_remaining") is None:
                update["free_items_remaining"] = NEW_SHOPPER_FREE_ITEMS
            db.users.update_one({"email": email}, {"$set": update})
            continue
        db.users.insert_one({
            "id": str(uuid.uuid4()), "email": email, "password_hash": pwd.hash(password),
            "full_name": name, "roles": roles, "is_active": True,
            "free_items_remaining": NEW_SHOPPER_FREE_ITEMS, "created_at": now_iso(),
        })
    print("Demo users ensured (each with 3 free-item bonus).")
    print("Done.")


if __name__ == "__main__":
    if "--wipe" in sys.argv:
        wipe()
    seed()
