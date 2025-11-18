"""
Service for listing operations.
"""

from typing import Optional, Tuple
from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories import DealsRepository
from app.schemas.listing import ListingFilters, ListingTeaser, ListingDetail
from app.schemas.common import PaginatedResponse, PaginationMetadata
from app.core.logging import get_logger

logger = get_logger(__name__)


class ListingsService:
    """
    Service for business listing operations.

    Handles anonymized listing data suitable for portal display.
    """

    def __init__(self, session: AsyncSession):
        self.session = session
        self.deals_repo = DealsRepository(session)

    async def get_listings(
        self, filters: ListingFilters
    ) -> PaginatedResponse[ListingTeaser]:
        """
        Get paginated listings with filters.

        Args:
            filters: Listing filter criteria

        Returns:
            Paginated response with listing teasers
        """
        logger.info(f"Getting listings with filters: {filters.model_dump()}")

        offset = (filters.page - 1) * filters.page_size

        # Get listings from repository
        listings, total_count = await self.deals_repo.get_active_listings(
            industry=filters.industry,
            region=filters.region,
            min_price=filters.min_price,
            max_price=filters.max_price,
            min_revenue=filters.min_revenue,
            max_revenue=filters.max_revenue,
            status=filters.status,
            limit=filters.page_size,
            offset=offset,
        )

        # Convert to teasers (anonymized)
        teasers = [self._build_listing_teaser(deal, company) for deal, company in listings]

        # Build pagination metadata
        total_pages = (total_count + filters.page_size - 1) // filters.page_size
        pagination = PaginationMetadata(
            page=filters.page,
            page_size=filters.page_size,
            total_items=total_count,
            total_pages=total_pages,
            has_next=filters.page < total_pages,
            has_prev=filters.page > 1,
        )

        logger.info(
            f"Returning {len(teasers)} listings, total: {total_count}, page: {filters.page}/{total_pages}"
        )

        return PaginatedResponse(items=teasers, pagination=pagination)

    async def get_listing_detail(self, listing_id: int) -> Optional[ListingDetail]:
        """
        Get detailed listing information (still anonymized).

        Args:
            listing_id: Listing/deal ID

        Returns:
            Listing detail or None
        """
        logger.info(f"Getting listing detail for ID: {listing_id}")

        result = await self.deals_repo.get_listing_with_company(listing_id)
        if not result:
            logger.warning(f"Listing {listing_id} not found")
            return None

        deal, company = result
        return self._build_listing_detail(deal, company)

    def _build_listing_teaser(self, deal, company) -> ListingTeaser:
        """
        Build anonymized listing teaser.

        Args:
            deal: Deal model
            company: Company model (optional)

        Returns:
            ListingTeaser schema
        """
        # Build anonymized revenue/EBITDA ranges
        revenue_range = self._get_value_range(company.revenue if company else None)
        ebitda_range = self._get_value_range(company.ebitda if company else None)
        asking_price_range = self._get_value_range(deal.amount)

        # Extract short description (from details or truncate)
        short_description = None
        if deal.details and "short_description" in deal.details:
            short_description = deal.details["short_description"]
        elif company and company.description:
            short_description = (
                company.description[:200] + "..."
                if len(company.description) > 200
                else company.description
            )

        return ListingTeaser(
            listing_id=deal.id,
            title=deal.name,
            industry=company.industry if company else None,
            region=self._anonymize_region(company.region if company else None),
            revenue_range=revenue_range,
            ebitda_range=ebitda_range,
            asking_price_range=asking_price_range,
            short_description=short_description,
            status=deal.status or "Active",
            posted_date=deal.created_at,
        )

    def _build_listing_detail(self, deal, company) -> ListingDetail:
        """
        Build detailed listing information (anonymized).

        Args:
            deal: Deal model
            company: Company model (optional)

        Returns:
            ListingDetail schema
        """
        revenue_range = self._get_value_range(company.revenue if company else None)
        ebitda_range = self._get_value_range(company.ebitda if company else None)
        asking_price_range = self._get_value_range(deal.amount)

        # Extract description and highlights
        description = None
        key_highlights = []

        if company and company.description:
            description = company.description

        if deal.details:
            if "description" in deal.details:
                description = deal.details["description"]
            if "key_highlights" in deal.details:
                key_highlights = deal.details["key_highlights"]

        # Extract year established
        year_established = None
        if company and company.details and "year_established" in company.details:
            year_established = company.details["year_established"]

        return ListingDetail(
            listing_id=deal.id,
            title=deal.name,
            industry=company.industry if company else None,
            region=self._anonymize_region(company.region if company else None),
            revenue_range=revenue_range,
            ebitda_range=ebitda_range,
            asking_price_range=asking_price_range,
            description=description,
            key_highlights=key_highlights,
            status=deal.status or "Active",
            posted_date=deal.created_at,
            updated_date=deal.updated_at,
            company_size=company.size if company else None,
            year_established=year_established,
        )

    def _get_value_range(self, value: Optional[float]) -> Optional[str]:
        """
        Convert exact value to anonymized range.

        Args:
            value: Exact value

        Returns:
            Range string like "$1M-$5M" or None
        """
        if value is None:
            return None

        ranges = [
            (0, 500_000, "Under $500K"),
            (500_000, 1_000_000, "$500K-$1M"),
            (1_000_000, 2_500_000, "$1M-$2.5M"),
            (2_500_000, 5_000_000, "$2.5M-$5M"),
            (5_000_000, 10_000_000, "$5M-$10M"),
            (10_000_000, 25_000_000, "$10M-$25M"),
            (25_000_000, 50_000_000, "$25M-$50M"),
            (50_000_000, float("inf"), "$50M+"),
        ]

        for min_val, max_val, label in ranges:
            if min_val <= value < max_val:
                return label

        return "Unknown"

    def _anonymize_region(self, region: Optional[str]) -> Optional[str]:
        """
        Anonymize region to high-level geographic area.

        Args:
            region: Specific region

        Returns:
            High-level region
        """
        if not region:
            return None

        # Simple mapping - can be enhanced
        region_lower = region.lower()

        if any(state in region_lower for state in ["ca", "california", "or", "oregon", "wa", "washington"]):
            return "West Coast"
        elif any(state in region_lower for state in ["ny", "new york", "nj", "new jersey", "pa", "pennsylvania"]):
            return "Northeast"
        elif any(state in region_lower for state in ["tx", "texas", "az", "arizona", "nm", "new mexico"]):
            return "Southwest"
        elif any(state in region_lower for state in ["fl", "florida", "ga", "georgia", "nc", "north carolina"]):
            return "Southeast"
        elif any(state in region_lower for state in ["il", "illinois", "mi", "michigan", "oh", "ohio"]):
            return "Midwest"

        return "United States"
