"""
Repository for Closings.
"""

from typing import Optional, List
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import FacilitatorClosing
from app.repositories.base import BaseRepository


class ClosingRepository(BaseRepository[FacilitatorClosing]):
    """Repository for closing operations."""

    def __init__(self, db: AsyncSession):
        super().__init__(FacilitatorClosing, db)

    async def get_by_engagement(
        self,
        engagement_id: int
    ) -> Optional[FacilitatorClosing]:
        """
        Get closing for an engagement.

        Note: Typically only one closing per engagement.

        Args:
            engagement_id: Engagement ID

        Returns:
            Closing instance or None
        """
        result = await self.db.execute(
            select(self.model)
            .where(self.model.engagement_id == engagement_id)
        )
        return result.scalar_one_or_none()

    async def get_by_buyer_intro(
        self,
        buyer_intro_id: int
    ) -> List[FacilitatorClosing]:
        """
        Get all closings for a specific buyer intro.

        Args:
            buyer_intro_id: Buyer intro ID

        Returns:
            List of closings
        """
        return await self.get_all(buyer_intro_id=buyer_intro_id)

    async def mark_invoiced(
        self,
        id: int,
        invoiced: bool = None,
        paid: bool = None
    ) -> None:
        """
        Mark closing as invoiced and/or paid.

        Args:
            id: Closing ID
            invoiced: Mark as invoiced (None to skip)
            paid: Mark as paid (None to skip)
        """
        update_data = {}
        if invoiced is not None:
            update_data["invoiced"] = invoiced
        if paid is not None:
            update_data["paid"] = paid

        if update_data:
            await self.update(id, **update_data)

    async def has_engagement_closed(self, engagement_id: int) -> bool:
        """
        Check if an engagement has a closing record.

        Args:
            engagement_id: Engagement ID

        Returns:
            True if closing exists, False otherwise
        """
        return await self.exists(engagement_id=engagement_id)
