"""
Auth router — register, login, logout, refresh, OAuth stubs.
"""
from datetime import datetime, timezone, timedelta
from typing import Optional
import secrets

from fastapi import APIRouter, Depends, HTTPException, Request, status, Body
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel, EmailStr

from app.database import get_db
from app.models.user import User, UserRole, Organization, OrgStatus, RefreshToken
from app.models.billing import Subscription, PlanType, SubStatus
from app.services.auth_service import (
    hash_password, verify_password, create_token_pair, hash_token, decode_access_token,
)
from app.config import settings
from app.utils.responses import success_response, error_response

router = APIRouter(prefix="/auth", tags=["Authentication"])


# ── Schemas ──────────────────────────────────────────────────────────────────
class RegisterRequest(BaseModel):
    full_name: str
    email: EmailStr
    password: str
    org_name: Optional[str] = None


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class RefreshRequest(BaseModel):
    refresh_token: str


class ForgotPasswordRequest(BaseModel):
    email: EmailStr


class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str


# ── POST /auth/register ───────────────────────────────────────────────────────
@router.post("/register")
async def register(data: RegisterRequest, db: AsyncSession = Depends(get_db)):
    # Check duplicate email
    existing = await db.execute(select(User).where(User.email == data.email))
    if existing.scalar_one_or_none():
        return error_response("Email already registered", 409)

    # Create org if org_name provided, else user is ungrouped until invited
    org = None
    if data.org_name:
        slug = data.org_name.lower().replace(" ", "-")[:50] + "-" + secrets.token_hex(4)
        org = Organization(name=data.org_name, slug=slug, status=OrgStatus.TRIAL)
        db.add(org)
        await db.flush()

    user = User(
        full_name=data.full_name,
        email=data.email,
        hashed_password=hash_password(data.password),
        role=UserRole.OWNER if org else UserRole.AGENT,
        org_id=org.id if org else None,
        is_verified=False,
    )
    db.add(user)
    await db.flush()

    # Create starter subscription
    if org:
        sub = Subscription(org_id=org.id, plan=PlanType.STARTER, status=SubStatus.TRIALING)
        db.add(sub)

    await db.commit()

    tokens = create_token_pair(str(user.id), str(org.id) if org else None, user.role.value)
    return success_response(
        data={**tokens, "user": {"id": str(user.id), "email": user.email, "full_name": user.full_name, "role": user.role}},
        message="Registration successful",
        status_code=201,
    )


# ── POST /auth/login ──────────────────────────────────────────────────────────
@router.post("/login")
async def login(data: LoginRequest, request: Request, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.email == data.email))
    user = result.scalar_one_or_none()

    if not user or not user.hashed_password or not verify_password(data.password, user.hashed_password):
        return error_response("Invalid email or password", 401)

    if not user.is_active:
        return error_response("Account is disabled. Contact support.", 403)

    tokens = create_token_pair(str(user.id), str(user.org_id) if user.org_id else None, user.role.value)

    # Store hashed refresh token
    expires_at = datetime.now(timezone.utc) + timedelta(days=settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS)
    rt = RefreshToken(
        user_id=user.id,
        token_hash=hash_token(tokens["refresh_token"]),
        expires_at=expires_at.isoformat(),
        user_agent=request.headers.get("user-agent"),
        ip_address=request.client.host if request.client else None,
    )
    db.add(rt)
    await db.commit()

    return success_response(
        data={
            **tokens,
            "user": {
                "id": str(user.id),
                "email": user.email,
                "full_name": user.full_name,
                "role": user.role,
                "org_id": str(user.org_id) if user.org_id else None,
            },
        },
        message="Login successful",
    )


# ── POST /auth/refresh ────────────────────────────────────────────────────────
@router.post("/refresh")
async def refresh_token(data: RefreshRequest, db: AsyncSession = Depends(get_db)):
    token_hash = hash_token(data.refresh_token)
    result = await db.execute(
        select(RefreshToken).where(RefreshToken.token_hash == token_hash)
    )
    rt = result.scalar_one_or_none()

    if not rt or rt.is_revoked:
        return error_response("Invalid or expired refresh token", 401)

    expires = datetime.fromisoformat(rt.expires_at)
    if datetime.now(timezone.utc) > expires:
        return error_response("Refresh token expired. Please login again.", 401)

    # Get user
    user_result = await db.execute(select(User).where(User.id == rt.user_id))
    user = user_result.scalar_one_or_none()
    if not user or not user.is_active:
        return error_response("User not found", 401)

    # Rotate: revoke old, issue new
    rt.is_revoked = True
    tokens = create_token_pair(str(user.id), str(user.org_id) if user.org_id else None, user.role.value)
    new_rt = RefreshToken(
        user_id=user.id,
        token_hash=hash_token(tokens["refresh_token"]),
        expires_at=(datetime.now(timezone.utc) + timedelta(days=settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS)).isoformat(),
    )
    db.add(new_rt)
    await db.commit()

    return success_response(data=tokens, message="Token refreshed")


# ── POST /auth/logout ─────────────────────────────────────────────────────────
@router.post("/logout")
async def logout(data: RefreshRequest, db: AsyncSession = Depends(get_db)):
    token_hash = hash_token(data.refresh_token)
    result = await db.execute(
        select(RefreshToken).where(RefreshToken.token_hash == token_hash)
    )
    rt = result.scalar_one_or_none()
    if rt:
        rt.is_revoked = True
        await db.commit()
    return success_response(message="Logged out successfully")


# ── POST /auth/forgot-password ────────────────────────────────────────────────
@router.post("/forgot-password")
async def forgot_password(data: ForgotPasswordRequest, db: AsyncSession = Depends(get_db)):
    # Always return success to prevent email enumeration
    result = await db.execute(select(User).where(User.email == data.email))
    user = result.scalar_one_or_none()
    if user:
        # In production: generate token, send email
        pass
    return success_response(message="If that email exists, a reset link has been sent.")
