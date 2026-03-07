"""
Dashboard router — overview stats, chart data, recent calls.
Maps to: /dashboard (Overview.tsx)
"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from datetime import datetime, timedelta, timezone

from app.database import get_db
from app.dependencies import get_tenant_user
from app.models.user import User
from app.models.call import Call, CallStatus, CallDirection
from app.models.campaign import Campaign, CampaignStatus
from app.utils.responses import success_response

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get("/overview")
async def get_overview(
    current_user: User = Depends(get_tenant_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Returns all stats for the Dashboard Overview page:
    - Total calls, active campaigns, success rate, revenue estimate
    """
    org_id = current_user.org_id

    # Total calls
    total_calls_result = await db.execute(
        select(func.count(Call.id)).where(Call.org_id == org_id)
    )
    total_calls = total_calls_result.scalar() or 0

    # Active campaigns
    active_campaigns_result = await db.execute(
        select(func.count(Campaign.id)).where(
            and_(Campaign.org_id == org_id, Campaign.status == CampaignStatus.ACTIVE)
        )
    )
    active_campaigns = active_campaigns_result.scalar() or 0

    # Success rate (answered / total)
    answered_result = await db.execute(
        select(func.count(Call.id)).where(
            and_(Call.org_id == org_id, Call.status == CallStatus.ANSWERED)
        )
    )
    answered = answered_result.scalar() or 0
    success_rate = round((answered / total_calls * 100), 1) if total_calls > 0 else 0.0

    # Previous week comparison (7 days ago)
    week_ago = (datetime.now(timezone.utc) - timedelta(days=7)).isoformat()
    prev_calls_result = await db.execute(
        select(func.count(Call.id)).where(
            and_(Call.org_id == org_id, Call.created_at < week_ago)
        )
    )
    prev_calls = prev_calls_result.scalar() or 0

    stats = {
        "total_calls": total_calls,
        "total_calls_change": _calc_change(total_calls, prev_calls),
        "active_campaigns": active_campaigns,
        "success_rate": success_rate,
        "total_revenue_usd": round(answered * 1.85, 2),  # stub metric
    }

    return success_response(data=stats)


@router.get("/chart")
async def get_chart_data(
    days: int = Query(7, ge=1, le=90),
    current_user: User = Depends(get_tenant_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Daily call volume and success count for charting.
    Returns array: [{ name: "Mon", calls: 40, success: 30 }, ...]
    """
    org_id = current_user.org_id
    chart_data = []

    for i in range(days - 1, -1, -1):
        day = datetime.now(timezone.utc) - timedelta(days=i)
        day_str = day.strftime("%a") if days <= 7 else day.strftime("%b %d")
        day_start = day.replace(hour=0, minute=0, second=0, microsecond=0).isoformat()
        day_end = day.replace(hour=23, minute=59, second=59).isoformat()

        day_calls_result = await db.execute(
            select(func.count(Call.id)).where(
                and_(
                    Call.org_id == org_id,
                    Call.created_at >= day_start,
                    Call.created_at <= day_end,
                )
            )
        )
        day_calls = day_calls_result.scalar() or 0

        day_success_result = await db.execute(
            select(func.count(Call.id)).where(
                and_(
                    Call.org_id == org_id,
                    Call.status == CallStatus.ANSWERED,
                    Call.created_at >= day_start,
                    Call.created_at <= day_end,
                )
            )
        )
        day_success = day_success_result.scalar() or 0

        chart_data.append({"name": day_str, "calls": day_calls, "success": day_success})

    return success_response(data=chart_data)


@router.get("/recent-calls")
async def get_recent_calls(
    limit: int = Query(5, ge=1, le=20),
    current_user: User = Depends(get_tenant_user),
    db: AsyncSession = Depends(get_db),
):
    """Recent calls list for Dashboard sidebar widget."""
    from app.models.call import Call
    result = await db.execute(
        select(Call)
        .where(Call.org_id == current_user.org_id)
        .order_by(Call.created_at.desc())
        .limit(limit)
    )
    calls = result.scalars().all()
    data = [
        {
            "id": str(c.id),
            "phone_number": c.phone_number,
            "status": c.status,
            "direction": c.direction,
            "duration_secs": c.duration_secs,
            "started_at": c.started_at,
        }
        for c in calls
    ]
    return success_response(data=data)


def _calc_change(current: int, previous: int) -> str:
    if previous == 0:
        return "+100%" if current > 0 else "0%"
    change = round(((current - previous) / previous) * 100, 1)
    return f"+{change}%" if change >= 0 else f"{change}%"
