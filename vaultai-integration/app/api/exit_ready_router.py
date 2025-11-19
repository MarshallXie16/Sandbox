"""
VaultAI Integration Layer - Exit Ready Router
API endpoints for Exit Ready AI services.
"""

from fastapi import APIRouter, Depends, HTTPException
from app.schemas.exit_ready import (
    TeaserRequest,
    TeaserResponse,
    ChecklistRequest,
    ChecklistResponse,
    SummaryRequest,
    SummaryResponse,
)
from app.services.exit_ready import exit_ready_service
from app.core.auth import get_current_service
from app.core.logging import get_logger

logger = get_logger(__name__)

router = APIRouter(
    prefix="/api/v1/vaultai/exit-ready",
    tags=["Exit Ready"],
)


@router.post("/teaser", response_model=TeaserResponse)
async def generate_teaser(
    request: TeaserRequest,
    service_id: str = Depends(get_current_service),
):
    """
    Generate investment teaser for a company.

    **Security**: Uses local provider by default for confidential data.

    Args:
        request: Company data for teaser generation.
        service_id: Calling service (from API key).

    Returns:
        Generated investment teaser.
    """
    try:
        return await exit_ready_service.generate_teaser(request, service_id)
    except Exception as e:
        logger.error(f"Teaser generation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/checklist", response_model=ChecklistResponse)
async def generate_checklist(
    request: ChecklistRequest,
    service_id: str = Depends(get_current_service),
):
    """
    Generate exit readiness checklist.

    Provides actionable checklist covering:
    - Financial readiness
    - Legal compliance
    - Operational efficiency
    - Strategic positioning

    Args:
        request: Company data for checklist generation.
        service_id: Calling service.

    Returns:
        Exit readiness checklist.
    """
    try:
        return await exit_ready_service.generate_checklist(request, service_id)
    except Exception as e:
        logger.error(f"Checklist generation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/summary", response_model=SummaryResponse)
async def summarize_data(
    request: SummaryRequest,
    service_id: str = Depends(get_current_service),
):
    """
    Summarize exit readiness data.

    Analyzes provided data and generates:
    - Concise summary
    - Key findings
    - Recommendations

    Args:
        request: Exit readiness data to summarize.
        service_id: Calling service.

    Returns:
        Summary with insights and recommendations.
    """
    try:
        return await exit_ready_service.summarize_data(request, service_id)
    except Exception as e:
        logger.error(f"Summary generation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
