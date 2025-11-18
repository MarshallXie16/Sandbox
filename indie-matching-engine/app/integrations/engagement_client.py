"""
Client for indie-engagement-tracker service.
"""

from typing import Dict, Optional

import httpx

from app.config import get_settings


class EngagementTrackerClient:
    """
    Client for fetching engagement scores from indie-engagement-tracker.

    For now, this is a stub implementation. When engagement tracker is ready,
    it will make HTTP requests to fetch real-time engagement data.
    """

    def __init__(self):
        self.settings = get_settings()
        self.base_url = self.settings.engagement_tracker_url
        self.api_key = self.settings.engagement_tracker_api_key
        self.enabled = self.settings.enable_engagement_integration

    async def get_engagement_score(self, contact_id: int) -> Optional[float]:
        """
        Get engagement score for a contact.

        Args:
            contact_id: Contact ID from CRM

        Returns:
            Engagement score (0-100) or None if unavailable
        """
        if not self.enabled or not self.base_url:
            return None

        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/api/v1/engagement/{contact_id}",
                    headers={"X-API-Key": self.api_key} if self.api_key else {},
                    timeout=5.0,
                )

                if response.status_code == 200:
                    data = response.json()
                    return data.get("score")

                return None

        except Exception as e:
            # Log error but don't fail matching
            print(f"Failed to fetch engagement score for contact {contact_id}: {e}")
            return None

    async def get_engagement_scores_batch(
        self, contact_ids: list[int]
    ) -> Dict[int, float]:
        """
        Get engagement scores for multiple contacts in batch.

        Args:
            contact_ids: List of contact IDs

        Returns:
            Dictionary mapping contact_id -> engagement_score
        """
        if not self.enabled or not self.base_url:
            return {}

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/api/v1/engagement/batch",
                    json={"contact_ids": contact_ids},
                    headers={"X-API-Key": self.api_key} if self.api_key else {},
                    timeout=10.0,
                )

                if response.status_code == 200:
                    data = response.json()
                    return data.get("scores", {})

                return {}

        except Exception as e:
            print(f"Failed to fetch batch engagement scores: {e}")
            return {}
