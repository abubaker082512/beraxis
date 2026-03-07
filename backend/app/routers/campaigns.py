"""
Campaigns router — CRUD, start/pause, CSV upload.
Maps to: /dashboard/campaigns (Campaigns.tsx)
"""
import csv
import io
import secrets
from typing import Optional
from fastapi import APIRouter, Depends, Query, UploadFile, File, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_
from pydantic import BaseModel

from app.database import get_db
from app.dependencies import get_tenant_user
from app.models.user import User
from app.models.campaign import Campaign, CampaignStatus, Lead, LeadStatus
from app.utils.responses import success_response, error_response, paginate

router = APIRouter(prefix="/campaigns", tags=["Campaigns"])


class CampaignCreate(BaseModel):
    name: str
    description: Optional[str] = None
    agent_id: Optional[str] = None
    schedule_timezone: str = "UTC"
    schedule_start_time: str = "09:00"
    schedule_end_time: str = "18:00"
    schedule_days: list = ["mon", "tue", "wed", "thu", "fri"]
    max_retries: int = 3


class CampaignUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    agent_id: Optional[str] = None
    schedule_timezone: Optional[str] = None
    schedule_start_time: Optional[str] = None
    schedule_end_time: Optional[str] = None
    schedule_days: Optional[list] = None
    max_retries: Optional[int] = None


def _campaign_to_dict(c: Campaign) -> dict:
    return {
        "id": str(c.id),
        "name": c.name,
        "description": c.description,
        "status": c.status,
        "agent_id": str(c.agent_id) if c.agent_id else None,
        "total_leads": c.total_leads,
        "calls_made": c.calls_made,
        "calls_answered": c.calls_answered,
        "success_rate": c.success_rate,
        "created_at": str(c.created_at),
        "schedule_timezone": c.schedule_timezone,
        "schedule_start_time": c.schedule_start_time,
        "schedule_end_time": c.schedule_end_time,
    }


@router.get("")
async def list_campaigns(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    search: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    current_user: User = Depends(get_tenant_user),
    db: AsyncSession = Depends(get_db),
):
    filters = [Campaign.org_id == current_user.org_id]
    if search:
        filters.append(Campaign.name.ilike(f"%{search}%"))
    if status:
        filters.append(Campaign.status == status)

    total_result = await db.execute(select(func.count(Campaign.id)).where(and_(*filters)))
    total = total_result.scalar() or 0

    result = await db.execute(
        select(Campaign)
        .where(and_(*filters))
        .order_by(Campaign.created_at.desc())
        .offset((page - 1) * limit)
        .limit(limit)
    )
    campaigns = result.scalars().all()
    return success_response(
        data=[_campaign_to_dict(c) for c in campaigns],
        pagination=paginate(campaigns, total, page, limit),
    )


@router.post("", status_code=201)
async def create_campaign(
    data: CampaignCreate,
    current_user: User = Depends(get_tenant_user),
    db: AsyncSession = Depends(get_db),
):
    campaign = Campaign(
        org_id=current_user.org_id,
        name=data.name,
        description=data.description,
        agent_id=data.agent_id,
        schedule_timezone=data.schedule_timezone,
        schedule_start_time=data.schedule_start_time,
        schedule_end_time=data.schedule_end_time,
        schedule_days=data.schedule_days,
        max_retries=data.max_retries,
        status=CampaignStatus.DRAFT,
    )
    db.add(campaign)
    await db.commit()
    return success_response(data=_campaign_to_dict(campaign), message="Campaign created", status_code=201)


@router.get("/{campaign_id}")
async def get_campaign(
    campaign_id: str,
    current_user: User = Depends(get_tenant_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Campaign).where(and_(Campaign.id == campaign_id, Campaign.org_id == current_user.org_id))
    )
    c = result.scalar_one_or_none()
    if not c:
        return error_response("Campaign not found", 404)
    return success_response(data=_campaign_to_dict(c))


