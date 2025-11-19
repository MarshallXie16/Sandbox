"""CRM analytics service."""

from app.core.logging import get_logger
from app.repositories.crm_read import CrmReadRepository
from app.schemas.analytics import CrmOverviewResponse

logger = get_logger(__name__)


class CrmAnalyticsService:
    """Service for CRM analytics calculations."""

    def __init__(self, repository: CrmReadRepository):
        """Initialize service with repository."""
        self.repository = repository

    async def get_basic_counts(self) -> CrmOverviewResponse:
        """
        Get basic CRM counts and overview.

        Returns:
            CRM overview response
        """
        contact_counts = await self.repository.get_contact_counts()
        company_count = await self.repository.get_company_count()
        listing_counts = await self.repository.get_listing_counts()

        return CrmOverviewResponse(
            total_contacts=contact_counts["total"],
            total_sellers=contact_counts["sellers"],
            total_buyers=contact_counts["buyers"],
            total_companies=company_count,
            total_listings=listing_counts["total"],
            active_listings=listing_counts["active"],
            listings_by_status=listing_counts["by_status"],
        )

    async def get_listing_pipeline(self) -> dict:
        """
        Get listing pipeline statistics.

        Returns:
            Dictionary with listing counts by status
        """
        listing_counts = await self.repository.get_listing_counts()
        return listing_counts
