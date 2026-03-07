"""
Call, Transcript, and CallAnalytics models.
"""
import uuid
import enum
from sqlalchemy import (
    Column, String, Integer, Float, Text, ForeignKey, Enum as SAEnum, Boolean
)
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from app.database import Base


class CallDirection(str, enum.Enum):
    INBOUND = "inbound"
    OUTBOUND = "outbound"


class CallStatus(str, enum.Enum):
    INITIATED = "initiated"
    RINGING = "ringing"
    ANSWERED = "answered"
    VOICEMAIL = "voicemail"
    FAILED = "failed"
    COMPLETED = "completed"
    NO_ANSWER = "no_answer"
    BUSY = "busy"


class SpeakerType(str, enum.Enum):
    AI = "ai"
    USER = "user"
    SYSTEM = "system"


class Call(Base):
    """Individual call record."""
    __tablename__ = "calls"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    org_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True)
    campaign_id = Column(UUID(as_uuid=True), ForeignKey("campaigns.id", ondelete="SET NULL"), nullable=True, index=True)
    lead_id = Column(UUID(as_uuid=True), ForeignKey("leads.id", ondelete="SET NULL"), nullable=True)
    agent_id = Column(UUID(as_uuid=True), ForeignKey("ai_agents.id", ondelete="SET NULL"), nullable=True)

    # Call Details
    direction = Column(SAEnum(CallDirection), nullable=False, index=True)
    status = Column(SAEnum(CallStatus), default=CallStatus.INITIATED, nullable=False, index=True)
    phone_number = Column(String(30), nullable=False)
    caller_id = Column(String(30), nullable=True)

    # Asterisk / SIP
    asterisk_channel_id = Column(String(255), nullable=True, unique=True)
    asterisk_call_id = Column(String(255), nullable=True)
    sip_call_id = Column(String(255), nullable=True)

    # Timing
    started_at = Column(String(50), nullable=True)
    answered_at = Column(String(50), nullable=True)
    ended_at = Column(String(50), nullable=True)
    duration_secs = Column(Integer, default=0)
    ring_duration_secs = Column(Integer, default=0)

    # Recording
    recording_url = Column(Text, nullable=True)
    recording_size_bytes = Column(Integer, nullable=True)
    recording_encrypted = Column(Boolean, default=False)

    # End reason
    hangup_cause = Column(String(100), nullable=True)
    notes = Column(Text, nullable=True)

    # Relationships
    campaign = relationship("Campaign", back_populates="calls")
    lead = relationship("Lead", back_populates="calls")
    agent = relationship("AIAgent", lazy="selectin")
    transcripts = relationship("Transcript", back_populates="call", lazy="noload", order_by="Transcript.sequence_num")
    analytics = relationship("CallAnalytics", back_populates="call", uselist=False)


class Transcript(Base):
    """Individual transcript line for a call."""
    __tablename__ = "transcripts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    call_id = Column(UUID(as_uuid=True), ForeignKey("calls.id", ondelete="CASCADE"), nullable=False, index=True)

    sequence_num = Column(Integer, nullable=False)
    speaker = Column(SAEnum(SpeakerType), nullable=False)
    text = Column(Text, nullable=False)
    confidence = Column(Float, nullable=True)
    sentiment_score = Column(Float, nullable=True)  # -1.0 to 1.0
    timestamp_offset_ms = Column(Integer, default=0)  # ms from call start

    call = relationship("Call", back_populates="transcripts")


class CallAnalytics(Base):
    """Post-call analytics — sentiment, summary, follow-up."""
    __tablename__ = "call_analytics"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    call_id = Column(UUID(as_uuid=True), ForeignKey("calls.id", ondelete="CASCADE"), nullable=False, unique=True)

    # Sentiment
    sentiment_overall = Column(String(20), nullable=True)   # positive|neutral|negative
    sentiment_positive_pct = Column(Float, default=0.0)
    sentiment_neutral_pct = Column(Float, default=0.0)
    sentiment_negative_pct = Column(Float, default=0.0)

    # AI Post-call Analysis
    ai_summary = Column(Text, nullable=True)
    key_topics = Column(JSONB, default=list)
    objections_raised = Column(JSONB, default=list)
    follow_up_required = Column(Boolean, default=False)
    follow_up_notes = Column(Text, nullable=True)
    outcome = Column(String(100), nullable=True)   # demo_booked | not_interested | callback | etc.

    # Word/talk stats
    total_words = Column(Integer, default=0)
    ai_talk_time_secs = Column(Integer, default=0)
    user_talk_time_secs = Column(Integer, default=0)
    silence_time_secs = Column(Integer, default=0)
    interruption_count = Column(Integer, default=0)

    call = relationship("Call", back_populates="analytics")
