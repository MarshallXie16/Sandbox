"""Repository for analytics-specific tables (this module's own data)."""

from datetime import date, datetime
from typing import Dict, List, Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.logging import get_logger
from app.models.analytics import (
    AnalyticsExitReadySummary,
    AnalyticsFacilitatorSummary,
    AnalyticsJob,
    AnalyticsSnapshot,
)

logger = get_logger(__name__)


class AnalyticsRepository:
    """Repository for analytics-specific tables."""

    def __init__(self, session: AsyncSession):
        """Initialize repository with database session."""
        self.session = session

    # Snapshot operations
    async def create_snapshot(
        self,
        snapshot_date: date,
        domain: str,
        data: Dict,
    ) -> AnalyticsSnapshot:
        """
        Create or update a snapshot.

        Args:
            snapshot_date: Date of snapshot
            domain: Domain (exit_ready, facilitator, etc.)
            data: Metrics data as dictionary

        Returns:
            Created snapshot instance
        """
        # Check if snapshot already exists
        stmt = select(AnalyticsSnapshot).where(
            AnalyticsSnapshot.snapshot_date == snapshot_date,
            AnalyticsSnapshot.domain == domain,
        )
        result = await self.session.execute(stmt)
        existing = result.scalar_one_or_none()

        if existing:
            # Update existing
            existing.data = data
            snapshot = existing
        else:
            # Create new
            snapshot = AnalyticsSnapshot(
                snapshot_date=snapshot_date,
                domain=domain,
                data=data,
            )
            self.session.add(snapshot)

        await self.session.commit()
        await self.session.refresh(snapshot)
        return snapshot

    async def get_snapshot(
        self,
        snapshot_date: date,
        domain: str,
    ) -> Optional[AnalyticsSnapshot]:
        """
        Get a specific snapshot.

        Args:
            snapshot_date: Date of snapshot
            domain: Domain

        Returns:
            Snapshot if found, None otherwise
        """
        stmt = select(AnalyticsSnapshot).where(
            AnalyticsSnapshot.snapshot_date == snapshot_date,
            AnalyticsSnapshot.domain == domain,
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_snapshots_by_domain(
        self,
        domain: str,
        limit: int = 30,
    ) -> List[AnalyticsSnapshot]:
        """
        Get recent snapshots for a domain.

        Args:
            domain: Domain
            limit: Maximum number of snapshots to return

        Returns:
            List of snapshots ordered by date descending
        """
        stmt = (
            select(AnalyticsSnapshot)
            .where(AnalyticsSnapshot.domain == domain)
            .order_by(AnalyticsSnapshot.snapshot_date.desc())
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    # Job tracking
    async def create_job(
        self,
        job_type: str,
        domain: Optional[str] = None,
        metadata: Optional[Dict] = None,
    ) -> AnalyticsJob:
        """
        Create a new analytics job record.

        Args:
            job_type: Type of job
            domain: Domain if applicable
            metadata: Additional metadata

        Returns:
            Created job instance
        """
        job = AnalyticsJob(
            job_type=job_type,
            status="running",
            domain=domain,
            started_at=datetime.utcnow(),
            metadata=metadata or {},
        )
        self.session.add(job)
        await self.session.commit()
        await self.session.refresh(job)
        return job

    async def complete_job(
        self,
        job_id: UUID,
        error_message: Optional[str] = None,
    ) -> AnalyticsJob:
        """
        Mark a job as completed or failed.

        Args:
            job_id: Job ID
            error_message: Error message if failed

        Returns:
            Updated job instance
        """
        stmt = select(AnalyticsJob).where(AnalyticsJob.id == job_id)
        result = await self.session.execute(stmt)
        job = result.scalar_one()

        job.status = "failed" if error_message else "completed"
        job.completed_at = datetime.utcnow()
        if error_message:
            job.error_message = error_message

        await self.session.commit()
        await self.session.refresh(job)
        return job
