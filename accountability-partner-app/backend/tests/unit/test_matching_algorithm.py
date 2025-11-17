"""Unit tests for matching algorithm."""
import pytest
from app.models.user import UserProfile
from app.services.matching_service import (
    calculate_complementarity_score,
    calculate_compatibility_score,
    calculate_availability_score,
    calculate_match_score,
    generate_match_explanation,
    rank_potential_matches
)
import uuid


class TestComplementarityScoring:
    """Test complementarity score calculation."""

    def test_perfect_complementarity(self):
        """Test perfect match where all struggles are addressed."""
        user1 = UserProfile(
            id=uuid.uuid4(),
            user_id=uuid.uuid4(),
            strengths=['career', 'fitness'],
            struggles=['fashion', 'cooking']
        )
        user2 = UserProfile(
            id=uuid.uuid4(),
            user_id=uuid.uuid4(),
            strengths=['fashion', 'cooking'],
            struggles=['career', 'fitness']
        )

        score = calculate_complementarity_score(user1, user2)
        assert score == 1.0, "Perfect complementarity should score 1.0"

    def test_no_complementarity(self):
        """Test no overlap between strengths and struggles."""
        user1 = UserProfile(
            id=uuid.uuid4(),
            user_id=uuid.uuid4(),
            strengths=['career'],
            struggles=['fitness']
        )
        user2 = UserProfile(
            id=uuid.uuid4(),
            user_id=uuid.uuid4(),
            strengths=['fashion'],
            struggles=['cooking']
        )

        score = calculate_complementarity_score(user1, user2)
        assert score == 0.0, "No overlap should score 0.0"

    def test_partial_complementarity(self):
        """Test partial overlap."""
        user1 = UserProfile(
            id=uuid.uuid4(),
            user_id=uuid.uuid4(),
            strengths=['career', 'fitness', 'finance'],
            struggles=['fashion', 'cooking']
        )
        user2 = UserProfile(
            id=uuid.uuid4(),
            user_id=uuid.uuid4(),
            strengths=['fashion'],  # Helps with 1 of 2 struggles
            struggles=['career', 'public_speaking']
        )

        score = calculate_complementarity_score(user1, user2)
        # user1 helps with 1 of user2's 2 struggles (career)
        # user2 helps with 1 of user1's 2 struggles (fashion)
        # Total: 2 helped out of 4 total struggles = 0.5
        assert score == 0.5, f"Expected 0.5, got {score}"

    def test_empty_lists(self):
        """Test handling of empty strengths/struggles."""
        user1 = UserProfile(
            id=uuid.uuid4(),
            user_id=uuid.uuid4(),
            strengths=[],
            struggles=[]
        )
        user2 = UserProfile(
            id=uuid.uuid4(),
            user_id=uuid.uuid4(),
            strengths=['career'],
            struggles=['fitness']
        )

        score = calculate_complementarity_score(user1, user2)
        assert score == 0.0, "Empty lists should score 0.0"

    def test_symmetric_scoring(self):
        """Test that scoring is symmetric."""
        user1 = UserProfile(
            id=uuid.uuid4(),
            user_id=uuid.uuid4(),
            strengths=['career', 'fitness'],
            struggles=['fashion']
        )
        user2 = UserProfile(
            id=uuid.uuid4(),
            user_id=uuid.uuid4(),
            strengths=['fashion', 'cooking'],
            struggles=['career']
        )

        score1 = calculate_complementarity_score(user1, user2)
        score2 = calculate_complementarity_score(user2, user1)
        assert score1 == score2, "Complementarity should be symmetric"


class TestCompatibilityScoring:
    """Test compatibility score calculation."""

    def test_matching_communication_style(self):
        """Test matching communication styles."""
        user1 = UserProfile(
            id=uuid.uuid4(),
            user_id=uuid.uuid4(),
            communication_style='direct',
            commitment_level='moderate',
            preferred_check_in_frequency='weekly'
        )
        user2 = UserProfile(
            id=uuid.uuid4(),
            user_id=uuid.uuid4(),
            communication_style='direct',
            commitment_level='moderate',
            preferred_check_in_frequency='weekly'
        )

        score = calculate_compatibility_score(user1, user2)
        assert score == 1.0, "Perfect compatibility should score 1.0"

    def test_complementary_communication_styles(self):
        """Test complementary communication styles."""
        user1 = UserProfile(
            id=uuid.uuid4(),
            user_id=uuid.uuid4(),
            communication_style='direct',
            commitment_level='moderate',
            preferred_check_in_frequency='weekly'
        )
        user2 = UserProfile(
            id=uuid.uuid4(),
            user_id=uuid.uuid4(),
            communication_style='supportive',
            commitment_level='moderate',
            preferred_check_in_frequency='weekly'
        )

        score = calculate_compatibility_score(user1, user2)
        # Direct + Supportive = 0.7, matching commitment = 1.0, matching frequency = 1.0
        # Total: 2.7 / 3.0 = 0.9
        assert score == pytest.approx(0.9, abs=0.01)

    def test_different_commitment_levels(self):
        """Test different commitment levels."""
        user1 = UserProfile(
            id=uuid.uuid4(),
            user_id=uuid.uuid4(),
            communication_style='direct',
            commitment_level='casual',
            preferred_check_in_frequency='weekly'
        )
        user2 = UserProfile(
            id=uuid.uuid4(),
            user_id=uuid.uuid4(),
            communication_style='direct',
            commitment_level='intense',
            preferred_check_in_frequency='weekly'
        )

        score = calculate_compatibility_score(user1, user2)
        # Matching style = 1.0, commitment diff = 2 (casual=1, intense=3) = 0.0, matching freq = 1.0
        # Total: 2.0 / 3.0 = 0.667
        assert score == pytest.approx(0.667, abs=0.01)


