"""
Matching run model for tracking batch scoring operations.
"""

from datetime import datetime
from typing import Optional

from sqlalchemy import DateTime, Integer, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin


class MatchingRun(Base, TimestampMixin):
    """
    Represents a batch matching run.

    Tracks when matches were computed, for which scope (all buyers, specific buyer, etc.),
    and the results/statistics.
    """

    __tablename__ = "matching_runs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    # Run metadata
    run_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        comment="Type of run: 'full', 'buyer', 'listing', 'incremental'",
    )

    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="pending",
        comment="Status: pending, running, completed, failed",
    )

    # Scope (optional filters)
    scope: Mapped[Optional[dict]] = mapped_column(
        JSON,
        nullable=True,
        comment="Scope parameters, e.g., {'buyer_id': 123} or {'listing_ids': [1,2,3]}",
    )

    # Results
    matches_computed: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True,
        comment="Number of matches computed",
    )

    buyers_processed: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True,
        comment="Number of buyers processed",
    )

    listings_processed: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True,
        comment="Number of listings processed",
    )

    # Timing
    started_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    completed_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    # Errors
    error_message: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )

    # Statistics
    stats: Mapped[Optional[dict]] = mapped_column(
        JSON,
        nullable=True,
        comment="Run statistics: avg_score, high_matches_count, etc.",
    )

    def __repr__(self) -> str:
        return (
            f"<MatchingRun(id={self.id}, run_type='{self.run_type}', "
            f"status='{self.status}', matches={self.matches_computed})>"
        )
