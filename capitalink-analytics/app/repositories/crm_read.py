"""Read-only repository for CRM data."""

from typing import Dict, Optional
from sqlalchemy import func, select, text
from sqlalchemy.ext.asyncio import AsyncEngine

from app.core.logging import get_logger
from app.repositories.base import BaseReadRepository

logger = get_logger(__name__)


class CrmReadRepository(BaseReadRepository):
    """
    Read-only repository for querying CRM data.

    Assumes upstream CRM database has tables like:
    - contacts (with type: seller/buyer)
    - companies
    - listings (with status, stage)
    - deals (with status)
    """

    def __init__(self, engine: Optional[AsyncEngine] = None):
        """Initialize CRM read repository."""
        super().__init__(engine)

    async def get_contact_counts(self) -> Dict[str, int]:
        """
        Get counts of contacts by type.

        Returns:
            Dictionary with total, sellers, buyers counts
        """
        if not self.is_available():
            logger.warning("CRM database not available")
            return {"total": 0, "sellers": 0, "buyers": 0}

        async with await self.get_session() as session:
            try:
                # Total contacts
                result = await session.execute(
                    text("SELECT COUNT(*) as count FROM contacts")
                )
                total = result.scalar() or 0

                # Sellers
                result = await session.execute(
                    text("SELECT COUNT(*) as count FROM contacts WHERE type = 'seller'")
                )
                sellers = result.scalar() or 0

                # Buyers
                result = await session.execute(
                    text("SELECT COUNT(*) as count FROM contacts WHERE type = 'buyer'")
                )
                buyers = result.scalar() or 0

                return {
                    "total": total,
                    "sellers": sellers,
                    "buyers": buyers,
                }
            except Exception as e:
                logger.error(f"Error getting contact counts: {e}")
                return {"total": 0, "sellers": 0, "buyers": 0}

    async def get_company_count(self) -> int:
        """
        Get total number of companies.

        Returns:
            Number of companies
        """
        if not self.is_available():
            return 0

        async with await self.get_session() as session:
            try:
                result = await session.execute(
                    text("SELECT COUNT(*) as count FROM companies")
                )
                return result.scalar() or 0
            except Exception as e:
                logger.error(f"Error getting company count: {e}")
                return 0

    async def get_listing_counts(self) -> Dict[str, int]:
        """
        Get listing counts by status.

        Returns:
            Dictionary with total, active, and by_status breakdown
        """
        if not self.is_available():
            return {"total": 0, "active": 0, "by_status": {}}

        async with await self.get_session() as session:
            try:
                # Total listings
                result = await session.execute(
                    text("SELECT COUNT(*) as count FROM listings")
                )
                total = result.scalar() or 0

                # Active listings (assuming 'active' status)
                result = await session.execute(
                    text("SELECT COUNT(*) as count FROM listings WHERE status = 'active'")
                )
                active = result.scalar() or 0

                # By status
                result = await session.execute(
                    text("SELECT status, COUNT(*) as count FROM listings GROUP BY status")
                )
                by_status = {row[0]: row[1] for row in result.fetchall()}

                return {
                    "total": total,
                    "active": active,
                    "by_status": by_status,
                }
            except Exception as e:
                logger.error(f"Error getting listing counts: {e}")
                return {"total": 0, "active": 0, "by_status": {}}

    async def get_deal_counts(self) -> Dict[str, int]:
        """
        Get deal counts by status.

        Returns:
            Dictionary with total and by_status breakdown
        """
        if not self.is_available():
            return {"total": 0, "by_status": {}}

        async with await self.get_session() as session:
            try:
                # Total deals
                result = await session.execute(
                    text("SELECT COUNT(*) as count FROM deals")
                )
                total = result.scalar() or 0

                # By status
                result = await session.execute(
                    text("SELECT status, COUNT(*) as count FROM deals GROUP BY status")
                )
                by_status = {row[0]: row[1] for row in result.fetchall()}

                return {
                    "total": total,
                    "by_status": by_status,
                }
            except Exception as e:
                logger.error(f"Error getting deal counts: {e}")
                return {"total": 0, "by_status": {}}
