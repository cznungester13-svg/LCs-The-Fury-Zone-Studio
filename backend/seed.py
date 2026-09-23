"""
Canonical seeder for LCs The Fury Zone.
Seeds departments, categories, brands, products, coupons and demo users
into the SAME database the API uses (MONGO_URL + DB_NAME from the environment).
Idempotent: safe to run repeatedly.
"""
import os
import uuid
import random
from datetime import datetime, timezone

from dotenv import load_dotenv
from pymongo import MongoClient
from passlib.context import CryptContext

load_dotenv()

MONGO_URL = os.getenv("MONGO_URI") or os.getenv("MONGODB_URL") or os.getenv("MONGO_URL")
DB_NAME = os.getenv("DB_NAME", "test_database")

client = MongoClient(MONGO_URL)
db = client[DB_NAME]

pwd = CryptContext(schemes=["bcrypt"], deprecated="auto")


def now_iso():
    return datetime.now(timezone.utc).isoformat()


DEPARTMENTS = {
    "Apparel": {
        "brand": "Fury Wear",
        "images": [
            "https://images.unsplash.com/photo-1521572267360-ee0c2909d518",
            "https://images.unsplash.com/photo-1503342217505-b0a15ec3261c",
            "https://images.unsplash.com/photo-1620799140408-edc6dcb6d633",
        ],
        "products": [
            ("Fury Oversized Hoodie", 64.0, ["hoodie", "streetwear"]),
            ("Zone Graphic Tee", 32.0, ["tee", "graphic"]),
            ("Rebel Cargo Pants", 78.0, ["pants", "cargo"]),
            ("Static Puffer Jacket", 149.0, ["jacket", "puffer"]),
            ("Peep Crew Sweatshirt", 58.0, ["crewneck"]),
            ("Night Ops Joggers", 54.0, ["joggers"]),
        ],
    },
    "Shoes & Accessories": {
        "brand": "Fury Wear",
        "images": [
            "https://images.unsplash.com/photo-1542291026-7eec264c27ff",
            "https://images.unsplash.com/photo-1595950653106-6c9ebd614d3a",
            "https://images.unsplash.com/photo-1600185365483-26d7a4cc7519",
        ],
        "products": [
            ("Fury Runner Sneakers", 119.0, ["sneakers", "shoes"]),
            ("Zone Crossbody Bag", 44.0, ["bag"]),
            ("Rebel Bucket Hat", 28.0, ["hat"]),
            ("Static Sunglasses", 36.0, ["sunglasses"]),
            ("Peep Canvas Tote", 24.0, ["tote"]),
        ],
    },
    "Electronics": {
        "brand": "ZoneTech",
        "images": [
            "https://images.unsplash.com/photo-1505740420928-5e560c06d30e",
            "https://images.unsplash.com/photo-1546868871-7041f2a55e12",
            "https://images.unsplash.com/photo-1583394838336-acd977736f90",
        ],
        "products": [
            ("Fury Wireless Earbuds", 59.0, ["earbuds", "audio"]),
            ("Zone Power Bank 20K", 39.0, ["powerbank"]),
            ("Braided USB-C Cable", 14.0, ["cable"]),
            ("Bluetooth Tracker Tag", 22.0, ["tracker"]),
            ("Static Phone Ring Holder", 9.0, ["accessory"]),
        ],
    },
    "Home Decor": {
        "brand": "Zone Home",
        "images": [
            "https://images.unsplash.com/photo-1513519245088-0e12902e5a38",
            "https://images.unsplash.com/photo-1538688525198-9b88f6f53126",
            "https://images.unsplash.com/photo-1579656381226-5fc0f0100c3b",
        ],
        "products": [
            ("Fury LED Strip Lights", 21.0, ["led", "lights"]),
            ("Zone Aromatherapy Diffuser", 29.0, ["diffuser"]),
            ("Rebel Wall Tapestry", 26.0, ["tapestry"]),
            ("Peep Desk Organizer", 18.0, ["organizer"]),
        ],
    },
    "Health & Beauty": {
        "brand": "Zone Glow",
        "images": [
            "https://images.unsplash.com/photo-1522337360788-8b13dee7a37e",
            "https://images.unsplash.com/photo-1512496015851-a90fb38ba796",
            "https://images.unsplash.com/photo-1571781926291-c477ebfd024b",
        ],
        "products": [
            ("Gel Nail Polish Kit", 34.0, ["nails"]),
            ("Jade Roller & Gua Sha", 19.0, ["skincare"]),
            ("Scalp Massager", 12.0, ["wellness"]),
            ("Makeup Sponge Set", 11.0, ["makeup"]),
        ],
    },
    "Camping & Recreation": {
        "brand": "Zone Outdoors",
        "images": [
            "https://images.unsplash.com/photo-1504280390367-361c6d9f38f4",
            "https://images.unsplash.com/photo-1510312305653-8ed496efae75",
            "https://images.unsplash.com/photo-1445308394109-4ec2920981b2",
        ],
        "products": [
            ("Portable Camping Stove", 49.0, ["camping"]),
            ("LED Tent Lantern", 24.0, ["lantern"]),
            ("Waterproof Dry Bag", 27.0, ["drybag"]),
            ("Insulated Picnic Cooler", 42.0, ["cooler"]),
        ],
    },
}


