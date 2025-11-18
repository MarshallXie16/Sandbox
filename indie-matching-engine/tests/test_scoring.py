"""
Tests for scoring components and rule-based scorer.
"""

import pytest

from app.core.scoring.components import (
    DealSizeScorer,
    EngagementScorer,
    ExperienceScorer,
    IndustryScorer,
    RegionScorer,
)
from app.core.scoring.config import get_scoring_config
from app.core.scoring.rule_scorer import RuleBasedScorer
from app.schemas.buyer import BuyerProfile
from app.schemas.listing import ListingProfile


class TestIndustryScorer:
    """Test industry matching logic."""

    def test_exact_match(self, sample_buyer, sample_listing):
        """Test exact industry match scores correctly."""
        config = get_scoring_config()
        scorer = IndustryScorer(config)

        score, reasons = scorer.score(sample_buyer, sample_listing)

        assert score == config.weights.industry_exact
        assert any("exact" in r.lower() for r in reasons)

    def test_related_match(self, sample_buyer):
        """Test related industry match."""
        config = get_scoring_config()
        scorer = IndustryScorer(config)

        # IT services is related to software in config
        listing = ListingProfile(
            id=101,
            name="IT Company",
            amount=1000000,
            industry="it_services",
            region="BC",
        )

        score, reasons = scorer.score(sample_buyer, listing)

        assert score == config.weights.industry_related
        assert any("related" in r.lower() for r in reasons)

    def test_no_match(self, sample_buyer, mismatched_listing):
        """Test industry mismatch."""
        config = get_scoring_config()
        scorer = IndustryScorer(config)

        score, reasons = scorer.score(sample_buyer, mismatched_listing)

        assert score == config.weights.industry_mismatch
        assert any("mismatch" in r.lower() for r in reasons)


class TestRegionScorer:
    """Test region matching logic."""

    def test_exact_match(self, sample_buyer, sample_listing):
        """Test exact region match."""
        config = get_scoring_config()
        scorer = RegionScorer(config)

        score, reasons = scorer.score(sample_buyer, sample_listing)

        assert score == config.weights.region_exact
        assert any("same region" in r.lower() for r in reasons)

    def test_nearby_match(self, sample_buyer):
        """Test nearby region match."""
        config = get_scoring_config()
        scorer = RegionScorer(config)

        # Alberta is related to Western Canada in config
        listing = ListingProfile(
            id=101,
            name="Company",
            amount=1000000,
            industry="software",
            region="Alberta",
        )

        buyer = BuyerProfile(
            id=1,
            email="test@example.com",
            industry_preferences=["software"],
            region_preferences=["Western Canada"],
            min_deal_size=500000,
            max_deal_size=2000000,
        )

        score, reasons = scorer.score(buyer, listing)

        assert score == config.weights.region_nearby
        assert any("nearby" in r.lower() for r in reasons)


class TestDealSizeScorer:
    """Test deal size matching logic."""

    def test_perfect_fit(self, sample_buyer, sample_listing):
        """Test deal size within buyer budget."""
        config = get_scoring_config()
        scorer = DealSizeScorer(config)

        score, reasons = scorer.score(sample_buyer, sample_listing)

        assert score == config.weights.deal_size_perfect
        assert any("within" in r.lower() for r in reasons)

    def test_outside_budget(self, sample_buyer, mismatched_listing):
        """Test deal size way outside budget."""
        config = get_scoring_config()
        scorer = DealSizeScorer(config)

        score, reasons = scorer.score(sample_buyer, mismatched_listing)

        # Should be negative for mismatch
        assert score <= 0
        assert any("outside" in r.lower() for r in reasons)

    def test_no_budget_specified(self, sample_listing):
        """Test when buyer has no budget specified."""
        config = get_scoring_config()
        scorer = DealSizeScorer(config)

        buyer = BuyerProfile(
            id=1,
            email="test@example.com",
            industry_preferences=["software"],
            region_preferences=["BC"],
        )

        score, reasons = scorer.score(buyer, sample_listing)

        assert score == 0
        assert any("no budget" in r.lower() for r in reasons)


