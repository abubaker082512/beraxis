"""
Contacts/Leads router — CRM functionality for managing leads outside/inside campaigns.
Maps to: /dashboard/contacts (Contacts.tsx)
"""
from typing import Optional
from fastapi import APIRouter, Depends, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_
from pydantic import BaseModel

from app.database import get_db
from app.dependencies import get_tenant_user
from app.models.user import User
from app.models.campaign import Lead, LeadStatus, Campaign
from app.utils.responses import success_response, error_response, paginate

router = APIRouter(prefix="/contacts", tags=["Contacts"])


class ContactCreate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone: str
    email: Optional[str] = None
    company: Optional[str] = None
    title: Optional[str] = None
    campaign_id: Optional[str] = None


class ContactUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    company: Optional[str] = None
    title: Optional[str] = None
    status: Optional[str] = None


def _lead_to_dict(l: Lead) -> dict:
    return {
        "id": str(l.id),
        "first_name": l.first_name,
        "last_name": l.last_name,
        "full_name": l.full_name,
        "phone": l.phone,
        "email": l.email,
        "company": l.company,
        "title": l.title,
        "status": l.status,
        "campaign_id": str(l.campaign_id) if l.campaign_id else None,
        "last_called_at": l.last_called_at,
        "created_at": str(l.created_at),
    }


@router.get("")
async def list_contacts(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    search: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    campaign_id: Optional[str] = Query(None),
    current_user: User = Depends(get_tenant_user),
    db: AsyncSession = Depends(get_db),
):
    filters = [Lead.org_id == current_user.org_id]
    if search:
        search_filter = or_(
            Lead.first_name.ilike(f"%{search}%"),
            Lead.last_name.ilike(f"%{search}%"),
            Lead.phone.ilike(f"%{search}%"),
            Lead.email.ilike(f"%{search}%"),
            Lead.company.ilike(f"%{search}%"),
        )
        filters.append(search_filter)
    if status:
        filters.append(Lead.status == status)
    if campaign_id:
        filters.append(Lead.campaign_id == campaign_id)

    total_result = await db.execute(select(func.count(Lead.id)).where(and_(*filters)))
    total = total_result.scalar() or 0

    result = await db.execute(
        select(Lead)
        .where(and_(*filters))
        .order_by(Lead.created_at.desc())
        .offset((page - 1) * limit)
        .limit(limit)
    )
    leads = result.scalars().all()

    return success_response(
        data=[_lead_to_dict(l) for l in leads],
        pagination=paginate(leads, total, page, limit),
    )


@router.post("", status_code=201)
async def create_contact(
    data: ContactCreate,
    current_user: User = Depends(get_tenant_user),
    db: AsyncSession = Depends(get_db),
):
    lead = Lead(org_id=current_user.org_id, status=LeadStatus.PENDING, **data.model_dump())
    db.add(lead)
    
    if data.campaign_id:
        # Update campaign total leads
        result = await db.execute(select(Campaign).where(Campaign.id == data.campaign_id))
        c = result.scalar_one_or_none()
        if c:
            c.total_leads += 1

    await db.commit()
    return success_response(data=_lead_to_dict(lead), message="Contact created", status_code=201)


@router.put("/{contact_id}")
async def update_contact(
    contact_id: str,
    data: ContactUpdate,
    current_user: User = Depends(get_tenant_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Lead).where(and_(Lead.id == contact_id, Lead.org_id == current_user.org_id))
    )
    l = result.scalar_one_or_none()
    if not l:
        return error_response("Contact not found", 404)

    for field, value in data.model_dump(exclude_none=True).items():
        if field == "status":
            setattr(l, field, LeadStatus(value))
        else:
            setattr(l, field, value)

    await db.commit()
    return success_response(data=_lead_to_dict(l), message="Contact updated")


@router.delete("/{contact_id}")
async def delete_contact(
    contact_id: str,
    current_user: User = Depends(get_tenant_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Lead).where(and_(Lead.id == contact_id, Lead.org_id == current_user.org_id))
    )
    l = result.scalar_one_or_none()
    if not l:
        return error_response("Contact not found", 404)

    # Decrement campaign count if attached
    if l.campaign_id:
        campaign_result = await db.execute(select(Campaign).where(Campaign.id == l.campaign_id))
        c = campaign_result.scalar_one_or_none()
        if c and c.total_leads > 0:
            c.total_leads -= 1

    await db.delete(l)
    await db.commit()
    return success_response(message="Contact deleted")


@router.get("/export")
async def export_contacts_csv(
    current_user: User = Depends(get_tenant_user),
    db: AsyncSession = Depends(get_db),
):
    import csv, io
    result = await db.execute(
        select(Lead).where(Lead.org_id == current_user.org_id).order_by(Lead.created_at.desc()).limit(10000)
    )
    leads = result.scalars().all()

    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=["id", "first_name", "last_name", "phone", "email", "company", "title", "status", "campaign_id", "created_at"])
    writer.writeheader()
    for l in leads:
        writer.writerow({
            "id": str(l.id), "first_name": l.first_name, "last_name": l.last_name, "phone": l.phone,
            "email": l.email, "company": l.company, "title": l.title, "status": l.status,
            "campaign_id": str(l.campaign_id) if l.campaign_id else "", "created_at": str(l.created_at)
        })

    output.seek(0)
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=contacts.csv"},
    )
