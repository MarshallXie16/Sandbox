"""Score history model - tracks historical scores for analysis."""
from datetime import datetime
from typing import Dict, Any, Optional

from sqlalchemy import Numeric, DateTime, Index, JSON, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class ScoreHistory(Base):
    """
    Records historical engagement scores for tracking changes over time.

    Allows analysis of score trends and debugging of scoring calculations.
    """

    __tablename__ = "score_history"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    # Foreign keys
    engagement_entity_id: Mapped[int] = mapped_column(
        ForeignKey("engagement_entities.id", ondelete="CASCADE"), nullable=False, index=True
    )
    scoring_profile_id: Mapped[int] = mapped_column(
        ForeignKey("scoring_profiles.id", ondelete="CASCADE"), nullable=False, index=True
    )

    # Score data
    score_value: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    score_components: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
    calculated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, index=True, server_default="now()"
    )

    # Relationships
    entity = relationship("EngagementEntity", back_populates="score_histories")
    scoring_profile = relationship("ScoringProfile", back_populates="score_histories")

    __table_args__ = (
        Index("idx_entity_calculated_at", "engagement_entity_id", "calculated_at"),
    )

    def __repr__(self) -> str:
        return f"<ScoreHistory(id={self.id}, entity_id={self.engagement_entity_id}, score={self.score_value}, calculated_at={self.calculated_at})>"
