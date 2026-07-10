import uuid
import asyncio
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field
from typing import Optional

from database import db, now_iso, NO_ID
from auth import require_roles
from notify import create_notification

router = APIRouter(prefix="/api/admin", tags=["admin"])

VALID_STATUSES = ["pending", "paid", "shipped", "delivered", "cancelled", "refunded"]


@router.get("/metrics")
async def metrics(admin=Depends(require_roles("admin"))):
    # Optimize Revenue via Native Database Aggregation
    pipeline = [
        {"$match": {"status": {"$nin": ["refunded", "cancelled"]}}},
        {"$group": {"_id": None, "total_revenue": {"$sum": "$total"}}}
    ]
    revenue_cursor = await db.orders.aggregate(pipeline).to_list(1)
    revenue = revenue_cursor[0]["total_revenue"] if revenue_cursor else 0.0

    # Optimize Commissions via Native Database Aggregation
    comm_pipeline = [
        {"$group": {"_id": None, "total_comm": {"$sum": "$commission"}}}
    ]
    comm_cursor = await db.commissions.aggregate(comm_pipeline).to_list(1)