def seed():
    print(f"Seeding into DB: {DB_NAME}")

    # Brands (dedupe by name)
    brand_ids = {}
    for dept in DEPARTMENTS.values():
        name = dept["brand"]
        if name not in brand_ids:
            existing = db.brands.find_one({"name": name}, {"_id": 0})
            if existing:
                brand_ids[name] = existing["id"]
            else:
                bid = str(uuid.uuid4())
                db.brands.insert_one({"id": bid, "name": name, "created_at": now_iso()})
                brand_ids[name] = bid

    featured_count = 0
    total_products = 0
    for dept_name, dept in DEPARTMENTS.items():
        dep = db.departments.find_one({"name": dept_name}, {"_id": 0})
        if dep:
            dep_id = dep["id"]
        else:
            dep_id = str(uuid.uuid4())
            db.departments.insert_one({
                "id": dep_id, "name": dept_name,
                "slug": dept_name.lower().replace(" & ", "-").replace(" ", "-"),
                "created_at": now_iso(),
            })
        cat = db.categories.find_one({"name": dept_name, "department_id": dep_id}, {"_id": 0})
        if cat:
            cat_id = cat["id"]
        else:
            cat_id = str(uuid.uuid4())
            db.categories.insert_one({
                "id": cat_id, "name": dept_name, "department_id": dep_id, "created_at": now_iso(),
            })

        for idx, (title, price, tags) in enumerate(dept["products"]):
            if db.products.find_one({"title": title}):
                total_products += 1
                continue
            featured = idx < 2
            if featured:
                featured_count += 1
            pid = str(uuid.uuid4())
            img = dept["images"][idx % len(dept["images"])]
            db.products.insert_one({
                "id": pid,
                "title": title,
                "description": f"{title} \u2014 hand-picked for The Fury Zone. Premium quality, instant vibes.",
                "price": float(price),
                "department_id": dep_id,
                "category_id": cat_id,
                "brand_id": brand_ids[dept["brand"]],
                "images": [f"{img}?auto=format&fit=crop&w=800&q=80"],
                "tags": tags,
                "variants": [],
                "stock": random.randint(10, 120),
                "featured": featured,
                "is_active": True,
                "created_at": now_iso(),
            })
            db.inventory.update_one(
                {"product_id": pid},
                {"$setOnInsert": {"id": str(uuid.uuid4()), "product_id": pid,
                                  "stock": 50, "reserved": 0, "updated_at": now_iso()}},
                upsert=True,
            )
            total_products += 1
    print(f"Products ensured: {total_products} (featured: {featured_count})")

    db.coupons.update_one(
        {"code": "FURY10"},
        {"$set": {"code": "FURY10", "percent_off": 10, "active": True, "created_at": now_iso()}},
        upsert=True,
    )
    db.coupons.update_one(
        {"code": "ZONE20"},
        {"$set": {"code": "ZONE20", "percent_off": 20, "active": True, "created_at": now_iso()}},
        upsert=True,
    )
    print("Coupons ensured: FURY10 (10%), ZONE20 (20%)")

    db.shop_settings.update_one(
        {"setting": "resell_market"},
        {"$set": {"active": True, "status": "open"}},
        upsert=True,
    )

    users = [
        ("admin@furyzone.com", "Admin123!", "Fury Admin", ["customer", "admin", "seller"]),
        ("customer@furyzone.com", "Customer123!", "Zone Customer", ["customer"]),
    ]
    for email, password, name, roles in users:
        existing = db.users.find_one({"email": email})
        if existing:
            db.users.update_one({"email": email}, {"$set": {"roles": roles}})
            continue
        db.users.insert_one({
            "id": str(uuid.uuid4()),
            "email": email,
            "password_hash": pwd.hash(password),
            "full_name": name,
            "roles": roles,
            "is_active": True,
            "created_at": now_iso(),
        })
    print("Demo users ensured: admin@furyzone.com / customer@furyzone.com")
    print("Done.")


if __name__ == "__main__":
    seed()
