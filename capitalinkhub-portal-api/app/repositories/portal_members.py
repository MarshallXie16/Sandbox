"""
Repository for PortalMember operations.
"""

from typing import Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.portal import PortalMember
from app.core.base_repository import BaseRepository


class PortalMembersRepository(BaseRepository[PortalMember]):
    """Repository for managing portal member mappings."""

    def __init__(self, session: AsyncSession):
        super().__init__(PortalMember, session)

    async def get_by_um_user_id(self, um_user_id: str) -> Optional[PortalMember]:
        """
        Get portal member by Ultimate Member user ID.

        Args:
            um_user_id: Ultimate Member user ID

        Returns:
            PortalMember or None
        """
        result = await self.session.execute(
            select(PortalMember).where(PortalMember.um_user_id == um_user_id)
        )
        return result.scalar_one_or_none()

    async def get_by_contact_id(self, contact_id: int) -> Optional[PortalMember]:
        """
        Get portal member by contact ID.

        Args:
            contact_id: CRM contact ID

        Returns:
            PortalMember or None
        """
        result = await self.session.execute(
            select(PortalMember).where(PortalMember.contact_id == contact_id)
        )
        return result.scalar_one_or_none()

    async def create_mapping(
        self, um_user_id: str, contact_id: int, role: str, metadata: Optional[dict] = None
    ) -> PortalMember:
        """
        Create a new portal member mapping.

        Args:
            um_user_id: Ultimate Member user ID
            contact_id: CRM contact ID
            role: Member role (buyer, seller, both)
            metadata: Additional metadata

        Returns:
            Created PortalMember
        """
        return await self.create(
            um_user_id=um_user_id,
            contact_id=contact_id,
            role=role,
            is_active=True,
            metadata=metadata or {},
        )

    async def get_active_members(self, role: Optional[str] = None, limit: int = 100) -> list[PortalMember]:
        """
        Get active portal members, optionally filtered by role.

        Args:
            role: Filter by role (buyer, seller, both)
            limit: Maximum results

        Returns:
            List of PortalMembers
        """
        query = select(PortalMember).where(PortalMember.is_active == True)

        if role:
            query = query.where(PortalMember.role == role)

        query = query.limit(limit)

        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def deactivate_member(self, member_id: int) -> Optional[PortalMember]:
        """
        Deactivate a portal member.

        Args:
            member_id: Portal member ID

        Returns:
            Updated PortalMember or None
        """
        return await self.update_by_id(member_id, is_active=False)
