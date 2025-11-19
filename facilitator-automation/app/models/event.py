"""
SQLAlchemy model for Events (audit trail).
Tracks all significant events in the facilitator workflow for compliance and auditing.
"""

from datetime import datetime
from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    Enum,
    ForeignKey,
    JSON,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.database import Base
from app.models.enums import EventType


class FacilitatorEvent(Base):
    """
    Represents an event in the facilitator workflow.

    This provides a complete audit trail of all significant actions:
    - Engagement lifecycle changes
    - Buyer introductions and status changes
    - Offers received and status changes
    - Closings recorded
    - Fee invoicing and payment tracking

    This is critical for compliance, dispute resolution, and audit purposes.
    """

    __tablename__ = "facilitator_events"

    # Primary Key
    id = Column(Integer, primary_key=True, index=True)

    # Foreign keys (all nullable as some events may be top-level)
    engagement_id = Column(
        Integer,
        ForeignKey("facilitator_engagements.id", ondelete="CASCADE"),
        nullable=True,
        index=True
    )
    buyer_intro_id = Column(
        Integer,
        ForeignKey("facilitator_buyer_intros.id", ondelete="CASCADE"),
        nullable=True,
        index=True
    )
    offer_id = Column(
        Integer,
        ForeignKey("facilitator_offers.id", ondelete="CASCADE"),
        nullable=True,
        index=True
    )
    closing_id = Column(
        Integer,
        ForeignKey("facilitator_closings.id", ondelete="CASCADE"),
        nullable=True,
        index=True
    )

    # Event metadata
    event_type = Column(
        Enum(EventType),
        nullable=False,
        index=True
    )

    # Event payload (structured data about what changed)
    # Example: {"old_status": "draft", "new_status": "active", "changed_by": "user@example.com"}
    payload = Column(
        JSON,
        nullable=True,
        comment="Structured event data"
    )

    # Additional context
    description = Column(String(500), nullable=True)
    actor = Column(
        String(100),
        nullable=True,
        comment="User or system that triggered the event"
    )

    # Timestamp
    created_at = Column(
        DateTime,
        nullable=False,
        server_default=func.now(),
        index=True
    )

    # Relationships
    engagement = relationship("FacilitatorEngagement", back_populates="events")
    buyer_intro = relationship("FacilitatorBuyerIntro", back_populates="events")
    offer = relationship("FacilitatorOffer", back_populates="events")
    closing = relationship("FacilitatorClosing", back_populates="events")

    def __repr__(self) -> str:
        return (
            f"<FacilitatorEvent("
            f"id={self.id}, "
            f"type={self.event_type.value}, "
            f"engagement_id={self.engagement_id}, "
            f"created_at={self.created_at}"
            f")>"
        )
