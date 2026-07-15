import uuid

from database import db, now_iso


async def create_notification(
    user_id: str,
    title: str,
    message: str,
    notification_type: str = "info",
    link: str = None
):
    notification = {
        "id": str(uuid.uuid4()),
        "user_id": user_id,
        "title": title,
        "message": message,
        "type": notification_type,
        "link": link,
        "read": False,
        "created_at": now_iso(),
    }

    await db.notifications.insert_one(notification)

    return notification


async def log_event(
    event_type: str,
    user_id: str = None,
    data: dict = None
):
    event = {
        "id": str(uuid.uuid4()),
        "event_type": event_type,
        "user_id": user_id,
        "data": data or {},
        "created_at": now_iso(),
    }

    await db.events.insert_one(event)

    return event
