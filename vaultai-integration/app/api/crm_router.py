"""
VaultAI Integration Layer - CRM Router
API endpoints for CRM and matching AI services.
"""

from fastapi import APIRouter, Depends, HTTPException
from app.schemas.crm import (
    MatchingRequest,
    MatchingResponse,
    EnrichProfileRequest,
    EnrichProfileResponse,
)
from app.services.crm import crm_service
from app.core.auth import get_current_service
from app.core.logging import get_logger

logger = get_logger(__name__)

router = APIRouter(
    prefix="/api/v1/vaultai/crm",
    tags=["CRM"],
)


@router.post("/match", response_model=MatchingResponse)
async def find_matches(
    request: MatchingRequest,
    service_id: str = Depends(get_current_service),
):
    """Find matching partners using AI."""
    try:
        return await crm_service.find_matches(request, service_id)
    except Exception as e:
        logger.error(f"Matching failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/enrich", response_model=EnrichProfileResponse)
async def enrich_profile(
    request: EnrichProfileRequest,
    service_id: str = Depends(get_current_service),
):
    """Enrich entity profile with AI insights."""
    try:
        return await crm_service.enrich_profile(request, service_id)
    except Exception as e:
        logger.error(f"Profile enrichment failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
