"""Exit Ready analytics API endpoints."""

from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, Query

from app.api.dependencies import get_exit_ready_service
from app.core.auth import verify_api_key
from app.schemas.analytics import (
    ExitReadyDurationsResponse,
    ExitReadyPipelineResponse,
    ExitReadyVolumeResponse,
)
from app.services.exit_ready_analytics import ExitReadyAnalyticsService

router = APIRouter(prefix="/exit-ready", tags=["Exit Ready Analytics"])


@router.get("/pipeline", response_model=ExitReadyPipelineResponse)
async def get_exit_ready_pipeline(
    service: ExitReadyAnalyticsService = Depends(get_exit_ready_service),
    _api_key: str = Depends(verify_api_key),
):
    """
    Get Exit Ready pipeline summary with case counts by status.

    Returns total cases and breakdown by status.
    """
    return await service.get_pipeline_summary()


@router.get("/durations", response_model=ExitReadyDurationsResponse)
async def get_exit_ready_durations(
    service: ExitReadyAnalyticsService = Depends(get_exit_ready_service),
    _api_key: str = Depends(verify_api_key),
):
    """
    Get average durations between Exit Ready stages.

    Returns average, median, min, max durations for each stage transition.
    """
    return await service.get_stage_durations()


@router.get("/volume", response_model=ExitReadyVolumeResponse)
async def get_exit_ready_volume(
    period: str = Query(default="month", regex="^(month|quarter)$"),
    from_date: Optional[str] = Query(default=None, description="Start date (YYYY-MM-DD)"),
    to_date: Optional[str] = Query(default=None, description="End date (YYYY-MM-DD)"),
    service: ExitReadyAnalyticsService = Depends(get_exit_ready_service),
    _api_key: str = Depends(verify_api_key),
):
    """
    Get Exit Ready case volume over time.

    Args:
        period: "month" or "quarter"
        from_date: Start date filter (optional)
        to_date: End date filter (optional)

    Returns time series of created/delivered/closed case counts.
    """
    # Parse dates if provided
    from_datetime = datetime.fromisoformat(from_date) if from_date else None
    to_datetime = datetime.fromisoformat(to_date) if to_date else None

    return await service.get_case_volume_over_time(
        period=period,
        from_date=from_datetime,
        to_date=to_datetime,
    )
