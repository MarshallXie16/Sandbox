"""
Main matching engine orchestrating scoring and recommendations.
"""

from datetime import datetime, timedelta
from typing import List, Optional

from sqlalchemy import delete, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.core.data_loader import DataLoader
from app.core.scoring.rule_scorer import RuleBasedScorer
from app.models.match import BuyerListingMatch
from app.models.matching_run import MatchingRun
from app.schemas.buyer import BuyerProfile
from app.schemas.listing import ListingProfile
from app.schemas.match import MatchScore
from app.schemas.recommendation import (
    BuyerRecommendation,
    ListingRecommendation,
    RecommendationResponse,
)


class MatchingEngine:
    """
    Main matching engine for computing and retrieving buyer-listing matches.

    Coordinates:
    - Data loading from CRM
    - Match scoring via RuleBasedScorer
    - Caching of match scores
    - Recommendation generation
    """

    def __init__(
        self,
        db: AsyncSession,
        scorer: Optional[RuleBasedScorer] = None,
    ):
        self.db = db
        self.scorer = scorer or RuleBasedScorer()
        self.data_loader = DataLoader(db)
        self.settings = get_settings()

    async def get_recommendations_for_buyer(
        self,
        buyer_id: int,
        min_score: Optional[float] = None,
        limit: int = 10,
        use_cached: bool = True,
    ) -> RecommendationResponse:
        """
        Get listing recommendations for a buyer.

        Args:
            buyer_id: Buyer (contact) ID
            min_score: Minimum match score (defaults to config)
            limit: Maximum recommendations to return
            use_cached: Use cached scores if available

        Returns:
            RecommendationResponse with ranked listing recommendations
        """
        if min_score is None:
            min_score = self.settings.min_recommendation_score

        # Load buyer
        buyer = await self.data_loader.load_buyer(buyer_id)
        if not buyer:
            return RecommendationResponse(
                buyer_id=buyer_id,
                recommendations=[],
                total_candidates=0,
                recommendations_count=0,
                min_score_used=min_score,
                cached=False,
            )

        # Try to use cached scores
        if use_cached and self.settings.enable_match_caching:
            cached_matches = await self._get_cached_matches_for_buyer(
                buyer_id, min_score, limit
            )
            if cached_matches:
                # Load listing profiles
                listing_ids = [m.listing_id for m in cached_matches]
                listings = await self.data_loader.load_listings(listing_ids=listing_ids)
                listings_by_id = {lst.id: lst for lst in listings}

                recommendations = []
                for match in cached_matches:
                    listing = listings_by_id.get(match.listing_id)
                    if listing:
                        rec = BuyerRecommendation(
                            listing=listing,
                            match_score=match,
                        )
                        recommendations.append(rec)

                return RecommendationResponse(
                    buyer_id=buyer_id,
                    recommendations=recommendations[:limit],
                    total_candidates=len(cached_matches),
                    recommendations_count=len(recommendations[:limit]),
                    min_score_used=min_score,
                    cached=True,
                )

        # Compute fresh scores
        listings = await self.data_loader.load_listings(limit=1000)
        match_scores = self.scorer.score_for_buyer(buyer, listings, min_score=min_score)

        # Build recommendations
        recommendations = []
        for match_score in match_scores[:limit]:
            listing = next((lst for lst in listings if lst.id == match_score.listing_id), None)
            if listing:
                rec = BuyerRecommendation(
                    listing=listing,
                    match_score=match_score,
                )
                recommendations.append(rec)

        return RecommendationResponse(
            buyer_id=buyer_id,
            recommendations=recommendations,
            total_candidates=len(match_scores),
            recommendations_count=len(recommendations),
            min_score_used=min_score,
            cached=False,
        )

    async def get_recommendations_for_listing(
        self,
        listing_id: int,
        min_score: Optional[float] = None,
        limit: int = 10,
        use_cached: bool = True,
    ) -> RecommendationResponse:
        """
        Get buyer recommendations for a listing.

        Args:
            listing_id: Listing (deal) ID
            min_score: Minimum match score (defaults to config)
            limit: Maximum recommendations to return
            use_cached: Use cached scores if available

        Returns:
            RecommendationResponse with ranked buyer recommendations
        """
        if min_score is None:
            min_score = self.settings.min_recommendation_score

        # Load listing
        listing = await self.data_loader.load_listing(listing_id)
        if not listing:
            return RecommendationResponse(
                listing_id=listing_id,
                recommendations=[],
                total_candidates=0,
                recommendations_count=0,
                min_score_used=min_score,
                cached=False,
            )

        # Try to use cached scores
        if use_cached and self.settings.enable_match_caching:
            cached_matches = await self._get_cached_matches_for_listing(
                listing_id, min_score, limit
            )
            if cached_matches:
                # Load buyer profiles
                buyer_ids = [m.buyer_id for m in cached_matches]
                buyers = await self.data_loader.load_buyers(buyer_ids=buyer_ids)
                buyers_by_id = {b.id: b for b in buyers}

                recommendations = []
                for match in cached_matches:
                    buyer = buyers_by_id.get(match.buyer_id)
                    if buyer:
                        rec = ListingRecommendation(
                            buyer=buyer,
                            match_score=match,
                        )
                        recommendations.append(rec)

                return RecommendationResponse(
                    listing_id=listing_id,
                    recommendations=recommendations[:limit],
                    total_candidates=len(cached_matches),
                    recommendations_count=len(recommendations[:limit]),
                    min_score_used=min_score,
                    cached=True,
                )

        # Compute fresh scores
        buyers = await self.data_loader.load_buyers(limit=1000)
        match_scores = self.scorer.score_for_listing(listing, buyers, min_score=min_score)

        # Build recommendations
        recommendations = []
        for match_score in match_scores[:limit]:
            buyer = next((b for b in buyers if b.id == match_score.buyer_id), None)
            if buyer:
                rec = ListingRecommendation(
                    buyer=buyer,
                    match_score=match_score,
                )
                recommendations.append(rec)

        return RecommendationResponse(
            listing_id=listing_id,
            recommendations=recommendations,
            total_candidates=len(match_scores),
            recommendations_count=len(recommendations),
            min_score_used=min_score,
            cached=False,
        )

    async def compute_and_cache_matches(
        self,
        buyer_ids: Optional[List[int]] = None,
        listing_ids: Optional[List[int]] = None,
        force_recompute: bool = False,
    ) -> MatchingRun:
        """
        Compute match scores and cache them in the database.

        Args:
            buyer_ids: Specific buyers to process (None = all active)
            listing_ids: Specific listings to process (None = all active)
            force_recompute: Force recomputation even if cached

        Returns:
            MatchingRun record with statistics
        """
        # Create matching run record
        run = MatchingRun(
            run_type="full" if not buyer_ids and not listing_ids else "partial",
            status="running",
            scope={"buyer_ids": buyer_ids, "listing_ids": listing_ids},
            started_at=datetime.utcnow(),
        )
        self.db.add(run)
        await self.db.commit()
        await self.db.refresh(run)

        try:
            # Load data
            buyers = await self.data_loader.load_buyers(buyer_ids=buyer_ids, limit=10000)
            listings = await self.data_loader.load_listings(listing_ids=listing_ids, limit=10000)

            # Compute all matches
            match_scores = self.scorer.score_batch(buyers, listings)

            # Filter by minimum score
            min_score = self.settings.min_recommendation_score
            filtered_matches = [m for m in match_scores if m.score >= min_score]

            # Cache matches
            await self._cache_matches(filtered_matches, run.id, force_recompute)

            # Update run record
            run.status = "completed"
            run.completed_at = datetime.utcnow()
            run.matches_computed = len(filtered_matches)
            run.buyers_processed = len(buyers)
            run.listings_processed = len(listings)
            run.stats = {
                "avg_score": sum(m.score for m in filtered_matches) / len(filtered_matches)
                if filtered_matches
                else 0,
                "high_matches": len([m for m in filtered_matches if m.score >= 70]),
            }

            await self.db.commit()
            await self.db.refresh(run)

            return run

        except Exception as e:
            # Mark run as failed
            run.status = "failed"
            run.error_message = str(e)
            run.completed_at = datetime.utcnow()
            await self.db.commit()
            raise

    async def _cache_matches(
        self,
        match_scores: List[MatchScore],
        matching_run_id: int,
        force_recompute: bool = False,
    ) -> None:
        """Cache match scores in database."""
        if force_recompute:
            # Delete existing matches for these pairs
            for match in match_scores:
                await self.db.execute(
                    delete(BuyerListingMatch).where(
                        BuyerListingMatch.buyer_id == match.buyer_id,
                        BuyerListingMatch.listing_id == match.listing_id,
                    )
                )

        # Insert or update matches
        for match in match_scores:
            existing = await self.db.execute(
                select(BuyerListingMatch).where(
                    BuyerListingMatch.buyer_id == match.buyer_id,
                    BuyerListingMatch.listing_id == match.listing_id,
                )
            )
            existing_match = existing.scalar_one_or_none()

            if existing_match:
                # Update
                existing_match.score = match.score
                existing_match.components = match.components.model_dump()
                existing_match.reason_codes = match.reason_codes
                existing_match.matching_run_id = matching_run_id
                existing_match.updated_at = datetime.utcnow()
            else:
                # Insert
                new_match = BuyerListingMatch(
                    buyer_id=match.buyer_id,
                    listing_id=match.listing_id,
                    score=match.score,
                    components=match.components.model_dump(),
                    reason_codes=match.reason_codes,
                    matching_run_id=matching_run_id,
                    buyer_email=match.buyer_email,
                    listing_name=match.listing_name,
                )
                self.db.add(new_match)

        await self.db.commit()

    async def _get_cached_matches_for_buyer(
        self,
        buyer_id: int,
        min_score: float,
        limit: int,
    ) -> List[MatchScore]:
        """Get cached matches for a buyer."""
        result = await self.db.execute(
            select(BuyerListingMatch)
            .where(
                BuyerListingMatch.buyer_id == buyer_id,
                BuyerListingMatch.score >= min_score,
            )
            .order_by(BuyerListingMatch.score.desc())
            .limit(limit * 2)  # Get extra for filtering
        )
        matches = result.scalars().all()

        # Check if matches are stale
        if matches and self._are_matches_stale(matches[0]):
            return []

        # Convert to MatchScore schema
        return [self._db_match_to_schema(m) for m in matches]

    async def _get_cached_matches_for_listing(
        self,
        listing_id: int,
        min_score: float,
        limit: int,
    ) -> List[MatchScore]:
        """Get cached matches for a listing."""
        result = await self.db.execute(
            select(BuyerListingMatch)
            .where(
                BuyerListingMatch.listing_id == listing_id,
                BuyerListingMatch.score >= min_score,
            )
            .order_by(BuyerListingMatch.score.desc())
            .limit(limit * 2)
        )
        matches = result.scalars().all()

        if matches and self._are_matches_stale(matches[0]):
            return []

        return [self._db_match_to_schema(m) for m in matches]

    def _are_matches_stale(self, match: BuyerListingMatch) -> bool:
        """Check if cached matches are stale."""
        if not self.settings.enable_match_caching:
            return True

        cache_age = datetime.utcnow() - match.updated_at
        max_age = timedelta(seconds=self.settings.cache_ttl_seconds)

        return cache_age > max_age

    def _db_match_to_schema(self, db_match: BuyerListingMatch) -> MatchScore:
        """Convert database match to schema."""
        from app.schemas.match import MatchScoreComponents

        return MatchScore(
            buyer_id=db_match.buyer_id,
            listing_id=db_match.listing_id,
            score=db_match.score,
            components=MatchScoreComponents(**db_match.components),
            reason_codes=db_match.reason_codes,
            buyer_email=db_match.buyer_email,
            listing_name=db_match.listing_name,
            computed_at=db_match.updated_at,
        )
