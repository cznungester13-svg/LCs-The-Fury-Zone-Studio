import uuid
import asyncio  # Added to support concurrent execution
from fastapi import APIRouter, HTTPException, Depends, Query
from pydantic import BaseModel, Field
from typing import List, Optional

from database import db, now_iso, NO_ID
from auth import get_current_user, require_roles

router = APIRouter(prefix="/api", tags=["catalog"])


# ---------- Taxonomy ----------
@router.get("/departments")
async def list_departments():
    return await db.departments.find({}, NO_ID).sort("name", 1).to_list(200)


@router.get("/categories")
async def list_categories(department_id: Optional[str] = None):
    q = {"department_id": department_id} if department_id else {}
    return await db.categories.find(q, NO_ID).sort("name", 1).to_list(500)


@router.get("/brands")
async def list_brands():
    return await db.brands.find({}, NO_ID).sort("name", 1).to_list(500)


class DepartmentIn(BaseModel):
    name: str
    slug: Optional[str] = None


@router.post("/departments")
async def create_department(body: DepartmentIn, admin=Depends(require_roles("admin"))):
    doc = {"id": str(uuid.uuid4()), "name": body.name,
           "slug": body.slug or body.name.lower().replace(" ", "-"), "created_at": now_iso()}
    await db.departments.insert_one(doc)
    return {k: v for k, v in doc.items() if k != "_id"}


class CategoryIn(BaseModel):
    name: str
    department_id: str


@router.post("/categories")
async def create_category(body: CategoryIn, admin=Depends(require_roles("admin"))):
    doc = {"id": str(uuid.uuid4()), "name": body.name, "department_id": body.department_id,
           "created_at": now_iso()}
    await db.categories.insert_one(doc)
    return {k: v for k, v in doc.items() if k != "_id"}


class BrandIn(BaseModel):
    name: str


@router.post("/brands")
async def create_brand(body: BrandIn, admin=Depends(require_roles("admin"))):
    doc = {"id": str(uuid.uuid4()), "name": body.name, "created_at": now_iso()}
    await db.brands.insert_one(doc)
    return {k: v for k, v in doc.items() if k != "_id"}


# ---------- Products ----------
class Variant(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    price: float
    stock: int = 0
    sku: Optional[str] = None


class ProductIn(BaseModel):
    title: str
    description: str = ""
    price: float
    department_id: Optional[str] = None
    category_id: Optional[str] = None
    brand_id: Optional[str] = None
    images: List[str] = []
    tags: List[str] = []
    variants: List[Variant] = []
    stock: int = 0
    featured: bool = False


async def _decorate_product(p: dict):
    if p.get("brand_id"):
        b = await db.brands.find_one({"id": p["brand_id"]}, NO_ID)
        p["brand_name"] = b["name"] if b else None
    reviews = await db.reviews.find({"target_id": p["id"], "target_type": "product"}, NO_ID).to_list(1000)
    p["rating"] = round(sum(r["rating"] for r in reviews) / len(reviews), 1) if reviews else 0
    p["review_count"] = len(reviews)
    return p


@router.get("/products")
async def list_products(
    search: Optional[str] = None,
    department_id: Optional[str] = None,
    category_id: Optional[str] = None,
    brand_id: Optional[str] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    featured: Optional[bool] = None,
    sort: str = "newest",
    limit: int = 60,
):
    q = {"is_active": {"$ne": False}}
    if search:
        q["$or"] = [{"title": {"$regex": search, "$options": "i"}},
                    {"description": {"$regex": search, "$options": "i"}},
                    {"tags": {"$regex": search, "$options": "i"}}]
    if department_id:
        q["department_id"] = department_id
    if category_id:
        q["category_id"] = category_id
    if brand_id:
        q["brand_id"] = brand_id
    if featured is not None:
        q["featured"] = featured
    price_q = {}
    if min_price is not None:
        price_q["$gte"] = min_price
    if max_price is not None:
        price_q["$lte"] = max_price
    if price_q:
        q["price"] = price_q
    sort_map = {"newest": ("created_at", -1), "price_asc": ("price", 1),
                "price_desc": ("price", -1)}
    field, direction = sort_map.get(sort, ("created_at", -1))
    
    # --- Performance Fix Applied Here ---
    items = await db.products.find(q, NO_ID).sort(field, direction).to_list(limit)
    
    # Fire all product decoration database calls at the exact same time
    await asyncio.gather(*[_decorate_product(p) for p in items])
    
    return items


@router.get("/products/{product_id}")
async def get_product(product_id: str):
    p = await db.products.find_one({"id": product_id}, NO_ID)
    if not p:
        raise HTTPException(status_code=404, detail="Product not found")
    return await _decorate_product(p)


@router.post("/products")
async def create_product(body: ProductIn, admin=Depends(require_roles("admin"))):
    doc = body.model_dump()
    doc["id"] = str(uuid.uuid4())
    doc["is_active"] = True
    doc["created_at"] = now_iso()
    await db.products.insert_one(doc)
    await db.inventory.insert_one({
        "id": str(uuid.uuid4()), "product_id": doc["id"],
        "stock": doc["stock"], "reserved": 0, "updated_at": now_iso(),
    })
    return {k: v for k, v in doc.items() if k != "_id"}


@router.put("/products/{product_id}")
async def update_product(product_id: str, body: ProductIn, admin=Depends(require_roles("admin"))):
    res = await db.products.update_one({"id": product_id}, {"$set": body.model_dump()})
    if res.matched_count == 0:
        raise HTTPException(status_code=404, detail="Product not found")
    return await db.products.find_one({"id": product_id}, NO_ID)


@router.delete("/products/{product_id}")
async def delete_product(product_id: str, admin=Depends(require_roles("admin"))):
    await db.products.update_one({"id": product_id}, {"$set": {"is_active": False}})
    return {"ok": True}


# ---------- Reviews ----------
class ReviewIn(BaseModel):
    target_id: str
    target_type: str = "product"  # product | listing
    rating: int = Field(ge=1, le=5)
    comment: str = ""


@router.get("/reviews")
async def list_reviews(target_id: str):
    return await db.reviews.find({"target_id": target_id}, NO_ID).sort("created_at", -1).to_list(500)


@router.post("/reviews")
async def create_review(body: ReviewIn, user: dict = Depends(get_current_user)):
    doc = {
        "id": str(uuid.uuid4()),
        "target_id": body.target_id,
        "target_type": body.target_type,
        "rating": body.rating,
        "comment": body.comment,
        "user_id": user["id"],
        "user_name": user.get("full_name", "User"),
        "created_at": now_iso(),
    }
    await db.reviews.insert_one(doc)
    return {k: v for k, v in doc.items() if k != "_id"}
