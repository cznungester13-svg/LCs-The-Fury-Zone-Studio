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
    
    # 1. Added your two new departments alongside the original 3
    all_departments = ["Footwear", "Apparel", "Electronics", "Home Textiles & Linens", "Modern Furniture & Decor"]
    for name in all_departments:
        did = str(uuid.uuid4())
        dept_ids[name] = did
        await db.departments.insert_one({"id": did, "name": name,
                                         "slug": name.replace(" ", "-").lower(), "created_at": now_iso()})

    brands = {}
    for name in ["FuryLab", "Streetline", "Voltage", "Northpeak"]:
        bid = str(uuid.uuid4())
        brands[name] = bid
        await db.brands.insert_one({"id": bid, "name": name, "created_at": now_iso()})

    cats = {}
    # 2. Included explicit subcategories for the new budget departments
    cat_map = {
        "Footwear": ["Sneakers", "Boots"], 
        "Apparel": ["Hoodies", "Tees"],
        "Electronics": ["Cameras", "Audio"],
        "Home Textiles & Linens": ["Linens"],
        "Modern Furniture & Decor": ["Decor"]
    }
    for dept, clist in cat_map.items():
        for c in clist:
            cid = str(uuid.uuid4())
            cats[c] = cid
            await db.categories.insert_one({"id": cid, "name": c,
                                            "department_id": dept_ids[dept], "created_at": now_iso()})

    # 3. Your original base core products list
    products = [
        ("Fury Runner Low", "Lightweight everyday sneaker with responsive cushioning.", 129.0,
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

    # --- START OF PROGRAMMATIC LOW-PRICE SEEDING LOOP ---
    LINEN_PRICES = [9.99, 14.50, 19.99, 24.99, 29.99]
    FURNITURE_PRICES = [19.99, 24.99, 29.99, 34.99, 44.99]

    linen_images = [
        "https://images.unsplash.com/photo-1724847885015-be191f1a47ef?crop=entropy&cs=srgb&fm=jpg&ixid=M3w4NjA1NzB8MHwxfHNlYXJjaHw0fHxjb3p5JTIwYmVkZGluZyUyMGxpbmVucyUyMHRvd2Vsc3xlbnwwfHx8fDE3ODMwOTE5NDB8MA&ixlib=rb-4.1.0&q=85",
        "https://images.unsplash.com/photo-1617811449482-31093c8cee16?crop=entropy&cs=srgb&fm=jpg&ixid=M3w4NjA1NzB8MHwxfHNlYXJjaHwyfHxjb3p5JTIwYmVkZGluZyUyMGxpbmVucyUyMHRvd2Vsc3xlbnwwfHx8fDE3ODMwOTE5NDB8MA&ixlib=rb-4.1.0&q=85",
        "https://images.unsplash.com/photo-1631015108968-ba3b87f89005?crop=entropy&cs=srgb&fm=jpg&ixid=M3w4NjA1NzB8MHwxfHNlYXJjaHwzfHxjb3p5JTIwYmVkZGluZyUyMGxpbmVucyUyMHRvd2Vsc3xlbnwwfHx8fDE3ODMwOTE5NDB8MA&ixlib=rb-4.1.0&q=85"
    ]

    furniture_images = [
        "https://images.unsplash.com/photo-1649511134921-67afc567280c?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NTY2Nzd8MHwxfHNlYXJjaHw0fHxtb2Rlcm4lMjBmdXJuaXR1cmUlMjBob21lJTIwZGVjb3J8ZW58MHx8fHwxNzgzMDkxOTM5fDA&ixlib=rb-4.1.0&q=85",
        "https://images.unsplash.com/photo-1616137422495-1e9e46e2aa77?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NTY2Nzd8MHwxfHNlYXJjaHzfHxtb2Rlcm4lMjBmdXJuaXR1cmUlMjBob21lJTIwZGVjb3J8ZW58MHx8fHwxNzgzMDkxOTM5fDA&ixlib=rb-4.1.0&q=85",
        "https://images.unsplash.com/photo-1673563932832-a0c9e0ed26f8?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NTY2Nzd8MHwxfHNlYXJjaHwyfHxtb2Rlcm4lMjBmdXJuaXR1cmUlMjBob21lJTIwZGVjb3J8ZW58MHx8fHwxNzgzMDkxOTM5fDA&ixlib=rb-4.1.0&q=85",
        "https://images.unsplash.com/photo-1693578616322-c8abe6c7393d?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NTY2Nzd8MHwxfHNlYXJjaHwxfHxtb2Rlcm4lMjBmdXJuaXR1cmUlMjBob21lJTIwZGVjb3J8ZW58MHx8fHwxNzgzMDkxOTM5fDA&ixlib=rb-4.1.0&q=85"
    ]

    linen_types = ["Egyptian Cotton Hand Towel", "Luxury Bath Sheet", "Cozy Microfiber Bedding Set", "Quilted Pillow Protectors", "Soft Linen Face Cloth Pack"]
    furniture_types = ["Minimalist Side Table", "Compact Accent Chair", "Geometric Floating Shelf", "Modern Sofa Cushion", "Contemporary Footrest Ottoman"]
    styles = ["Nordic Chic", "Eco-Comfort", "Urban Minimalist", "Classic Loft", "Boho Elements"]

    # Auto-generate 50 items for Textiles (matching image array perfectly)
    for idx in range(1, 51):
        l_type = linen_types[idx % len(linen_types)]
        style = styles[idx % len(styles)]
        title = f"{style} {l_type} (Batch #{idx})"
        desc = f"High-quality {l_type.lower()} styled in an aesthetic {style.lower()} presentation. Designed for premium durability and modern home utility."
        price = random.choice(LINEN_PRICES)
        img = linen_images[idx % len(linen_images)]
        products.append((title, desc, price, "Home Textiles & Linens", "Linens", "Streetline", [img], ["home", "linens"], False, random.randint(30, 100)))

    # Auto-generate 50 items for Furniture (matching image array perfectly)
    for idx in range(1, 51):
        f_type = furniture_types[idx % len(furniture_types)]
        style = styles[idx % len(styles)]
        title = f"{style} {f_type} (Batch #{idx})"
        desc = f"An architectural {f_type.lower()} curated with {style.lower()} principles. Perfect compact profile for living spaces and home styling."
        price = random.choice(FURNITURE_PRICES)
        img = furniture_images[idx % len(furniture_images)]
        products.append((title, desc, price, "Modern Furniture & Decor", "Decor", "FuryLab", [img], ["furniture", "decor"], False, random.randint(10, 45)))
    # --- END OF PROGRAMMATIC SEEDING LOOP ---

    # 4. Executes database insertions using the exact matching system keys
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

    if not await db.coupons.find_one({"code": "FURY10"}):
        await db.coupons.insert_one({"id": str(uuid.uuid4()), "code": "FURY10",
                                     "percent_off": 10, "description": "10% off your order",
                                     "active": True, "created_at": now_iso()})

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