class TestAvailabilityScoring:
    """Test availability score calculation."""

    def test_full_day_overlap(self):
        """Test full overlap in available days."""
        user1 = UserProfile(
            id=uuid.uuid4(),
            user_id=uuid.uuid4(),
            available_days_of_week=[1, 2, 3, 4, 5],  # Mon-Fri
            preferred_check_in_time='evening'
        )
        user2 = UserProfile(
            id=uuid.uuid4(),
            user_id=uuid.uuid4(),
            available_days_of_week=[1, 2, 3, 4, 5],  # Mon-Fri
            preferred_check_in_time='evening'
        )

        score = calculate_availability_score(user1, user2)
        assert score == 1.0, "Full overlap should score 1.0"

    def test_partial_day_overlap(self):
        """Test partial overlap in available days."""
        user1 = UserProfile(
            id=uuid.uuid4(),
            user_id=uuid.uuid4(),
            available_days_of_week=[1, 3, 5],  # Mon, Wed, Fri
            preferred_check_in_time='morning'
        )
        user2 = UserProfile(
            id=uuid.uuid4(),
            user_id=uuid.uuid4(),
            available_days_of_week=[2, 3, 4],  # Tue, Wed, Thu
            preferred_check_in_time='morning'
        )

        score = calculate_availability_score(user1, user2)
        # Overlap: [3] (Wed), Union: [1,2,3,4,5] = 1/5 = 0.2
        # Day score = 0.2, Time score = 1.0 (matching)
        # Total: (0.2 * 0.7) + (1.0 * 0.3) = 0.14 + 0.3 = 0.44
        assert score == pytest.approx(0.44, abs=0.01)

    def test_no_day_overlap(self):
        """Test no overlap in available days."""
        user1 = UserProfile(
            id=uuid.uuid4(),
            user_id=uuid.uuid4(),
            available_days_of_week=[1, 2],  # Mon, Tue
            preferred_check_in_time='evening'
        )
        user2 = UserProfile(
            id=uuid.uuid4(),
            user_id=uuid.uuid4(),
            available_days_of_week=[6, 7],  # Sat, Sun
            preferred_check_in_time='morning'
        )

        score = calculate_availability_score(user1, user2)
        # No overlap: 0/4 = 0.0, different times = 0.3
        # Total: (0.0 * 0.7) + (0.3 * 0.3) = 0.09
        assert score == pytest.approx(0.09, abs=0.01)


class TestOverallMatchScoring:
    """Test overall match score calculation."""

    def test_perfect_match(self):
        """Test a perfect match scenario."""
        user1 = UserProfile(
            id=uuid.uuid4(),
            user_id=uuid.uuid4(),
            strengths=['career', 'fitness'],
            struggles=['fashion', 'relationships'],
            communication_style='direct',
            commitment_level='moderate',
            preferred_check_in_frequency='3x_week',
            available_days_of_week=[1, 3, 5],
            preferred_check_in_time='evening'
        )
        user2 = UserProfile(
            id=uuid.uuid4(),
            user_id=uuid.uuid4(),
            strengths=['fashion', 'relationships'],
            struggles=['career', 'fitness'],
            communication_style='direct',
            commitment_level='moderate',
            preferred_check_in_frequency='3x_week',
            available_days_of_week=[1, 3, 5],
            preferred_check_in_time='evening'
        )

        score = calculate_match_score(user1, user2)
        # Complementarity: 1.0 (50%)
        # Compatibility: 1.0 (30%)
        # Availability: 1.0 (20%)
        # Total: 1.0
        assert score == pytest.approx(1.0, abs=0.01)

    def test_poor_match(self):
        """Test a poor match scenario."""
        user1 = UserProfile(
            id=uuid.uuid4(),
            user_id=uuid.uuid4(),
            strengths=['career'],
            struggles=['fitness'],
            communication_style='direct',
            commitment_level='casual',
            preferred_check_in_frequency='weekly',
            available_days_of_week=[1, 2],
            preferred_check_in_time='morning'
        )
        user2 = UserProfile(
            id=uuid.uuid4(),
            user_id=uuid.uuid4(),
            strengths=['fashion'],
            struggles=['cooking'],
            communication_style='motivational',
            commitment_level='intense',
            preferred_check_in_frequency='daily',
            available_days_of_week=[6, 7],
            preferred_check_in_time='evening'
        )

        score = calculate_match_score(user1, user2)
        # No complementarity, poor compatibility, poor availability
        assert score < 0.3, f"Poor match should score < 0.3, got {score}"

    def test_symmetric_match_score(self):
        """Test that match scoring is symmetric."""
        user1 = UserProfile(
            id=uuid.uuid4(),
            user_id=uuid.uuid4(),
            strengths=['career'],
            struggles=['fashion'],
            communication_style='direct'
        )
        user2 = UserProfile(
            id=uuid.uuid4(),
            user_id=uuid.uuid4(),
            strengths=['fashion'],
            struggles=['career'],
            communication_style='supportive'
        )

        score1 = calculate_match_score(user1, user2)
        score2 = calculate_match_score(user2, user1)
        assert score1 == score2, "Match score should be symmetric"


