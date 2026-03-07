"""
Celery background tasks:
- Campaign dialer logic
- Call analytics processing (Sentiment/Summary)
- Billing usage aggregation
- Recording upload to external storage
"""
import asyncio
import logging
from datetime import datetime, timezone
from celery import shared_task
from sqlalchemy import select, and_, func

from app.workers.celery_app import celery_app
from app.database import AsyncSessionLocal
from app.models.campaign import Campaign, CampaignStatus, Lead, LeadStatus
from app.models.call import Call, CallStatus, CallAnalytics, Transcript
from app.models.billing import UsageLog, Subscription, PlanType, PLAN_LIMITS
from app.models.user import Organization
from app.telephony.router import telephony_router

logger = logging.getLogger(__name__)


# ── Utility for async in Celery ───────────────────────────────────────────────
def run_async(coro):
    loop = asyncio.get_event_loop()
    if loop.is_running():
        # Fallback if somehow triggered inside an async loop (test contexts)
        import nest_asyncio
        nest_asyncio.apply()
        return asyncio.run(coro)
    return loop.run_until_complete(coro)


# ── Campaign Orchestration ────────────────────────────────────────────────────
@shared_task(name="app.workers.tasks.sweep_active_campaigns")
def sweep_active_campaigns():
    """Runs minutely via Beat. Finds active campaigns and queues dialing."""
    async def _sweep():
        async with AsyncSessionLocal() as db:
            # Simple check: find campaigns that are active
            result = await db.execute(select(Campaign).where(Campaign.status == CampaignStatus.ACTIVE))
            active_campaigns = result.scalars().all()
            for c in active_campaigns:
                # Trigger the dialer for this campaign
                process_campaign_dial.delay(str(c.id))
    run_async(_sweep())


@shared_task(name="app.workers.tasks.process_campaign_dial")
def process_campaign_dial(campaign_id: str):
    """Pulls next lead from campaign queue and dials."""
    async def _dial():
        async with AsyncSessionLocal() as db:
            result = await db.execute(select(Campaign).where(Campaign.id == campaign_id))
            c = result.scalar_one_or_none()
            
            if not c or c.status != CampaignStatus.ACTIVE:
                return "Campaign inactive or missing"
            
            # Fetch a pending lead
            lead_result = await db.execute(
                select(Lead).where(
                    and_(Lead.campaign_id == campaign_id, Lead.status == LeadStatus.PENDING)
                ).limit(1).with_for_update(skip_locked=True)
            )
            lead = lead_result.scalar_one_or_none()
            
            if not lead:
                # No more pending leads list. Mark campaign completed?
                # c.status = CampaignStatus.COMPLETED
                # await db.commit()
                return "No pending leads"

            # Create Call record
            call = Call(
                org_id=c.org_id,
                campaign_id=c.id,
                lead_id=lead.id,
                agent_id=c.agent_id,
                direction="outbound",
                status=CallStatus.INITIATED,
                phone_number=lead.phone
            )
            db.add(call)
            
            # Mark lead called
            lead.status = LeadStatus.CALLED
            lead.last_called_at = datetime.now(timezone.utc).isoformat()
            c.calls_made += 1
            
            await db.commit()
            
            # Trigger Asterisk outbound call via Telephony Router
            logger.info(f"Originating call to {lead.phone} for campaign {c.id}")
            provider = telephony_router.get_provider("asterisk")
            try:
                # Using the new make_call method which is optimized for AudioSocket
                call_id_ari = await provider.make_call(
                    to_number=lead.phone,
                    lead_id=str(lead.id),
                    campaign_id=str(c.id)
                )
                if not call_id_ari:
                    call.status = CallStatus.FAILED
                    await db.commit()
                    return f"ARI Call Failed to {lead.phone}"
            except Exception as e:
                logger.error(f"Failed to originate call: {e}")
                call.status = CallStatus.FAILED
                await db.commit()
                return f"ARI Call Error: {str(e)}"
            
            return f"Initiated {lead.phone} ({call.id})"

    return run_async(_dial())


# ── Analytics & Post-Call ─────────────────────────────────────────────────────
@shared_task(name="app.workers.tasks.post_call_analytics")
def post_call_analytics(call_id: str):
    """Runs after a call finishes to generate LLM summary and sentiment."""
    async def _analyze():
        async with AsyncSessionLocal() as db:
            call = (await db.execute(select(Call).where(Call.id == call_id))).scalar_one_or_none()
            if not call:
                return "Call not found"

            transcripts = (await db.execute(
                select(Transcript).where(Transcript.call_id == call_id).order_by(Transcript.sequence_num)
            )).scalars().all()
            
            if not transcripts:
                return "No transcript to analyze"
                
            full_text = "\n".join([f"{t.speaker}: {t.text}" for t in transcripts])
            word_count = len(full_text.split())

            # Perform mock summary and sentiment logic for stub
            # In production, this makes a blocking call to the Llama 3 LLM asking it to summarize
            
            summary = "[AI Summary generated from transcript]"
            sentiment = "positive" if "yes" in full_text.lower() or "great" in full_text.lower() else ("negative" if "no" in full_text.lower() else "neutral")
            
            analytics = CallAnalytics(
                call_id=call.id,
                sentiment_overall=sentiment,
                sentiment_positive_pct=80.0 if sentiment == "positive" else 20.0,
                sentiment_neutral_pct=10.0,
                sentiment_negative_pct=10.0 if sentiment == "positive" else 70.0,
                ai_summary=summary,
                key_topics=["pricing", "availability"],
                follow_up_required="yes" in full_text.lower(),
                follow_up_notes="Customer requested callback" if "yes" in full_text.lower() else None,
                total_words=word_count,
            )
            db.add(analytics)
            await db.commit()
            return f"Analytics generated for {call_id}"

    return run_async(_analyze())


# ── Billing & Usage ───────────────────────────────────────────────────────────
@shared_task(name="app.workers.tasks.aggregate_usage")
def aggregate_usage():
    """Calculates minutes used per tenant in the past hour and writes UsageLog."""
    async def _aggregate():
        async with AsyncSessionLocal() as db:
            now = datetime.now(timezone.utc)
            billing_period = now.strftime("%Y-%m")
            
            # Find recently completed calls that haven't been billed
            # (Simplified approach: in prod, use a boolean billed flag on Call)
            result = await db.execute(
                select(Call.org_id, func.sum(Call.duration_secs))
                .where(Call.status == CallStatus.COMPLETED)
                .group_by(Call.org_id)
            )
            agg_data = result.all()
            
            for org_id, total_secs in agg_data:
                mins = round(total_secs / 60.0, 2)
                if mins <= 0: continue
                
                # Check limits
                sub = (await db.execute(select(Subscription).where(Subscription.org_id == org_id))).scalar_one_or_none()
                if sub:
                    # Append usage log
                    ul = UsageLog(org_id=org_id, minutes_used=mins, amount_usd=0.0, billing_period=billing_period)
                    db.add(ul)
            await db.commit()
    return run_async(_aggregate())


@shared_task(name="app.workers.tasks.store_recording")
def store_recording(call_id: str, local_filepath: str):
    """Compresses WAV to MP3 and uploads to S3-compatible storage."""
    # Stub: mock S3 upload
    async def _store():
        async with AsyncSessionLocal() as db:
            call = (await db.execute(select(Call).where(Call.id == call_id))).scalar_one_or_none()
            if call:
                call.recording_url = f"https://s3.amazonaws.com/beraxis-recordings/{call_id}.mp3"
                await db.commit()
    return run_async(_store())
