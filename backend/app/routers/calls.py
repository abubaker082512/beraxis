"""
Calls router — call logs, recordings, transcripts, sentiment.
Maps to: /dashboard/call-logs (CallLogs.tsx)
"""
from typing import Optional
from fastapi import APIRouter, Depends, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_

from app.database import get_db
from app.dependencies import get_tenant_user
from app.models.user import User
from app.models.call import Call, CallAnalytics, Transcript, CallStatus
from app.utils.responses import success_response, error_response, paginate

router = APIRouter(prefix="/calls", tags=["Calls"])


def _call_to_dict(c: Call) -> dict:
    return {
        "id": str(c.id),
        "direction": c.direction,
        "status": c.status,
        "phone_number": c.phone_number,
        "duration_secs": c.duration_secs,
        "started_at": c.started_at,
        "ended_at": c.ended_at,
        "recording_url": c.recording_url,
        "campaign_id": str(c.campaign_id) if c.campaign_id else None,
        "lead_id": str(c.lead_id) if c.lead_id else None,
        "created_at": str(c.created_at),
    }


@router.get("")
async def list_calls(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    search: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    direction: Optional[str] = Query(None),
    sentiment: Optional[str] = Query(None),
    campaign_id: Optional[str] = Query(None),
    current_user: User = Depends(get_tenant_user),
    db: AsyncSession = Depends(get_db),
):
    """
    List call logs with full filtering support.
    Supports: search by phone, filter by status/direction/sentiment/campaign.
    """
    filters = [Call.org_id == current_user.org_id]
    if search:
        filters.append(Call.phone_number.ilike(f"%{search}%"))
    if status:
        filters.append(Call.status == status)
    if direction:
        filters.append(Call.direction == direction)
    if campaign_id:
        filters.append(Call.campaign_id == campaign_id)

    query = select(Call).where(and_(*filters))
    if sentiment:
        query = query.join(CallAnalytics, Call.id == CallAnalytics.call_id).where(
            CallAnalytics.sentiment_overall == sentiment
        )

    total_result = await db.execute(select(func.count()).select_from(query.subquery()))
    total = total_result.scalar() or 0

    result = await db.execute(
        query.order_by(Call.created_at.desc()).offset((page - 1) * limit).limit(limit)
    )
    calls = result.scalars().all()

    return success_response(
        data=[_call_to_dict(c) for c in calls],
        pagination=paginate(calls, total, page, limit),
    )


@router.get("/export")
async def export_calls_csv(
    current_user: User = Depends(get_tenant_user),
    db: AsyncSession = Depends(get_db),
):
    """Export call logs as CSV."""
    import csv, io
    result = await db.execute(
        select(Call).where(Call.org_id == current_user.org_id).order_by(Call.created_at.desc()).limit(10000)
    )
    calls = result.scalars().all()

    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=["id", "phone_number", "direction", "status", "duration_secs", "started_at", "ended_at"])
    writer.writeheader()
    for c in calls:
        writer.writerow({"id": str(c.id), "phone_number": c.phone_number, "direction": c.direction, "status": c.status, "duration_secs": c.duration_secs, "started_at": c.started_at, "ended_at": c.ended_at})

    output.seek(0)
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=call_logs.csv"},
    )


@router.get("/{call_id}")
async def get_call(
    call_id: str,
    current_user: User = Depends(get_tenant_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Call).where(and_(Call.id == call_id, Call.org_id == current_user.org_id))
    )
    c = result.scalar_one_or_none()
    if not c:
        return error_response("Call not found", 404)
    return success_response(data=_call_to_dict(c))


@router.get("/{call_id}/transcript")
async def get_transcript(
    call_id: str,
    current_user: User = Depends(get_tenant_user),
    db: AsyncSession = Depends(get_db),
):
    call_result = await db.execute(
        select(Call).where(and_(Call.id == call_id, Call.org_id == current_user.org_id))
    )
    if not call_result.scalar_one_or_none():
        return error_response("Call not found", 404)

    result = await db.execute(
        select(Transcript)
        .where(Transcript.call_id == call_id)
        .order_by(Transcript.sequence_num)
    )
    transcripts = result.scalars().all()
    data = [
        {
            "id": str(t.id),
            "speaker": t.speaker,
            "text": t.text,
            "confidence": t.confidence,
            "sentiment_score": t.sentiment_score,
            "timestamp_offset_ms": t.timestamp_offset_ms,
        }
        for t in transcripts
    ]
    return success_response(data=data)


@router.get("/{call_id}/analytics")
async def get_call_analytics(
    call_id: str,
    current_user: User = Depends(get_tenant_user),
    db: AsyncSession = Depends(get_db),
):
    call_result = await db.execute(
        select(Call).where(and_(Call.id == call_id, Call.org_id == current_user.org_id))
    )
    if not call_result.scalar_one_or_none():
        return error_response("Call not found", 404)

    result = await db.execute(select(CallAnalytics).where(CallAnalytics.call_id == call_id))
    analytics = result.scalar_one_or_none()
    if not analytics:
        return error_response("Analytics not available for this call", 404)

    return success_response(data={
        "sentiment_overall": analytics.sentiment_overall,
        "sentiment_positive_pct": analytics.sentiment_positive_pct,
        "sentiment_neutral_pct": analytics.sentiment_neutral_pct,
        "sentiment_negative_pct": analytics.sentiment_negative_pct,
        "ai_summary": analytics.ai_summary,
        "key_topics": analytics.key_topics,
        "follow_up_required": analytics.follow_up_required,
        "follow_up_notes": analytics.follow_up_notes,
        "outcome": analytics.outcome,
        "total_words": analytics.total_words,
        "interruption_count": analytics.interruption_count,
    })


@router.post("/test-outbound")
async def test_outbound_call(
    payload: dict,
    # current_user: User = Depends(get_tenant_user), # Optional for test
):
    """Simple test endpoint to trigger an outbound call via Asterisk/AudioSocket."""
    to_number = payload.get("to_number", "beraxis_user")
    from app.telephony.router import telephony_router
    try:
        asterisk = telephony_router.get_provider("asterisk")
        call_id = await asterisk.make_call(to_number, lead_id="test", campaign_id="test")
        return success_response(data={"call_id": call_id, "message": f"Calling {to_number}..."})
    except Exception as e:
        return error_response(f"Outbound call failed: {str(e)}")
