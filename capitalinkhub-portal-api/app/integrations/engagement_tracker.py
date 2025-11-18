"""
Integration client for Indie Engagement Tracker.

This is currently a stub/placeholder implementation.
Future: Can be switched to HTTP API client or direct DB access.
"""

from typing import Optional, Protocol
from datetime import datetime

from app.core.logging import get_logger

logger = get_logger(__name__)


class EngagementTrackerClient(Protocol):
    """
    Protocol for engagement tracker integration.

    This defines the interface that any engagement tracker implementation must follow.
    """

    async def get_engagement_score(self, contact_id: int) -> int:
        """Get engagement score for a contact (0-100)."""
        ...

    async def get_recent_events(
        self, contact_id: int, days: int = 30, limit: int = 10
    ) -> list[dict]:
        """Get recent engagement events for a contact."""
        ...


class StubEngagementTrackerClient:
    """
    Stub implementation of engagement tracker.

    Returns placeholder data. Replace with real implementation when
    indie-engagement-tracker is available.
    """

    async def get_engagement_score(self, contact_id: int) -> int:
        """
        Get engagement score for a contact.

        Args:
            contact_id: Contact ID

        Returns:
            Engagement score (0-100)
        """
        logger.debug(f"Stub: Getting engagement score for contact {contact_id}")
        # Return a middle-range score as placeholder
        return 50

    async def get_recent_events(
        self, contact_id: int, days: int = 30, limit: int = 10
    ) -> list[dict]:
        """
        Get recent engagement events.

        Args:
            contact_id: Contact ID
            days: Number of days to look back
            limit: Maximum events to return

        Returns:
            List of engagement events (stub data)
        """
        logger.debug(
            f"Stub: Getting recent events for contact {contact_id}, days={days}, limit={limit}"
        )
        # Return empty list - real implementation would fetch from tracker API/DB
        return []


class HttpEngagementTrackerClient:
    """
    HTTP-based engagement tracker client.

    Future implementation for calling indie-engagement-tracker API.
    """

    def __init__(self, base_url: str, api_key: str):
        self.base_url = base_url
        self.api_key = api_key
        logger.info(f"Initialized HTTP engagement tracker client: {base_url}")

    async def get_engagement_score(self, contact_id: int) -> int:
        """
        Get engagement score via HTTP API.

        Args:
            contact_id: Contact ID

        Returns:
            Engagement score
        """
        # TODO: Implement HTTP call to engagement tracker API
        # Example:
        # async with httpx.AsyncClient() as client:
        #     response = await client.get(
        #         f"{self.base_url}/api/v1/contacts/{contact_id}/score",
        #         headers={"X-API-Key": self.api_key}
        #     )
        #     return response.json()["score"]

        logger.warning("HTTP engagement tracker not yet implemented, using stub")
        return 50

    async def get_recent_events(
        self, contact_id: int, days: int = 30, limit: int = 10
    ) -> list[dict]:
        """
        Get recent events via HTTP API.

        Args:
            contact_id: Contact ID
            days: Days to look back
            limit: Max events

        Returns:
            List of events
        """
        # TODO: Implement HTTP call
        logger.warning("HTTP engagement tracker not yet implemented, using stub")
        return []


def get_engagement_tracker_client(
    base_url: Optional[str] = None, api_key: Optional[str] = None
) -> EngagementTrackerClient:
    """
    Factory function to get engagement tracker client.

    Returns HTTP client if base_url is provided, otherwise returns stub.

    Args:
        base_url: Optional base URL for HTTP client
        api_key: Optional API key for HTTP client

    Returns:
        EngagementTrackerClient implementation
    """
    if base_url and api_key:
        logger.info("Using HTTP engagement tracker client")
        return HttpEngagementTrackerClient(base_url, api_key)
    else:
        logger.info("Using stub engagement tracker client")
        return StubEngagementTrackerClient()
