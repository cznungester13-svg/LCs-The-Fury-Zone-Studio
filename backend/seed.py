"""
Canonical seeder for LCs The Fury Zone.
15 departments x 50 Temu-style low-price products with category-matched images,
into the SAME database the API uses (MONGO_URL + DB_NAME).
Run: python3 seed.py   (add --wipe to rebuild the catalog from scratch)
"""
import os
import sys
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

NEW_SHOPPER_FREE_ITEMS = 3


def now_iso():
    return datetime.now(timezone.utc).isoformat()


def img(pid):
    if str(pid).startswith("http"):
        return pid
    return f"https://images.unsplash.com/photo-{pid}?auto=format&fit=crop&w=800&q=80"


ADJ = ["Cozy", "Vintage", "Premium", "Deluxe", "Classic", "Retro", "Mini", "Portable",
       "Handmade", "Eco", "Soft", "Ultra", "Compact", "Trendy", "Essential", "Signature",
       "Everyday", "Bold", "Sleek", "Cute"]

# name, slug, price_range, subcats, keywords, image ids
DEPARTMENTS = [
    ("Apparel", "apparel", (2.99, 16.99), ["Men's", "Women's", "Kids"],
     ["Graphic Hoodie", "Vintage Tee", "Lounge Set", "Stretch Leggings", "Pajama Pants",
      "Cozy Socks", "Thermal Top", "Denim Jacket", "Flannel Shirt", "Joggers"],
     ["1521572267360-ee0c2909d518", "1503342217505-b0a15ec3261c", "1583743814966-8936f5b7be1a",
      "1620799140408-edc6dcb6d633", "1479064555552-3ef4979f8908"]),

    ("Shoes, Handbags & Accessories", "shoes-accessories", (3.99, 18.99), ["Men's", "Women's", "Kids"],
     ["Running Sneakers", "Crossbody Bag", "Canvas Tote", "Slippers", "Bucket Hat",
      "Sunglasses", "Card Holder", "Ankle Boots", "Backpack", "Woven Belt"],
     ["1542291026-7eec264c27ff", "1584917865442-de89df76afd3", "1595950653106-6c9ebd614d3a",
      "1600185365483-26d7a4cc7519", "1548036328-c9fa89d128fa"]),

    ("Health & Beauty", "health-beauty", (1.99, 14.99), None,
     ["Gel Nail Polish Set", "Mini UV LED Lamp", "Jade Roller & Gua Sha", "Makeup Sponge Blender",
      "Exfoliating Foot Peel", "Scalp Massager", "Facial Cleansing Brush", "Lip Care Trio"],
     ["1522337360788-8b13dee7a37e", "1512496015851-a90fb38ba796", "1571781926291-c477ebfd024b",
      "1596462502278-27bfdc403348"]),

    ("Home & Garden", "home-garden", (2.49, 15.99), None,
     ["Solar Garden Lights", "Plant Mister", "Pruning Shears", "Hanging Planter",
      "Seed Starting Tray", "Wind Chime", "Watering Can", "Garden Kneeling Pad"],
     ["1585320806297-9794b3e4eeae", "1416879595882-3373a0480b5b", "1466692476868-aef1dfb1e735"]),

    ("Tools, Home Improvement & Office Supplies", "tools-office", (1.49, 16.99), None,
     ["Multi-Bit Screwdriver", "Magnetic Wristband", "LED Headlamp", "Tape Measure",
      "Zip Tie Assortment", "Sticky Note Pack", "Gel Pen Set", "Desk Stapler",
      "Notebook Bundle", "Cable Organizer"],
     ["1581092160607-ee22621dd758", "1504148455328-c376907d081c", "1530124566582-a618bc2615dc",
      "1572981779307-38b8cabb2407", "1497032628192-86f99bcd76bc", "1524995997946-a1c2e315a42f",
      "1517842645767-c639042777db", "1587145820266-a5951ee6f620"]),

    ("Jewelry", "jewelry", (0.49, 5.99), None,
     ["Dainty Layered Necklace", "Minimalist Ring Set", "Huggie Earrings", "Charm Bracelet",
      "Stackable Rings", "Pendant Necklace", "Stud Earring Pack", "Anklet Chain"],
     ["1515562141207-7a88fb7ce338", "1535223289827-42f1e9919769", "1531306728370-e2ebd9d7bb99",
      "1611591437281-460bfbe1220a", "1599643478518-a784e5dc4c8f"]),

    ("Electronics & Gadgets", "electronics", (2.99, 19.99), None,
     ["Braided USB-C Cable", "Phone Ring Holder", "Wireless Earbuds", "Mini Power Bank",
      "Screen Cleaner Kit", "Bluetooth Tracker", "LED Strip Light", "Phone Tripod"],
     ["1505740420928-5e560c06d30e", "1546868871-7041f2a55e12", "1583394838336-acd977736f90",
      "1498049794561-7780e7231661"]),

    ("Hobbies, Arts & Crafts", "hobbies-crafts", (1.29, 13.99), None,
     ["Acrylic Yarn Cake", "Ergonomic Crochet Hook", "Knitting Needle Set", "Stitch Markers Set",
      "Embroidery Floss Pack", "Blending Markers", "Sketchbook", "Washi Tape Set", "Bead Kit"],
     ["https://images.unsplash.com/photo-1550376026-7375b92bb318?auto=format&fit=crop&w=800&q=80",
      "https://images.unsplash.com/photo-1584992236310-6edddc08acff?auto=format&fit=crop&w=800&q=80",
      "https://images.pexels.com/photos/8931780/pexels-photo-8931780.jpeg?auto=compress&cs=tinysrgb&w=800",
      "https://images.unsplash.com/photo-1668072587859-f0f30c8fa938?auto=format&fit=crop&w=800&q=80"]),

    ("Automotive & E-Bike Accessories", "automotive-ebike", (2.49, 17.99), None,
     ["Car Phone Mount", "Microfiber Towel Pack", "E-Bike Handlebar Grips", "LED Valve Lights",
      "Seat Cushion", "Key Fob Cover", "Trunk Organizer", "Bike Phone Bag"],
     ["1503376780353-7e6692767b70", "1489824904134-891ab64532f1", "1558981403-c5f9899a28bc",
      "1449965408869-eaa3f722e40d"]),

    ("Bed & Bath", "bed-bath", (3.49, 18.99), None,
     ["Microfiber Sheet Set", "Plush Bath Towel", "Memory Foam Pillow", "Shower Curtain",
      "Bath Mat", "Weighted Blanket", "Bathrobe", "Throw Blanket"],
     ["1584100936595-c0654b55a2e2", "1616046229478-9901c5536a45", "1522771739844-6a9f6d5f14af",
      "1631049307264-da0ec9d70304"]),

    ("Home Decor", "home-decor", (2.49, 16.99), None,
     ["Faux Succulent", "Wall Tapestry", "Throw Pillow Cover", "Aromatherapy Diffuser",
      "Desk Organizer", "Framed Art Print", "Scented Candle", "String Fairy Lights"],
     ["1513519245088-0e12902e5a38", "1538688525198-9b88f6f53126", "1579656381226-5fc0f0100c3b",
      "1567016432779-094069958ea5"]),

    ("Wicca & Wiccan Supplies", "wicca", (1.99, 14.99), None,
     ["Raw Crystal Cluster", "Sage Cleansing Stick", "Mini Cauldron", "Altar Cloth",
      "Chakra Incense Cones", "Tarot Card Bag", "Ritual Candle Set", "Pendulum"],
     ["https://images.pexels.com/photos/4040598/pexels-photo-4040598.jpeg?auto=compress&cs=tinysrgb&w=800",
      "https://images.unsplash.com/photo-1621923647893-901f834b3e6a?auto=format&fit=crop&w=800&q=80",
      "https://images.unsplash.com/photo-1477313372947-d68a7d410e9f?auto=format&fit=crop&w=800&q=80",
      "https://images.pexels.com/photos/16926698/pexels-photo-16926698.jpeg?auto=compress&cs=tinysrgb&w=800"]),

    ("Camping & Outdoor Entertainment", "camping-outdoor", (3.99, 19.99), None,
     ["Portable Camping Stove", "LED Tent Lantern", "Waterproof Dry Bag", "Insulated Cooler",
      "Paracord Bracelet", "Folding Camp Chair", "Hammock", "Portable Firepit"],
     ["1504280390367-361c6d9f38f4", "1510312305653-8ed496efae75", "1478131143081-80f7f84ca84d"]),

    ("Children's Toys & Entertainment", "kids-toys", (2.49, 19.99), None,
     ["Building Blocks Set", "Plush Toy", "Remote Control Car", "Jigsaw Puzzle",
      "Family Board Game", "Kids Art Kit", "Action Figure", "Dollhouse Set",
      "Slime Making Kit", "Colorful Kite"],
     ["1558060370-d644479cb6f7", "1596461404969-9ae70f2830c1", "1566576912321-d58ddd7a6088",
      "1587654780291-39c9404d746b", "1512314889357-e157c22f938d", "1545558014-8692077e9b5c",
      "1610631787813-9eeb1a2386cc"]),

    ("Collectibles & Oddities", "collectibles", (0.99, 17.99), None,
     ["Enamel Pin", "Vinyl Figure", "Trading Card Pack", "Mini Figurine", "Retro Keychain",
      "Sticker Pack", "Bobblehead", "Souvenir Magnet", "Novelty Coin"],
     ["1606107557195-0e29a4b5b4aa", "1608889825205-eebdb9fc5806", "1611930022073-b7a4ba5fcccd",
      "1578632767115-351597cf2477", "1600334129128-685c5582fd35", "1518331647614-7a1f04cd34cf"]),
]


