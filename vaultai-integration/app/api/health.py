"""
VaultAI Integration Layer - Health Check Router
Provides health check and status endpoints.
"""

from fastapi import APIRouter
from app.schemas.base import HealthCheckResponse
from app.core.config import settings
from app.llm.router import llm_router

router = APIRouter(prefix="/health", tags=["Health"])


@router.get("/", response_model=HealthCheckResponse)
async def health_check():
    """
    Health check endpoint.

    Returns service status and available providers.
    """
    return HealthCheckResponse(
        status="healthy",
        version="1.0.0",
        providers_available=list(llm_router.providers.keys()),
    )


@router.get("/providers")
async def list_providers():
    """
    List all configured LLM providers.

    Returns:
        Dictionary of provider names and their status.
    """
    providers_status = {}

    for provider_name, client in llm_router.providers.items():
        providers_status[provider_name] = {
            "configured": True,
            "base_url": client.config.base_url,
            "model": client.config.model,
        }

    return {
        "default_provider": settings.LLM_DEFAULT_PROVIDER,
        "providers": providers_status,
    }
