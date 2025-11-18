"""
Integration clients for external services.

Exports:
- Engagement tracker clients
- Matching engine clients
"""

from app.integrations.engagement_tracker import (
    get_engagement_tracker_client,
    EngagementTrackerClient,
    StubEngagementTrackerClient,
    HttpEngagementTrackerClient,
)
from app.integrations.matching_engine import (
    get_matching_engine_client,
    MatchingEngineClient,
    StubMatchingEngineClient,
    HttpMatchingEngineClient,
)

__all__ = [
    "get_engagement_tracker_client",
    "EngagementTrackerClient",
    "StubEngagementTrackerClient",
    "HttpEngagementTrackerClient",
    "get_matching_engine_client",
    "MatchingEngineClient",
    "StubMatchingEngineClient",
    "HttpMatchingEngineClient",
]
