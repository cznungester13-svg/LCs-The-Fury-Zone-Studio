"""Product catalog seed data + generator for LC Multi-Dept Resale Marketplace."""
import random

# 6 departments, each seeded with exactly 50 items.
DEPARTMENTS = [
    {
        "slug": "fashion",
        "name": "Fashion & Apparel",
        "tagline": "Pre-loved threads. Wear it again.",
        "images": [
            "https://images.pexels.com/photos/6069961/pexels-photo-6069961.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
            "https://images.unsplash.com/photo-1647664856968-880b8eccd588?crop=entropy&cs=srgb&fm=jpg&ixid=M3w4NTYxOTF8MHwxfHNlYXJjaHwzfHx2aW50YWdlJTIwdGhyaWZ0JTIwY2xvdGhpbmclMjBmYXNoaW9ufGVufDB8fHx8MTc4NzY4OTIxM3ww&ixlib=rb-4.1.0&q=85",
            "https://images.unsplash.com/photo-1521335629791-ce4aec67dd15?crop=entropy&cs=srgb&fm=jpg&ixid=M3w4NTYxOTF8MHwxfHNlYXJjaHwyfHx2aW50YWdlJTIwdGhyaWZ0JTIwY2xvdGhpbmclMjBmYXNoaW9ufGVufDB8fHx8MTc4NzY4OTIxM3ww&ixlib=rb-4.1.0&q=85",
            "https://images.unsplash.com/photo-1543436115-0d6fbe97ece0?crop=entropy&cs=srgb&fm=jpg&ixid=M3w4NTYxOTF8MHwxfHNlYXJjaHw0fHx2aW50YWdlJTIwdGhyaWZ0JTIwY2xvdGhpbmclMjBmYXNoaW9ufGVufDB8fHx8MTc4NzY4OTIxM3ww&ixlib=rb-4.1.0&q=85",
            "https://images.pexels.com/photos/16729452/pexels-photo-16729452.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
            "https://images.unsplash.com/photo-1520006403909-838d6b92c22e?crop=entropy&cs=srgb&fm=jpg&ixid=M3w4NTYxOTF8MHwxfHNlYXJjaHwxfHx2aW50YWdlJTIwdGhyaWZ0JTIwY2xvdGhpbmclMjBmYXNoaW9ufGVufDB8fHx8MTc4NzY4OTIxM3ww&ixlib=rb-4.1.0&q=85",
        ],
        "items": [
            "Vintage Denim Jacket", "Retro Band Tee", "Flannel Shirt", "Corduroy Pants",
            "Wool Overcoat", "Leather Bomber", "Graphic Hoodie", "Pleated Skirt",
            "Cardigan Sweater", "Windbreaker", "Cargo Pants", "Silk Blouse",
            "Denim Overalls", "Trench Coat", "Knit Beanie", "Plaid Scarf",
        ],
    },
    {
        "slug": "electronics",
        "name": "Electronics",
        "tagline": "Refurbished tech that still slaps.",
        "images": [
            "https://images.unsplash.com/photo-1550745165-9bc0b252726f?crop=entropy&cs=srgb&fm=jpg&ixid=M3w4NjAzMjd8MHwxfHNlYXJjaHwxfHx1c2VkJTIwcmV0cm8lMjBlbGVjdHJvbmljcyUyMGdhZGdldHN8ZW58MHx8fHwxNzg3Njg5MjEzfDA&ixlib=rb-4.1.0&q=85",
            "https://images.unsplash.com/photo-1573399054516-90665ecc44be?crop=entropy&cs=srgb&fm=jpg&ixid=M3w4NjAzMjd8MHwxfHNlYXJjaHwyfHx1c2VkJTIwcmV0cm8lMjBlbGVjdHJvbmljcyUyMGdhZGdldHN8ZW58MHx8fHwxNzg3Njg5MjEzfDA&ixlib=rb-4.1.0&q=85",
            "https://images.unsplash.com/photo-1697465379722-98040bb9c509?crop=entropy&cs=srgb&fm=jpg&ixid=M3w4NjAzMjd8MHwxfHNlYXJjaHwzfHx1c2VkJTIwcmV0cm8lMjBlbGVjdHJvbmljcyUyMGdhZGdldHN8ZW58MHx8fHwxNzg3Njg5MjEzfDA&ixlib=rb-4.1.0&q=85",
            "https://images.pexels.com/photos/5744291/pexels-photo-5744291.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
            "https://images.unsplash.com/photo-1623969451926-10c5e52b707a?crop=entropy&cs=srgb&fm=jpg&ixid=M3w4NjAzMjd8MHwxfHNlYXJjaHw0fHx1c2VkJTIwcmV0cm8lMjBlbGVjdHJvbmljcyUyMGdhZGdldHN8ZW58MHx8fHwxNzg3Njg5MjEzfDA&ixlib=rb-4.1.0&q=85",
            "https://images.pexels.com/photos/5744289/pexels-photo-5744289.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
        ],
        "items": [
            "Retro Game Console", "CRT Television", "Portable Cassette Player", "Vintage Radio",
            "Classic MP3 Player", "Film Camera", "Boombox Speaker", "Handheld Console",
            "Turntable Player", "Desktop Monitor", "Wired Headphones", "Alarm Clock Radio",
            "Pocket Calculator", "Walkie Talkie Set", "Mini Amplifier", "Digital Camera",
        ],
    },
    {
        "slug": "home",
        "name": "Home & Decor",
        "tagline": "Give old treasures a new room.",
        "images": [
            "https://images.unsplash.com/photo-1572950588591-00baf1832071?crop=entropy&cs=srgb&fm=jpg&ixid=M3w4NjA3MDR8MHwxfHNlYXJjaHwzfHxzZWNvbmQlMjBoYW5kJTIwaG9tZSUyMGRlY29yJTIwdGhyaWZ0fGVufDB8fHx8MTc4NzY4OTIxM3ww&ixlib=rb-4.1.0&q=85",
            "https://images.unsplash.com/photo-1600078307129-97e9d51d19cc?crop=entropy&cs=srgb&fm=jpg&ixid=M3w4NjA3MDR8MHwxfHNlYXJjaHwyfHxzZWNvbmQlMjBoYW5kJTIwaG9tZSUyMGRlY29yJTIwdGhyaWZ0fGVufDB8fHx8MTc4NzY4OTIxM3ww&ixlib=rb-4.1.0&q=85",
            "https://images.unsplash.com/photo-1613837233238-c1e78d8b8f07?crop=entropy&cs=srgb&fm=jpg&ixid=M3w4NjA3MDR8MHwxfHNlYXJjaHwxfHxzZWNvbmQlMjBoYW5kJTIwaG9tZSUyMGRlY29yJTIwdGhyaWZ0fGVufDB8fHx8MTc4NzY4OTIxM3ww&ixlib=rb-4.1.0&q=85",
            "https://images.unsplash.com/photo-1720370048021-eb1df3446335?crop=entropy&cs=srgb&fm=jpg&ixid=M3w4NjA3MDR8MHwxfHNlYXJjaHw0fHxzZWNvbmQlMjBoYW5kJTIwaG9tZSUyMGRlY29yJTIwdGhyaWZ0fGVufDB8fHx8MTc4NzY4OTIxM3ww&ixlib=rb-4.1.0&q=85",
            "https://images.pexels.com/photos/30163749/pexels-photo-30163749.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
            "https://images.pexels.com/photos/14020942/pexels-photo-14020942.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
        ],
        "items": [
            "Ceramic Table Lamp", "Wooden Rocking Chair", "Vintage Wall Clock", "Woven Basket",
            "Brass Candle Holder", "Framed Art Print", "Retro Side Table", "Glass Vase",
            "Patterned Throw Rug", "Antique Mirror", "Storage Trunk", "Decorative Bowl",
            "Bookend Set", "Floor Cushion", "Ceramic Planter", "Wall Tapestry",
        ],
    },
    {
        "slug": "books",
        "name": "Books & Media",
        "tagline": "Cracked spines, endless stories.",
        "images": [
            "https://images.unsplash.com/photo-1550399105-c4db5fb85c18?crop=entropy&cs=srgb&fm=jpg&ixid=M3w4NTYxODd8MHwxfHNlYXJjaHwzfHx1c2VkJTIwYm9va3MlMjBzdGFjayUyMHNlY29uZGhhbmR8ZW58MHx8fHwxNzg3Njg5MjEzfDA&ixlib=rb-4.1.0&q=85",
            "https://images.unsplash.com/photo-1495446815901-a7297e633e8d?crop=entropy&cs=srgb&fm=jpg&ixid=M3w4NTYxODd8MHwxfHNlYXJjaHwyfHx1c2VkJTIwYm9va3MlMjBzdGFjayUyMHNlY29uZGhhbmR8ZW58MHx8fHwxNzg3Njg5MjEzfDA&ixlib=rb-4.1.0&q=85",
            "https://images.unsplash.com/photo-1497633762265-9d179a990aa6?crop=entropy&cs=srgb&fm=jpg&ixid=M3w4NTYxODd8MHwxfHNlYXJjaHwxfHx1c2VkJTIwYm9va3MlMjBzdGFjayUyMHNlY29uZGhhbmR8ZW58MHx8fHwxNzg3Njg5MjEzfDA&ixlib=rb-4.1.0&q=85",
            "https://images.unsplash.com/photo-1519682337058-a94d519337bc?crop=entropy&cs=srgb&fm=jpg&ixid=M3w4NTYxODd8MHwxfHNlYXJjaHw0fHx1c2VkJTIwYm9va3MlMjBzdGFjayUyMHNlY29uZGhhbmR8ZW58MHx8fHwxNzg3Njg5MjEzfDA&ixlib=rb-4.1.0&q=85",
            "https://images.pexels.com/photos/5009160/pexels-photo-5009160.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
            "https://images.pexels.com/photos/5009227/pexels-photo-5009227.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
        ],
        "items": [
            "Classic Paperback Novel", "Hardcover Anthology", "Poetry Collection", "Sci-Fi Trilogy",
            "Mystery Thriller", "Vintage Comic Bundle", "Cookbook Edition", "History Volume",
            "Travel Guidebook", "Illustrated Fairy Tales", "Graphic Novel", "Reference Encyclopedia",
            "Self-Help Bestseller", "Fantasy Epic", "Biography Memoir", "Art Book",
        ],
    },
    {
        "slug": "sports",
        "name": "Sports & Outdoors",
        "tagline": "Gear up for less. Way less.",
        "images": [
            "https://images.unsplash.com/photo-1493244040629-496f6d136cc4?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NDQ2NDN8MHwxfHNlYXJjaHwzfHx1c2VkJTIwc3BvcnRzJTIwZXF1aXBtZW50JTIwb3V0ZG9vciUyMGdlYXJ8ZW58MHx8fHwxNzg3Njg5MjEzfDA&ixlib=rb-4.1.0&q=85",
            "https://images.unsplash.com/photo-1485809052957-5113b0ff51af?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NDQ2NDN8MHwxfHNlYXJjaHwxfHx1c2VkJTIwc3BvcnRzJTIwZXF1aXBtZW50JTIwb3V0ZG9vciUyMGdlYXJ8ZW58MHx8fHwxNzg3Njg5MjEzfDA&ixlib=rb-4.1.0&q=85",
            "https://images.unsplash.com/photo-1653681498612-37ec55093e29?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NDQ2NDN8MHwxfHNlYXJjaHwyfHx1c2VkJTIwc3BvcnRzJTIwZXF1aXBtZW50JTIwb3V0ZG9vciUyMGdlYXJ8ZW58MHx8fHwxNzg3Njg5MjEzfDA&ixlib=rb-4.1.0&q=85",
            "https://images.pexels.com/photos/163390/baseball-ball-box-sports-163390.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
            "https://images.unsplash.com/photo-1596055746427-d5f61aa5df99?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NDQ2NDN8MHwxfHNlYXJjaHw0fHx1c2VkJTIwc3BvcnRzJTIwZXF1aXBtZW50JTIwb3V0ZG9vciUyMGdlYXJ8ZW58MHx8fHwxNzg3Njg5MjEzfDA&ixlib=rb-4.1.0&q=85",
            "https://images.pexels.com/photos/26890727/pexels-photo-26890727.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
        ],
        "items": [
            "Hiking Backpack", "Baseball Glove", "Golf Club Set", "Camping Tent",
            "Yoga Mat", "Tennis Racket", "Mountain Bike Helmet", "Dumbbell Pair",
            "Sleeping Bag", "Basketball", "Skateboard Deck", "Fishing Rod",
            "Trekking Poles", "Boxing Gloves", "Soccer Cleats", "Climbing Harness",
        ],
    },
    {
        "slug": "toys",
        "name": "Toys & Games",
        "tagline": "Nostalgia by the boxful.",
        "images": [
            "https://images.unsplash.com/photo-1645342224134-c52883591cf6?crop=entropy&cs=srgb&fm=jpg&ixid=M3w4NTYxOTB8MHwxfHNlYXJjaHwzfHx2aW50YWdlJTIwdG95cyUyMGJvYXJkJTIwZ2FtZXMlMjBjb2xsZWN0aWJsZXN8ZW58MHx8fHwxNzg3Njg5MjEzfDA&ixlib=rb-4.1.0&q=85",
            "https://images.unsplash.com/photo-1637120149073-54319e6f9fc3?crop=entropy&cs=srgb&fm=jpg&ixid=M3w4NTYxOTB8MHwxfHNlYXJjaHwxfHx2aW50YWdlJTIwdG95cyUyMGJvYXJkJTIwZ2FtZXMlMjBjb2xsZWN0aWJsZXN8ZW58MHx8fHwxNzg3Njg5MjEzfDA&ixlib=rb-4.1.0&q=85",
            "https://images.unsplash.com/photo-1769288361254-abb4783a6070?crop=entropy&cs=srgb&fm=jpg&ixid=M3w4NTYxOTB8MHwxfHNlYXJjaHwyfHx2aW50YWdlJTIwdG95cyUyMGJvYXJkJTIwZ2FtZXMlMjBjb2xsZWN0aWJsZXN8ZW58MHx8fHwxNzg3Njg5MjEzfDA&ixlib=rb-4.1.0&q=85",
            "https://images.unsplash.com/photo-1688126674706-bf7e1c027203?crop=entropy&cs=srgb&fm=jpg&ixid=M3w4NTYxOTB8MHwxfHNlYXJjaHw0fHx2aW50YWdlJTIwdG95cyUyMGJvYXJkJTIwZ2FtZXMlMjBjb2xsZWN0aWJsZXN8ZW58MHx8fHwxNzg3Njg5MjEzfDA&ixlib=rb-4.1.0&q=85",
            "https://images.pexels.com/photos/9078167/pexels-photo-9078167.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
            "https://images.pexels.com/photos/35285848/pexels-photo-35285848.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
        ],
        "items": [
            "Classic Board Game", "Collectible Action Figure", "Wooden Puzzle", "Vintage Doll",
            "Building Block Set", "Toy Race Car", "Plush Teddy Bear", "Card Game Deck",
            "Retro Arcade Toy", "Marble Run Kit", "Stuffed Animal", "Model Train Car",
            "Spinning Top Set", "Dinosaur Figurine", "Play Kitchen Set", "Rubik's Style Cube",
        ],
    },
]

