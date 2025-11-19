"""
SQLAlchemy model for Facilitator Engagements.
Represents Phase 2 engagement between Capital Link (as facilitator) and a seller.
"""

from datetime import datetime
from typing import Optional
from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    Numeric,
    Text,
    Enum,
    JSON,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.database import Base
from app.models.enums import EngagementStatus


class FacilitatorEngagement(Base):
    """
    Represents a facilitator engagement for a seller/listing.

    This is the core entity that tracks the relationship between
    Capital Link (as facilitator, NOT broker) and a seller/company/listing.

    Legal context: This is a facilitator/finder agreement, not a brokerage agreement.
    No fiduciary duty, no agency role.
    """

    __tablename__ = "facilitator_engagements"

    # Primary Key
    id = Column(Integer, primary_key=True, index=True)

    # Human-readable engagement code (e.g., FAC-2025-0007)
    engagement_code = Column(String(50), unique=True, nullable=False, index=True)

    # Links to CRM entities (seller/company/listing)
    # These would be foreign keys if CRM is in same DB, or just IDs if using API
    seller_contact_id = Column(Integer, nullable=False, index=True)
    company_id = Column(Integer, nullable=True, index=True)
    listing_id = Column(Integer, nullable=True, index=True)

    # Engagement status
    status = Column(
        Enum(EngagementStatus),
        nullable=False,
        default=EngagementStatus.DRAFT,
        index=True
    )

    # Engagement timeline
    start_date = Column(DateTime, nullable=True)
    end_date = Column(DateTime, nullable=True)
    tail_end_date = Column(
        DateTime,
        nullable=True,
        comment="Date until which introduced buyers are still valid for success fee"
    )

    # Commercial terms
    offer_fee_fixed = Column(
        Numeric(12, 2),
        nullable=False,
        default=5000.00,
        comment="Fixed fee due when an introduced buyer makes an offer"
    )
    success_fee_rate = Column(
        Numeric(5, 4),
        nullable=False,
        default=0.05,
        comment="Success fee rate (0.05 = 5%)"
    )
    currency = Column(String(3), nullable=False, default="CAD")

    # Structured terms and notes
    terms = Column(
        JSON,
        nullable=True,
        comment="Additional structured terms (caps, minimums, special conditions)"
    )
    notes = Column(Text, nullable=True)

    # Audit fields
    created_at = Column(DateTime, nullable=False, server_default=func.now())
    updated_at = Column(
        DateTime,
        nullable=False,
        server_default=func.now(),
        onupdate=func.now()
    )
    created_by = Column(String(100), nullable=True)

    # Relationships
    buyer_intros = relationship(
        "FacilitatorBuyerIntro",
        back_populates="engagement",
        cascade="all, delete-orphan",
        lazy="selectin"
    )
    offers = relationship(
        "FacilitatorOffer",
        back_populates="engagement",
        cascade="all, delete-orphan",
        lazy="selectin"
    )
    closings = relationship(
        "FacilitatorClosing",
        back_populates="engagement",
        cascade="all, delete-orphan",
        lazy="selectin"
    )
    events = relationship(
        "FacilitatorEvent",
        back_populates="engagement",
        cascade="all, delete-orphan",
        lazy="selectin"
    )

    def __repr__(self) -> str:
        return (
            f"<FacilitatorEngagement("
            f"id={self.id}, "
            f"code={self.engagement_code}, "
            f"status={self.status.value}, "
            f"seller_contact_id={self.seller_contact_id}"
            f")>"
        )

    def is_active(self) -> bool:
        """Check if engagement is in an active state."""
        active_states = {
            EngagementStatus.ACTIVE,
            EngagementStatus.SHORTLISTING,
            EngagementStatus.OUTREACH_IN_PROGRESS,
            EngagementStatus.OFFERS_IN_PLAY,
            EngagementStatus.UNDER_AGREEMENT,
        }
        return self.status in active_states

    def is_closed(self) -> bool:
        """Check if engagement is closed."""
        closed_states = {
            EngagementStatus.CLOSED_SUCCESS,
            EngagementStatus.CLOSED_NO_DEAL,
            EngagementStatus.TERMINATED,
        }
        return self.status in closed_states
