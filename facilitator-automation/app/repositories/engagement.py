"""
Repository for Facilitator Engagements.
"""

from typing import Optional, List
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models import FacilitatorEngagement, EngagementStatus
from app.repositories.base import BaseRepository


class EngagementRepository(BaseRepository[FacilitatorEngagement]):
    """Repository for engagement operations."""

    def __init__(self, db: AsyncSession):
        super().__init__(FacilitatorEngagement, db)

    async def get_by_code(self, engagement_code: str) -> Optional[FacilitatorEngagement]:
        """Get engagement by engagement code."""
        result = await self.db.execute(
            select(self.model).where(self.model.engagement_code == engagement_code)
        )
        return result.scalar_one_or_none()

    async def get_with_relations(self, id: int) -> Optional[FacilitatorEngagement]:
        """
        Get engagement with all related entities loaded.

        Args:
            id: Engagement ID

        Returns:
            Engagement with buyer_intros, offers, closings, and events loaded
        """
        result = await self.db.execute(
            select(self.model)
            .where(self.model.id == id)
            .options(
                selectinload(self.model.buyer_intros),
                selectinload(self.model.offers),
                selectinload(self.model.closings),
                selectinload(self.model.events),
            )
        )
        return result.scalar_one_or_none()

    async def get_by_seller(
        self,
        seller_contact_id: int,
        skip: int = 0,
        limit: int = 100
    ) -> List[FacilitatorEngagement]:
        """Get all engagements for a seller."""
        return await self.get_all(
            skip=skip,
            limit=limit,
            seller_contact_id=seller_contact_id
        )

    async def get_by_status(
        self,
        status: EngagementStatus,
        skip: int = 0,
        limit: int = 100
    ) -> List[FacilitatorEngagement]:
        """Get all engagements with a specific status."""
        return await self.get_all(
            skip=skip,
            limit=limit,
            status=status
        )

    async def get_active_engagements(
        self,
        skip: int = 0,
        limit: int = 100
    ) -> List[FacilitatorEngagement]:
        """
        Get all active engagements.

        Active states: ACTIVE, SHORTLISTING, OUTREACH_IN_PROGRESS,
        OFFERS_IN_PLAY, UNDER_AGREEMENT
        """
        active_statuses = [
            EngagementStatus.ACTIVE,
            EngagementStatus.SHORTLISTING,
            EngagementStatus.OUTREACH_IN_PROGRESS,
            EngagementStatus.OFFERS_IN_PLAY,
            EngagementStatus.UNDER_AGREEMENT,
        ]

        result = await self.db.execute(
            select(self.model)
            .where(self.model.status.in_(active_statuses))
            .order_by(self.model.id.desc())
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())

    async def generate_engagement_code(self) -> str:
        """
        Generate a unique engagement code.

        Format: FAC-YYYY-NNNN
        Example: FAC-2025-0001
        """
        from datetime import datetime

        year = datetime.now().year

        # Get the count of engagements created this year
        result = await self.db.execute(
            select(self.model)
            .where(self.model.engagement_code.like(f"FAC-{year}-%"))
        )
        count = len(list(result.scalars().all()))

        # Generate code
        sequence = count + 1
        return f"FAC-{year}-{sequence:04d}"
