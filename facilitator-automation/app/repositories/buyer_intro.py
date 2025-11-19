"""
Repository for Introduced Buyers.
"""

from typing import Optional, List
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models import FacilitatorBuyerIntro, BuyerIntroStatus
from app.repositories.base import BaseRepository


class BuyerIntroRepository(BaseRepository[FacilitatorBuyerIntro]):
    """Repository for buyer intro operations."""

    def __init__(self, db: AsyncSession):
        super().__init__(FacilitatorBuyerIntro, db)

    async def get_by_engagement(
        self,
        engagement_id: int,
        skip: int = 0,
        limit: int = 100
    ) -> List[FacilitatorBuyerIntro]:
        """Get all buyer intros for an engagement."""
        return await self.get_all(
            skip=skip,
            limit=limit,
            engagement_id=engagement_id
        )

    async def get_by_buyer_and_engagement(
        self,
        buyer_contact_id: int,
        engagement_id: int
    ) -> Optional[FacilitatorBuyerIntro]:
        """
        Check if a buyer has already been introduced to this engagement.

        Args:
            buyer_contact_id: CRM contact ID for the buyer
            engagement_id: Engagement ID

        Returns:
            BuyerIntro instance or None
        """
        result = await self.db.execute(
            select(self.model)
            .where(
                self.model.buyer_contact_id == buyer_contact_id,
                self.model.engagement_id == engagement_id
            )
        )
        return result.scalar_one_or_none()

    async def get_with_offers(self, id: int) -> Optional[FacilitatorBuyerIntro]:
        """Get buyer intro with all offers loaded."""
        result = await self.db.execute(
            select(self.model)
            .where(self.model.id == id)
            .options(selectinload(self.model.offers))
        )
        return result.scalar_one_or_none()

    async def get_active_by_engagement(
        self,
        engagement_id: int,
        skip: int = 0,
        limit: int = 100
    ) -> List[FacilitatorBuyerIntro]:
        """
        Get active buyer intros for an engagement.

        Active statuses: INVITED, NDA_PENDING, NDA_SIGNED, TEASER_SENT,
        INFO_ACCESS, OFFER_MADE
        """
        active_statuses = [
            BuyerIntroStatus.INVITED,
            BuyerIntroStatus.NDA_PENDING,
            BuyerIntroStatus.NDA_SIGNED,
            BuyerIntroStatus.TEASER_SENT,
            BuyerIntroStatus.INFO_ACCESS,
            BuyerIntroStatus.OFFER_MADE,
        ]

        result = await self.db.execute(
            select(self.model)
            .where(
                self.model.engagement_id == engagement_id,
                self.model.status.in_(active_statuses)
            )
            .order_by(self.model.id.desc())
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())

    async def is_buyer_introduced(
        self,
        buyer_contact_id: int,
        engagement_id: int
    ) -> bool:
        """
        Check if a buyer has been introduced to an engagement.

        This is critical for "Introduced Buyer" semantics.

        Args:
            buyer_contact_id: CRM contact ID for the buyer
            engagement_id: Engagement ID

        Returns:
            True if buyer has been introduced, False otherwise
        """
        return await self.exists(
            buyer_contact_id=buyer_contact_id,
            engagement_id=engagement_id
        )
