"""
VaultAI Integration Layer - Facilitator Router
API endpoints for Facilitator AI services.
"""

from fastapi import APIRouter, Depends, HTTPException
from app.schemas.facilitator import (
    DraftMessageRequest,
    DraftMessageResponse,
    SummarizeNegotiationRequest,
    SummarizeNegotiationResponse,
)
from app.services.facilitator import facilitator_service
from app.core.auth import get_current_service
from app.core.logging import get_logger

logger = get_logger(__name__)

router = APIRouter(
    prefix="/api/v1/vaultai/facilitator",
    tags=["Facilitator"],
)


@router.post("/draft-message", response_model=DraftMessageResponse)
async def draft_message(
    request: DraftMessageRequest,
    service_id: str = Depends(get_current_service),
):
    """Draft facilitation message."""
    try:
        return await facilitator_service.draft_message(request, service_id)
    except Exception as e:
        logger.error(f"Message drafting failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/summarize", response_model=SummarizeNegotiationResponse)
async def summarize_negotiation(
    request: SummarizeNegotiationRequest,
    service_id: str = Depends(get_current_service),
):
    """Summarize negotiation progress."""
    try:
        return await facilitator_service.summarize_negotiation(request, service_id)
    except Exception as e:
        logger.error(f"Negotiation summarization failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
