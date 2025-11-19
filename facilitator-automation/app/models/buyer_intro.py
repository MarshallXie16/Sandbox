"""
SQLAlchemy model for Introduced Buyers.
Tracks which buyers have been introduced to a seller/listing under a facilitator engagement.
"""

from datetime import datetime
from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    Text,
    Enum,
    ForeignKey,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.database import Base
from app.models.enums import BuyerIntroStatus, IntroductionChannel


class FacilitatorBuyerIntro(Base):
    """
    Represents an Introduced Buyer under a facilitator engagement.

    This is the SOURCE OF TRUTH for "Introduced Buyer" status, which is
    critical for success fee calculation. Only buyers with an entry in this
    table are eligible for success fee if they close a deal.

    Legal context: This table documents the introduction relationship,
    establishing the facilitator's claim to success fees if this specific
    buyer closes a deal with the seller.
    """

    __tablename__ = "facilitator_buyer_intros"

    # Primary Key
    id = Column(Integer, primary_key=True, index=True)

    # Foreign key to engagement
    engagement_id = Column(
        Integer,
        ForeignKey("facilitator_engagements.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    # Link to CRM contact (buyer)
    buyer_contact_id = Column(Integer, nullable=False, index=True)

    # Introduction metadata
    introduced_at = Column(DateTime, nullable=False, server_default=func.now())
    introduction_channel = Column(
        Enum(IntroductionChannel),
        nullable=False,
        default=IntroductionChannel.EMAIL
    )

    # Status tracking
    status = Column(
        Enum(BuyerIntroStatus),
        nullable=False,
        default=BuyerIntroStatus.INVITED,
        index=True
    )

    # Timeline tracking
    nda_sent_at = Column(DateTime, nullable=True)
    nda_signed_at = Column(DateTime, nullable=True)
    teaser_sent_at = Column(DateTime, nullable=True)
    info_access_granted_at = Column(DateTime, nullable=True)
    last_contact_at = Column(DateTime, nullable=True)

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
    engagement = relationship("FacilitatorEngagement", back_populates="buyer_intros")
    offers = relationship(
        "FacilitatorOffer",
        back_populates="buyer_intro",
        cascade="all, delete-orphan",
        lazy="selectin"
    )
    closings = relationship(
        "FacilitatorClosing",
        back_populates="buyer_intro",
        cascade="all, delete-orphan",
        lazy="selectin"
    )
    events = relationship(
        "FacilitatorEvent",
        back_populates="buyer_intro",
        cascade="all, delete-orphan",
        lazy="selectin"
    )

    def __repr__(self) -> str:
        return (
            f"<FacilitatorBuyerIntro("
            f"id={self.id}, "
            f"engagement_id={self.engagement_id}, "
            f"buyer_contact_id={self.buyer_contact_id}, "
            f"status={self.status.value}"
            f")>"
        )

    def is_active(self) -> bool:
        """Check if this buyer intro is in an active state."""
        active_statuses = {
            BuyerIntroStatus.INVITED,
            BuyerIntroStatus.NDA_PENDING,
            BuyerIntroStatus.NDA_SIGNED,
            BuyerIntroStatus.TEASER_SENT,
            BuyerIntroStatus.INFO_ACCESS,
            BuyerIntroStatus.OFFER_MADE,
        }
        return self.status in active_statuses

    def has_nda_signed(self) -> bool:
        """Check if NDA has been signed."""
        return self.nda_signed_at is not None
