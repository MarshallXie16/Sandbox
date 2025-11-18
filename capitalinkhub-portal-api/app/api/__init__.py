"""
FastAPI routers for API v1.

Exports all routers to be mounted in main application.
"""

from app.api import health, members, listings, interests, recommendations, resources

__all__ = [
    "health",
    "members",
    "listings",
    "interests",
    "recommendations",
    "resources",
]
