"""
SQLAlchemy model for Exit Ready document tracking.
"""
from datetime import datetime
from typing import Optional
from sqlalchemy import (
    Integer,
    String,
    Text,
    Boolean,
    DateTime,
    ForeignKey,
    Index,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.db import Base


class ExitReadyDoc(Base):
    """
    Tracks the document checklist for each Exit Ready case.
    """

    __tablename__ = "exit_ready_docs"

    # Primary key
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    # Foreign key to case
    case_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("exit_ready_cases.id", ondelete="CASCADE"), nullable=False
    )

    # Document metadata
    doc_type: Mapped[str] = mapped_column(String(100), nullable=False)
    label: Mapped[str] = mapped_column(String(255), nullable=False)
    required: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    # Document status
    status: Mapped[str] = mapped_column(
        String(50), nullable=False, default="pending"
    )  # pending, received, waived

    # Tracking
    received_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    file_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=datetime.utcnow
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    # Relationship
    case: Mapped["ExitReadyCase"] = relationship("ExitReadyCase", back_populates="documents")

    # Indexes
    __table_args__ = (
        Index("ix_exit_ready_docs_case_id", "case_id"),
        Index("ix_exit_ready_docs_case_status", "case_id", "status"),
    )

    def __repr__(self) -> str:
        return f"<ExitReadyDoc(id={self.id}, case_id={self.case_id}, doc_type={self.doc_type}, status={self.status})>"
