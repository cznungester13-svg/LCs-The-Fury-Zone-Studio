"""Automated catalog generator for LC's The Fury Zone.
Generates 50+ products per department, each mapped to a category-matching product image."""
import hashlib


def _u(pid):
    return f"https://images.unsplash.com/photo-{pid}?auto=format&fit=crop&w=800&q=80"


def _px(pid):
    return f"https://images.pexels.com/photos/{pid}/pexels-photo-{pid}.jpeg?auto=compress&cs=tinysrgb&w=800"


def _h(s):
    return int(hashlib.md5(s.encode()).hexdigest(), 16)


DEPARTMENTS = [
    {"id": "apparel", "name": "Apparel & Shoes", "image": _u("1441984904996-e0b6ba687e04")},
    {"id": "home_garden", "name": "Home & Garden", "image": _u("1617806265182-7b3f847f0b75")},
    {"id": "bed_bath", "name": "Bed & Bath", "image": _u("1634665810235-011d663754e7")},
    {"id": "kitchen", "name": "Kitchen & Appliances", "image": _u("1608354580875-30bd4168b351")},
    {"id": "arts_crafts", "name": "Arts & Crafts", "image": _u("1513364776144-60967b0f800f")},
    {"id": "beauty", "name": "Health & Beauty", "image": _u("1522335789203-aabd1fc54bc9")},
    {"id": "electronics", "name": "Electronics", "image": _u("1618366712010-f4ae9c647dcb")},
    {"id": "pets", "name": "Pets & Supplies", "image": _px("7615529")},
    {"id": "jewelry", "name": "Jewelry", "image": _px("28976815")},
]

