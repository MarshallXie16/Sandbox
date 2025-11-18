"""
Repository for Company operations.
"""

from typing import Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.crm import Company
from app.core.base_repository import BaseRepository


class CompaniesRepository(BaseRepository[Company]):
    """Repository for managing companies."""

    def __init__(self, session: AsyncSession):
        super().__init__(Company, session)

    async def get_by_name(self, name: str) -> Optional[Company]:
        """
        Get company by name.

        Args:
            name: Company name

        Returns:
            Company or None
        """
        result = await self.session.execute(
            select(Company).where(Company.name == name)
        )
        return result.scalar_one_or_none()

    async def get_by_industry(self, industry: str, limit: int = 100) -> list[Company]:
        """
        Get companies by industry.

        Args:
            industry: Industry sector
            limit: Maximum number of results

        Returns:
            List of companies
        """
        result = await self.session.execute(
            select(Company).where(Company.industry == industry).limit(limit)
        )
        return list(result.scalars().all())

    async def get_by_region(self, region: str, limit: int = 100) -> list[Company]:
        """
        Get companies by region.

        Args:
            region: Geographic region
            limit: Maximum number of results

        Returns:
            List of companies
        """
        result = await self.session.execute(
            select(Company).where(Company.region == region).limit(limit)
        )
        return list(result.scalars().all())
