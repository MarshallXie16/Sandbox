"""
Repository for Contact operations.
"""

from typing import Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.crm import Contact
from app.core.base_repository import BaseRepository


class ContactsRepository(BaseRepository[Contact]):
    """Repository for managing contacts."""

    def __init__(self, session: AsyncSession):
        super().__init__(Contact, session)

    async def get_by_email(self, email: str) -> Optional[Contact]:
        """
        Get contact by primary email.

        Args:
            email: Email address

        Returns:
            Contact or None
        """
        result = await self.session.execute(
            select(Contact).where(Contact.primary_email == email)
        )
        return result.scalar_one_or_none()

    async def get_by_category(self, category: str, limit: int = 100) -> list[Contact]:
        """
        Get contacts by category (buyer, seller, both).

        Args:
            category: Contact category
            limit: Maximum number of results

        Returns:
            List of contacts
        """
        result = await self.session.execute(
            select(Contact).where(Contact.category == category).limit(limit)
        )
        return list(result.scalars().all())

    async def create_contact(
        self,
        email: str,
        first_name: Optional[str] = None,
        last_name: Optional[str] = None,
        category: str = "buyer",
        **kwargs
    ) -> Contact:
        """
        Create a new contact.

        Args:
            email: Primary email
            first_name: First name
            last_name: Last name
            category: Contact category
            **kwargs: Additional fields

        Returns:
            Created contact
        """
        return await self.create(
            primary_email=email,
            first_name=first_name,
            last_name=last_name,
            category=category,
            **kwargs
        )
