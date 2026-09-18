import os
import random
from pymongo import MongoClient

# Connect to your MongoDB database
MONGO_URI = os.getenv("MONGO_URI", "mongodb+srv://cluster.mongodb.net/")
client = MongoClient(MONGO_URI)
db = client.get_database("fury_zone")

def seed_database():
    print("🚀 Starting customized store and chat initialization...")

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

    # 3. Your 14 Custom Departments
    departments = [
        "Apparel (Men's, Women's, Children)",
        "Shoes, Handbags & Accessories",
        "Bed & Bath",
        "Home Decor",
        "Kitchen & Kitchen Supplies",
        "Home & Garden",
        "Tools, Gadgets & Home Improvement",
        "Hobbies & Arts & Crafts (Yarn & Crochet)",
        "Electronics",
        "Jewelry, Gag Gifts & Party Supplies",
        "Wicca & Wicca Supplies",
        "Health & Beauty (Nail Kits & Wellness)",
        "Automotive & E-Bike Supplies",
        "Recreation, E-Bikes & Camping"
    ]

    image_pool = [
        "https://images.unsplash.com/photo-1523275335684-37898b6baf30",
        "https://images.unsplash.com/photo-1505740420928-5e560c06d30e",
        "https://images.unsplash.com/photo-1526170375885-4d8ecf77b99f",
        "https://images.unsplash.com/photo-1542291026-7eec264c27ff",
        "https://images.unsplash.com/photo-1572635196237-14b3f281503f"
    ]

    print("📦 Generating all departments with 50 items each...")
    
    for dept_idx, dept_name in enumerate(departments, start=1):
        items = []
        for i in range(1, 51):
            item_name = f"{dept_name.split('(')[0].strip()} Item #{i}"
            items.append({
                "item_id": f"dept-{dept_idx}-item-{i}",
                "name": item_name,
                "department": dept_name,
                "price": round(random.uniform(9.99, 199.99), 2),
                "image_url": random.choice(image_pool),
                "description": f"Premium selection for {dept_name.lower()}, hand-picked for The Fury Zone Studio.",
                "in_stock": True,
                "featured": i <= 5
            })
        
        db.departments.update_one(
            {"department_name": dept_name},
            {"$set": {"department_name": dept_name, "items": items, "total_items": 50}},
            upsert=True
        )
        print(f"   -> Populated '{dept_name}' with 50 items.")

    print("🎉 All custom departments, 700 items, the resell shop, and 'Chatting with the Peeps' are successfully configured!")

if __name__ == "__main__":
    seed_database()
