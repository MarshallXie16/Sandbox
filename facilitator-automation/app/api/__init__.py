"""
FastAPI routers for Facilitator Automation API.
"""

from app.api import health, engagements, buyers, offers, closings

__all__ = ["health", "engagements", "buyers", "offers", "closings"]