class TestMatchExplanation:
    """Test match explanation generation."""

    def test_explanation_generation(self):
        """Test generating human-readable match explanation."""
        user1 = UserProfile(
            id=uuid.uuid4(),
            user_id=uuid.uuid4(),
            strengths=['career', 'fitness'],
            struggles=['fashion', 'cooking']
        )
        user2 = UserProfile(
            id=uuid.uuid4(),
            user_id=uuid.uuid4(),
            strengths=['fashion', 'cooking', 'relationships'],
            struggles=['career']
        )

        explanation = generate_match_explanation(user1, user2)

        assert set(explanation['you_help_with']) == {'career'}, "Should identify career as help area"
        assert set(explanation['they_help_with']) == {'fashion', 'cooking'}, "Should identify fashion and cooking"

    def test_no_help_needed(self):
        """Test explanation when no help is needed."""
        user1 = UserProfile(
            id=uuid.uuid4(),
            user_id=uuid.uuid4(),
            strengths=['career'],
            struggles=['fitness']
        )
        user2 = UserProfile(
            id=uuid.uuid4(),
            user_id=uuid.uuid4(),
            strengths=['fashion'],
            struggles=['cooking']
        )

        explanation = generate_match_explanation(user1, user2)

        assert explanation['you_help_with'] == [], "No help areas should be empty"
        assert explanation['they_help_with'] == [], "No help areas should be empty"


class TestRankingMatches:
    """Test ranking multiple potential matches."""

    def test_ranking_order(self):
        """Test that matches are ranked by score."""
        target_user = UserProfile(
            id=uuid.uuid4(),
            user_id=uuid.uuid4(),
            strengths=['career', 'fitness'],
            struggles=['fashion', 'cooking']
        )

        # Perfect match
        candidate1 = UserProfile(
            id=uuid.uuid4(),
            user_id=uuid.uuid4(),
            strengths=['fashion', 'cooking'],
            struggles=['career', 'fitness'],
            communication_style='direct',
            commitment_level='moderate'
        )

        # Partial match
        candidate2 = UserProfile(
            id=uuid.uuid4(),
            user_id=uuid.uuid4(),
            strengths=['fashion'],
            struggles=['career'],
            communication_style='direct',
            commitment_level='casual'
        )

        # Poor match
        candidate3 = UserProfile(
            id=uuid.uuid4(),
            user_id=uuid.uuid4(),
            strengths=['music'],
            struggles=['art'],
            communication_style='motivational',
            commitment_level='intense'
        )

        # Add target user's fields for compatibility scoring
        target_user.communication_style = 'direct'
        target_user.commitment_level = 'moderate'

        matches = rank_potential_matches(target_user, [candidate1, candidate2, candidate3], top_n=3)

        # Verify ranking order (highest score first)
        assert len(matches) == 3
        assert matches[0]['match_score'] > matches[1]['match_score']
        assert matches[1]['match_score'] > matches[2]['match_score']
        assert matches[0]['user_profile'].user_id == candidate1.user_id, "Best match should be first"

    def test_top_n_limit(self):
        """Test that only top N matches are returned."""
        target_user = UserProfile(
            id=uuid.uuid4(),
            user_id=uuid.uuid4(),
            strengths=['career'],
            struggles=['fashion']
        )

        candidates = [
            UserProfile(id=uuid.uuid4(), user_id=uuid.uuid4(), strengths=['fashion'], struggles=['career'])
            for _ in range(10)
        ]

        matches = rank_potential_matches(target_user, candidates, top_n=3)

        assert len(matches) == 3, "Should return only top 3 matches"

    def test_exclude_self(self):
        """Test that user is not matched with themselves."""
        user_id = uuid.uuid4()
        target_user = UserProfile(
            id=uuid.uuid4(),
            user_id=user_id,
            strengths=['career'],
            struggles=['fashion']
        )

        # Include user themselves in candidates
        candidates = [
            target_user,  # Should be excluded
            UserProfile(id=uuid.uuid4(), user_id=uuid.uuid4(), strengths=['fashion'], struggles=['career'])
        ]

        matches = rank_potential_matches(target_user, candidates, top_n=5)

        assert len(matches) == 1, "Should exclude self from matches"
        assert matches[0]['user_profile'].user_id != user_id, "Should not match with self"