# Each type: (product_noun, [images], (price_lo, price_hi), [descriptor tags])
TYPES = {
    "apparel": [
        ("Men's Crew T-Shirt", [_u("1571455786673-9d9d6c194f90"), _u("1678872844677-d650b788709b"), _u("1503341338985-c0477be52513")], (9, 24)),
        ("Women's Summer Dress", [_u("1496747611176-843222e1e57c"), _u("1657373307141-349a3393d4d9"), _u("1721990336298-90832e791b5a"), _u("1567966456076-905a50a06d8c")], (14, 39)),
        ("Kids' Outfit Set", [_u("1566454544259-f4b94c3d758c"), _u("1560859259-fcf2b952aed8"), _u("1758782213532-bbb5fd89885e"), _u("1685770101390-58e99f56202e")], (10, 28)),
        ("Leather Handbag", [_u("1548036328-c9fa89d128fa"), _u("1546241183-0ed3f8a4a824"), _u("1524679813234-66a389fe1a42"), _px("9327162"), _px("4830924"), _px("7953286")], (24, 69)),
        ("Women's Heels", [_u("1769787147452-921f573829bd"), _u("1621996659490-3275b4d0d951"), _u("1553808373-b2c5b7ddb117"), _u("1534653299134-96a171b61581")], (19, 49)),
        ("Denim Jeans", [_u("1637069585336-827b298fe84a"), _u("1721637286605-ae9be19d681f"), _u("1602293589930-45aad59ba3ab"), _u("1714729382668-7bc3bb261662")], (18, 44)),
        ("Pullover Hoodie", [_u("1564557287817-3785e38ec1f5"), _u("1609873814058-a8928924184a"), _u("1620799140188-3b2a02fd9a77"), _px("7479825")], (16, 39)),
        ("Court Sneakers", [_u("1608231387042-66d1773070a5"), _u("1560769629-975ec94e6a86"), _u("1600185365926-3a2ce3cdb9eb")], (22, 54)),
        ("Everyday Backpack", [_u("1622560480605-d83c853bc5c3"), _u("1577733975197-3b950ca5cabe"), _u("1622560480654-d96214fdc887")], (19, 48)),
        ("Polarized Sunglasses", [_u("1572635196237-14b3f281503f"), _u("1584036553516-bf83210aa16c"), _u("1577803645773-f96470509666")], (12, 34)),
    ],
    "home_garden": [
        ("Indoor Potted Plant", [_px("5825393"), _px("5598263")], (12, 34)),
        ("Garden Tool Set", [_px("3971211"), _px("11397558"), _px("9507250"), _px("6231715"), _px("8543388"), _px("9507245")], (14, 42)),
        ("Patio Furniture", [_u("1560990883-9b76fec399a9"), _u("1768527339600-3127e34acdad"), _u("1613317447829-eea2ed59640f"), _px("238385"), _px("10032378")], (39, 89)),
        ("Woven Area Rug", [_u("1594040226829-7f251ab46d80"), _u("1572123979839-3749e9973aba"), _u("1534889156217-d643df14f14a"), _px("34601066")], (24, 64)),
        ("Home Decor Piece", [_u("1617806265182-7b3f847f0b75"), _u("1633505899118-4ca6bd143043"), _u("1583847268964-b28dc8f51f92")], (15, 45)),
        ("Scented Soy Candle", [_u("1603905179139-db12ab535ca9"), _u("1572726729207-a78d6feb18d7")], (9, 28)),
    ],
    "bed_bath": [
        ("Cotton Bed Sheet Set", [_u("1634665810235-011d663754e7"), _u("1596433904500-97b901c5d274"), _u("1587614977104-693ef4e858e4")], (19, 49)),
        ("Bath Towel Set", [_u("1523471826770-c437b4636fe6"), _u("1574421233376-06f2ccf017f7"), _u("1638232928539-6e91c47ddec5"), _px("45980"), _px("7691101")], (12, 34)),
        ("Throw Pillow", [_u("1629949009765-40fc74c9ec21"), _u("1691256676366-370303d55b61"), _u("1629949009710-2df14c41a72e")], (9, 26)),
    ],
    "kitchen": [
        ("Coffee Maker", [_u("1608354580875-30bd4168b351"), _u("1680539882932-559b099446cc"), _u("1635749269192-489bdda05932")], (29, 79)),
        ("Toaster Oven", [_u("1738898101611-2a9a3d4c75b5")], (24, 59)),
        ("Countertop Blender", [_u("1585237672814-8f85a8118bf6"), _px("12689255"), _px("19599327")], (22, 64)),
        ("Cookware Set", [_u("1584990347193-6bebebfeaeee"), _u("1518291344630-4857135fb581")], (34, 84)),
        ("Ceramic Mug Set", [_u("1590422749897-47036da0b0ff"), _u("1643946404043-178456b0e3f8"), _u("1516390118834-21602d501886")], (11, 29)),
    ],
    "arts_crafts": [
        ("Paint Brush Set", [_u("1513364776144-60967b0f800f"), _px("12181027"), _px("5357091")], (8, 28)),
        ("Knitting Yarn Bundle", [_u("1584992236310-6edddc08acff"), _u("1595341595379-cf1cb694ea1f"), _u("1550376026-7375b92bb318")], (7, 24)),
        ("Handmade Pottery", [_u("1589051079002-b140a970f568"), _u("1649810617979-16001a60c89c"), _u("1630509866796-192affe5e971")], (18, 52)),
    ],
    "beauty": [
        ("Facial Serum", [_u("1713768704571-6aeb0d0e5105"), _u("1613803745799-ba6c10aace85"), _u("1679394270597-e90694d70350")], (12, 38)),
        ("Makeup Kit", [_u("1522335789203-aabd1fc54bc9"), _u("1596462502278-27bfdc403348"), _u("1512496015851-a90fb38ba796")], (14, 44)),
        ("Eau de Parfum", [_u("1523293182086-7651a899d37f"), _u("1615634260167-c8cdede054de"), _u("1458538977777-0549b2370168"), _px("21008941"), _px("20591858")], (19, 59)),
        ("Hair Care Bottle", [_u("1597931752949-98c74b5b159f"), _u("1701992678972-d5a053ad0fb0"), _u("1747858989102-cca0f4dc4a11"), _px("13516802"), _px("8467957")], (9, 29)),
    ],
    "electronics": [
        ("Wireless Headphones", [_u("1618366712010-f4ae9c647dcb"), _u("1628329567705-f8f7150c3cff"), _u("1612858249937-1cc0852093dd"), _u("1641048930621-ab5d225ae5b0")], (29, 89)),
        ("Smartwatch", [_u("1557935728-e6d1eaabe558"), _u("1434494878577-86c23bcb06b9"), _u("1508685096489-7aacd43bd3b1"), _px("18662969")], (34, 89)),
        ("Bluetooth Speaker", [_u("1608043152269-423dbba4e7e1")], (19, 64)),
        ("Wireless Earbuds", [_px("14741306"), _px("3921827")], (18, 59)),
        ("Tech Accessory Kit", [_u("1615655406736-b37c4fabf923")], (14, 49)),
    ],
    "pets": [
        ("Dog Plush Toy", [_px("14084426"), _px("11110936")], (7, 22)),
        ("Cozy Pet Bed", [_px("7615529"), _u("1541188495357-ad2dc89487f4"), _u("1573682127988-f67136e7f12a"), _px("11060021"), _u("1532968165171-2bd36064c6a0")], (16, 44)),
    ],
    "jewelry": [
        ("Gold Necklace", [_px("28976815"), _px("4735885")], (24, 69)),
        ("Diamond-Cut Ring", [_px("2849742"), _px("5737315"), _u("1626784215021-2e39ccf971cd")], (19, 64)),
        ("Statement Earrings", [_u("1475179593777-bd12fd56b85d"), _px("5370644"), _px("5497303")], (14, 44)),
        ("Charm Bracelet", [_u("1629224316810-9d8805b95e76")], (12, 39)),
        ("Classic Watch", [_u("1523275335684-37898b6baf30"), _u("1542496658-e33a6d0d50f6"), _u("1524592094714-0f0654e20314")], (29, 79)),
    ],
}

