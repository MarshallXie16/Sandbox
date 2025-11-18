"""
Individual scoring components for match evaluation.
"""

from typing import List, Optional, Tuple

from app.core.scoring.config import ScoringConfig
from app.schemas.buyer import BuyerProfile
from app.schemas.listing import ListingProfile


class IndustryScorer:
    """Scores industry match between buyer preferences and listing."""

    def __init__(self, config: ScoringConfig):
        self.config = config
        self.weights = config.weights
        self.relations = config.industry_relations

    def score(
        self,
        buyer: BuyerProfile,
        listing: ListingProfile,
    ) -> Tuple[float, List[str]]:
        """
        Compute industry match score.

        Returns:
            Tuple of (score, reason_codes)
        """
        reasons = []
        listing_industry = (listing.industry or "").lower().strip()

        if not listing_industry or not buyer.industry_preferences:
            return 0.0, ["No industry information available"]

        buyer_industries = [ind.lower().strip() for ind in buyer.industry_preferences]

        # Check for exact match
        if listing_industry in buyer_industries:
            score = self.weights.industry_exact
            reasons.append(f"Exact industry match: {listing_industry}")
            return score, reasons

        # Check for related industry
        for buyer_ind in buyer_industries:
            related = self.relations.get(buyer_ind, [])
            related_lower = [r.lower() for r in related]

            if listing_industry in related_lower:
                score = self.weights.industry_related
                reasons.append(f"Related industries: {buyer_ind} ↔ {listing_industry}")
                return score, reasons

        # No match
        score = self.weights.industry_mismatch
        reasons.append(f"Industry mismatch: buyer wants {buyer_industries}, listing is {listing_industry}")
        return score, reasons


class RegionScorer:
    """Scores geographic/region match."""

    def __init__(self, config: ScoringConfig):
        self.config = config
        self.weights = config.weights
        self.relations = config.region_relations

    def score(
        self,
        buyer: BuyerProfile,
        listing: ListingProfile,
    ) -> Tuple[float, List[str]]:
        """
        Compute region match score.

        Returns:
            Tuple of (score, reason_codes)
        """
        reasons = []
        listing_region = (listing.region or "").strip()

        if not listing_region or not buyer.region_preferences:
            return 0.0, ["No region information available"]

        buyer_regions = [reg.strip() for reg in buyer.region_preferences]

        # Check for exact match
        if listing_region in buyer_regions:
            score = self.weights.region_exact
            reasons.append(f"Same region: {listing_region}")
            return score, reasons

        # Check for nearby/related regions
        for buyer_reg in buyer_regions:
            related = self.relations.get(buyer_reg, [])

            if listing_region in related:
                score = self.weights.region_nearby
                reasons.append(f"Nearby regions: {buyer_reg} ↔ {listing_region}")
                return score, reasons

        # No match
        score = self.weights.region_mismatch
        reasons.append(f"Different regions: buyer prefers {buyer_regions}, listing in {listing_region}")
        return score, reasons


