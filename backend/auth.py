import os
import uuid
from datetime import datetime, timedelta, timezone

import jwt
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext
from pydantic import BaseModel, EmailStr

from database import db, now_iso, NO_ID


router = APIRouter(prefix="/api/auth", tags=["auth"])

pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto"
)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")

JWT_SECRET = os.getenv("JWT_SECRET", "change-this-secret")
JWT_ALGORITHM = "HS256"


# ---------------- Password helpers ----------------

def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(password: str, hashed: str) -> bool:
    return pwd_context.verify(password, hashed)


# ---------------- JWT helpers ----------------

def create_token(user_id: str) -> str:
    payload = {
        "sub": user_id,
        "exp": datetime.now(timezone.utc) + timedelta(days=7),
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)


# ---------------- Current user ----------------

async def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(
            token,
            JWT_SECRET,
            algorithms=[JWT_ALGORITHM]
        )
        user_id = payload.get("sub")

        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token"
            )

    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication"
        )

    user = await db.users.find_one({"id": user_id}, NO_ID)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )

    return user


async def get_current_admin(user: dict = Depends(get_current_user)):
    if "admin" not in user.get("roles", []):
        raise HTTPException(
            status_code=403,
            detail="Admin access required"
        )
    return user


def require_roles(role: str):
    async def checker(user: dict = Depends(get_current_user)):
        if role not in user.get("roles", []):
            raise HTTPException(
                status_code=403,
                detail="Permission denied"
            )
        return user

    return checker


# ---------------- Seller profile ----------------

async def ensure_seller_profile(user_id: str, store_name: str):
    existing = await db.seller_profiles.find_one(
        {"user_id": user_id},
        NO_ID
    )

    if existing:
        return existing

    profile = {
        "id": str(uuid.uuid4()),
        "user_id": user_id,
        "store_name": store_name,
        "created_at": now_iso(),
        "status": "active",
    }

    await db.seller_profiles.insert_one(profile)

    return profile


# ---------------- Models ----------------

class RegisterIn(BaseModel):
    email: EmailStr
    password: str
    full_name: str


class LoginIn(BaseModel):
    email: EmailStr
    password: str


# ---------------- Routes ----------------

@router.post("/register")
async def register(body: RegisterIn):
    existing = await db.users.find_one(
        {"email": body.email},
        NO_ID
    )

    if existing:
        raise HTTPException(
            status_code=400,
            detail="Email already registered"
        )

    user = {
        "id": str(uuid.uuid4()),
        "email": body.email,
        "password_hash": hash_password(body.password),
        "full_name": body.full_name,
        "roles": ["customer"],
        "is_active": True,
        "created_at": now_iso(),
    }

    await db.users.insert_one(user)

    return {
        "message": "Account created",
        "user_id": user["id"]
    }


@router.post("/login")
async def login(body: LoginIn):
    user = await db.users.find_one(
        {"email": body.email},
        NO_ID
    )

    if not user:
        raise HTTPException(
            status_code=401,
            detail="Invalid login"
        )

    if not verify_password(
        body.password,
        user["password_hash"]
    ):
        raise HTTPException(
            status_code=401,
            detail="Invalid login"
        )

    token = create_token(user["id"])

    return {
        "access_token": token,
        "token_type": "bearer",
        "user": {
            "id": user["id"],
            "email": user["email"],
            "roles": user.get("roles", [])
        }
    }