CONDITIONS = ["Like New", "Gently Used", "Well Loved", "Vintage", "Refurbished"]
QUALIFIERS = ["Retro", "Classic", "Vintage", "Pre-Loved", "Thrifted", "Salvaged", "Reclaimed", "Rare"]


def _price(rng):
    # aggressively low resale prices
    return round(rng.choice([0.99, 1.49, 1.99, 2.50, 2.99, 3.49, 3.99, 4.50, 4.99,
                             5.99, 6.99, 7.50, 8.99, 9.99, 11.00, 12.99, 14.50, 16.99, 19.99]), 2)


def generate_products():
    """Deterministically generate exactly 50 items per department (300 total)."""
    rng = random.Random(42)
    products = []
    for dept in DEPARTMENTS:
        for i in range(50):
            base = dept["items"][i % len(dept["items"])]
            qual = QUALIFIERS[i % len(QUALIFIERS)]
            name = f"{qual} {base} #{i + 1:02d}"
            img = dept["images"][i % len(dept["images"])]
            condition = CONDITIONS[i % len(CONDITIONS)]
            price = _price(rng)
            orig = round(price * rng.uniform(1.6, 3.0), 2)
            products.append({
                "name": name,
                "department": dept["slug"],
                "department_name": dept["name"],
                "category": base,
                "condition": condition,
                "price": price,
                "original_price": orig,
                "image": img,
                "sku": f"{dept['slug'][:3].upper()}-{i + 1:03d}",
                "description": f"{condition} {base.lower()} in solid shape. A genuine thrift-store find rescued and priced to move. Grab this {qual.lower()} piece before someone else does.",
                "stock": rng.randint(1, 12),
                "rating": round(rng.uniform(3.6, 5.0), 1),
            })
    return products


def department_meta():
    return [
        {"slug": d["slug"], "name": d["name"], "tagline": d["tagline"], "image": d["images"][0]}
        for d in DEPARTMENTS
    ]
