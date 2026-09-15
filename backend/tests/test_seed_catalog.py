import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from seed import get_product_images, resolve_product_department


def test_get_product_images_matches_jewelry_keywords():
    urls = get_product_images(
        "Celestial Gold Ring Set",
        "Handcrafted sterling silver ring with a polished finish for elegant styling.",
        "Jewelry",
        "Accessories",
    )

    assert urls
    assert any("ring" in url.lower() for url in urls)


def test_non_craft_items_are_not_assigned_to_crafts_department():
    assert resolve_product_department(
        "UV-400 Protection Classic Sunglasses",
        "Lightweight polarized sunglasses for outdoor wear.",
        "Handbags & Accessories",
        "Sunglasses",
    ) == "Shoes, Handbags & Accessories"

    assert resolve_product_department(
        "Classic Designer-Style Tote Handbag",
        "Spacious vegan leather tote with a structured silhouette.",
        "Handbags & Accessories",
        "Bags",
    ) == "Shoes, Handbags & Accessories"

    assert resolve_product_department(
        "Premium Acrylic Crochet Yarn Pack",
        "A rich assortment of yarn colors for crochet projects and handmade décor.",
        "Arts, Crafts & Hobbies",
        "Crochet & Yarn",
    ) == "Hobbies, Arts & Crafts"
