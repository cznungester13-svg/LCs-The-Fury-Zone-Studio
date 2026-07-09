import os
import uuid
import httpx
import logging
from pathlib import Path
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends, Response
from typing import List

from database import db, now_iso, NO_ID
from auth import get_current_user

logger = logging.getLogger(__name__)

STORAGE_URL = "https://integrations.emergentagent.com/objstore/api/v1/storage"
EMERGENT_KEY = os.environ.get("EMERGENT_LLM_KEY")
APP_NAME = "furyzone"

storage_key = None

MIME_TYPES = {
    "jpg": "image/jpeg", "jpeg": "image/jpeg", "png": "image/png",
    "gif": "image/gif", "webp": "image/webp",
}

router = APIRouter(prefix="/api", tags=["files"])


async def init_storage_async(client: httpx.AsyncClient):
    global storage_key
    if storage_key:
        return storage_key
    resp = await client.post(f"{STORAGE_URL}/init", json={"emergent_key": EMERGENT_KEY}, timeout=30.0)
    resp.raise_for_status()
    storage_key = resp.json()["storage_key"]
    return storage_key


async def put_object_async(path: str, data: bytes, content_type: str) -> dict:
    async with httpx.AsyncClient() as client:
        key = await init_storage_async(client)
        resp = await client.put(
            f"{STORAGE_URL}/objects/{path}",
            headers={"X-Storage-Key": key, "Content-Type": content_type},
            content=data, 
            timeout=120.0,
        )
        resp.raise_for_status()
        return resp.json()


async def get_object_async(path: str):
    async with httpx.AsyncClient() as client:
        key = await init_storage_async(client)
        resp = await client.get(
            f"{STORAGE_URL}/objects/{path}",
            headers={"X-Storage-Key": key}, 
            timeout=60.0,
        )
        resp.raise_for_status()
        return resp.content, resp.headers.get("Content-Type", "application/octet-stream")


@router.post("/upload")
async def upload(file: UploadFile = File(...), user: dict = Depends(get_current_user)):
    # Safe path extension parsing via pathlib
    original_path = Path(file.filename or "file.bin")
    ext = original_path.suffix.lstrip('.').lower() or "bin"
    
    content_type = MIME_TYPES.get(ext, file.content_type or "application/octet-stream")
    path = f"{APP_NAME}/uploads/{user['id']}/{uuid.uuid4()}.{ext}"
    
    data = await file.read()
    if len(data) > 8 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="File too large (max 8MB)")
        
    try:
        result = await put_object_async(path, data, content_type)
    except Exception as e:
        logger.error(f"Upload failed: {e}")
        raise HTTPException(status_code=500, detail="Upload failed")
        
    await db.files.insert_one({
        "id": str(uuid.uuid4()),
        "storage_path": result["path"],
        "original_filename": file.filename,
        "content_type": content_type,
        "size": result.get("size", len(data)),
        "owner_id": user["id"],
        "is_deleted": False,
        "created_at": now_iso(),
    })
backend_url = os.environ.get("PUBLIC_BASE", "").rstrip("/")
    return {
        "path": result["path"], 
        "url": f"{backend_url}/api/files/{result['path']}"
    }

@router.get("/files/{path:path}")
async def serve_file(path: str):
    record = await db.files.find_one({"storage_path": path, "is_deleted": False}, NO_ID)
    if not record:
        raise HTTPException(status_code=404, detail="File not found")
    try:
        data, content_type = await get_object_async(path)
    except Exception:
        raise HTTPException(status_code=404, detail="File not found")
        
    return Response(content=data, media_type=record.get("content_type", content_type),
                    headers={"Cache-Control": "public, max-age=86400"})
