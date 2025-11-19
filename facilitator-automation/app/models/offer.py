"""
SQLAlchemy model for Offers.
Represents non-binding expressions of interest/offers from introduced buyers.
"""

from datetime import datetime
from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    Numeric,
    Text,
    Enum,
    Boolean,
    ForeignKey,
    JSON,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.database import Base
from app.models.enums import OfferStatus


class FacilitatorOffer(Base):
    """
    Represents an offer from an introduced buyer.

    This tracks non-binding expressions of interest and formal offers.
    When an offer is received, a fixed offer fee (default $5k) may be due.

    Legal context: These are tracked as part of workflow/milestones, not as
    legal documents. The actual offer documents are stored elsewhere (CRM, file system).
    """

    __tablename__ = "facilitator_offers"

    # Primary Key
    id = Column(Integer, primary_key=True, index=True)

    # Foreign keys
    engagement_id = Column(
        Integer,
        ForeignKey("facilitator_engagements.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    buyer_intro_id = Column(
        Integer,
        ForeignKey("facilitator_buyer_intros.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    # Offer details
    offer_date = Column(DateTime, nullable=False)
    headline_price = Column(Numeric(15, 2), nullable=False)
    currency = Column(String(3), nullable=False, default="CAD")

    # Deal structure (simplified JSON)
    # Example: {"deal_type": "asset", "cash": 2000000, "earnout": 500000}
    structure = Column(
        JSON,
        nullable=True,
        comment="Basic deal structure: cash, earnout, vendor takeback, etc."
    )

    # Status
    status = Column(
        Enum(OfferStatus),
        nullable=False,
        default=OfferStatus.RECEIVED,
        index=True
    )

    # Offer fee tracking (default $5k when offer is received)
    offer_fee_amount = Column(
        Numeric(12, 2),
        nullable=False,
        default=5000.00,
        comment="Fixed fee due at offer stage"
    )
    offer_fee_invoiced = Column(Boolean, nullable=False, default=False)
    offer_fee_paid = Column(Boolean, nullable=False, default=False)

    # Notes
    notes = Column(Text, nullable=True)

    # Audit fields
    created_at = Column(DateTime, nullable=False, server_default=func.now())
    updated_at = Column(
        DateTime,
        nullable=False,
        server_default=func.now(),
        onupdate=func.now()
    )

    # Relationships
    engagement = relationship("FacilitatorEngagement", back_populates="offers")
    buyer_intro = relationship("FacilitatorBuyerIntro", back_populates="offers")
    events = relationship(
        "FacilitatorEvent",
        back_populates="offer",
        cascade="all, delete-orphan",
        lazy="selectin"
    )

    def __repr__(self) -> str:
        return (
            f"<FacilitatorOffer("
            f"id={self.id}, "
            f"engagement_id={self.engagement_id}, "
            f"buyer_intro_id={self.buyer_intro_id}, "
            f"headline_price={self.headline_price}, "
            f"status={self.status.value}"
            f")>"
        )

    def is_active(self) -> bool:
        """Check if offer is in an active state."""
        active_statuses = {
            OfferStatus.RECEIVED,
            OfferStatus.UNDER_REVIEW,
            OfferStatus.ACCEPTED,
        }
        return self.status in active_statuses

    def is_fee_fully_paid(self) -> bool:
        """Check if offer fee has been invoiced and paid."""
        return self.offer_fee_invoiced and self.offer_fee_paid
