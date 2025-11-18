"""
Service for buyer interest tracking.
"""

from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError

from app.repositories import (
    PortalInterestsRepository,
    PortalMembersRepository,
    DealsRepository,
    ActivitiesRepository,
)
from app.schemas.interest import (
    InterestCreateRequest,
    InterestResponse,
    MemberInterest,
)
from app.schemas.listing import ListingTeaser
from app.services.listings import ListingsService
from app.core.logging import get_logger

logger = get_logger(__name__)


class InterestService:
    """
    Service for managing buyer interests in listings.
    """

    def __init__(self, session: AsyncSession):
        self.session = session
        self.interests_repo = PortalInterestsRepository(session)
        self.members_repo = PortalMembersRepository(session)
        self.deals_repo = DealsRepository(session)
        self.activities_repo = ActivitiesRepository(session)
        self.listings_service = ListingsService(session)

    async def create_interest(
        self, listing_id: int, request: InterestCreateRequest
    ) -> InterestResponse:
        """
        Create a new buyer interest in a listing.

        Creates both:
        1. PortalInterest record
        2. Activity record in CRM

        Args:
            listing_id: Listing/deal ID
            request: Interest creation request

        Returns:
            Interest response

        Raises:
            ValueError: If member or listing not found or interest already exists
        """
        logger.info(
            f"Creating interest: member_id={request.member_id}, listing_id={listing_id}"
        )

        # Validate member exists
        member = await self.members_repo.get_by_id(request.member_id)
        if not member:
            raise ValueError(f"Member {request.member_id} not found")

        # Validate listing exists
        listing = await self.deals_repo.get_by_id(listing_id)
        if not listing:
            raise ValueError(f"Listing {listing_id} not found")

        # Check if interest already exists
        existing_interest = await self.interests_repo.get_by_member_and_listing(
            request.member_id, listing_id
        )
        if existing_interest:
            logger.warning(
                f"Interest already exists: member_id={request.member_id}, listing_id={listing_id}"
            )
            # Return existing interest
            return InterestResponse(
                interest_id=existing_interest.id,
                member_id=existing_interest.member_id,
                listing_id=existing_interest.listing_id,
                status=existing_interest.status,
                created_at=existing_interest.created_at,
            )

        # Create interest record
        try:
            interest = await self.interests_repo.create_interest(
                member_id=request.member_id,
                contact_id=member.contact_id,
                listing_id=listing_id,
                note=request.note,
            )
            await self.session.flush()

            # Create activity in CRM
            await self.activities_repo.create_activity(
                activity_type="portal_interest",
                contact_id=member.contact_id,
                deal_id=listing_id,
                subject=f"Interest expressed via portal",
                description=f"Member {member.um_user_id} expressed interest in listing {listing.name}. Note: {request.note or 'N/A'}",
                metadata={
                    "source": "portal_api",
                    "member_id": request.member_id,
                    "interest_id": interest.id,
                    "note": request.note,
                },
            )

            await self.session.commit()

            logger.info(f"Interest created successfully: {interest.id}")

            return InterestResponse(
                interest_id=interest.id,
                member_id=interest.member_id,
                listing_id=interest.listing_id,
                status=interest.status,
                created_at=interest.created_at,
            )

        except IntegrityError as e:
            await self.session.rollback()
            logger.error(f"Integrity error creating interest: {e}")
            raise ValueError("Interest already exists or constraint violation")

    async def get_member_interests(self, member_id: int) -> list[MemberInterest]:
        """
        Get all interests for a member with listing information.

        Args:
            member_id: Portal member ID

        Returns:
            List of member interests with listings
        """
        logger.info(f"Getting interests for member: {member_id}")

        # Get interests with deal and company
        interests_data = await self.interests_repo.get_member_interests(member_id)

        result = []
        for interest, deal, company in interests_data:
            # Build listing teaser
            listing_teaser = self.listings_service._build_listing_teaser(deal, company)

            member_interest = MemberInterest(
                interest_id=interest.id,
                listing=listing_teaser,
                status=interest.status,
                note=interest.note,
                created_at=interest.created_at,
                updated_at=interest.updated_at,
            )
            result.append(member_interest)

        logger.info(f"Found {len(result)} interests for member {member_id}")
        return result

    async def update_interest_status(
        self, interest_id: int, status: str
    ) -> Optional[InterestResponse]:
        """
        Update the status of an interest.

        Args:
            interest_id: Interest ID
            status: New status

        Returns:
            Updated interest response or None
        """
        logger.info(f"Updating interest {interest_id} status to: {status}")

        interest = await self.interests_repo.update_interest_status(interest_id, status)
        if not interest:
            return None

        await self.session.commit()

        return InterestResponse(
            interest_id=interest.id,
            member_id=interest.member_id,
            listing_id=interest.listing_id,
            status=interest.status,
            created_at=interest.created_at,
        )
