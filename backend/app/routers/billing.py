"""
Billing router — subscription, invoices, usage tracking.
Maps to: /dashboard/billing (Billing.tsx)
"""
from typing import Optional
from fastapi import APIRouter, Depends, Request, Header
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from pydantic import BaseModel
import stripe

from app.database import get_db
from app.dependencies import get_tenant_user
from app.models.user import User
from app.models.billing import Subscription, Invoice, UsageLog, PlanType, PLAN_LIMITS
from app.config import settings
from app.utils.responses import success_response, error_response

stripe.api_key = settings.STRIPE_SECRET_KEY
router = APIRouter(prefix="/billing", tags=["Billing"])


class SubscribeRequest(BaseModel):
    plan: str
    payment_method_id: Optional[str] = None


@router.get("/subscription")
async def get_subscription(
    current_user: User = Depends(get_tenant_user),
    db: AsyncSession = Depends(get_db),
):
    """Current plan + usage. Maps to Billing.tsx hero card."""
    result = await db.execute(
        select(Subscription).where(Subscription.org_id == current_user.org_id)
    )
    sub = result.scalar_one_or_none()

    # Usage for current billing period
    import datetime
    period = datetime.datetime.now().strftime("%Y-%m")
    usage_result = await db.execute(
        select(func.sum(UsageLog.minutes_used)).where(
            and_(UsageLog.org_id == current_user.org_id, UsageLog.billing_period == period)
        )
    )
    minutes_used = float(usage_result.scalar() or 0)
    plan_key = sub.plan.value if sub else "starter"
    monthly_limit = PLAN_LIMITS[plan_key]["monthly_minutes"]

    return success_response(data={
        "plan": plan_key,
        "status": sub.status if sub else "trialing",
        "monthly_cost_usd": PLAN_LIMITS[plan_key]["price"],
        "next_billing_date": sub.current_period_end if sub else None,
        "card_brand": sub.card_brand if sub else None,
        "card_last4": sub.card_last4 if sub else None,
        "minutes_used": minutes_used,
        "monthly_minutes_limit": monthly_limit,
        "usage_pct": round((minutes_used / monthly_limit * 100) if monthly_limit > 0 else 0, 1),
        "stripe_customer_id": sub.stripe_customer_id if sub else None,
    })


@router.get("/invoices")
async def get_invoices(
    current_user: User = Depends(get_tenant_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Invoice)
        .where(Invoice.org_id == current_user.org_id)
        .order_by(Invoice.created_at.desc())
        .limit(24)
    )
    invoices = result.scalars().all()
    data = [
        {
            "id": str(inv.id),
            "invoice_number": inv.invoice_number,
            "amount_usd": inv.amount_usd,
            "total_usd": inv.total_usd,
            "status": inv.status,
            "period_start": inv.period_start,
            "period_end": inv.period_end,
            "paid_at": inv.paid_at,
            "invoice_url": inv.invoice_url,
            "created_at": str(inv.created_at),
        }
        for inv in invoices
    ]
    return success_response(data=data)


@router.post("/subscribe")
async def subscribe(
    data: SubscribeRequest,
    current_user: User = Depends(get_tenant_user),
    db: AsyncSession = Depends(get_db),
):
    if data.plan not in PLAN_LIMITS:
        return error_response("Invalid plan", 400)

    result = await db.execute(select(Subscription).where(Subscription.org_id == current_user.org_id))
    sub = result.scalar_one_or_none()

    try:
        price_map = {
            "starter": settings.STRIPE_STARTER_PRICE_ID,
            "professional": settings.STRIPE_PROFESSIONAL_PRICE_ID,
            "enterprise": settings.STRIPE_ENTERPRISE_PRICE_ID,
        }

        if not sub:
            customer = stripe.Customer.create(email=current_user.email, name=current_user.full_name)
            stripe_sub = stripe.Subscription.create(
                customer=customer.id,
                items=[{"price": price_map[data.plan]}],
                payment_method=data.payment_method_id,
                expand=["latest_invoice.payment_intent"],
            )
            sub = Subscription(
                org_id=current_user.org_id,
                plan=PlanType(data.plan),
                stripe_customer_id=customer.id,
                stripe_subscription_id=stripe_sub.id,
                stripe_price_id=price_map[data.plan],
            )
            db.add(sub)
        else:
            # Update existing
            sub.plan = PlanType(data.plan)

        await db.commit()
        return success_response(data={"plan": data.plan}, message=f"Subscribed to {data.plan} plan")
    except stripe.StripeError as e:
        return error_response(f"Payment error: {str(e)}", 402)
    except Exception:
        return error_response("Subscription failed. Check Stripe configuration.", 500)


