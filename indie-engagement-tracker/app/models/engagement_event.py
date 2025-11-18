"""Engagement event model - represents individual engagement activities."""
from datetime import datetime
from typing import Dict, Any, Optional

from sqlalchemy import String, Numeric, DateTime, Index, JSON, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class EngagementEvent(Base):
    """
    Represents a single engagement event (email, call, meeting, etc.).

    Events are immutable once created and are used to calculate scores.
    """

    __tablename__ = "engagement_events"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    # Foreign key to engagement entity (optional - populated after entity resolution)
    engagement_entity_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("engagement_entities.id", ondelete="CASCADE"), nullable=True, index=True
    )

    # Core event data
    external_id: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    entity_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    source_system: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    event_type: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    weight: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    metadata: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)

    # Timestamps
    occurred_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)
    ingested_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, index=True, server_default="now()"
    )

    # Relationships
    entity = relationship("EngagementEntity", back_populates="events")

    __table_args__ = (
        Index("idx_source_event_type", "source_system", "event_type"),
        Index("idx_external_id_occurred_at", "external_id", "occurred_at"),
    )

    def __repr__(self) -> str:
        return f"<EngagementEvent(id={self.id}, type={self.event_type}, source={self.source_system}, weight={self.weight}, occurred_at={self.occurred_at})>"