class DealSizeScorer:
    """Scores deal size alignment with buyer budget."""

    def __init__(self, config: ScoringConfig):
        self.config = config
        self.weights = config.weights
        self.tolerance = config.deal_size_tolerance

    def score(
        self,
        buyer: BuyerProfile,
        listing: ListingProfile,
    ) -> Tuple[float, List[str]]:
        """
        Compute deal size match score.

        Returns:
            Tuple of (score, reason_codes)
        """
        reasons = []
        deal_size = listing.amount

        if deal_size is None or deal_size <= 0:
            return 0.0, ["No deal size information available"]

        min_budget = buyer.min_deal_size
        max_budget = buyer.max_deal_size

        if min_budget is None and max_budget is None:
            return 0.0, ["Buyer has no budget preferences specified"]

        # Perfect fit - within range
        if min_budget is not None and max_budget is not None:
            if min_budget <= deal_size <= max_budget:
                score = self.weights.deal_size_perfect
                reasons.append(
                    f"Deal size ${deal_size:,.0f} within budget range "
                    f"(${min_budget:,.0f}-${max_budget:,.0f})"
                )
                return score, reasons

            # Calculate how far outside the range
            if deal_size < min_budget:
                gap = min_budget - deal_size
                tolerance_amount = min_budget * self.tolerance.acceptable
            else:  # deal_size > max_budget
                gap = deal_size - max_budget
                tolerance_amount = max_budget * self.tolerance.acceptable

            # Acceptable - within tolerance
            if gap <= tolerance_amount:
                score = self.weights.deal_size_acceptable
                reasons.append(
                    f"Deal size ${deal_size:,.0f} close to budget range "
                    f"(${min_budget:,.0f}-${max_budget:,.0f})"
                )
                return score, reasons

            # Stretch - within stretch tolerance
            stretch_tolerance = (
                max_budget if deal_size > max_budget else min_budget
            ) * self.tolerance.stretch
            if gap <= stretch_tolerance:
                score = self.weights.deal_size_stretch
                reasons.append(
                    f"Deal size ${deal_size:,.0f} is a stretch for budget "
                    f"(${min_budget:,.0f}-${max_budget:,.0f})"
                )
                return score, reasons

            # Mismatch
            score = self.weights.deal_size_mismatch
            reasons.append(
                f"Deal size ${deal_size:,.0f} outside budget range "
                f"(${min_budget:,.0f}-${max_budget:,.0f})"
            )
            return score, reasons

        # Only min or max specified
        if min_budget is not None and deal_size >= min_budget:
            score = self.weights.deal_size_perfect
            reasons.append(f"Deal size ${deal_size:,.0f} meets minimum budget ${min_budget:,.0f}")
            return score, reasons

        if max_budget is not None and deal_size <= max_budget:
            score = self.weights.deal_size_perfect
            reasons.append(f"Deal size ${deal_size:,.0f} under maximum budget ${max_budget:,.0f}")
            return score, reasons

        score = self.weights.deal_size_mismatch
        reasons.append("Deal size outside buyer's budget")
        return score, reasons


class ExperienceScorer:
    """Scores experience match between buyer and listing industry."""

    def __init__(self, config: ScoringConfig):
        self.config = config
        self.weights = config.weights

    def score(
        self,
        buyer: BuyerProfile,
        listing: ListingProfile,
    ) -> Tuple[float, List[str]]:
        """
        Compute experience match score.

        Returns:
            Tuple of (score, reason_codes)
        """
        reasons = []
        experience_level = (buyer.experience_level or "").lower()

        if not experience_level:
            return 0.0, ["No experience level specified"]

        # Map experience level to score
        if experience_level in ["serial", "experienced"]:
            score = self.weights.experience_strong
            reasons.append(f"Buyer has strong experience ({buyer.experience_level})")
            return score, reasons

        if experience_level in ["some_experience", "moderate"]:
            score = self.weights.experience_moderate
            reasons.append(f"Buyer has some experience ({buyer.experience_level})")
            return score, reasons

        # first_time or minimal
        score = self.weights.experience_minimal
        reasons.append(f"Buyer is new to business ownership ({buyer.experience_level})")
        return score, reasons


class EngagementScorer:
    """Scores based on buyer engagement level."""

    def __init__(self, config: ScoringConfig):
        self.config = config
        self.weights = config.weights
        self.thresholds = config.engagement_thresholds

    def score(
        self,
        buyer: BuyerProfile,
        listing: ListingProfile,
    ) -> Tuple[float, List[str]]:
        """
        Compute engagement boost score.

        Returns:
            Tuple of (score, reason_codes)
        """
        reasons = []
        engagement_score = buyer.engagement_score

        if engagement_score is None:
            return 0.0, ["No engagement data available"]

        if engagement_score >= self.thresholds.high:
            score = self.weights.engagement_high
            reasons.append(f"High engagement ({engagement_score:.0f}/100)")
            return score, reasons

        if engagement_score >= self.thresholds.medium:
            score = self.weights.engagement_medium
            reasons.append(f"Moderate engagement ({engagement_score:.0f}/100)")
            return score, reasons

        score = self.weights.engagement_low
        reasons.append(f"Low engagement ({engagement_score:.0f}/100)")
        return score, reasons
