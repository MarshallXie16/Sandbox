"""Dashboard routes."""

from datetime import datetime

from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from app.api.dependencies import (
    get_crm_service,
    get_exit_ready_service,
    get_facilitator_service,
)
from app.services.crm_analytics import CrmAnalyticsService
from app.services.exit_ready_analytics import ExitReadyAnalyticsService
from app.services.facilitator_analytics import FacilitatorAnalyticsService

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])
templates = Jinja2Templates(directory="app/ui/templates")


@router.get("", response_class=HTMLResponse)
@router.get("/", response_class=HTMLResponse)
async def dashboard_home(
    request: Request,
    crm_service: CrmAnalyticsService = Depends(get_crm_service),
    exit_ready_service: ExitReadyAnalyticsService = Depends(get_exit_ready_service),
    facilitator_service: FacilitatorAnalyticsService = Depends(get_facilitator_service),
):
    """Main dashboard page."""
    # Get all summary data
    crm_data = await crm_service.get_basic_counts()
    exit_ready_data = await exit_ready_service.get_pipeline_summary()
    facilitator_data = await facilitator_service.get_engagement_status_summary()
    revenue_data = await facilitator_service.get_revenue_summary()

    return templates.TemplateResponse(
        "dashboard.html",
        {
            "request": request,
            "crm": crm_data,
            "exit_ready": exit_ready_data,
            "facilitator": facilitator_data,
            "revenue": revenue_data,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        },
    )


@router.get("/exit-ready", response_class=HTMLResponse)
async def dashboard_exit_ready(
    request: Request,
    service: ExitReadyAnalyticsService = Depends(get_exit_ready_service),
):
    """Exit Ready detailed analytics page."""
    pipeline_data = await service.get_pipeline_summary()
    durations_data = await service.get_stage_durations()
    volume_data = await service.get_case_volume_over_time()

    return templates.TemplateResponse(
        "exit_ready.html",
        {
            "request": request,
            "pipeline": pipeline_data,
            "durations": durations_data,
            "volume": volume_data,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        },
    )


@router.get("/facilitator", response_class=HTMLResponse)
async def dashboard_facilitator(
    request: Request,
    service: FacilitatorAnalyticsService = Depends(get_facilitator_service),
):
    """Facilitator detailed analytics page."""
    engagements_data = await service.get_engagement_status_summary()
    revenue_data = await service.get_revenue_summary()
    funnel_data = await service.get_buyer_intro_funnel()

    return templates.TemplateResponse(
        "facilitator.html",
        {
            "request": request,
            "engagements": engagements_data,
            "revenue": revenue_data,
            "funnel": funnel_data,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        },
    )
