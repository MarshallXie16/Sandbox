"""
Health check endpoint.
"""

from fastapi import APIRouter

from app.schemas.common import HealthResponse
from app.core.config import settings

router = APIRouter()


@router.get("/health", response_model=HealthResponse, tags=["Health"])
async def health_check():
    """
    Health check endpoint.

    Returns basic API status and version information.
    Does not require authentication.
    """
    return HealthResponse(
        status="ok",
        version=settings.PORTAL_VERSION,
        env=settings.PORTAL_ENV,
    )
