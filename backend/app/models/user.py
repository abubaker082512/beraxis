"""
User, Organization, and Role models — Multi-tenant SaaS.
"""
import uuid
import enum
from sqlalchemy import (
    Column, String, Boolean, Text, ForeignKey, Enum as SAEnum, UniqueConstraint
)
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from app.database import Base


class UserRole(str, enum.Enum):
    SUPERADMIN = "superadmin"   # Platform admin
    OWNER = "owner"             # Org owner
    ADMIN = "admin"             # Org admin
    AGENT = "agent"             # Standard user
    VIEWER = "viewer"           # Read-only


class OrgStatus(str, enum.Enum):
    ACTIVE = "active"
    SUSPENDED = "suspended"
    TRIAL = "trial"


class Organization(Base):
    """Tenant / client organization."""
    __tablename__ = "organizations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    slug = Column(String(100), unique=True, nullable=False, index=True)
    status = Column(SAEnum(OrgStatus), default=OrgStatus.TRIAL, nullable=False)
    plan = Column(String(50), default="starter", nullable=False)
    max_concurrent_calls = Column(String(10), default="5")
    monthly_minutes_limit = Column(String(10), default="500")
    logo_url = Column(Text, nullable=True)
    webhook_url = Column(Text, nullable=True)
    settings = Column(JSONB, default=dict, nullable=False)

    # Relationships
    users = relationship("User", back_populates="organization", lazy="selectin")
    campaigns = relationship("Campaign", back_populates="organization", lazy="noload")
    subscription = relationship("Subscription", back_populates="organization", uselist=False)


class User(Base):
    """Platform user — belongs to an organization."""
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    org_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=True)   # Null for OAuth users
    full_name = Column(String(255), nullable=False)
    role = Column(SAEnum(UserRole), default=UserRole.AGENT, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    is_verified = Column(Boolean, default=False, nullable=False)
    avatar_url = Column(Text, nullable=True)

    # OAuth
    google_id = Column(String(255), unique=True, nullable=True)
    github_id = Column(String(255), unique=True, nullable=True)

    # API Access
    api_key = Column(String(64), unique=True, nullable=True, index=True)

    # Relationships
    organization = relationship("Organization", back_populates="users")
    refresh_tokens = relationship("RefreshToken", back_populates="user", lazy="noload")


class RefreshToken(Base):
    """Stores JWT refresh tokens for rotation."""
    __tablename__ = "refresh_tokens"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    token_hash = Column(String(255), unique=True, nullable=False, index=True)
    expires_at = Column(String(50), nullable=False)
    is_revoked = Column(Boolean, default=False, nullable=False)
    user_agent = Column(Text, nullable=True)
    ip_address = Column(String(45), nullable=True)

    user = relationship("User", back_populates="refresh_tokens")