def gen_names(keywords, n, rnd):
    combos = [f"{a} {k}" for a in ADJ for k in keywords]
    rnd.shuffle(combos)
    # dedupe preserving order
    seen, out = set(), []
    for c in combos:
        if c not in seen:
            seen.add(c)
            out.append(c)
        if len(out) >= n:
            break
    return out


def wipe():
    for c in ["products", "departments", "categories", "brands", "inventory", "carts"]:
        db[c].delete_many({})
    print("Wiped catalog collections.")


def seed():
    print(f"Seeding into DB: {DB_NAME}")
    total = 0
    for d_idx, (name, slug, prange, subcats, keywords, imgs) in enumerate(DEPARTMENTS):
        rnd = random.Random(1000 + d_idx)
        dep = db.departments.find_one({"slug": slug}, {"_id": 0})
        if dep:
            dep_id = dep["id"]
        else:
            dep_id = str(uuid.uuid4())
            db.departments.insert_one({"id": dep_id, "name": name, "slug": slug,
                                       "image": img(imgs[0]), "order": d_idx,
                                       "created_at": now_iso()})
        cat = db.categories.find_one({"department_id": dep_id, "name": name}, {"_id": 0})
        if cat:
            cat_id = cat["id"]
        else:
            cat_id = str(uuid.uuid4())
            db.categories.insert_one({"id": cat_id, "name": name, "department_id": dep_id,
                                      "created_at": now_iso()})

        names = gen_names(keywords, 50, rnd)
        for i, base in enumerate(names):
            title = f"{subcats[i % len(subcats)]} {base}" if subcats else base
            if db.products.find_one({"title": title, "department_id": dep_id}):
                total += 1
                continue
            price = round(rnd.uniform(*prange), 2)
            original = round(price * rnd.uniform(2.8, 4.8), 2)
            pid = str(uuid.uuid4())
            tags = [w.lower() for w in base.split()]
            if subcats:
                tags.append(subcats[i % len(subcats)].lower())
            db.products.insert_one({
                "id": pid,
                "title": title,
                "description": f"{title} \u2014 flash-deal pricing at The Fury Zone. Top-rated pick, unbeatable value while stock lasts.",
                "price": price,
                "original_price": original,
                "department_id": dep_id,
                "category_id": cat_id,
                "brand_id": None,
                "images": [img(imgs[i % len(imgs)])],
                "tags": tags,
                "subcategory": subcats[i % len(subcats)] if subcats else None,
                "variants": [],
                "stock": rnd.randint(15, 400),
                "sold_count": rnd.randint(30, 9500),
                "rating": round(rnd.uniform(4.4, 4.9), 1),
                "featured": i < 2,
                "is_active": True,
                "created_at": now_iso(),
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
