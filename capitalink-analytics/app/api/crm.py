"""CRM analytics API endpoints."""

from fastapi import APIRouter, Depends

from app.api.dependencies import get_crm_service
from app.core.auth import verify_api_key
from app.schemas.analytics import CrmOverviewResponse
from app.services.crm_analytics import CrmAnalyticsService

router = APIRouter(prefix="/crm", tags=["CRM Analytics"])


@router.get("/overview", response_model=CrmOverviewResponse)
async def get_crm_overview(
    service: CrmAnalyticsService = Depends(get_crm_service),
    _api_key: str = Depends(verify_api_key),
):
    """
    Get CRM overview statistics.

    Returns counts of contacts (sellers/buyers), companies, listings,
    and listing status breakdown.
    """
    return await service.get_basic_counts()
