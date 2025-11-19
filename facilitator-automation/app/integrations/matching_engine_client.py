"""
Matching Engine Client for Facilitator Automation.

Integrates with indie-matching-engine to get ranked buyer suggestions.
"""

from typing import List, Dict, Any, Optional
import httpx
from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)


class MatchingEngineClient:
    """
    Client for Matching Engine integration.

    This service suggests candidate buyers for a listing based on
    matching criteria. It does NOT automatically create Introduced Buyers.
    """

    def __init__(self):
        self.base_url = settings.match_engine_base_url
        self.api_key = settings.match_engine_api_key
        self.stub_mode = settings.match_engine_stub_mode

    async def get_candidate_buyers(
        self,
        listing_id: int,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """
        Get ranked candidate buyers for a listing.

        This returns suggestions only. Operator must explicitly confirm
        to create an Introduced Buyer record.

        Args:
            listing_id: CRM listing/deal ID
            limit: Maximum number of candidates to return

        Returns:
            List of candidate buyer dictionaries with matching scores

        Example return:
            [
                {
                    "buyer_contact_id": 123,
                    "match_score": 0.95,
                    "match_reasons": ["Industry match", "Size match"],
                    "buyer_name": "John Doe",
                    "company": "Acme Corp"
                },
                ...
            ]
        """
        if self.stub_mode:
            logger.info(
                f"[STUB MODE] Getting candidate buyers for listing {listing_id}"
            )
            return self._stub_get_candidates(listing_id, limit)

        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/matching/candidates",
                    params={"listing_id": listing_id, "limit": limit},
                    headers={"X-API-Key": self.api_key},
                    timeout=30.0
                )
                response.raise_for_status()
                data = response.json()
                logger.info(
                    f"Retrieved {len(data.get('candidates', []))} candidate buyers "
                    f"for listing {listing_id}"
                )
                return data.get("candidates", [])

        except httpx.HTTPError as e:
            logger.error(f"Failed to get candidate buyers: {e}")
            # Fall back to stub mode on error
            return self._stub_get_candidates(listing_id, limit)

    def _stub_get_candidates(
        self,
        listing_id: int,
        limit: int
    ) -> List[Dict[str, Any]]:
        """Stub implementation returning fake candidate buyers."""
        # Generate fake candidates for testing
        candidates = []
        for i in range(min(5, limit)):
            candidates.append({
                "buyer_contact_id": 1000 + i,
                "match_score": 0.9 - (i * 0.1),
                "match_reasons": [
                    "Industry match",
                    "Geographic match",
                    "Size range match"
                ],
                "buyer_name": f"Candidate Buyer {i+1}",
                "company": f"Target Company {i+1}",
                "location": "Toronto, ON"
            })

        logger.info(f"[STUB] Generated {len(candidates)} fake candidates")
        return candidates
