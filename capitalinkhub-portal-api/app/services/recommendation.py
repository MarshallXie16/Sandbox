"""
Service for generating listing recommendations.
"""

from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories import PortalMembersRepository, PortalInterestsRepository, DealsRepository
from app.schemas.recommendation import RecommendationsResponse, RecommendationScore
from app.services.listings import ListingsService
from app.core.logging import get_logger

logger = get_logger(__name__)


class RecommendationService:
    """
    Service for generating personalized listing recommendations.

    Currently uses a simple heuristic algorithm.
    Future: Can integrate with indie-matching-engine API.
    """

    def __init__(self, session: AsyncSession):
        self.session = session
        self.members_repo = PortalMembersRepository(session)
        self.interests_repo = PortalInterestsRepository(session)
        self.deals_repo = DealsRepository(session)
        self.listings_service = ListingsService(session)

    async def get_recommendations(
        self, member_id: int, limit: int = 10
    ) -> Optional[RecommendationsResponse]:
        """
        Get personalized recommendations for a member.

        Algorithm (simple heuristic):
        1. Get member's past interests
        2. Extract common attributes (industry, region, price range)
        3. Find similar active listings
        4. Exclude already interested listings
        5. Return top N with match scores

        Args:
            member_id: Portal member ID
            limit: Maximum number of recommendations

        Returns:
            Recommendations response or None if member not found
        """
        logger.info(f"Generating recommendations for member: {member_id}")

        # Validate member exists
        member = await self.members_repo.get_by_id(member_id)
        if not member:
            logger.warning(f"Member {member_id} not found")
            return None

        # Get member's interests
        interests_data = await self.interests_repo.get_member_interests(member_id)
        interested_listing_ids = {interest.listing_id for interest, _, _ in interests_data}

        # Extract preferences from interests
        preferences = self._extract_preferences(interests_data)

        logger.info(f"Extracted preferences: {preferences}")

        # Get active listings matching preferences
        candidate_listings, _ = await self.deals_repo.get_active_listings(
            industry=preferences.get("industry"),
            region=preferences.get("region"),
            min_price=preferences.get("min_price"),
            max_price=preferences.get("max_price"),
            limit=limit * 2,  # Get more than needed for filtering
        )

        # Score and filter recommendations
        recommendations = []
        for deal, company in candidate_listings:
            # Skip already interested
            if deal.id in interested_listing_ids:
                continue

            # Calculate match score
            match_score, reasons = self._calculate_match_score(
                deal, company, preferences
            )

            # Build listing teaser
            listing_teaser = self.listings_service._build_listing_teaser(deal, company)

            recommendations.append(
                RecommendationScore(
                    listing=listing_teaser,
                    match_score=match_score,
                    match_reasons=reasons,
                )
            )

        # Sort by match score and limit
        recommendations.sort(key=lambda r: r.match_score, reverse=True)
        recommendations = recommendations[:limit]

        logger.info(f"Generated {len(recommendations)} recommendations for member {member_id}")

        return RecommendationsResponse(
            member_id=member_id,
            recommendations=recommendations,
            total_recommendations=len(recommendations),
            algorithm="heuristic_v1",
        )

    def _extract_preferences(self, interests_data) -> dict:
        """
        Extract preferences from past interests.

        Args:
            interests_data: List of (interest, deal, company) tuples

        Returns:
            Dictionary of preferences
        """
        if not interests_data:
            return {}

        # Count occurrences of each attribute
        industries = []
        regions = []
        prices = []

        for _, deal, company in interests_data:
            if company:
                if company.industry:
                    industries.append(company.industry)
                if company.region:
                    regions.append(company.region)
            if deal.amount:
                prices.append(deal.amount)

        preferences = {}

        # Most common industry
        if industries:
            preferences["industry"] = max(set(industries), key=industries.count)

        # Most common region
        if regions:
            preferences["region"] = max(set(regions), key=regions.count)

        # Price range from past interests
        if prices:
            avg_price = sum(prices) / len(prices)
            preferences["min_price"] = avg_price * 0.7  # ±30%
            preferences["max_price"] = avg_price * 1.3

        return preferences

    def _calculate_match_score(
        self, deal, company, preferences: dict
    ) -> tuple[float, list[str]]:
        """
        Calculate match score for a listing.

        Args:
            deal: Deal model
            company: Company model (optional)
            preferences: Member preferences

        Returns:
            Tuple of (score, list of reasons)
        """
        score = 0.0
        reasons = []

        # Industry match (30 points)
        if (
            preferences.get("industry")
            and company
            and company.industry == preferences["industry"]
        ):
            score += 30
            reasons.append(f"Matches your preferred industry: {company.industry}")

        # Region match (20 points)
        if (
            preferences.get("region")
            and company
            and company.region == preferences["region"]
        ):
            score += 20
            reasons.append(f"Located in your preferred region: {company.region}")

        # Price range match (25 points)
        if deal.amount and preferences.get("min_price") and preferences.get("max_price"):
            if preferences["min_price"] <= deal.amount <= preferences["max_price"]:
                score += 25
                reasons.append("Price matches your typical range")

        # Recent listing (15 points)
        from datetime import datetime, timedelta

        if deal.created_at > datetime.utcnow() - timedelta(days=30):
            score += 15
            reasons.append("Recently listed")

        # Active status (10 points)
        if deal.status in ["Active", "New", "Open"]:
            score += 10
            reasons.append("Currently active")

        # If no specific reasons, add generic one
        if not reasons:
            reasons.append("Matches general criteria")
            score = 40  # Base score

        return score, reasons
