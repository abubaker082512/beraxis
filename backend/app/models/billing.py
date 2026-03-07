"""
Billing models — Subscription, UsageLog, Invoice.
"""
import uuid
import enum
from sqlalchemy import (
    Column, String, Integer, Float, Boolean, Text, ForeignKey, Enum as SAEnum
)
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from app.database import Base


class PlanType(str, enum.Enum):
    STARTER = "starter"
    PROFESSIONAL = "professional"
    ENTERPRISE = "enterprise"


class SubStatus(str, enum.Enum):
    ACTIVE = "active"
    TRIALING = "trialing"
    PAST_DUE = "past_due"
    CANCELED = "canceled"
    PAUSED = "paused"


class InvoiceStatus(str, enum.Enum):
    PENDING = "pending"
    PAID = "paid"
    FAILED = "failed"
    REFUNDED = "refunded"


PLAN_LIMITS = {
    "starter": {"monthly_minutes": 500, "max_agents": 2, "max_campaigns": 5, "price": 59},
    "professional": {"monthly_minutes": 2500, "max_agents": 10, "max_campaigns": 25, "price": 179},
    "enterprise": {"monthly_minutes": -1, "max_agents": -1, "max_campaigns": -1, "price": 499},
}


class Subscription(Base):
    """Tenant subscription plan."""
    __tablename__ = "subscriptions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    org_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, unique=True)

    plan = Column(SAEnum(PlanType), default=PlanType.STARTER, nullable=False)
    status = Column(SAEnum(SubStatus), default=SubStatus.TRIALING, nullable=False)

    # Stripe IDs
    stripe_customer_id = Column(String(255), unique=True, nullable=True)
    stripe_subscription_id = Column(String(255), unique=True, nullable=True)
    stripe_price_id = Column(String(255), nullable=True)

    # Billing cycle
    current_period_start = Column(String(50), nullable=True)
    current_period_end = Column(String(50), nullable=True)
    cancel_at_period_end = Column(Boolean, default=False)

    # Overage
    overage_rate_per_min = Column(Float, default=0.05)
    overage_enabled = Column(Boolean, default=False)

    # Payment method (masked for display)
    card_brand = Column(String(20), nullable=True)
    card_last4 = Column(String(4), nullable=True)
    card_exp_month = Column(Integer, nullable=True)
    card_exp_year = Column(Integer, nullable=True)

    organization = relationship("Organization", back_populates="subscription")
    invoices = relationship("Invoice", back_populates="subscription", lazy="noload")


class UsageLog(Base):
    """Per-call minute usage — for billing aggregation."""
    __tablename__ = "usage_logs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    org_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True)
    call_id = Column(UUID(as_uuid=True), ForeignKey("calls.id", ondelete="SET NULL"), nullable=True)

    minutes_used = Column(Float, nullable=False)
    billing_period = Column(String(7), nullable=False)   # "2026-03"
    is_overage = Column(Boolean, default=False)
    cost_usd = Column(Float, default=0.0)


class Invoice(Base):
    """Billing invoice record."""
    __tablename__ = "invoices"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    org_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True)
    subscription_id = Column(UUID(as_uuid=True), ForeignKey("subscriptions.id", ondelete="SET NULL"), nullable=True)

    invoice_number = Column(String(50), unique=True, nullable=False)
    stripe_invoice_id = Column(String(255), unique=True, nullable=True)

    amount_usd = Column(Float, nullable=False)
    tax_usd = Column(Float, default=0.0)
    total_usd = Column(Float, nullable=False)

    status = Column(SAEnum(InvoiceStatus), default=InvoiceStatus.PENDING, nullable=False)
    period_start = Column(String(50), nullable=True)
    period_end = Column(String(50), nullable=True)
    paid_at = Column(String(50), nullable=True)
    invoice_url = Column(Text, nullable=True)
    invoice_pdf = Column(Text, nullable=True)
    line_items = Column(JSONB, default=list)

    subscription = relationship("Subscription", back_populates="invoices")
