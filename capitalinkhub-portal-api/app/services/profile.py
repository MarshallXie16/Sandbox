"""
Service for member profile operations.
"""

from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories import (
    ContactsRepository,
    CompaniesRepository,
    PortalMembersRepository,
)
from app.schemas.member import (
    MemberResolveRequest,
    MemberResolveResponse,
    MemberProfile,
    ContactProfile,
    CompanyProfile,
)
from app.core.logging import get_logger

logger = get_logger(__name__)


class ProfileService:
    """
    Service for member profile and resolution operations.
    """

    def __init__(self, session: AsyncSession):
        self.session = session
        self.contacts_repo = ContactsRepository(session)
        self.companies_repo = CompaniesRepository(session)
        self.portal_members_repo = PortalMembersRepository(session)

    async def resolve_member(
        self, request: MemberResolveRequest
    ) -> MemberResolveResponse:
        """
        Resolve or create portal member mapping.

        Logic:
        1. Try to find existing mapping by um_user_id
        2. If not found, try to find contact by email
        3. If contact not found, create new contact
        4. Create portal member mapping
        5. Return full profile

        Args:
            request: Member resolve request

        Returns:
            Member resolution response with profile
        """
        logger.info(
            f"Resolving member: um_user_id={request.um_user_id}, email={request.email}"
        )

        # Try to find existing mapping
        existing_member = await self.portal_members_repo.get_by_um_user_id(
            request.um_user_id
        )

        is_new = False

        if existing_member:
            logger.info(f"Found existing portal member: {existing_member.id}")
            # Get contact
            contact = await self.contacts_repo.get_by_id(existing_member.contact_id)
            if not contact:
                logger.error(f"Contact not found for member {existing_member.id}")
                raise ValueError(
                    f"Contact {existing_member.contact_id} not found for member"
                )
        else:
            # Try to find contact by email
            contact = await self.contacts_repo.get_by_email(request.email)

            if not contact:
                # Create new contact
                logger.info(f"Creating new contact for email: {request.email}")
                contact = await self.contacts_repo.create_contact(
                    email=request.email,
                    first_name=request.first_name,
                    last_name=request.last_name,
                    category=request.role,
                )
                await self.session.commit()

            # Create portal member mapping
            logger.info(
                f"Creating portal member mapping: um_user_id={request.um_user_id}, contact_id={contact.id}"
            )
            existing_member = await self.portal_members_repo.create_mapping(
                um_user_id=request.um_user_id,
                contact_id=contact.id,
                role=request.role,
            )
            await self.session.commit()
            is_new = True

        # Build profile
        profile = await self._build_member_profile(existing_member)

        return MemberResolveResponse(
            member_id=existing_member.id,
            contact_id=existing_member.contact_id,
            um_user_id=existing_member.um_user_id,
            role=existing_member.role,
            is_new=is_new,
            profile=profile,
        )

    async def get_member_profile(self, member_id: int) -> Optional[MemberProfile]:
        """
        Get full member profile by member ID.

        Args:
            member_id: Portal member ID

        Returns:
            Member profile or None
        """
        member = await self.portal_members_repo.get_by_id(member_id)
        if not member:
            return None

        return await self._build_member_profile(member)

    async def _build_member_profile(self, member) -> MemberProfile:
        """
        Build a complete member profile.

        Args:
            member: PortalMember instance

        Returns:
            MemberProfile schema
        """
        # Get contact
        contact = await self.contacts_repo.get_by_id(member.contact_id)
        if not contact:
            raise ValueError(f"Contact {member.contact_id} not found")

        contact_profile = ContactProfile(
            id=contact.id,
            first_name=contact.first_name,
            last_name=contact.last_name,
            email=contact.primary_email,
            phone=contact.phone,
            title=contact.title,
            category=contact.category,
        )

        # Get company if exists
        company_profile = None
        if contact.company_id:
            company = await self.companies_repo.get_by_id(contact.company_id)
            if company:
                company_profile = CompanyProfile(
                    id=company.id,
                    name=company.name,
                    website=company.website,
                    industry=company.industry,
                    region=company.region,
                )

        return MemberProfile(
            member_id=member.id,
            contact_id=member.contact_id,
            um_user_id=member.um_user_id,
            role=member.role,
            contact=contact_profile,
            company=company_profile,
        )
