"""Health check endpoint."""

from fastapi import APIRouter

from app import __version__
from app.core.config import settings
from app.schemas.analytics import HealthResponse

router = APIRouter()


@router.get("/health", response_model=HealthResponse, tags=["Health"])
async def health_check():
    """
    Health check endpoint.

    Returns service status, version, and environment.
    """
    return HealthResponse(
        status="ok",
        version=__version__,
        env=settings.analytics_env,
    )