class TestExperienceScorer:
    """Test experience level scoring."""

    def test_strong_experience(self, sample_buyer, sample_listing):
        """Test experienced buyer."""
        config = get_scoring_config()
        scorer = ExperienceScorer(config)

        score, reasons = scorer.score(sample_buyer, sample_listing)

        assert score == config.weights.experience_strong
        assert any("strong experience" in r.lower() or "experienced" in r.lower() for r in reasons)

    def test_first_time_buyer(self, sample_listing):
        """Test first-time buyer."""
        config = get_scoring_config()
        scorer = ExperienceScorer(config)

        buyer = BuyerProfile(
            id=1,
            email="test@example.com",
            industry_preferences=["software"],
            region_preferences=["BC"],
            experience_level="first_time",
        )

        score, reasons = scorer.score(buyer, sample_listing)

        assert score == config.weights.experience_minimal


class TestEngagementScorer:
    """Test engagement scoring."""

    def test_high_engagement(self, sample_buyer, sample_listing):
        """Test high engagement score."""
        config = get_scoring_config()
        scorer = EngagementScorer(config)

        score, reasons = scorer.score(sample_buyer, sample_listing)

        assert score == config.weights.engagement_high
        assert any("high" in r.lower() for r in reasons)

    def test_no_engagement_data(self, sample_listing):
        """Test when no engagement data available."""
        config = get_scoring_config()
        scorer = EngagementScorer(config)

        buyer = BuyerProfile(
            id=1,
            email="test@example.com",
            industry_preferences=["software"],
            region_preferences=["BC"],
        )

        score, reasons = scorer.score(buyer, sample_listing)

        assert score == 0
        assert any("no engagement" in r.lower() for r in reasons)


class TestRuleBasedScorer:
    """Test the complete rule-based scorer."""

    def test_score_match(self, sample_buyer, sample_listing):
        """Test scoring a buyer-listing match."""
        scorer = RuleBasedScorer()

        match_score = scorer.score_match(sample_buyer, sample_listing)

        assert match_score.buyer_id == sample_buyer.id
        assert match_score.listing_id == sample_listing.id
        assert 0 <= match_score.score <= 100
        assert match_score.components.industry_score > 0
        assert match_score.components.region_score > 0
        assert match_score.components.deal_size_score > 0
        assert len(match_score.reason_codes) > 0

    def test_high_quality_match(self, sample_buyer, sample_listing):
        """Test that a good match scores high."""
        scorer = RuleBasedScorer()

        match_score = scorer.score_match(sample_buyer, sample_listing)

        # Should be a high-quality match
        assert match_score.score >= 60

    def test_poor_match(self, sample_buyer, mismatched_listing):
        """Test that a poor match scores low."""
        scorer = RuleBasedScorer()

        match_score = scorer.score_match(sample_buyer, mismatched_listing)

        # Should score poorly
        assert match_score.score < 40

    def test_score_batch(self, multiple_buyers, multiple_listings):
        """Test batch scoring."""
        scorer = RuleBasedScorer()

        matches = scorer.score_batch(multiple_buyers, multiple_listings)

        # Should have N buyers × M listings matches
        expected_count = len(multiple_buyers) * len(multiple_listings)
        assert len(matches) == expected_count

        # All scores should be in valid range
        for match in matches:
            assert 0 <= match.score <= 100

    def test_score_for_buyer(self, sample_buyer, multiple_listings):
        """Test scoring listings for a buyer."""
        scorer = RuleBasedScorer()

        matches = scorer.score_for_buyer(sample_buyer, multiple_listings, min_score=0)

        # Should return matches sorted by score
        assert len(matches) > 0
        for i in range(len(matches) - 1):
            assert matches[i].score >= matches[i + 1].score

    def test_score_for_listing(self, sample_listing, multiple_buyers):
        """Test scoring buyers for a listing."""
        scorer = RuleBasedScorer()

        matches = scorer.score_for_listing(sample_listing, multiple_buyers, min_score=0)

        # Should return matches sorted by score
        assert len(matches) > 0
        for i in range(len(matches) - 1):
            assert matches[i].score >= matches[i + 1].score
