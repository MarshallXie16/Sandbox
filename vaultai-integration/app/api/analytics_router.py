"""
VaultAI Integration Layer - Analytics Router
API endpoints for Analytics AI services.
"""

from fastapi import APIRouter, Depends, HTTPException
from app.schemas.analytics import (
    GenerateInsightsRequest,
    GenerateInsightsResponse,
    GenerateReportRequest,
    GenerateReportResponse,
    ExplainMetricRequest,
    ExplainMetricResponse,
)
from app.services.analytics import analytics_service
from app.core.auth import get_current_service
from app.core.logging import get_logger

logger = get_logger(__name__)

router = APIRouter(
    prefix="/api/v1/vaultai/analytics",
    tags=["Analytics"],
)


@router.post("/insights", response_model=GenerateInsightsResponse)
async def generate_insights(
    request: GenerateInsightsRequest,
    service_id: str = Depends(get_current_service),
):
    """Generate insights from analytics data."""
    try:
        return await analytics_service.generate_insights(request, service_id)
    except Exception as e:
        logger.error(f"Insights generation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/report", response_model=GenerateReportResponse)
async def generate_report(
    request: GenerateReportRequest,
    service_id: str = Depends(get_current_service),
):
    """Generate analytics report."""
    try:
        return await analytics_service.generate_report(request, service_id)
    except Exception as e:
        logger.error(f"Report generation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/explain", response_model=ExplainMetricResponse)
async def explain_metric(
    request: ExplainMetricRequest,
    service_id: str = Depends(get_current_service),
):
    """Explain a metric or trend."""
    try:
        return await analytics_service.explain_metric(request, service_id)
    except Exception as e:
        logger.error(f"Metric explanation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
