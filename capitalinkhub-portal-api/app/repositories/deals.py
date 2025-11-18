"""
Repository for Deal operations (listings).
"""

from typing import Optional, Tuple
from sqlalchemy import select, and_, or_, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from app.models.crm import Deal, Company
from app.core.base_repository import BaseRepository


class DealsRepository(BaseRepository[Deal]):
    """Repository for managing deals (listings)."""

    def __init__(self, session: AsyncSession):
        super().__init__(Deal, session)

    async def get_active_listings(
        self,
        industry: Optional[str] = None,
        region: Optional[str] = None,
        min_price: Optional[float] = None,
        max_price: Optional[float] = None,
        min_revenue: Optional[float] = None,
        max_revenue: Optional[float] = None,
        status: Optional[str] = None,
        limit: int = 20,
        offset: int = 0,
    ) -> Tuple[list[Tuple[Deal, Optional[Company]]], int]:
        """
        Get active listings with filters and pagination.

        Args:
            industry: Filter by industry
            region: Filter by region
            min_price: Minimum asking price
            max_price: Maximum asking price
            min_revenue: Minimum revenue
            max_revenue: Maximum revenue
            status: Deal status filter
            limit: Max results
            offset: Offset for pagination

        Returns:
            Tuple of (list of (deal, company) tuples, total_count)
        """
        # Build base query with company join
        query = select(Deal, Company).outerjoin(
            Company, Deal.company_id == Company.id
        )

        # Build filter conditions
        filters = []

        # Default: only active deals
        if status:
            filters.append(Deal.status == status)
        else:
            filters.append(Deal.status.in_(["Active", "New", "Open"]))

        # Price filters
        if min_price is not None:
            filters.append(Deal.amount >= min_price)
        if max_price is not None:
            filters.append(Deal.amount <= max_price)

        # Company-based filters (industry, region, revenue)
        if industry:
            filters.append(Company.industry == industry)
        if region:
            filters.append(Company.region == region)
        if min_revenue is not None:
            filters.append(Company.revenue >= min_revenue)
        if max_revenue is not None:
            filters.append(Company.revenue <= max_revenue)

        # Apply filters
        if filters:
            query = query.where(and_(*filters))

        # Get total count
        count_query = select(func.count()).select_from(Deal)
        if filters:
            # Rebuild count query with same filters
            count_query = count_query.outerjoin(Company, Deal.company_id == Company.id)
            count_query = count_query.where(and_(*filters))

        total_result = await self.session.execute(count_query)
        total_count = total_result.scalar_one()

        # Apply ordering and pagination
        query = query.order_by(Deal.created_at.desc()).offset(offset).limit(limit)

        # Execute query
        result = await self.session.execute(query)
        listings = [(row[0], row[1]) for row in result.all()]

        return listings, total_count

    async def get_listing_with_company(
        self, listing_id: int
    ) -> Optional[Tuple[Deal, Optional[Company]]]:
        """
        Get a single listing with its associated company.

        Args:
            listing_id: Deal ID

        Returns:
            Tuple of (deal, company) or None
        """
        query = (
            select(Deal, Company)
            .outerjoin(Company, Deal.company_id == Company.id)
            .where(Deal.id == listing_id)
        )

        result = await self.session.execute(query)
        row = result.first()

        if row:
            return (row[0], row[1])
        return None

    async def get_by_status(self, status: str, limit: int = 100) -> list[Deal]:
        """
        Get deals by status.

        Args:
            status: Deal status
            limit: Maximum results

        Returns:
            List of deals
        """
        result = await self.session.execute(
            select(Deal).where(Deal.status == status).limit(limit)
        )
        return list(result.scalars().all())
