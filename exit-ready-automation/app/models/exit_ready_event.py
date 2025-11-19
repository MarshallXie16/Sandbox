"""
SQLAlchemy model for Exit Ready event/audit logging.
"""
from datetime import datetime
from typing import Optional
from sqlalchemy import (
    Integer,
    String,
    DateTime,
    JSON,
    ForeignKey,
    Index,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.db import Base


class ExitReadyEvent(Base):
    """
    Audit log for Exit Ready case events.
    Tracks all significant actions and state changes.
    """

    __tablename__ = "exit_ready_events"

    # Primary key
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    # Foreign key to case
    case_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("exit_ready_cases.id", ondelete="CASCADE"), nullable=False
    )

    # Event metadata
    event_type: Mapped[str] = mapped_column(String(100), nullable=False)
    # Event types: status_changed, intake_imported, valuation_run, report_exported, etc.

    payload: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    # Flexible payload for event-specific data

    # Actor (who triggered the event)
    actor: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    # e.g., "system", "admin@example.com", "cli:operator"

    # Timestamp
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=datetime.utcnow, index=True
    )

    # Relationship
    case: Mapped["ExitReadyCase"] = relationship("ExitReadyCase", back_populates="events")

    # Indexes
    __table_args__ = (
        Index("ix_exit_ready_events_case_id", "case_id"),
        Index("ix_exit_ready_events_event_type", "event_type"),
        Index("ix_exit_ready_events_case_created", "case_id", "created_at"),
    )

    def __repr__(self) -> str:
        return f"<ExitReadyEvent(id={self.id}, case_id={self.case_id}, event_type={self.event_type}, created_at={self.created_at})>"
