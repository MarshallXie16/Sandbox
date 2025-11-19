"""
SQLAlchemy model for Exit Ready cases.
"""
from datetime import datetime
from typing import Optional
from sqlalchemy import (
    Integer,
    String,
    Text,
    DateTime,
    JSON,
    ForeignKey,
    Index,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.db import Base
from app.core.workflow import CaseStatus


class ExitReadyCase(Base):
    """
    Represents one Exit Ready engagement (Phase 1) for a given owner & company.
    """

    __tablename__ = "exit_ready_cases"

    # Primary key
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    # Core identifiers
    case_code: Mapped[str] = mapped_column(
        String(50), unique=True, nullable=False, index=True
    )
    status: Mapped[str] = mapped_column(
        String(50), nullable=False, default=CaseStatus.CREATED.value, index=True
    )

    # Foreign keys to CRM (not enforced, reference only)
    contact_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True, index=True)
    company_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True, index=True)

    # Cached contact/company data for convenience
    owner_name: Mapped[str] = mapped_column(String(255), nullable=False)
    owner_email: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    company_name: Mapped[str] = mapped_column(String(255), nullable=False)
    industry: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    region: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=datetime.utcnow
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    # Intake & docs
    intake_form_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    intake_sent_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    intake_received_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    intake_payload: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)

    # Financials & valuation
    normalized_financials: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    normalized_financials_last_run_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime, nullable=True
    )
    valuation_payload: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    valuation_last_run_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    # Drafts & documents
    drafts: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    drafts_generated_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    report_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    teaser_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    cim_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)

    # Delivery & next steps
    report_ready_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    delivered_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    delivery_channel: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    next_step: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Relationships
    documents: Mapped[list["ExitReadyDoc"]] = relationship(
        "ExitReadyDoc", back_populates="case", cascade="all, delete-orphan"
    )
    events: Mapped[list["ExitReadyEvent"]] = relationship(
        "ExitReadyEvent", back_populates="case", cascade="all, delete-orphan"
    )

    # Indexes
    __table_args__ = (
        Index("ix_exit_ready_cases_status_created", "status", "created_at"),
        Index("ix_exit_ready_cases_owner_email", "owner_email"),
    )

    def __repr__(self) -> str:
        return f"<ExitReadyCase(id={self.id}, case_code={self.case_code}, status={self.status})>"