@router.put("/{campaign_id}")
async def update_campaign(
    campaign_id: str,
    data: CampaignUpdate,
    current_user: User = Depends(get_tenant_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Campaign).where(and_(Campaign.id == campaign_id, Campaign.org_id == current_user.org_id))
    )
    c = result.scalar_one_or_none()
    if not c:
        return error_response("Campaign not found", 404)

    for field, value in data.model_dump(exclude_none=True).items():
        setattr(c, field, value)
    await db.commit()
    return success_response(data=_campaign_to_dict(c), message="Campaign updated")


@router.delete("/{campaign_id}")
async def delete_campaign(
    campaign_id: str,
    current_user: User = Depends(get_tenant_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Campaign).where(and_(Campaign.id == campaign_id, Campaign.org_id == current_user.org_id))
    )
    c = result.scalar_one_or_none()
    if not c:
        return error_response("Campaign not found", 404)
    await db.delete(c)
    await db.commit()
    return success_response(message="Campaign deleted")


@router.post("/{campaign_id}/start")
async def start_campaign(
    campaign_id: str,
    current_user: User = Depends(get_tenant_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Campaign).where(and_(Campaign.id == campaign_id, Campaign.org_id == current_user.org_id))
    )
    c = result.scalar_one_or_none()
    if not c:
        return error_response("Campaign not found", 404)
    if c.total_leads == 0:
        return error_response("Cannot start a campaign with no leads", 400)

    c.status = CampaignStatus.ACTIVE
    await db.commit()

    # Trigger Celery task
    try:
        from app.workers.tasks import process_campaign_dial
        process_campaign_dial.delay(str(campaign_id))
    except Exception:
        pass  # Celery not available locally

    return success_response(data={"status": c.status}, message="Campaign started")


@router.post("/{campaign_id}/pause")
async def pause_campaign(
    campaign_id: str,
    current_user: User = Depends(get_tenant_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Campaign).where(and_(Campaign.id == campaign_id, Campaign.org_id == current_user.org_id))
    )
    c = result.scalar_one_or_none()
    if not c:
        return error_response("Campaign not found", 404)
    c.status = CampaignStatus.PAUSED
    await db.commit()
    return success_response(data={"status": c.status}, message="Campaign paused")


@router.post("/{campaign_id}/leads/upload")
async def upload_leads_csv(
    campaign_id: str,
    file: UploadFile = File(...),
    current_user: User = Depends(get_tenant_user),
    db: AsyncSession = Depends(get_db),
):
    """Upload a CSV of leads to a campaign. Required columns: phone. Optional: first_name, last_name, email, company."""
    if not file.filename or not file.filename.endswith(".csv"):
        return error_response("Please upload a valid CSV file", 400)

    result = await db.execute(
        select(Campaign).where(and_(Campaign.id == campaign_id, Campaign.org_id == current_user.org_id))
    )
    c = result.scalar_one_or_none()
    if not c:
        return error_response("Campaign not found", 404)

    content = await file.read()
    decoded = content.decode("utf-8", errors="ignore")
    reader = csv.DictReader(io.StringIO(decoded))

    if "phone" not in (reader.fieldnames or []):
        return error_response("CSV must contain a 'phone' column", 400)

    leads_added = 0
    for row in reader:
        phone = row.get("phone", "").strip()
        if not phone:
            continue
        lead = Lead(
            org_id=current_user.org_id,
            campaign_id=c.id,
            phone=phone,
            first_name=row.get("first_name", "").strip() or None,
            last_name=row.get("last_name", "").strip() or None,
            email=row.get("email", "").strip() or None,
            company=row.get("company", "").strip() or None,
            custom_vars={k: v for k, v in row.items() if k not in ("phone", "first_name", "last_name", "email", "company")},
        )
        db.add(lead)
        leads_added += 1

    c.total_leads += leads_added
    await db.commit()
    return success_response(data={"leads_added": leads_added, "total_leads": c.total_leads}, message=f"{leads_added} leads imported successfully")