@router.post("/cancel")
async def cancel_subscription(
    current_user: User = Depends(get_tenant_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Subscription).where(Subscription.org_id == current_user.org_id))
    sub = result.scalar_one_or_none()
    if not sub:
        return error_response("No active subscription found", 404)
    sub.cancel_at_period_end = True
    await db.commit()
    return success_response(message="Subscription will be canceled at end of billing period")


@router.get("/usage")
async def get_usage(
    current_user: User = Depends(get_tenant_user),
    db: AsyncSession = Depends(get_db),
):
    """Last 6 months usage breakdown."""
    import datetime
    data = []
    for i in range(5, -1, -1):
        dt = datetime.datetime.now()
        period_dt = dt.replace(day=1) - datetime.timedelta(days=i * 28)
        period = period_dt.strftime("%Y-%m")
        result = await db.execute(
            select(func.sum(UsageLog.minutes_used)).where(
                and_(UsageLog.org_id == current_user.org_id, UsageLog.billing_period == period)
            )
        )
        mins = float(result.scalar() or 0)
        data.append({"month": period_dt.strftime("%b %Y"), "period": period, "minutes_used": mins})
    return success_response(data=data)


@router.post("/webhook")
async def stripe_webhook(request: Request, stripe_signature: str = Header(None)):
    """Stripe webhook handler — handles payment events."""
    from app.database import AsyncSessionLocal
    import datetime
    
    payload = await request.body()
    try:
        event = stripe.Webhook.construct_event(payload, stripe_signature, settings.STRIPE_WEBHOOK_SECRET)
    except Exception:
        return error_response("Invalid webhook signature", 400)

    async with AsyncSessionLocal() as db:
        # Handle events
        if event["type"] == "invoice.payment_succeeded":
            invoice_data = event["data"]["object"]
            customer_id = invoice_data.get("customer")
            
            # Find subscription by customer ID
            stmt = select(Subscription).where(Subscription.stripe_customer_id == customer_id)
            sub = (await db.execute(stmt)).scalar_one_or_none()
            
            if sub:
                sub.status = "active"
                sub.current_period_end = datetime.datetime.fromtimestamp(
                    invoice_data.get("period_end", 0)
                )
                
                # Record invoice
                new_inv = Invoice(
                    org_id=sub.org_id,
                    stripe_invoice_id=invoice_data.get("id"),
                    invoice_number=invoice_data.get("number"),
                    amount_usd=invoice_data.get("amount_due", 0) / 100.0,
                    total_usd=invoice_data.get("total", 0) / 100.0,
                    status="paid",
                    invoice_url=invoice_data.get("hosted_invoice_url")
                )
                db.add(new_inv)
                await db.commit()
                logger.info(f"Processed payment for Org {sub.org_id}")

        elif event["type"] == "customer.subscription.deleted":
            sub_data = event["data"]["object"]
            sub_id = sub_data.get("id")
            
            stmt = select(Subscription).where(Subscription.stripe_subscription_id == sub_id)
            sub = (await db.execute(stmt)).scalar_one_or_none()
            if sub:
                sub.status = "canceled"
                await db.commit()
                logger.info(f"Canceled subscription {sub_id}")

    return success_response(message="Webhook processed")
