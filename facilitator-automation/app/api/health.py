"""
Health check endpoint.
"""

from fastapi import APIRouter
from datetime import datetime
from app.core.config import settings
from app import __version__

router = APIRouter(tags=["health"])


@router.get("/health")
async def health_check():
    """
    Health check endpoint.

    Returns service status, version, and environment information.
    """
    return {
        "status": "ok",
        "service": "facilitator-automation",
        "version": __version__,
        "environment": settings.facilitator_env,
        "timestamp": datetime.now().isoformat()
    }
