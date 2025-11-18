"""Scoring profile model - defines rules for calculating engagement scores."""
from typing import Dict, Any, Optional

from sqlalchemy import String, Boolean, JSON, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin


class ScoringProfile(Base, TimestampMixin):
    """
    Defines rules for calculating engagement scores.

    Rules are stored as JSON and define:
    - Base weights per event type
    - Time decay configuration
    - Bonus multipliers
    - Custom scoring logic
    """

    __tablename__ = "scoring_profiles"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False, unique=True, index=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    rules: Mapped[Dict[str, Any]] = mapped_column(JSON, nullable=False)
    is_default: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False, index=True)

    # Relationships
    score_histories = relationship("ScoreHistory", back_populates="scoring_profile")

    def __repr__(self) -> str:
        return f"<ScoringProfile(id={self.id}, name={self.name}, is_default={self.is_default})>"

    def get_event_weight(self, event_type: str) -> float:
        """Get the base weight for an event type."""
        event_weights = self.rules.get("event_weights", {})
        return float(event_weights.get(event_type, 0.0))

    def get_decay_config(self) -> Dict[str, Any]:
        """Get time decay configuration."""
        return self.rules.get("time_decay", {
            "enabled": True,
            "decay_days": 90,
            "decay_factor": 0.5
        })
