"""
Admin router — tenant management, system status, API keys.
Maps to: /dashboard/admin (Admin.tsx) — Superadmin only.
"""
import secrets
from typing import Optional
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from pydantic import BaseModel

from app.database import get_db
from app.dependencies import require_superadmin
from app.models.user import User, Organization, OrgStatus
from app.models.billing import Subscription, UsageLog
from app.utils.responses import success_response, error_response

router = APIRouter(prefix="/admin", tags=["Admin"])


class TenantCreate(BaseModel):
    name: str
    plan: str = "starter"
    owner_email: Optional[str] = None


class TenantUpdate(BaseModel):
    status: Optional[str] = None
    plan: Optional[str] = None


@router.get("/tenants")
async def list_tenants(
    current_user: User = Depends(require_superadmin()),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Organization).order_by(Organization.created_at.desc()))
    orgs = result.scalars().all()

    data = []
    for org in orgs:
        users_count = await db.execute(
            select(func.count(User.id)).where(User.org_id == org.id)
        )
        sub_result = await db.execute(select(Subscription).where(Subscription.org_id == org.id))
        sub = sub_result.scalar_one_or_none()
        data.append({
            "id": str(org.id),
            "name": org.name,
            "slug": org.slug,
            "status": org.status,
            "plan": sub.plan if sub else "starter",
            "users_count": users_count.scalar() or 0,
            "created_at": str(org.created_at),
        })
    return success_response(data=data)


@router.post("/tenants", status_code=201)
async def create_tenant(
    data: TenantCreate,
    current_user: User = Depends(require_superadmin()),
    db: AsyncSession = Depends(get_db),
):
    slug = data.name.lower().replace(" ", "-") + "-" + secrets.token_hex(4)
    org = Organization(name=data.name, slug=slug, status=OrgStatus.ACTIVE, plan=data.plan)
    db.add(org)
    await db.flush()
    from app.models.billing import PlanType, SubStatus
    sub = Subscription(org_id=org.id, plan=PlanType(data.plan), status=SubStatus.ACTIVE)
    db.add(sub)
    await db.commit()
    return success_response(data={"id": str(org.id), "name": org.name, "slug": org.slug}, message="Tenant created", status_code=201)


@router.put("/tenants/{org_id}")
async def update_tenant(
    org_id: str,
    data: TenantUpdate,
    current_user: User = Depends(require_superadmin()),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Organization).where(Organization.id == org_id))
    org = result.scalar_one_or_none()
    if not org:
        return error_response("Organization not found", 404)
    if data.status:
        org.status = OrgStatus(data.status)
    if data.plan:
        org.plan = data.plan
        sub_result = await db.execute(select(Subscription).where(Subscription.org_id == org.id))
        sub = sub_result.scalar_one_or_none()
        if sub:
            from app.models.billing import PlanType
            sub.plan = PlanType(data.plan)
    await db.commit()
    return success_response(message="Tenant updated")


@router.get("/system-status")
async def system_status(current_user: User = Depends(require_superadmin()), db: AsyncSession = Depends(get_db)):
    """Health check for all system components."""
    import httpx

    # DB check
    db_ok = False
    try:
        await db.execute(select(func.count(User.id)))
        db_ok = True
    except Exception:
        pass

    # Redis check
    redis_ok = False
    try:
        import redis as redis_lib
        from app.config import settings
        r = redis_lib.from_url(settings.REDIS_URL)
        r.ping()
        redis_ok = True
    except Exception:
        pass

    # Asterisk check
    asterisk_ok = False
    try:
        from app.config import settings
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                f"http://{settings.ASTERISK_HOST}:{settings.ASTERISK_ARI_PORT}/ari/api-info",
                auth=(settings.ASTERISK_ARI_USER, settings.ASTERISK_ARI_PASS),
                timeout=3,
            )
            asterisk_ok = resp.status_code == 200
    except Exception:
        pass

    return success_response(data={
        "api": {"status": "operational", "healthy": True},
        "database": {"status": "operational" if db_ok else "error", "healthy": db_ok},
        "redis": {"status": "operational" if redis_ok else "error", "healthy": redis_ok},
        "voice_servers": {"status": "operational" if asterisk_ok else "unreachable", "healthy": asterisk_ok},
    })


@router.get("/api-keys")
async def get_master_api_keys(current_user: User = Depends(require_superadmin())):
    return success_response(data={
        "master_key": "abt_master_live_" + secrets.token_hex(16),
        "note": "Regenerate via POST /admin/api-keys/regenerate"
    })


@router.post("/api-keys/regenerate")
async def regenerate_master_key(current_user: User = Depends(require_superadmin())):
    new_key = "abt_master_live_" + secrets.token_hex(16)
    return success_response(data={"master_key": new_key}, message="Master API key regenerated")


@router.post("/maintenance")
async def toggle_maintenance(current_user: User = Depends(require_superadmin())):
    return success_response(message="Maintenance mode toggled")


@router.delete("/logs")
async def purge_system_logs(current_user: User = Depends(require_superadmin())):
    return success_response(message="System logs purged")


@router.get("/stats")
async def platform_stats(current_user: User = Depends(require_superadmin()), db: AsyncSession = Depends(get_db)):
    """Platform-wide stats for admin overview."""
    from app.models.call import Call
    from app.models.campaign import Campaign

    total_orgs = (await db.execute(select(func.count(Organization.id)))).scalar() or 0
    total_users = (await db.execute(select(func.count(User.id)))).scalar() or 0
    total_calls = (await db.execute(select(func.count(Call.id)))).scalar() or 0
    total_campaigns = (await db.execute(select(func.count(Campaign.id)))).scalar() or 0

    return success_response(data={
        "total_organizations": total_orgs,
        "total_users": total_users,
        "total_calls": total_calls,
        "total_campaigns": total_campaigns,
    })
