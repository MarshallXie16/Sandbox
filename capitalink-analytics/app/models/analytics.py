"""Analytics-specific database models."""

from datetime import date, datetime
from typing import Any, Dict, Optional
from uuid import UUID, uuid4

from sqlalchemy import Boolean, Date, Float, Integer, JSON, String, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin


class AnalyticsSnapshot(Base, TimestampMixin):
    """
    Generic snapshot table for daily metrics with flexible JSON payload.

    This table stores aggregated metrics from various domains (Exit Ready,
    Facilitator, CRM, etc.) on a daily basis.
    """

    __tablename__ = "analytics_snapshots"

    id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
    )
    snapshot_date: Mapped[date] = mapped_column(
        Date,
        nullable=False,
        index=True,
    )
    domain: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        index=True,
        comment="Domain: exit_ready, facilitator, crm, revenue, buyer_activity, etc.",
    )
    data: Mapped[Dict[str, Any]] = mapped_column(
        JSON,
        nullable=False,
        comment="Aggregated metrics as JSON",
    )

    __table_args__ = (
        UniqueConstraint("snapshot_date", "domain", name="uq_snapshot_date_domain"),
    )

    def __repr__(self) -> str:
        return f"<AnalyticsSnapshot(date={self.snapshot_date}, domain={self.domain})>"


class AnalyticsExitReadySummary(Base, TimestampMixin):
    """
    Denormalized per-case metrics for Exit Ready module.

    Stores summary information and duration metrics for each Exit Ready case.
    """

    __tablename__ = "analytics_exit_ready_summary"

    id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
    )
    case_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        nullable=False,
        unique=True,
        index=True,
        comment="Reference to exit_ready_cases.id",
    )
    status: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        index=True,
    )
    seller_contact_id: Mapped[Optional[UUID]] = mapped_column(
        PGUUID(as_uuid=True),
        nullable=True,
    )
    company_id: Mapped[Optional[UUID]] = mapped_column(
        PGUUID(as_uuid=True),
        nullable=True,
    )

    # Timestamps
    case_created_at: Mapped[datetime] = mapped_column(nullable=False)
    intake_completed_at: Mapped[Optional[datetime]] = mapped_column(nullable=True)
    docs_collecting_started_at: Mapped[Optional[datetime]] = mapped_column(nullable=True)
    financials_ready_at: Mapped[Optional[datetime]] = mapped_column(nullable=True)
    valuation_completed_at: Mapped[Optional[datetime]] = mapped_column(nullable=True)
    report_ready_at: Mapped[Optional[datetime]] = mapped_column(nullable=True)
    delivered_at: Mapped[Optional[datetime]] = mapped_column(nullable=True)
    closed_at: Mapped[Optional[datetime]] = mapped_column(nullable=True)

    # Duration metrics (in days)
    total_duration_days: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    duration_intake_to_docs: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    duration_docs_to_valuation: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    duration_valuation_to_report: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    duration_report_to_delivered: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    # Conversion tracking
    linked_facilitator_engagement_id: Mapped[Optional[UUID]] = mapped_column(
        PGUUID(as_uuid=True),
        nullable=True,
        comment="If this case led to a Facilitator engagement",
    )

    def __repr__(self) -> str:
        return f"<AnalyticsExitReadySummary(case_id={self.case_id}, status={self.status})>"


class AnalyticsFacilitatorSummary(Base, TimestampMixin):
    """
    Per-engagement summary for Facilitator module.

    Stores aggregated metrics about buyers, offers, and revenue for each
    Facilitator engagement.
    """

    __tablename__ = "analytics_facilitator_summary"

    id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
    )
    engagement_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        nullable=False,
        unique=True,
        index=True,
        comment="Reference to facilitator_engagements.id",
    )
    seller_contact_id: Mapped[Optional[UUID]] = mapped_column(
        PGUUID(as_uuid=True),
        nullable=True,
    )
    company_id: Mapped[Optional[UUID]] = mapped_column(
        PGUUID(as_uuid=True),
        nullable=True,
    )
    listing_id: Mapped[Optional[UUID]] = mapped_column(
        PGUUID(as_uuid=True),
        nullable=True,
    )
    status: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        index=True,
    )

    # Buyer and offer metrics
    num_introduced_buyers: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
    )
    num_offers: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
    )
    closed_with_introduced_buyer: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
    )

    # Financial metrics
    final_price: Mapped[Optional[float]] = mapped_column(
        Float,
        nullable=True,
        comment="Final closing price",
    )
    success_fee_gross_amount: Mapped[Optional[float]] = mapped_column(
        Float,
        nullable=True,
        comment="Gross success fee (5% of price)",
    )
    success_fee_net_amount: Mapped[Optional[float]] = mapped_column(
        Float,
        nullable=True,
        comment="Net success fee after credits",
    )
    offer_fee_collected: Mapped[Optional[float]] = mapped_column(
        Float,
        nullable=True,
        comment="Total offer fees collected ($5k each)",
    )
    total_revenue: Mapped[Optional[float]] = mapped_column(
        Float,
        nullable=True,
        comment="Total revenue from this engagement",
    )

    # Timestamps
    engagement_created_at: Mapped[datetime] = mapped_column(nullable=False)
    engagement_closed_at: Mapped[Optional[datetime]] = mapped_column(nullable=True)

    def __repr__(self) -> str:
        return (
            f"<AnalyticsFacilitatorSummary(engagement_id={self.engagement_id}, "
            f"status={self.status})>"
        )


class AnalyticsJob(Base, TimestampMixin):
    """
    Tracks analytics job runs (snapshots, aggregations, etc.).

    Useful for monitoring and debugging analytics processes.
    """

    __tablename__ = "analytics_jobs"

    id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
    )
    job_type: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        index=True,
        comment="Type of job: snapshot, aggregation, export, etc.",
    )
    status: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="running",
        comment="Status: running, completed, failed",
    )
    domain: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
        comment="Domain if applicable",
    )
    started_at: Mapped[datetime] = mapped_column(
        nullable=False,
        default=datetime.utcnow,
    )
    completed_at: Mapped[Optional[datetime]] = mapped_column(nullable=True)
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    metadata: Mapped[Optional[Dict[str, Any]]] = mapped_column(
        JSON,
        nullable=True,
        comment="Additional job metadata",
    )

    def __repr__(self) -> str:
        return f"<AnalyticsJob(type={self.job_type}, status={self.status})>"
