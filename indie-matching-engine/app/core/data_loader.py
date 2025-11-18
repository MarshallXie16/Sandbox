"""
Data loader for fetching buyers and listings from CRM database.
"""

from typing import List, Optional

from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.buyer import BuyerProfile
from app.schemas.listing import ListingProfile


class DataLoader:
    """
    Loads buyer and listing data from indie-crm-core database.

    Since we're accessing the CRM database directly, we use raw SQL
    or dynamic table reflection to read contacts, companies, and deals.
    """

    def __init__(self, db: AsyncSession):
        self.db = db

    async def load_buyers(
        self,
        buyer_ids: Optional[List[int]] = None,
        limit: int = 100,
        min_engagement: Optional[float] = None,
    ) -> List[BuyerProfile]:
        """
        Load buyer profiles from CRM contacts table.

        Args:
            buyer_ids: Specific buyer IDs to load (if None, loads active buyers)
            limit: Maximum number of buyers to load
            min_engagement: Minimum engagement score filter

        Returns:
            List of BuyerProfile objects
        """
        # Build query
        # Assumes contacts table has: id, primary_email, first_name, last_name,
        # category, details (JSONB with buyer_profile)
        query = """
            SELECT
                id,
                primary_email,
                first_name,
                last_name,
                details
            FROM contacts
            WHERE
                category = 'buyer'
                AND status = 'active'
        """

        params = {}

        if buyer_ids:
            query += " AND id = ANY(:buyer_ids)"
            params["buyer_ids"] = buyer_ids

        if min_engagement is not None:
            query += " AND COALESCE((details->'engagement_score')::float, 0) >= :min_engagement"
            params["min_engagement"] = min_engagement

        query += " ORDER BY id LIMIT :limit"
        params["limit"] = limit

        result = await self.db.execute(text(query), params)
        rows = result.fetchall()

        buyers = []
        for row in rows:
            details = row.details or {}
            buyer_profile = details.get("buyer_profile", {})

            buyer = BuyerProfile(
                id=row.id,
                email=row.primary_email,
                first_name=row.first_name,
                last_name=row.last_name,
                industry_preferences=buyer_profile.get("industry_preferences", []),
                region_preferences=buyer_profile.get("region_preferences", []),
                min_deal_size=buyer_profile.get("min_deal_size"),
                max_deal_size=buyer_profile.get("max_deal_size"),
                deal_types=buyer_profile.get("deal_types", []),
                experience_level=buyer_profile.get("experience_level"),
                engagement_score=details.get("engagement_score"),
                notes=buyer_profile.get("notes"),
            )
            buyers.append(buyer)

        return buyers

    async def load_buyer(self, buyer_id: int) -> Optional[BuyerProfile]:
        """
        Load a single buyer by ID.

        Args:
            buyer_id: Buyer (contact) ID

        Returns:
            BuyerProfile or None if not found
        """
        buyers = await self.load_buyers(buyer_ids=[buyer_id], limit=1)
        return buyers[0] if buyers else None

    async def load_listings(
        self,
        listing_ids: Optional[List[int]] = None,
        limit: int = 100,
        status: Optional[str] = None,
    ) -> List[ListingProfile]:
        """
        Load listing profiles from CRM deals + companies tables.

        Args:
            listing_ids: Specific listing (deal) IDs to load
            limit: Maximum number of listings to load
            status: Filter by deal status

        Returns:
            List of ListingProfile objects
        """
        # Build query
        # Joins deals with companies, filters for active listings
        query = """
            SELECT
                d.id,
                d.name,
                d.amount,
                d.status,
                d.stage_id,
                d.company_id,
                d.details,
                c.name as company_name,
                c.industry as company_industry,
                c.region as company_region
            FROM deals d
            LEFT JOIN companies c ON d.company_id = c.id
            WHERE
                (d.details->>'is_listing')::boolean = true
        """

        params = {}

        if listing_ids:
            query += " AND d.id = ANY(:listing_ids)"
            params["listing_ids"] = listing_ids

        if status:
            query += " AND d.status = :status"
            params["status"] = status
        else:
            # Default: only active listings
            query += " AND d.status IN ('Active', 'New', 'ComingSoon')"

        query += " ORDER BY d.id LIMIT :limit"
        params["limit"] = limit

        result = await self.db.execute(text(query), params)
        rows = result.fetchall()

        listings = []
        for row in rows:
            details = row.details or {}
            listing_details = details.get("listing", {})

            listing = ListingProfile(
                id=row.id,
                name=row.name,
                company_id=row.company_id,
                company_name=row.company_name,
                amount=row.amount,
                status=row.status,
                stage=row.stage_id,
                industry=listing_details.get("industry") or row.company_industry,
                region=listing_details.get("region") or row.company_region,
                revenue=listing_details.get("revenue"),
                ebitda=listing_details.get("ebitda"),
                deal_size_band=listing_details.get("deal_size_band"),
                tags=listing_details.get("tags", []),
                description=listing_details.get("description"),
            )
            listings.append(listing)

        return listings

    async def load_listing(self, listing_id: int) -> Optional[ListingProfile]:
        """
        Load a single listing by ID.

        Args:
            listing_id: Listing (deal) ID

        Returns:
            ListingProfile or None if not found
        """
        listings = await self.load_listings(listing_ids=[listing_id], limit=1)
        return listings[0] if listings else None
