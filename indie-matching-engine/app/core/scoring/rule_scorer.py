"""
Rule-based scorer implementation.
"""

from datetime import datetime
from typing import List

from app.core.scoring.components import (
    DealSizeScorer,
    EngagementScorer,
    ExperienceScorer,
    IndustryScorer,
    RegionScorer,
)
from app.core.scoring.config import ScoringConfig, get_scoring_config
from app.core.scoring.scorer import MatchScorer
from app.schemas.buyer import BuyerProfile
from app.schemas.listing import ListingProfile
from app.schemas.match import MatchScore, MatchScoreComponents


class RuleBasedScorer(MatchScorer):
    """
    Rule-based scoring implementation using configurable weights.

    Combines multiple scoring components (industry, region, deal size, etc.)
    based on weights defined in YAML configuration.
    """

    def __init__(self, config: ScoringConfig = None):
        """
        Initialize rule-based scorer.

        Args:
            config: Scoring configuration (if None, loads from default path)
        """
        self.config = config or get_scoring_config()

        # Initialize component scorers
        self.industry_scorer = IndustryScorer(self.config)
        self.region_scorer = RegionScorer(self.config)
        self.deal_size_scorer = DealSizeScorer(self.config)
        self.experience_scorer = ExperienceScorer(self.config)
        self.engagement_scorer = EngagementScorer(self.config)

    def score_match(
        self,
        buyer: BuyerProfile,
        listing: ListingProfile,
    ) -> MatchScore:
        """
        Compute match score between a buyer and a listing.

        Args:
            buyer: Buyer profile
            listing: Listing profile

        Returns:
            MatchScore with overall score, components, and explanations
        """
        # Score each component
        industry_score, industry_reasons = self.industry_scorer.score(buyer, listing)
        region_score, region_reasons = self.region_scorer.score(buyer, listing)
        deal_size_score, deal_size_reasons = self.deal_size_scorer.score(buyer, listing)
        experience_score, experience_reasons = self.experience_scorer.score(buyer, listing)
        engagement_score, engagement_reasons = self.engagement_scorer.score(buyer, listing)

        # Calculate overall score
        overall_score = (
            industry_score
            + region_score
            + deal_size_score
            + experience_score
            + engagement_score
        )

        # Clamp to 0-100 range
        overall_score = max(0.0, min(100.0, overall_score))

        # Combine all reason codes
        all_reasons = (
            industry_reasons
            + region_reasons
            + deal_size_reasons
            + experience_reasons
            + engagement_reasons
        )

        # Create components breakdown
        components = MatchScoreComponents(
            industry_score=industry_score,
            region_score=region_score,
            deal_size_score=deal_size_score,
            experience_score=experience_score,
            engagement_score=engagement_score,
        )

        # Build match score
        match_score = MatchScore(
            buyer_id=buyer.id,
            listing_id=listing.id,
            score=overall_score,
            components=components,
            reason_codes=all_reasons,
            buyer_email=buyer.email,
            listing_name=listing.name,
            computed_at=datetime.utcnow(),
        )

        return match_score

    def score_batch(
        self,
        buyers: List[BuyerProfile],
        listings: List[ListingProfile],
    ) -> List[MatchScore]:
        """
        Compute match scores for all buyer-listing combinations.

        Args:
            buyers: List of buyer profiles
            listings: List of listing profiles

        Returns:
            List of MatchScore objects for all combinations
        """
        matches = []

        for buyer in buyers:
            for listing in listings:
                match_score = self.score_match(buyer, listing)
                matches.append(match_score)

        return matches

    def score_for_buyer(
        self,
        buyer: BuyerProfile,
        listings: List[ListingProfile],
        min_score: float = None,
    ) -> List[MatchScore]:
        """
        Score all listings for a specific buyer.

        Args:
            buyer: Buyer profile
            listings: List of listing profiles
            min_score: Minimum score threshold (filters results)

        Returns:
            List of MatchScore objects, sorted by score descending
        """
        if min_score is None:
            min_score = self.config.thresholds.min_recommendation_score

        matches = []
        for listing in listings:
            match_score = self.score_match(buyer, listing)
            if match_score.score >= min_score:
                matches.append(match_score)

        # Sort by score descending
        matches.sort(key=lambda m: m.score, reverse=True)

        return matches

    def score_for_listing(
        self,
        listing: ListingProfile,
        buyers: List[BuyerProfile],
        min_score: float = None,
    ) -> List[MatchScore]:
        """
        Score all buyers for a specific listing.

        Args:
            listing: Listing profile
            buyers: List of buyer profiles
            min_score: Minimum score threshold (filters results)

        Returns:
            List of MatchScore objects, sorted by score descending
        """
        if min_score is None:
            min_score = self.config.thresholds.min_recommendation_score

        matches = []
        for buyer in buyers:
            match_score = self.score_match(buyer, listing)
            if match_score.score >= min_score:
                matches.append(match_score)

        # Sort by score descending
        matches.sort(key=lambda m: m.score, reverse=True)

        return matches
