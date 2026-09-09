import random
from database import db, now_iso


async def update_catalog():
    """
    Updates existing catalog products with:
    - lower customer-friendly pricing
    - original price
    - discount percentage
    - ratings
    - sold counts
    """

    products = await db.products.find({}).to_list(length=None)

    if not products:
        print("No products found.")
        return

    updated = 0

    for product in products:
        price = product.get("price", 0)

        # Create original price if it does not exist
        original_price = product.get(
            "original_price",
            round(price * 1.35, 2)
        )

        # Add Temu-style shopping data
        update = {
            "original_price": original_price,
            "discount_percent": round(
                ((original_price - price) / original_price) * 100
            ),
            "rating": product.get(
                "rating",
                round(random.uniform(4.3, 5.0), 1)
            ),
            "sold_count": product.get(
                "sold_count",
                random.randint(50, 5000)
            ),
            "updated_at": now_iso(),
        }

        # Lower only expensive items
        if price > 100:
            new_price = round(price * 0.60, 2)

            update["price"] = new_price

            if "variants" in product:
                update["variants"] = [
                    {
                        **variant,
                        "price": new_price
                    }
                    for variant in product["variants"]
                ]

        await db.products.update_one(
            {"id": product["id"]},
            {"$set": update}
        )

        updated += 1

    print(f"Updated {updated} products successfully.")


if __name__ == "__main__":
    import asyncio
    asyncio.run(update_catalog())
