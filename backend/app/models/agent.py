"""
AI Agent model — configures personality, prompt, voice, and conversation flow.
"""
import uuid
from sqlalchemy import Column, String, Float, Boolean, Text, ForeignKey, Integer
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from app.database import Base


class AIAgent(Base):
    """AI Agent configuration — reusable across campaigns."""
    __tablename__ = "ai_agents"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    org_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True)

    # Identity
    name = Column(String(255), nullable=False)
    identity = Column(String(255), nullable=True)   # e.g. "Sarah, Senior Sales Rep"
    description = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)

    # Prompt
    system_prompt = Column(Text, nullable=True)
    dynamic_variables = Column(JSONB, default=list)  # [{"key": "first_name", "default": ""}]
    knowledge_base = Column(Text, nullable=True)
    objection_handling = Column(JSONB, default=list)

    # Conversation Flow
    flow_steps = Column(JSONB, default=list)
    # [{"title": "Greeting", "content": "Hello {{first_name}}...", "type": "statement|question"}]

    # Voice Settings
    voice_id = Column(String(100), nullable=True)          # Piper voice model name
    voice_speed = Column(Float, default=1.0)               # 0.5 – 2.0
    voice_stability = Column(Float, default=0.75)          # 0.0 – 1.0
    voice_sample_url = Column(Text, nullable=True)         # Cloned voice sample

    # LLM Overrides (per-agent, falls back to global settings)
    llm_temperature = Column(Float, nullable=True)
    llm_max_tokens = Column(Integer, nullable=True)

    # Stats
    total_calls = Column(Integer, default=0)
    avg_call_duration_secs = Column(Integer, default=0)
    overall_sentiment_score = Column(Float, default=0.0)

    # Version / audit
    version = Column(Integer, default=1)

    organization = relationship("Organization")
