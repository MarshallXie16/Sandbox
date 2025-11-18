"""
SQLAlchemy models for portal-specific tables.

These tables are managed by this service and track portal-specific data
like member mappings, interests, and resources.
"""

from datetime import datetime
from typing import Optional
from sqlalchemy import String, Integer, TIMESTAMP, JSON, Text, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class PortalMember(Base):
    """
    Portal member mapping table.

    Maps Ultimate Member user IDs to IndieStack CRM contact IDs.
    This is the canonical mapping for WordPress users to CRM contacts.
    """

    __tablename__ = "portal_members"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    um_user_id: Mapped[str] = mapped_column(
        String(100), nullable=False, unique=True, index=True
    )  # WordPress/Ultimate Member user ID
    contact_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("contacts.id"), nullable=False, index=True
    )
    role: Mapped[str] = mapped_column(
        String(50), nullable=False
    )  # buyer, seller, both
    is_active: Mapped[bool] = mapped_column(default=True, nullable=False)
    metadata: Mapped[Optional[dict]] = mapped_column(JSON)  # JSONB for flexible data
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP, default=datetime.utcnow, nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        TIMESTAMP, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    def __repr__(self) -> str:
        return f"<PortalMember(id={self.id}, um_user_id={self.um_user_id}, contact_id={self.contact_id}, role={self.role})>"


class PortalInterest(Base):
    """
    Portal interest tracking table.

    Tracks when a buyer expresses interest in a listing (deal).
    Each interest creates both a database record and an activity in the CRM.
    """

    __tablename__ = "portal_interests"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    member_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("portal_members.id"), nullable=False, index=True
    )
    contact_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("contacts.id"), nullable=False, index=True
    )
    listing_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("deals.id"), nullable=False, index=True
    )
    note: Mapped[Optional[str]] = mapped_column(Text)  # Optional buyer note
    status: Mapped[str] = mapped_column(
        String(50), default="new", nullable=False
    )  # new, contacted, qualified, disqualified
    metadata: Mapped[Optional[dict]] = mapped_column(JSON)  # JSONB
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP, default=datetime.utcnow, nullable=False, index=True
    )
    updated_at: Mapped[datetime] = mapped_column(
        TIMESTAMP, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    __table_args__ = (
        UniqueConstraint("member_id", "listing_id", name="uq_member_listing_interest"),
    )

    def __repr__(self) -> str:
        return f"<PortalInterest(id={self.id}, member_id={self.member_id}, listing_id={self.listing_id}, status={self.status})>"


class PortalResource(Base):
    """
    Portal resource metadata table.

    Stores metadata for downloadable resources, templates, and gated content.
    Actual files are stored externally (S3, CDN, etc.).
    """

    __tablename__ = "portal_resources"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    slug: Mapped[str] = mapped_column(
        String(100), nullable=False, unique=True, index=True
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)
    category: Mapped[str] = mapped_column(
        String(50), nullable=False, index=True
    )  # buyer, seller, general
    resource_type: Mapped[str] = mapped_column(
        String(50), nullable=False
    )  # pdf, template, video, etc.
    file_url: Mapped[Optional[str]] = mapped_column(String(500))  # External URL
    file_size: Mapped[Optional[int]] = mapped_column(Integer)  # Size in bytes
    is_gated: Mapped[bool] = mapped_column(
        default=True, nullable=False
    )  # Requires login
    is_active: Mapped[bool] = mapped_column(default=True, nullable=False)
    download_count: Mapped[int] = mapped_column(default=0, nullable=False)
    metadata: Mapped[Optional[dict]] = mapped_column(JSON)  # JSONB
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP, default=datetime.utcnow, nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        TIMESTAMP, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    def __repr__(self) -> str:
        return f"<PortalResource(id={self.id}, slug={self.slug}, category={self.category})>"
