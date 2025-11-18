"""Engagement entity model - represents contacts, companies, or deals being tracked."""
from datetime import datetime
from typing import Dict, Any, Optional

from sqlalchemy import String, Numeric, DateTime, Index, JSON, Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
import enum

from app.models.base import Base, TimestampMixin


class EntityType(str, enum.Enum):
    """Types of entities that can be tracked."""

    CONTACT = "contact"
    COMPANY = "company"
    DEAL = "deal"


class EngagementEntity(Base, TimestampMixin):
    """
    Represents an entity (contact, company, or deal) being tracked for engagement.

    Stores the latest engagement score and aggregated data.
    """

    __tablename__ = "engagement_entities"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    external_id: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    entity_type: Mapped[EntityType] = mapped_column(
        SQLEnum(EntityType, name="entity_type_enum", create_constraint=True),
        nullable=False,
        index=True,
    )
    latest_score: Mapped[float] = mapped_column(Numeric(10, 2), default=0.0, nullable=False)
    score_breakdown: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
    last_activity_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    # Relationships
    events = relationship("EngagementEvent", back_populates="entity", cascade="all, delete-orphan")
    score_histories = relationship(
        "ScoreHistory", back_populates="entity", cascade="all, delete-orphan"
    )

    __table_args__ = (
        Index("idx_external_id_entity_type", "external_id", "entity_type", unique=True),
        Index("idx_latest_score", "latest_score"),
        Index("idx_last_activity_at", "last_activity_at"),
    )

    def __repr__(self) -> str:
        return f"<EngagementEntity(id={self.id}, external_id={self.external_id}, type={self.entity_type}, score={self.latest_score})>"
