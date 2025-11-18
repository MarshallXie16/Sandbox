"""
Integration client for Indie Matching Engine.

This is currently a stub/placeholder implementation.
Future: Will call indie-matching-engine HTTP API for ML-based recommendations.
"""

from typing import Optional, Protocol

from app.core.logging import get_logger

logger = get_logger(__name__)


class MatchingEngineClient(Protocol):
    """
    Protocol for matching engine integration.

    This defines the interface for any matching engine implementation.
    """

    async def get_recommendations(
        self, contact_id: int, limit: int = 10
    ) -> list[dict]:
        """Get recommended listings for a buyer contact."""
        ...

    async def calculate_match_score(
        self, contact_id: int, listing_id: int
    ) -> float:
        """Calculate match score between a buyer and a listing."""
        ...


class StubMatchingEngineClient:
    """
    Stub implementation of matching engine.

    Returns placeholder data. Replace with real HTTP client when
    indie-matching-engine is available.
    """

    async def get_recommendations(
        self, contact_id: int, limit: int = 10
    ) -> list[dict]:
        """
        Get recommended listings (stub).

        Args:
            contact_id: Contact ID
            limit: Maximum recommendations

        Returns:
            List of recommendation dictionaries (empty for stub)
        """
        logger.debug(
            f"Stub: Getting recommendations for contact {contact_id}, limit={limit}"
        )
        # Return empty - actual recommendation logic is in RecommendationService
        return []

    async def calculate_match_score(
        self, contact_id: int, listing_id: int
    ) -> float:
        """
        Calculate match score (stub).

        Args:
            contact_id: Contact ID
            listing_id: Listing ID

        Returns:
            Match score (50.0 as default)
        """
        logger.debug(
            f"Stub: Calculating match score: contact={contact_id}, listing={listing_id}"
        )
        return 50.0


class HttpMatchingEngineClient:
    """
    HTTP-based matching engine client.

    Future implementation for calling indie-matching-engine API.
    """

    def __init__(self, base_url: str, api_key: str):
        self.base_url = base_url
        self.api_key = api_key
        logger.info(f"Initialized HTTP matching engine client: {base_url}")

    async def get_recommendations(
        self, contact_id: int, limit: int = 10
    ) -> list[dict]:
        """
        Get recommendations via HTTP API.

        Args:
            contact_id: Contact ID
            limit: Max recommendations

        Returns:
            List of recommendations
        """
        # TODO: Implement HTTP call to matching engine API
        # Example:
        # async with httpx.AsyncClient() as client:
        #     response = await client.post(
        #         f"{self.base_url}/api/v1/recommendations",
        #         headers={"X-API-Key": self.api_key},
        #         json={"contact_id": contact_id, "limit": limit}
        #     )
        #     return response.json()["recommendations"]

        logger.warning("HTTP matching engine not yet implemented, using stub")
        return []

    async def calculate_match_score(
        self, contact_id: int, listing_id: int
    ) -> float:
        """
        Calculate match score via HTTP API.

        Args:
            contact_id: Contact ID
            listing_id: Listing ID

        Returns:
            Match score
        """
        # TODO: Implement HTTP call
        logger.warning("HTTP matching engine not yet implemented, using stub")
        return 50.0


def get_matching_engine_client(
    base_url: Optional[str] = None, api_key: Optional[str] = None
) -> MatchingEngineClient:
    """
    Factory function to get matching engine client.

    Returns HTTP client if base_url is provided, otherwise returns stub.

    Args:
        base_url: Optional base URL for HTTP client
        api_key: Optional API key for HTTP client

    Returns:
        MatchingEngineClient implementation
    """
    if base_url and api_key:
        logger.info("Using HTTP matching engine client")
        return HttpMatchingEngineClient(base_url, api_key)
    else:
        logger.info("Using stub matching engine client")
        return StubMatchingEngineClient()
