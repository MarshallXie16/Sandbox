"""
Base scorer interface.
"""

from abc import ABC, abstractmethod
from typing import Dict, List

from app.schemas.buyer import BuyerProfile
from app.schemas.listing import ListingProfile
from app.schemas.match import MatchScore, MatchScoreComponents


class MatchScorer(ABC):
    """
    Abstract base class for match scoring implementations.

    Allows for different scoring strategies (rule-based, ML-based, hybrid, etc.)
    """

    @abstractmethod
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
        pass

    @abstractmethod
    def score_batch(
        self,
        buyers: List[BuyerProfile],
        listings: List[ListingProfile],
    ) -> List[MatchScore]:
        """
        Compute match scores for multiple buyer-listing pairs.

        Args:
            buyers: List of buyer profiles
            listings: List of listing profiles

        Returns:
            List of MatchScore objects for all combinations
        """
        pass
