import secrets
import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException

from auth import get_current_user, require_roles
from database import db, now_iso, NO_ID

router = APIRouter(prefix="/raffle", tags=["raffle"])
PRIZES = ["$50 Fury Zone gift card", "Mystery Fury Zone prize", "Free shipping for a month"]


def current_week():
    now = datetime.now(timezone.utc)
    return f"{now.isocalendar().year}-W{now.isocalendar().week:02d}"


async def get_or_create_raffle():
    week = current_week()
    raffle = await db.raffles.find_one({"week": week}, NO_ID)
    if raffle:
        return raffle
    raffle = {
        "id": str(uuid.uuid4()), "week": week, "name": "Weekly Fury Zone Raffle",
        "prize": PRIZES[datetime.now(timezone.utc).isocalendar().week % len(PRIZES)],
        "status": "open", "winner_id": None, "created_at": now_iso(),
    }
    await db.raffles.insert_one(raffle)
    return raffle


@router.get("/current")
async def current_raffle():
    raffle = await get_or_create_raffle()
    entries = await db.raffle_entries.count_documents({"raffle_id": raffle["id"]})
    return {**raffle, "entry_count": entries}


@router.post("/enter")
async def enter_raffle(user: dict = Depends(get_current_user)):
    raffle = await get_or_create_raffle()
    if raffle["status"] != "open":
        raise HTTPException(status_code=400, detail="This raffle is closed")
    existing = await db.raffle_entries.find_one({"raffle_id": raffle["id"], "user_id": user["id"]})
    if existing:
        return {"entered": True, "already_entered": True}
    await db.raffle_entries.insert_one({
        "id": str(uuid.uuid4()), "raffle_id": raffle["id"],
        "user_id": user["id"], "created_at": now_iso(),
    })
    return {"entered": True, "already_entered": False}


@router.post("/draw")
async def draw_raffle(admin: dict = Depends(require_roles("admin"))):
    raffle = await get_or_create_raffle()
    if raffle["status"] != "open":
        raise HTTPException(status_code=400, detail="This raffle is already closed")
    entries = await db.raffle_entries.find({"raffle_id": raffle["id"]}, NO_ID).to_list(100000)
    winner = secrets.choice(entries) if entries else None
    await db.raffles.update_one(
        {"id": raffle["id"]},
        {"$set": {"status": "drawn", "winner_id": winner["user_id"] if winner else None, "drawn_at": now_iso()}},
    )
    return {"raffle_id": raffle["id"], "winner_id": winner["user_id"] if winner else None, "prize": raffle["prize"]}
