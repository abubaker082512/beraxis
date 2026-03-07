"""
Settings router — user profile, organization settings, API key management.
Maps to: /dashboard/settings (Settings.tsx)
"""
import secrets
from typing import Optional
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from pydantic import BaseModel

from app.database import get_db
from app.dependencies import get_tenant_user, require_admin
from app.models.user import User, Organization
from app.utils.responses import success_response, error_response

router = APIRouter(prefix="/settings", tags=["Settings"])


class ProfileUpdate(BaseModel):
    full_name: Optional[str] = None
    avatar_url: Optional[str] = None


class OrgUpdate(BaseModel):
    name: Optional[str] = None
    webhook_url: Optional[str] = None


@router.get("")
async def get_settings(
    current_user: User = Depends(get_tenant_user),
    db: AsyncSession = Depends(get_db),
):
    org_result = await db.execute(select(Organization).where(Organization.id == current_user.org_id))
    org = org_result.scalar_one_or_none()
    
    return success_response(data={
        "profile": {
            "full_name": current_user.full_name,
            "email": current_user.email,
            "role": current_user.role,
        },
        "organization": {
            "name": org.name if org else None,
            "plan": org.plan if org else None,
            "webhook_url": org.webhook_url if org else None,
        }
    })


@router.put("/profile")
async def update_profile(
    data: ProfileUpdate,
    current_user: User = Depends(get_tenant_user),
    db: AsyncSession = Depends(get_db),
):
    if data.full_name:
        current_user.full_name = data.full_name
    if data.avatar_url:
        current_user.avatar_url = data.avatar_url
    await db.commit()
    return success_response(message="Profile updated")


@router.put("/organization")
async def update_organization(
    data: OrgUpdate,
    current_user: User = Depends(require_admin()),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Organization).where(Organization.id == current_user.org_id))
    org = result.scalar_one_or_none()
    if not org:
        return error_response("Organization not found", 404)
        
    if data.name:
        org.name = data.name
    if data.webhook_url is not None:
        org.webhook_url = data.webhook_url
    await db.commit()
    return success_response(message="Organization updated")


@router.get("/api-keys")
async def list_api_keys(
    current_user: User = Depends(get_tenant_user),
):
    keys = [{"id": "key_1", "key": current_user.api_key}] if current_user.api_key else []
    return success_response(data=keys)


@router.post("/api-keys")
async def generate_api_key(
    current_user: User = Depends(get_tenant_user),
    db: AsyncSession = Depends(get_db),
):
    new_key = "bx_" + secrets.token_hex(20)
    current_user.api_key = new_key
    await db.commit()
    return success_response(data={"key": new_key}, message="API Key generated")


@router.delete("/api-keys")
async def revoke_api_key(
    current_user: User = Depends(get_tenant_user),
    db: AsyncSession = Depends(get_db),
):
    current_user.api_key = None
    await db.commit()
    return success_response(message="API Key revoked")