BRANDS = ["FuryLine", "Nova", "Urban Co.", "Everlane", "Aура", "Peak", "Loft", "Maker's", "Vanta", "Zenith", "Harbor", "Meadow", "Craftly", "Studio 9", "Northbound"]
ADJ = ["Classic", "Premium", "Everyday", "Signature", "Deluxe", "Essential", "Modern", "Vintage", "Cozy", "Pro", "Ultra", "Soft", "Bold", "Luxe", "Eco"]
COLORS = ["Black", "White", "Navy", "Sand", "Sage", "Charcoal", "Ivory", "Olive", "Blush", "Slate", "Terracotta", "Stone"]
DISCOUNTS = [0.15, 0.2, 0.25, 0.3, 0.4]

PER_DEPARTMENT = 56


def _price(seed, lo, hi):
    dollars = lo + (seed % max(1, (hi - lo)))
    return round(dollars + 0.99, 2)


def generate_products():
    products = []
    for dept in DEPARTMENTS:
        dept_id = dept["id"]
        types = TYPES[dept_id]
        idx = 0
        while len([p for p in products if p["category"] == dept_id]) < PER_DEPARTMENT:
            t = types[idx % len(types)]
            noun, imgs, (lo, hi) = t
            n = idx // len(types)
            seed = _h(f"{dept_id}-{noun}-{n}")
            brand = BRANDS[seed % len(BRANDS)]
            adj = ADJ[(seed // 7) % len(ADJ)]
            color = COLORS[(seed // 13) % len(COLORS)]
            price = _price(seed, lo, hi)
            has_deal = (seed % 10) < 3
            original = round(price / (1 - DISCOUNTS[seed % len(DISCOUNTS)]), 2) if has_deal else None
            badge = None
            if has_deal:
                badge = "Deal"
            elif seed % 11 == 0:
                badge = "Best Seller"
            elif seed % 17 == 0:
                badge = "New"
            pid = f"{dept_id}-{idx}"
            name = f"{brand} {adj} {color} {noun}"
            products.append({
                "id": pid,
                "name": name,
                "category": dept_id,
                "price": price,
                "original_price": original,
                "rating": round(4.2 + (seed % 8) * 0.1, 1),
                "reviews": 12 + (seed % 3800),
                "seller": brand,
                "image": imgs[n % len(imgs)],
                "description": f"{adj} {color.lower()} {noun.lower()} from {brand}. Quality-checked, ships fast, and backed by our 30-day happiness guarantee. Free shipping on orders over $50.",
                "badge": badge,
                "stock": 15 + (seed % 120),
            })
            idx += 1
    return products


def category_counts(products):
    counts = {}
    for p in products:
        counts[p["category"]] = counts.get(p["category"], 0) + 1
    return counts
