"""
SQLAlchemy model for Closings.
Represents the final closing/deal outcome under a facilitator engagement.
"""

from datetime import datetime
from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    Numeric,
    Text,
    Boolean,
    ForeignKey,
    JSON,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.database import Base


class FacilitatorClosing(Base):
    """
    Represents a closing/deal outcome under a facilitator engagement.

    This records the final deal closure with an introduced buyer and
    calculates the success fee:
    - Gross success fee = final_price * success_fee_rate (typically 5%)
    - Credit = any offer fees already paid (typically $5k)
    - Net success fee = gross - credit

    Legal context: Success fees are ONLY calculated when closing with an
    Introduced Buyer (i.e., a buyer with an entry in facilitator_buyer_intros).
    This is the core of the facilitator/finder agreement.
    """

    __tablename__ = "facilitator_closings"

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
        index=True,
        comment="The introduced buyer that closed the deal - REQUIRED for success fee"
    )

    # Closing details
    closing_date = Column(DateTime, nullable=False)
    final_price = Column(Numeric(15, 2), nullable=False)
    currency = Column(String(3), nullable=False, default="CAD")

    # Final deal structure (simplified JSON)
    final_structure = Column(
        JSON,
        nullable=True,
        comment="Final deal structure summary"
    )

    # Success fee calculation
    # These are calculated at closing time and stored for audit trail
    success_fee_rate = Column(
        Numeric(5, 4),
        nullable=False,
        comment="Success fee rate applied (copied from engagement at closing time)"
    )
    success_fee_gross_amount = Column(
        Numeric(15, 2),
        nullable=False,
        comment="Gross success fee = final_price * success_fee_rate"
    )
    offer_fee_credit_amount = Column(
        Numeric(12, 2),
        nullable=False,
        default=0.00,
        comment="Credit for offer fees already paid (capped at gross amount)"
    )
    success_fee_net_amount = Column(
        Numeric(15, 2),
        nullable=False,
        comment="Net success fee = gross - credit"
    )

    # Payment tracking
    invoiced = Column(Boolean, nullable=False, default=False)
    paid = Column(Boolean, nullable=False, default=False)

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
    engagement = relationship("FacilitatorEngagement", back_populates="closings")
    buyer_intro = relationship("FacilitatorBuyerIntro", back_populates="closings")
    events = relationship(
        "FacilitatorEvent",
        back_populates="closing",
        cascade="all, delete-orphan",
        lazy="selectin"
    )

    def __repr__(self) -> str:
        return (
            f"<FacilitatorClosing("
            f"id={self.id}, "
            f"engagement_id={self.engagement_id}, "
            f"buyer_intro_id={self.buyer_intro_id}, "
            f"final_price={self.final_price}, "
            f"success_fee_net={self.success_fee_net_amount}"
            f")>"
        )

    def is_fully_paid(self) -> bool:
        """Check if success fee has been invoiced and paid."""
        return self.invoiced and self.paid

    def get_total_facilitator_revenue(self) -> float:
        """
        Calculate total revenue from this closing.
        This is: offer_fee_credit_amount (already paid) + success_fee_net_amount (due).
        """
        return float(self.offer_fee_credit_amount + self.success_fee_net_amount)
