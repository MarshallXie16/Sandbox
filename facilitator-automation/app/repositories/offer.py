"""
Repository for Offers.
"""

from typing import List
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from decimal import Decimal

from app.models import FacilitatorOffer, OfferStatus
from app.repositories.base import BaseRepository


class OfferRepository(BaseRepository[FacilitatorOffer]):
    """Repository for offer operations."""

    def __init__(self, db: AsyncSession):
        super().__init__(FacilitatorOffer, db)

    async def get_by_engagement(
        self,
        engagement_id: int,
        skip: int = 0,
        limit: int = 100
    ) -> List[FacilitatorOffer]:
        """Get all offers for an engagement."""
        return await self.get_all(
            skip=skip,
            limit=limit,
            engagement_id=engagement_id
        )

    async def get_by_buyer_intro(
        self,
        buyer_intro_id: int,
        skip: int = 0,
        limit: int = 100
    ) -> List[FacilitatorOffer]:
        """Get all offers from a specific buyer."""
        return await self.get_all(
            skip=skip,
            limit=limit,
            buyer_intro_id=buyer_intro_id
        )

    async def get_active_by_engagement(
        self,
        engagement_id: int,
        skip: int = 0,
        limit: int = 100
    ) -> List[FacilitatorOffer]:
        """
        Get active offers for an engagement.

        Active statuses: RECEIVED, UNDER_REVIEW, ACCEPTED
        """
        active_statuses = [
            OfferStatus.RECEIVED,
            OfferStatus.UNDER_REVIEW,
            OfferStatus.ACCEPTED,
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

    async def get_paid_offer_fees_for_buyer(
        self,
        buyer_intro_id: int
    ) -> Decimal:
        """
        Get total paid offer fees for a specific buyer intro.

        This is used to calculate credit when closing a deal.

        Args:
            buyer_intro_id: Buyer intro ID

        Returns:
            Total paid offer fees
        """
        from sqlalchemy import func, and_

        result = await self.db.execute(
            select(func.sum(self.model.offer_fee_amount))
            .where(
                and_(
                    self.model.buyer_intro_id == buyer_intro_id,
                    self.model.offer_fee_paid == True
                )
            )
        )
        total = result.scalar_one_or_none()
        return Decimal(total) if total else Decimal("0.00")

    async def mark_fee_status(
        self,
        id: int,
        invoiced: bool = None,
        paid: bool = None
    ) -> None:
        """
        Mark offer fee as invoiced and/or paid.

        Args:
            id: Offer ID
            invoiced: Mark as invoiced (None to skip)
            paid: Mark as paid (None to skip)
        """
        update_data = {}
        if invoiced is not None:
            update_data["offer_fee_invoiced"] = invoiced
        if paid is not None:
            update_data["offer_fee_paid"] = paid

        if update_data:
            await self.update(id, **update_data)
