"""Exit Ready analytics service."""

from datetime import datetime
from typing import Dict, List, Optional

from app.core.logging import get_logger
from app.repositories.exit_ready_read import ExitReadyReadRepository
from app.schemas.analytics import (
    ExitReadyDurationsResponse,
    ExitReadyPipelineResponse,
    ExitReadyVolumeDataPoint,
    ExitReadyVolumeResponse,
    StageDuration,
)

logger = get_logger(__name__)


class ExitReadyAnalyticsService:
    """Service for Exit Ready analytics calculations."""

    def __init__(self, repository: ExitReadyReadRepository):
        """Initialize service with repository."""
        self.repository = repository

    async def get_pipeline_summary(self) -> ExitReadyPipelineResponse:
        """
        Get Exit Ready pipeline summary with case counts by status.

        Returns:
            Pipeline summary response
        """
        data = await self.repository.get_pipeline_summary()

        return ExitReadyPipelineResponse(
            total_cases=data["total"],
            by_status=data["by_status"],
        )

    async def get_stage_durations(self) -> ExitReadyDurationsResponse:
        """
        Calculate average durations between key stages.

        Returns:
            Stage durations response
        """
        cases = await self.repository.get_cases_with_timestamps()

        if not cases:
            return ExitReadyDurationsResponse(durations=[])

        # Calculate durations for different stages
        stage_calculations = {
            "created_to_intake": ("created_at", "intake_completed_at"),
            "intake_to_docs": ("intake_completed_at", "docs_collecting_started_at"),
            "docs_to_financials": ("docs_collecting_started_at", "financials_ready_at"),
            "financials_to_valuation": ("financials_ready_at", "valuation_completed_at"),
            "valuation_to_report": ("valuation_completed_at", "report_ready_at"),
            "report_to_delivered": ("report_ready_at", "delivered_at"),
            "created_to_delivered": ("created_at", "delivered_at"),
        }

        durations: List[StageDuration] = []

        for stage_name, (start_field, end_field) in stage_calculations.items():
            stage_durations = []

            for case in cases:
                start_time = case.get(start_field)
                end_time = case.get(end_field)

                if start_time and end_time:
                    duration_days = (end_time - start_time).days
                    if duration_days >= 0:  # Sanity check
                        stage_durations.append(duration_days)

            if stage_durations:
                avg = sum(stage_durations) / len(stage_durations)
                sorted_durations = sorted(stage_durations)
                median_idx = len(sorted_durations) // 2
                median = sorted_durations[median_idx]

                durations.append(
                    StageDuration(
                        stage=stage_name,
                        average_days=round(avg, 1),
                        median_days=float(median),
                        min_days=min(stage_durations),
                        max_days=max(stage_durations),
                        sample_size=len(stage_durations),
                    )
                )
            else:
                durations.append(
                    StageDuration(
                        stage=stage_name,
                        average_days=None,
                        median_days=None,
                        min_days=None,
                        max_days=None,
                        sample_size=0,
                    )
                )

        return ExitReadyDurationsResponse(durations=durations)

    async def get_case_volume_over_time(
        self,
        period: str = "month",
        from_date: Optional[datetime] = None,
        to_date: Optional[datetime] = None,
    ) -> ExitReadyVolumeResponse:
        """
        Get case volume over time (monthly or quarterly).

        Args:
            period: "month" or "quarter"
            from_date: Start date (optional)
            to_date: End date (optional)

        Returns:
            Volume response with time series data
        """
        # For now, only support monthly (quarterly can be added later)
        if period not in ["month", "quarter"]:
            period = "month"

        volume_data = await self.repository.get_case_volume_by_month(from_date, to_date)

        data_points = [
            ExitReadyVolumeDataPoint(
                period=item["month"],
                created=item["created"],
                delivered=item["delivered"],
                closed=item["closed"],
            )
            for item in volume_data
        ]

        return ExitReadyVolumeResponse(
            period_type=period,
            data=data_points,
        )

    async def get_exit_to_facilitator_conversion(self) -> Dict[str, int]:
        """
        Get conversion rate from Exit Ready to Facilitator.

        Returns:
            Dictionary with total cases and converted cases
        """
        pipeline = await self.repository.get_pipeline_summary()
        total_cases = pipeline["total"]
        converted_count = await self.repository.count_cases_linked_to_facilitator()

        return {
            "total_exit_ready_cases": total_cases,
            "converted_to_facilitator": converted_count,
            "conversion_rate": (
                round((converted_count / total_cases) * 100, 2) if total_cases > 0 else 0.0
            ),
        }
