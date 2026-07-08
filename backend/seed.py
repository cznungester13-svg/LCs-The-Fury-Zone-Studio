import os
import uuid
from database import db, now_iso
from auth import hash_password, ensure_seller_profile

IMG = {
    "hero": "https://images.pexels.com/photos/29548609/pexels-photo-29548609.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
    "hoodie": "https://images.pexels.com/photos/11317811/pexels-photo-11317811.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
    "sneaker_white": "https://images.pexels.com/photos/12628400/pexels-photo-12628400.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
    "sneaker_grey": "https://images.pexels.com/photos/1456733/pexels-photo-1456733.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
    "camera": "https://images.pexels.com/photos/821653/pexels-photo-821653.jpeg",
}


async def seed_admin():
    email = os.environ.get("ADMIN_EMAIL", "admin@furyzone.com")
    password = os.environ.get("ADMIN_PASSWORD", "Admin@123")
    existing = await db.users.find_one({"email": email})
    if existing is None:
        await db.users.insert_one({
            "id": str(uuid.uuid4()), "email": email, "password_hash": hash_password(password),
            "full_name": "Fury Admin", "phone": None, "roles": ["admin", "customer"],
            "is_active": True, "avatar_url": None, "created_at": now_iso(),
        })


async def _seed_user(email, name, roles):
    u = await db.users.find_one({"email": email})
    if u:
        return u["id"]
    uid = str(uuid.uuid4())
    await db.users.insert_one({
        "id": uid, "email": email, "password_hash": hash_password("Password@123"),
        "full_name": name, "phone": None, "roles": roles, "is_active": True,
        "avatar_url": None, "created_at": now_iso(),
    })
    if "seller" in roles:
        await ensure_seller_profile(uid, f"{name}'s Store")
    return uid


async def seed_catalog():
    if await db.products.count_documents({}) > 0:
        return
    dept_ids = {}
    for name in ["Footwear", "Apparel", "Electronics"]:
        did = str(uuid.uuid4())
        dept_ids[name] = did
        await db.departments.insert_one({"id": did, "name": name,
                                         "slug": name.lower(), "created_at": now_iso()})

    brands = {}
    for name in ["FuryLab", "Streetline", "Voltage", "Northpeak"]:
        bid = str(uuid.uuid4())
        brands[name] = bid
        await db.brands.insert_one({"id": bid, "name": name, "created_at": now_iso()})

    cats = {}
    cat_map = {"Footwear": ["Sneakers", "Boots"], "Apparel": ["Hoodies", "Tees"],
               "Electronics": ["Cameras", "Audio"]}
    for dept, clist in cat_map.items():
        for c in clist:
            cid = str(uuid.uuid4())
            cats[c] = cid
            await db.categories.insert_one({"id": cid, "name": c,
                                            "department_id": dept_ids[dept], "created_at": now_iso()})

    products = [\n        ("Fury Runner Low", "Lightweight everyday sneaker with responsive cushioning.", 129.0,
         "Footwear", "Sneakers", "FuryLab", [IMG["sneaker_white"], IMG["sneaker_grey"]],
         ["sneakers", "running"], True, 40),
        ("Voltage Trail Grey", "Rugged trail runner built for grip and speed.", 149.0,
         "Footwear", "Sneakers", "Voltage", [IMG["sneaker_grey"]], ["sneakers", "trail"], True, 25),
        ("Streetline Heavy Hoodie", "400gsm heavyweight fleece hoodie, boxy fit.", 89.0,
         "Apparel", "Hoodies", "Streetline", [IMG["hoodie"]], ["hoodie", "streetwear"], True, 60),
        ("Fury Zone Tee", "Premium cotton tee with bold Fury Zone print.", 39.0,
         "Apparel", "Tees", "FuryLab", [IMG["hero"]], ["tee", "cotton"], False, 120),
        ("Northpeak Field Camera", "Compact mirrorless camera for creators.", 749.0,
         "Electronics", "Cameras", "Northpeak", [IMG["camera"]], ["camera", "photo"], True, 15),
    ]
    for title, desc, price, dept, cat, brand, imgs, tags, feat, stock in products:
        pid = str(uuid.uuid4())
        await db.products.insert_one({
            "id": pid, "title": title, "description": desc, "price": price,
            "department_id": dept_ids[dept], "category_id": cats[cat], "brand_id": brands[brand],
            "images": imgs, "tags": tags,
            "variants": [
                {"id": str(uuid.uuid4()), "name": "Standard", "price": price, "stock": stock, "sku": None},
            ],
            "stock": stock, "featured": feat, "is_active": True, "created_at": now_iso(),
        })
        await db.inventory.insert_one({"id": str(uuid.uuid4()), "product_id": pid,
                                       "stock": stock, "reserved": 0, "updated_at": now_iso()})

    # demo sellers + resale listings
    seller1 = await _seed_user("seller@furyzone.com", "Riley Sells", ["customer", "seller"])
    await _seed_user("buyer@furyzone.com", "Sam Buyer", ["customer"])

    # Fix: Guard targeted specifically against individual sample contents instead of global table size
    if await db.resale_listings.count_documents({"seller_id": seller1}) == 0:
        listings = [
            ("Vintage Film Camera", "Well-loved classic film camera, fully working.", 210.0,
             "good", [IMG["camera"]]),
            ("Used Grey Trail Sneakers", "Worn a handful of times, size 10, great grip left.", 65.0,
             "like_new", [IMG["sneaker_grey"]]),
            ("Cropped Streetwear Hoodie", "Barely worn cropped hoodie, super clean.", 45.0,
             "like_new", [IMG["hoodie"]]),
        ]
        for title, desc, price, cond, imgs in listings:
            await db.resale_listings.insert_one({
                "id": str(uuid.uuid4()), "seller_id": seller1, "title": title,
                "description": desc, "price": price, "condition": cond,
                "category_id": None, "brand_id": None, "images": imgs, "tags": [],
                "status": "active", "created_at": now_iso(),
            })

    # Fix: Ensure default coupon is safely seeded by checking explicitly for its unique key code
    if not await db.coupons.find_one({"code": "FURY10"}):
        await db.coupons.insert_one({"id": str(uuid.uuid4()), "code": "FURY10",
                                     "percent_off": 10, "description": "10% off your order",
                                     "active": True, "created_at": now_iso()})


async def create_indexes():
    await db.users.create_index("email", unique=True)
    await db.users.create_index("id")
    await db.products.create_index("id")
    await db.resale_listings.create_index("id")
    await db.resale_listings.create_index("status")
    await db.orders.create_index("user_id")
    await db.payment_transactions.create_index("session_id")


async def run_seed():
    await create_indexes()
    await seed_admin()
    await seed_catalog()
