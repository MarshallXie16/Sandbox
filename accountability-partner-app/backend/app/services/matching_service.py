"""Matching algorithm service for calculating user compatibility."""
from typing import List, Dict, Set
from app.models.user import UserProfile


def calculate_complementarity_score(user1: UserProfile, user2: UserProfile) -> float:
    """
    Calculate how well users' strengths and struggles complement each other.

    This is the core of the matching algorithm. Users are a good match when:
    - User1's struggles align with User2's strengths
    - User2's struggles align with User1's strengths

    Args:
        user1: First user's profile
        user2: Second user's profile

    Returns:
        Float between 0.0 (no complementarity) and 1.0 (perfect complementarity)

    Examples:
        >>> user1 = UserProfile(strengths=['career', 'fitness'], struggles=['fashion', 'cooking'])
        >>> user2 = UserProfile(strengths=['fashion', 'cooking'], struggles=['career', 'fitness'])
        >>> calculate_complementarity_score(user1, user2)
        1.0  # Perfect match

        >>> user3 = UserProfile(strengths=['music'], struggles=['art'])
        >>> calculate_complementarity_score(user1, user3)
        0.0  # No overlap
    """
    # Handle empty lists
    if not user1.struggles and not user2.struggles:
        return 0.0

    user1_strengths = set(user1.strengths or [])
    user1_struggles = set(user1.struggles or [])
    user2_strengths = set(user2.strengths or [])
    user2_struggles = set(user2.struggles or [])

    # How many of user1's struggles can user2 help with?
    user1_helped = len(user1_struggles & user2_strengths)

    # How many of user2's struggles can user1 help with?
    user2_helped = len(user2_struggles & user1_strengths)

    # Total possible help opportunities
    total_struggles = len(user1_struggles) + len(user2_struggles)

    if total_struggles == 0:
        return 0.0

    # Score is the percentage of struggles that can be addressed
    complementarity = (user1_helped + user2_helped) / total_struggles

    return min(complementarity, 1.0)  # Cap at 1.0


def calculate_compatibility_score(user1: UserProfile, user2: UserProfile) -> float:
    """
    Calculate personality and preference compatibility.

    Users are more compatible when they have:
    - Same or complementary communication styles
    - Similar commitment levels
    - Matching check-in preferences

    Args:
        user1: First user's profile
        user2: Second user's profile

    Returns:
        Float between 0.0 (incompatible) and 1.0 (highly compatible)
    """
    compatibility_points = 0.0
    max_points = 3.0

    # Communication style compatibility
    if user1.communication_style and user2.communication_style:
        if user1.communication_style == user2.communication_style:
            compatibility_points += 1.0
        # Some styles are complementary
        elif (user1.communication_style == 'direct' and user2.communication_style == 'supportive') or \
             (user1.communication_style == 'supportive' and user2.communication_style == 'direct'):
            compatibility_points += 0.7

    # Commitment level compatibility
    if user1.commitment_level and user2.commitment_level:
        commitment_levels = {'casual': 1, 'moderate': 2, 'intense': 3}
        level1 = commitment_levels.get(user1.commitment_level, 2)
        level2 = commitment_levels.get(user2.commitment_level, 2)

        # Prefer matching or adjacent levels
        diff = abs(level1 - level2)
        if diff == 0:
            compatibility_points += 1.0
        elif diff == 1:
            compatibility_points += 0.5

    # Check-in frequency compatibility
    if user1.preferred_check_in_frequency and user2.preferred_check_in_frequency:
        if user1.preferred_check_in_frequency == user2.preferred_check_in_frequency:
            compatibility_points += 1.0
        else:
            compatibility_points += 0.3  # Different is okay, just not ideal

    return compatibility_points / max_points


def calculate_availability_score(user1: UserProfile, user2: UserProfile) -> float:
    """
    Calculate scheduling compatibility based on available days and times.

    Args:
        user1: First user's profile
        user2: Second user's profile

    Returns:
        Float between 0.0 (no overlap) and 1.0 (full overlap)
    """
    # Available days overlap
    days1 = set(user1.available_days_of_week or [])
    days2 = set(user2.available_days_of_week or [])

    if not days1 and not days2:
        return 0.5  # Neutral if no preferences set

    if not days1 or not days2:
        return 0.3  # Slight penalty if one hasn't set preferences

    overlapping_days = days1 & days2
    total_unique_days = days1 | days2

    if not total_unique_days:
        return 0.5

    day_score = len(overlapping_days) / len(total_unique_days)

    # Preferred time compatibility
    time_score = 0.5  # Default neutral
    if user1.preferred_check_in_time and user2.preferred_check_in_time:
        if user1.preferred_check_in_time == user2.preferred_check_in_time:
            time_score = 1.0
        else:
            time_score = 0.3  # Different times are less ideal but manageable

    # Weighted average (days more important than time)
    availability = (day_score * 0.7) + (time_score * 0.3)

    return min(availability, 1.0)


def calculate_match_score(user1: UserProfile, user2: UserProfile) -> float:
    """
    Calculate overall match score between two users.

    This combines three factors:
    - Complementarity (50%): Do their strengths/struggles complement each other?
    - Compatibility (30%): Do their personalities and preferences align?
    - Availability (20%): Can they realistically check in together?

    Args:
        user1: First user's profile
        user2: Second user's profile

    Returns:
        Float between 0.0 (terrible match) and 1.0 (perfect match)

    Note:
        This function is symmetric: calculate_match_score(A, B) == calculate_match_score(B, A)
    """
    complementarity = calculate_complementarity_score(user1, user2)
    compatibility = calculate_compatibility_score(user1, user2)
    availability = calculate_availability_score(user1, user2)

    # Weighted average
    match_score = (
        (complementarity * 0.5) +
        (compatibility * 0.3) +
        (availability * 0.2)
    )

    return round(match_score, 3)  # Round to 3 decimal places


def generate_match_explanation(user1: UserProfile, user2: UserProfile) -> Dict[str, List[str]]:
    """
    Generate human-readable explanation of why users were matched.

    Args:
        user1: First user's profile
        user2: Second user's profile

    Returns:
        Dictionary with 'you_help_with' and 'they_help_with' lists
    """
    user1_strengths = set(user1.strengths or [])
    user1_struggles = set(user1.struggles or [])
    user2_strengths = set(user2.strengths or [])
    user2_struggles = set(user2.struggles or [])

    # What can user1 help user2 with?
    you_help_with = list(user1_strengths & user2_struggles)

    # What can user2 help user1 with?
    they_help_with = list(user2_strengths & user1_struggles)

    return {
        "you_help_with": you_help_with,
        "they_help_with": they_help_with
    }


def rank_potential_matches(
    user: UserProfile,
    candidates: List[UserProfile],
    top_n: int = 5
) -> List[Dict]:
    """
    Rank a list of potential matches for a user.

    Args:
        user: The user to find matches for
        candidates: List of potential match candidates
        top_n: Number of top matches to return (default: 5)

    Returns:
        List of match dictionaries sorted by compatibility score (highest first)
    """
    matches = []

    for candidate in candidates:
        # Don't match user with themselves
        if user.user_id == candidate.user_id:
            continue

        score = calculate_match_score(user, candidate)
        explanation = generate_match_explanation(user, candidate)

        matches.append({
            "user_profile": candidate,
            "match_score": score,
            "explanation": explanation
        })

    # Sort by score (highest first) and return top N
    matches.sort(key=lambda x: x["match_score"], reverse=True)
    return matches[:top_n]
