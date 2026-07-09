import os
import uuid
import random
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
    
    # Fully expanded list including Home & Garden and Handbags departments
    all_departments = [
        "Footwear", "Apparel", "Electronics", "Bed & Bath", "Modern Furniture & Decor",
        "Kitchen & Small Appliances", "Health & Beauty", "Pets & Pet Supplies", 
        "Jewelry", "Arts, Crafts & Hobbies", "Home, Garden & Tools", "Handbags & Accessories"
    ]
    for name in all_departments:
        did = str(uuid.uuid4())
        dept_ids[name] = did
        await db.departments.insert_one({"id": did, "name": name,
                                         "slug": name.replace(" ", "-").replace("&", "and").replace(",", "").lower(), "created_at": now_iso()})

    brands = {}
    for name in ["FuryLab", "Streetline", "Voltage", "Northpeak", "CraftCore", "BeautyPure", "PetPride", "GlowStyle", "HomeFit"]:
        bid = str(uuid.uuid4())
        brands[name] = bid
        await db.brands.insert_one({"id": bid, "name": name, "created_at": now_iso()})

    cats = {}
    cat_map = {
        "Footwear": ["Sneakers", "Boots"], 
        "Apparel": ["Hoodies", "Tees"],
        "Electronics": ["Cameras", "Audio"],
        "Bed & Bath": ["Linens", "Bath Accessories"],
        "Modern Furniture & Decor": ["Decor"],
        "Kitchen & Small Appliances": ["Appliances", "Cookware"],
        "Health & Beauty": ["Skincare", "Cosmetics", "Nail Care"],
        "Pets & Pet Supplies": ["Pet Essentials"],
        "Jewelry": ["Accessories"],
        "Arts, Crafts & Hobbies": ["Crochet & Yarn", "Craft Kits"],
        "Home, Garden & Tools": ["Garden Supplies", "Home Tools"],
        "Handbags & Accessories": ["Bags", "Sunglasses"]
    }
    for dept, clist in cat_map.items():
        for c in clist:
            cid = str(uuid.uuid4())
            cats[c] = cid
            await db.categories.insert_one({"id": cid, "name": c,
                                            "department_id": dept_ids[dept], "created_at": now_iso()})

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

    styles = ["Nordic Chic", "Eco-Comfort", "Urban Minimalist", "Classic Loft", "Boho Elements"]

    # 1. FOOTWEAR GENERATOR (50 Budget Items)
    footwear_prices = [24.99, 29.99, 34.99, 39.99, 44.99]
    footwear_images = ["https://images.unsplash.com/photo-1542291026-7eec264c27ff?w=600&auto=format&fit=crop&q=60"]
    for idx in range(1, 51):
        products.append((f"{styles[idx % 5]} Classic Sneaker (Batch #{idx})", "Comfortable daily footwear choice.", random.choice(footwear_prices), "Footwear", "Sneakers", "Streetline", footwear_images, ["shoes"], False, random.randint(20, 80)))

    # 2. APPAREL GENERATOR (50 Budget Items)
    apparel_prices = [12.99, 14.99, 19.99, 24.99, 29.99]
    apparel_images = ["https://images.unsplash.com/photo-1521572267360-ee0c2909d518?w=600&auto=format&fit=crop&q=60"]
    for idx in range(1, 51):
        products.append((f"{styles[idx % 5]} Essential Tee (Batch #{idx})", "Soft standard cotton fit.", random.choice(apparel_prices), "Apparel", "Tees", "FuryLab", apparel_images, ["apparel"], False, random.randint(40, 150)))

    # 3. ELECTRONICS GENERATOR (50 Budget Items)
    electronics_prices = [15.99, 19.99, 24.99, 34.99, 49.99]
    electronics_images = ["https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=600&auto=format&fit=crop&q=60"]
    for idx in range(1, 51):
        products.append((f"{styles[idx % 5]} Audio Earbuds (Batch #{idx})", "Reliable audio experience on a budget.", random.choice(electronics_prices), "Electronics", "Audio", "Voltage", electronics_images, ["tech"], False, random.randint(15, 60)))

    # 4. BED & BATH (With your requested Bathroom Decor items - 50 Items)
    LINEN_PRICES = [12.99, 14.50, 19.99, 24.99, 29.99]
    linen_images = ["https://images.unsplash.com/photo-1617811449482-31093c8cee16?w=600&auto=format&fit=crop&q=60"]
    bath_decor_types = ["Complete Shower Curtain Set with Rings", "Anti-Slip Microfiber Bath Mat", "Rustproof Hanging Shower Caddy", "Minimalist Toothbrush Holder Stand", "Luxury Cotton Bath Sheet Pack"]
    for idx in range(1, 51):
        b_decor = bath_decor_types[idx % len(bath_decor_types)]
        products.append((f"{styles[idx % 5]} {b_decor} (#{idx})", f"Aesthetic and highly practical {b_decor.lower()} designed to stylize your bathroom setup cleanly.", random.choice(LINEN_PRICES), "Bed & Bath", "Bath Accessories", "Streetline", linen_images, ["bath", "decor"], False, random.randint(30, 100)))

    # 5. MODERN FURNITURE & DECOR (50 Items)
    FURNITURE_PRICES = [19.99, 24.99, 29.99, 34.99, 44.99]
    furniture_images = ["https://images.unsplash.com/photo-1616137422495-1e9e46e2aa77?w=600&auto=format&fit=crop&q=60"]
    for idx in range(1, 51):
        products.append((f"{styles[idx % 5]} Accent Decor (Batch #{idx})", "Stunning geometric accent pieces for home styling.", random.choice(FURNITURE_PRICES), "Modern Furniture & Decor", "Decor", "FuryLab", furniture_images, ["decor"], False, random.randint(10, 45)))

    # 6. KITCHEN & SMALL APPLIANCES (With Cookware & Bakeware - 50 Budget Items)
    kitchen_prices = [16.99, 22.99, 27.50, 34.99, 45.00]
    kitchen_images = ["https://images.unsplash.com/photo-1556910103-1c02745aae4d?w=600&auto=format&fit=crop&q=60"]
    kitchen_types = ["Non-Stick Premium Cookware Set", "Heavy-Duty Carbon Steel Bakeware Set", "Personal Countertop Blender", "Electric Rapid Heating Kettle", "Digital Precision Food Scale"]
    for idx in range(1, 51):
        k_type = kitchen_types[idx % len(kitchen_types)]
        products.append((f"{styles[idx % 5]} {k_type} (#{idx})", f"Durable {k_type.lower()} curated for seamless kitchen utility and culinary efficiency.", random.choice(kitchen_prices), "Kitchen & Small Appliances", "Cookware", "Voltage", kitchen_images, ["kitchen", "cookware"], False, random.randint(15, 50)))

    # 7. HEALTH & BEAUTY (With Acrylic Nails Kits - 50 Budget Items)
    beauty_prices = [9.99, 14.99, 19.99, 24.99, 32.50]
    beauty_images = ["https://images.unsplash.com/photo-1522335789203-aabd1fc54bc9?w=600&auto=format&fit=crop&q=60"]
    beauty_types = ["Professional Acrylic Nails Kit with UV Lamp", "Organic Facial Hydration Serum", "Synthetic Makeup Brush Set (12-Piece)", "Natural Jade Facial Massage Roller", "Botanical Lip Care Balm Multi-Pack"]
    for idx in range(1, 51):
        b_type = beauty_types[idx % len(beauty_types)]
        products.append((f"{styles[idx % 5]} {b_type} (#{idx})", f"Premium formulation {b_type.lower()} curated to support high-end beauty and cosmetic styling routines.", random.choice(beauty_prices), "Health & Beauty", "Nail Care" if "Nails" in b_type else "Skincare", "BeautyPure", beauty_images, ["beauty", "cosmetics"], False, random.randint(35, 120)))

    # 8. PETS & PET SUPPLIES (50 Budget Items)
    pet_prices = [9.99, 14.99, 18.50, 22.99, 29.99]
    pet_images = ["https://images.unsplash.com/photo-1516734212186-a967f81ad0d7?w=600&auto=format&fit=crop&q=60"]
    pet_types = ["Orthopedic Pet Cushion Bed", "Double Ceramic Feeding Bowl", "Durable Rope Chew Toy Pack", "Self-Cleaning Grooming Brush", "Reflective Weatherproof Leash"]
    for idx in range(1, 51):
        p_type = pet_types[idx % len(pet_types)]
        products.append((f"{styles[idx % 5]} {p_type} (#{idx})", f"Premium durability {p_type.lower()} to ensure maximum comfort and happiness for your pets.", random.choice(pet_prices), "Pets & Pet Supplies", "Pet Essentials", "PetPride", pet_images, ["pets", "supplies"], False, random.randint(20, 90)))

    # 9. JEWELRY (With Wicca Jewelry & Cheap Engagement Sets - 50 Budget Items)
    jewelry_prices = [11.99, 15.99, 19.99, 24.99, 29.99]
    jewelry_images = ["https://images.unsplash.com/photo-1535632066927-ab7c9ab60908?w=600&auto=format&fit=crop&q=60"]
    jewelry_types = ["Aesthetic Gothic Wicca Pendant Necklace", "Affordable Cubic Zirconia Engagement Set", "Minimalist Sterling Silver Band Ring", "Classic Stud Earrings Multi-Pack", "Adjustable Layered Charm Bracelet"]
    for idx in range(1, 51):
        j_type = jewelry_types[idx % len(jewelry_types)]
        products.append((f"{styles[idx % 5]} {j_type} (#{idx})", f"Finely crafted {j_type.lower()} detailed beautifully to accentuate personal flair and statement styling.", random.choice(jewelry_prices), "Jewelry", "Accessories", "GlowStyle", jewelry_images, ["jewelry", "rings"], False, random.randint(15, 75)))

    # 10. ARTS, CRAFTS & HOBBIES (50 Items)
    craft_prices = [8.99, 12.99, 16.50, 21.99, 27.99]
    craft_images = ["https://images.unsplash.com/photo-1584992231908-03ff25fb26a4?w=600&auto=format&fit=crop&q=60"]
    craft_types = ["Premium Acrylic Crochet Yarn Pack", "Ergonomic Aluminum Crochet Hooks Set", "Heavyweight Mixed Media Sketchbook", "Professional Acrylic Paint Set", "Macrame Cotton Cord Spool"]
    for idx in range(1, 51):
        c_type = craft_types[idx % len(craft_types)]
        products.append((f"{styles[idx % 5]} {c_type} (#{idx})", f"High-quality {c_type.lower()} ideal for all your artistic hobby projects and DIY creations.", random.choice(craft_prices), "Arts, Crafts & Hobbies", "Crochet & Yarn", "CraftCore", craft_images, ["crafts", "yarn", "crochet"], False, random.randint(25, 110)))

    # 11. HOME, GARDEN & TOOLS (New Department - 50 Items)
    garden_prices = [12.99, 18.50, 24.99, 32.00, 45.00]
    garden_images = ["https://images.unsplash.com/photo-1416879595882-3373a0480b5b?w=600&auto=format&fit=crop&q=60"]
    garden_types = ["Ergonomic Garden Hand Trowel Set", "Heavy Duty Waterproof Garden Hose", "Solar-Powered Pathway LED Lights (Pack of 6)", "Multi-Pocket Fabric Tool Organizer", "Indoor/Outdoor Geometric Planter Pot"]
    for idx in range(1, 51):
        g_type = garden_types[idx % len(garden_types)]
        products.append((f"{styles[idx % 5]} {g_type} (#{idx})", f"Reliable {g_type.lower()} designed to assist with home improvement and lawn care updates.", random.choice(garden_prices), "Home, Garden & Tools", "Garden Supplies", "HomeFit", garden_images, ["home", "garden"], False, random.randint(15, 65)))

    # 12. HANDBAGS & ACCESSORIES (New Department - 50 Items)
    bag_prices = [15.99, 19.99, 25.50, 29.99, 39.99]
    bag_images = ["https://images.unsplash.com/photo-1584917865442-de89df76afd3?w=600&auto=format&fit=crop&q=60"]
    bag_types = ["Classic Designer-Style Tote Handbag", "UV-400 Protection Classic Sunglasses", "Compact Faux-Leather Crossbody Purse", "Slim RFID Blocking Travel Wallet", "Aesthetic Shoulder Hobo Bag"]
    for idx in range(1, 51):
        b_type = bag_types[idx % len(bag_types)]
        products.append((f"{styles[idx % 5]} {b_type} (#{idx})", f"Chic {b_type.lower()} adding a seamless and highly functional finish to daily streetwear.", random.choice(bag_prices), "Handbags & Accessories", "Bags" if "Bag" in b_type or "Purse" in b_type else "Sunglasses", "GlowStyle", bag_images, ["accessories", "bags"], False, random.randint(20, 85)))


    # Database insertions execution
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

    # Demo sellers + resale listings
    seller1 = await _seed_user("seller@furyzone.com", "Riley Sells", ["customer", "seller"])
    await _seed_user("buyer@furyzone.com", "Sam Buyer", ["customer"])

    if await db.resale_listings.count_documents({"seller_id": seller1}) == 0:
        listings = [
            ("Vintage Film Camera", "Well-loved classic film camera, fully working.", 210.0, "good", [IMG["camera"]]),
            ("Used Grey Trail Sneakers", "Worn a handful of times, size 10, great grip left.", 65.0, "like_new", [IMG["sneaker_grey"]]),
            ("Cropped Streetwear Hoodie", "Barely worn cropped hoodie, super clean.", 45.0, "like_new", [IMG["hoodie"]]),
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
