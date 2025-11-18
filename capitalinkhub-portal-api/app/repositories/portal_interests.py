"""
Repository for PortalInterest operations.
"""

from typing import Optional, Tuple
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from app.models.portal import PortalInterest
from app.models.crm import Deal, Company
from app.core.base_repository import BaseRepository


class PortalInterestsRepository(BaseRepository[PortalInterest]):
    """Repository for managing buyer interests in listings."""

    def __init__(self, session: AsyncSession):
        super().__init__(PortalInterest, session)

    async def get_by_member_and_listing(
        self, member_id: int, listing_id: int
    ) -> Optional[PortalInterest]:
        """
        Get interest by member and listing (check if exists).

        Args:
            member_id: Portal member ID
            listing_id: Listing/deal ID

        Returns:
            PortalInterest or None
        """
        result = await self.session.execute(
            select(PortalInterest).where(
                and_(
                    PortalInterest.member_id == member_id,
                    PortalInterest.listing_id == listing_id,
                )
            )
        )
        return result.scalar_one_or_none()

    async def create_interest(
        self,
        member_id: int,
        contact_id: int,
        listing_id: int,
        note: Optional[str] = None,
        metadata: Optional[dict] = None,
    ) -> PortalInterest:
        """
        Create a new interest record.

        Args:
            member_id: Portal member ID
            contact_id: Contact ID
            listing_id: Listing/deal ID
            note: Optional buyer note
            metadata: Additional metadata

        Returns:
            Created PortalInterest
        """
        return await self.create(
            member_id=member_id,
            contact_id=contact_id,
            listing_id=listing_id,
            note=note,
            status="new",
            metadata=metadata or {},
        )

    async def get_member_interests(
        self, member_id: int
    ) -> list[Tuple[PortalInterest, Deal, Optional[Company]]]:
        """
        Get all interests for a member with listing and company info.

        Args:
            member_id: Portal member ID

        Returns:
            List of (interest, deal, company) tuples
        """
        query = (
            select(PortalInterest, Deal, Company)
            .join(Deal, PortalInterest.listing_id == Deal.id)
            .outerjoin(Company, Deal.company_id == Company.id)
            .where(PortalInterest.member_id == member_id)
            .order_by(PortalInterest.created_at.desc())
        )

        result = await self.session.execute(query)
        return [(row[0], row[1], row[2]) for row in result.all()]

    async def get_listing_interests(
        self, listing_id: int
    ) -> list[PortalInterest]:
        """
        Get all interests for a specific listing.

        Args:
            listing_id: Listing/deal ID

        Returns:
            List of interests
        """
        result = await self.session.execute(
            select(PortalInterest)
            .where(PortalInterest.listing_id == listing_id)
            .order_by(PortalInterest.created_at.desc())
        )
        return list(result.scalars().all())

    async def update_interest_status(
        self, interest_id: int, status: str
    ) -> Optional[PortalInterest]:
        """
        Update the status of an interest.

        Args:
            interest_id: Interest ID
            status: New status

        Returns:
            Updated interest or None
        """
        return await self.update_by_id(interest_id, status=status)
