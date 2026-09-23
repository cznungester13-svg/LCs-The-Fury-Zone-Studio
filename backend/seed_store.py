import os
import random
from dotenv import load_dotenv
from pymongo import MongoClient

# Use environment configuration only (never hardcode credentials).
load_dotenv()
MONGO_URI = os.getenv("MONGO_URI") or os.getenv("MONGODB_URL") or os.getenv("MONGO_URL")
client = MongoClient(MONGO_URI)
db = client[os.getenv("DB_NAME", "test_database")]

def seed_database():
    print("🚀 Starting Temu-style ultra-discount store initialization...")

    # 1. Setup Chat Room: "Chatting with the Peeps"
    db.chat_rooms.update_one(
        {"name": "Chatting with the Peeps"},
        {
            "$set": {
                "name": "Chatting with the Peeps",
                "description": "The official hangout zone for all members.",
                "active": True,
                "moderated": True
            }
        },
        upsert=True
    )
    print("✅ Chat room 'Chatting with the Peeps' is active.")

    # 2. Setup Resell Shop Status
    db.shop_settings.update_one(
        {"setting": "resell_market"},
        {"$set": {"active": True, "status": "open"}},
        upsert=True
    )
    print("✅ Resell shop is active and ready to sell.")

    # 3. 14 Departments with Temu-style thematic image pools & keywords
    department_data = {
        "Apparel (Men's, Women's, Children)": {
            "keywords": ["Thermal", "Vintage Tee", "Lounge Set", "Graphic Hoodie", "Cozy Socks", "Stretch Leggings", "Pajama Pants"],
            "images": [
                "https://images.unsplash.com/photo-1521572267360-ee0c2909d518",
                "https://images.unsplash.com/photo-1503342217505-b0a15ec3261c",
                "https://images.unsplash.com/photo-1583743814966-8936f5b7be1a"
            ]
        },
        "Shoes, Handbags & Accessories": {
            "keywords": ["Crossbody Bag", "Running Sneakers", "Canvas Tote", "Slippers", "Card Holder", "Bucket Hat", "Statement Sunglasses"],
            "images": [
                "https://images.unsplash.com/photo-1542291026-7eec264c27ff",
                "https://images.unsplash.com/photo-1584917865442-de89df76afd3",
                "https://images.unsplash.com/photo-1595950653106-6c9ebd614d3a"
            ]
        },
        "Bed & Bath": {
            "keywords": ["Microfiber Sheet Set", "Plush Bath Towel", "Memory Foam Pillow", "Shower Curtain", "Bath Mat", "Weighted Blanket"],
            "images": [
                "https://images.unsplash.com/photo-1584100936595-c0654b55a2e2",
                "https://images.unsplash.com/photo-1616046229478-9901c5536a45",
                "https://images.unsplash.com/photo-1522771739844-6a9f6d5f14af"
            ]
        },
        "Home Decor": {
            "keywords": ["LED Strip Lights", "Faux Succulent", "Wall Tapestry", "Throw Pillow Cover", "Aromatherapy Diffuser", "Desk Organizer"],
            "images": [
                "https://images.unsplash.com/photo-1513519245088-0e12902e5a38",
                "https://images.unsplash.com/photo-1538688525198-9b88f6f53126",
                "https://images.unsplash.com/photo-1579656381226-5fc0f0100c3b"
            ]
        },
        "Kitchen & Kitchen Supplies": {
            "keywords": ["Silicone Spatula Set", "Garlic Press", "Insulated Travel Mug", "Digital Food Scale", "Reusable Food Bags", "Mini Chopper"],
            "images": [
                "https://images.unsplash.com/photo-1556911220-e15b29be8c8f",
                "https://images.unsplash.com/photo-1588854337236-6889d631faa8",
                "https://images.unsplash.com/photo-1590794056226-77efefb1570f"
            ]
        },
        "Home & Garden": {
            "keywords": ["Solar Garden Lights", "Plant Mister", "Pruning Shears", "Hanging Planter", "Seed Starting Tray", "Wind Chime"],
            "images": [
                "https://images.unsplash.com/photo-1585320806297-9794b3e4eeae",
                "https://images.unsplash.com/photo-1416879595882-3373a0480b5b",
                "https://images.unsplash.com/photo-1592417817098-8f3d691a4bf5"
            ]
        },
        "Tools, Gadgets & Home Improvement": {
            "keywords": ["Multi-Bit Screwdriver", "Magnetic Wristband", "LED Headlamp", "Precision Hammer", "Zip Tie Assortment", "Tape Measure"],
            "images": [
                "https://images.unsplash.com/photo-1581092160607-ee22621dd758",
                "https://images.unsplash.com/photo-1504148455328-c376907d081c",
                "https://images.unsplash.com/photo-1530124566582-a618bc2615dc"
            ]
        },
        "Hobbies & Arts & Crafts (Yarn & Crochet)": {
            "keywords": ["Acrylic Yarn Cake", "Ergonomic Crochet Hook", "Stitch Markers Set", "Embroidery Floss", "Blending Markers", "Sketchbook"],
            "images": [
                "https://images.unsplash.com/photo-1615485290382-441e4d049cb5",
                "https://images.unsplash.com/photo-1513364776144-60967b0f800f",
                "https://images.unsplash.com/photo-1582211594533-268f4f1edcb9"
            ]
        },
        "Electronics": {
            "keywords": ["Braided USB-C Cable", "Phone Ring Holder", "Wireless Earbuds", "Mini Power Bank", "Phone Screen Cleaner", "Bluetooth Tracker"],
            "images": [
                "https://images.unsplash.com/photo-1505740420928-5e560c06d30e",
                "https://images.unsplash.com/photo-1546868871-7041f2a55e12",
                "https://images.unsplash.com/photo-1583394838336-acd977736f90"
            ]
        },
        "Jewelry, Gag Gifts & Party Supplies": {
            "keywords": ["Dainty Layered Necklace", "Funny Desk Sign", "LED Party Glasses", "Minimalist Ring Set", "Confetti Popper", "Keychain"],
            "images": [
                "https://images.unsplash.com/photo-1515562141207-7a88fb7ce338",
                "https://images.unsplash.com/photo-1535223289827-42f1e9919769",
                "https://images.unsplash.com/photo-1531306728370-e2ebd9d7bb99"
            ]
        },
        "Wicca & Wicca Supplies": {
            "keywords": ["Raw Crystal Cluster", "Smudge Cleansing Stick", "Mini Cauldron", "Pentedram Altar Cloth", "Chakra Incense Cones", "Tarot Bag"],
            "images": [
                "https://images.unsplash.com/photo-1563245372-f21724e3856d",
                "https://images.unsplash.com/photo-1600585154340-be6161a56a0c",
                "https://images.unsplash.com/photo-1518709268805-4e9042af9f23"
            ]
        },
        "Health & Beauty (Nail Kits & Wellness)": {
            "keywords": ["Gel Nail Polish Set", "Mini UV LED Lamp", "Jade Roller & Gua Sha", "Makeup Sponge Blender", "Exfoliating Foot Peel", "Scalp Massager"],
            "images": [
                "https://images.unsplash.com/photo-1522337360788-8b13dee7a37e",
                "https://images.unsplash.com/photo-1512496015851-a90fb38ba796",
                "https://images.unsplash.com/photo-1571781926291-c477ebfd024b"
            ]
        },
        "Automotive & E-Bike Supplies": {
            "keywords": ["Car Phone Mount", "Microfiber Cleaning Towel", "E-Bike Handlebar Grips", "LED Tire Valve Lights", "Seat Cushion", "Key Fob Cover"],
            "images": [
                "https://images.unsplash.com/photo-1503376780353-7e6692767b70",
                "https://images.unsplash.com/photo-1489824904134-891ab64532f1",
                "https://images.unsplash.com/photo-1558981403-c5f9899a28bc"
            ]
        },
        "Recreation, E-Bikes & Camping": {
            "keywords": ["Portable Camping Stove", "LED Tent Lantern", "Waterproof Dry Bag", "Insulated Picnic Cooler", "Paracord Survival Bracelet", "Bike Phone Bag"],
            "images": [
                "https://images.unsplash.com/photo-1504280390367-361c6d9f38f4",
                "https://images.unsplash.com/photo-1510312305653-8ed496efae75",
                "https://images.unsplash.com/photo-1445308394109-4ec2920981b2"
            ]
        }
    }

    print("📦 Generating Temu-style ultra-low price items across all 14 departments...")
    
    for dept_idx, (dept_name, data) in enumerate(department_data.items(), start=1):
        items = []
        for i in range(1, 51):
            base_keyword = random.choice(data["keywords"])
            item_name = f"Hot Deal {base_keyword} #{i}"
            
            # Temu-style pricing: Super cheap ($1.49 to $16.99) with high original price crossed out
            price = round(random.uniform(1.49, 16.99), 2)
            original_price = round(price * random.uniform(3.0, 5.5), 2)
            discount_percent = int(round((1 - (price / original_price)) * 100))
            
            items.append({
                "item_id": f"dept-{dept_idx}-item-{i}",
                "name": item_name,
                "department": dept_name,
                "price": price,
                "original_price": original_price,
                "discount_percentage": f"{discount_percent}% OFF",
                "image_url": random.choice(data["images"]),
                "description": f"Limited-time flash deal! Top-rated {base_keyword.lower()} hand-selected for unbeatable value at The Fury Zone Studio.",
                "rating": round(random.uniform(4.5, 4.9), 1),
                "sold_count": f"{random.randint(50, 9800)}+ sold",
                "in_stock": True,
                "badge": "Flash Sale 🔥" if i % 3 == 0 else "Best Seller ⭐"
            })
        
        db.departments.update_one(
            {"department_name": dept_name},
            {"$set": {"department_name": dept_name, "items": items, "total_items": 50}},
            upsert=True
        )
        print(f"   -> Populated '{dept_name}' with 50 ultra-discounted items.")

    print("🎉 All 700 items updated with Temu-style pricing, discounts, ratings, and targeted images!")

if __name__ == "__main__":
    seed_database()