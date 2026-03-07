"""
Campaign and Lead models.
"""
import uuid
import enum
from sqlalchemy import (
    Column, String, Integer, Float, Text, ForeignKey, Enum as SAEnum, Boolean
)
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from app.database import Base


class CampaignStatus(str, enum.Enum):
    DRAFT = "draft"
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    ARCHIVED = "archived"


class LeadStatus(str, enum.Enum):
    PENDING = "pending"
    CALLING = "calling"
    CALLED = "called"
    ANSWERED = "answered"
    VOICEMAIL = "voicemail"
    FAILED = "failed"
    DNC = "dnc"             # Do Not Call
    CONVERTED = "converted"


class Campaign(Base):
    """Outbound calling campaign."""
    __tablename__ = "campaigns"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    org_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True)
    agent_id = Column(UUID(as_uuid=True), ForeignKey("ai_agents.id", ondelete="SET NULL"), nullable=True)

    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    status = Column(SAEnum(CampaignStatus), default=CampaignStatus.DRAFT, nullable=False)

    # Statistics (denormalized for fast reads)
    total_leads = Column(Integer, default=0)
    calls_made = Column(Integer, default=0)
    calls_answered = Column(Integer, default=0)
    calls_voicemail = Column(Integer, default=0)
    calls_failed = Column(Integer, default=0)
    conversions = Column(Integer, default=0)

    # Scheduling
    schedule_timezone = Column(String(50), default="UTC")
    schedule_start_time = Column(String(10), default="09:00")   # HH:MM
    schedule_end_time = Column(String(10), default="18:00")
    schedule_days = Column(JSONB, default=list)                  # ["mon","tue",...]

    # Settings
    max_retries = Column(Integer, default=3)
    retry_delay_hours = Column(Integer, default=24)
    caller_id_override = Column(String(50), nullable=True)
    settings = Column(JSONB, default=dict)

    # Relationships
    organization = relationship("Organization", back_populates="campaigns")
    leads = relationship("Lead", back_populates="campaign", lazy="noload")
    calls = relationship("Call", back_populates="campaign", lazy="noload")
    agent = relationship("AIAgent", lazy="selectin")

    @property
    def success_rate(self) -> float:
        if self.calls_made == 0:
            return 0.0
        return round((self.calls_answered / self.calls_made) * 100, 1)


class Lead(Base):
    """Individual lead / contact within a campaign."""
    __tablename__ = "leads"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    org_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True)
    campaign_id = Column(UUID(as_uuid=True), ForeignKey("campaigns.id", ondelete="CASCADE"), nullable=True, index=True)

    # Contact Info
    first_name = Column(String(100), nullable=True)
    last_name = Column(String(100), nullable=True)
    phone = Column(String(30), nullable=False)
    email = Column(String(255), nullable=True)
    company = Column(String(255), nullable=True)
    title = Column(String(100), nullable=True)

    # Status
    status = Column(SAEnum(LeadStatus), default=LeadStatus.PENDING, nullable=False, index=True)
    retry_count = Column(Integer, default=0)
    last_called_at = Column(String(50), nullable=True)

    # Custom data from CSV import
    custom_vars = Column(JSONB, default=dict)

    # Relationships
    campaign = relationship("Campaign", back_populates="leads")
    calls = relationship("Call", back_populates="lead", lazy="noload")

    @property
    def full_name(self) -> str:
        parts = [self.first_name or "", self.last_name or ""]
        return " ".join(p for p in parts if p).strip() or "Unknown"
