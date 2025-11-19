"""
VaultAI Integration Layer - Analytics Service
AI services for Analytics module (Module 8).
"""

import uuid
import json
from datetime import datetime

from app.llm.router import llm_router
from app.schemas.llm import ChatMessage, LLMRequest
from app.schemas.analytics import (
    GenerateInsightsRequest,
    GenerateInsightsResponse,
    GenerateReportRequest,
    GenerateReportResponse,
    ExplainMetricRequest,
    ExplainMetricResponse,
)
from app.core.logging import get_logger
from app.core.database import AsyncSessionLocal
from app.models.llm_log import LLMLog

logger = get_logger(__name__)


class AnalyticsService:
    """AI services for Analytics module."""

    def __init__(self):
        self.domain = "analytics"

    async def generate_insights(
        self,
        request: GenerateInsightsRequest,
        service_id: str = "unknown",
    ) -> GenerateInsightsResponse:
        """Generate insights from analytics data."""
        logger.info(f"Generating insights for {request.data_type}")

        system_prompt = """You are a data analyst generating insights from analytics data.

Provide:
- Key insights
- Trends
- Actionable recommendations

Respond in JSON:
{
  "insights": ["Insight 1", "Insight 2"],
  "trends": ["Trend 1", "Trend 2"],
  "recommendations": ["Recommendation 1", "Recommendation 2"],
  "summary": "Overall summary"
}"""

        data_str = json.dumps(request.data, indent=2)
        focus_str = ""
        if request.focus_areas:
            focus_str = "\n\nFocus areas: " + ", ".join(request.focus_areas)

        user_prompt = f"""Analyze this {request.data_type} data:

{data_str}

Time period: {request.time_period or 'Not specified'}{focus_str}

Generate insights."""

        llm_request = LLMRequest(
            messages=[
                ChatMessage(role="system", content=system_prompt),
                ChatMessage(role="user", content=user_prompt),
            ],
            temperature=0.5,
            max_tokens=1500,
        )

        request_id = str(uuid.uuid4())
        response = await llm_router.chat(
            request=llm_request,
            task_type="analytics_insights",
        )

        try:
            data = json.loads(response.content)
            insights = data.get("insights", [])
            trends = data.get("trends", [])
            recommendations = data.get("recommendations", [])
            summary = data.get("summary", "")
        except json.JSONDecodeError:
            insights = []
            trends = []
            recommendations = []
            summary = response.content

        await self._log_request(request_id, "insights", service_id, llm_request.messages, response)

        return GenerateInsightsResponse(
            insights=insights,
            trends=trends,
            recommendations=recommendations,
            summary=summary,
        )

    async def generate_report(
        self,
        request: GenerateReportRequest,
        service_id: str = "unknown",
    ) -> GenerateReportResponse:
        """Generate analytics report."""
        logger.info(f"Generating {request.report_type} report")

        system_prompt = f"""You are an analyst creating a {request.report_type} analytics report.

Format: {request.format}

The report should be:
- Well-structured
- Data-driven
- Actionable"""

        data_str = json.dumps(request.data, indent=2)
        sections_str = ""
        if request.sections:
            sections_str = "\n\nInclude these sections: " + ", ".join(request.sections)

        user_prompt = f"""Create a {request.report_type} report from this data:

{data_str}{sections_str}"""

        llm_request = LLMRequest(
            messages=[
                ChatMessage(role="system", content=system_prompt),
                ChatMessage(role="user", content=user_prompt),
            ],
            temperature=0.5,
            max_tokens=2500,
        )

        request_id = str(uuid.uuid4())
        response = await llm_router.chat(
            request=llm_request,
            task_type="analytics_report",
        )

        word_count = len(response.content.split())

        await self._log_request(request_id, "report", service_id, llm_request.messages, response)

        return GenerateReportResponse(
            report=response.content,
            format=request.format or "markdown",
            word_count=word_count,
        )

    async def explain_metric(
        self,
        request: ExplainMetricRequest,
        service_id: str = "unknown",
    ) -> ExplainMetricResponse:
        """Explain a metric or trend."""
        logger.info(f"Explaining metric: {request.metric_name}")

        system_prompt = """You are an analyst explaining metrics in plain language.

Provide:
- Clear explanation
- Interpretation
- Contributing factors
- Suggestions for improvement

Respond in JSON:
{
  "explanation": "Plain-language explanation",
  "interpretation": "What it means",
  "factors": ["Factor 1", "Factor 2"],
  "suggestions": ["Suggestion 1", "Suggestion 2"]
}"""

        historical_str = ""
        if request.historical_values:
            historical_str = f"\n\nHistorical values: {request.historical_values}"

        context_str = ""
        if request.context:
            context_str = f"\n\nContext: {json.dumps(request.context, indent=2)}"

        user_prompt = f"""Explain this metric:

Metric: {request.metric_name}
Current value: {request.current_value}{historical_str}{context_str}"""

        llm_request = LLMRequest(
            messages=[
                ChatMessage(role="system", content=system_prompt),
                ChatMessage(role="user", content=user_prompt),
            ],
            temperature=0.5,
            max_tokens=1000,
        )

        request_id = str(uuid.uuid4())
        response = await llm_router.chat(
            request=llm_request,
            task_type="analytics_explain",
        )

        try:
            data = json.loads(response.content)
            explanation = data.get("explanation", "")
            interpretation = data.get("interpretation", "")
            factors = data.get("factors", [])
            suggestions = data.get("suggestions", [])
        except json.JSONDecodeError:
            explanation = response.content
            interpretation = ""
            factors = []
            suggestions = []

        await self._log_request(request_id, "explain", service_id, llm_request.messages, response)

        return ExplainMetricResponse(
            explanation=explanation,
            interpretation=interpretation,
            factors=factors,
            suggestions=suggestions,
        )

    async def _log_request(self, request_id, task_type, service_id, messages, response):
        """Log request."""
        try:
            async with AsyncSessionLocal() as db:
                log = LLMLog(
                    request_id=request_id,
                    domain=self.domain,
                    task_type=task_type,
                    service_identifier=service_id,
                    provider=response.provider,
                    model=response.model,
                    messages=[msg.model_dump() for msg in messages],
                    response_content=response.content,
                    finish_reason=response.finish_reason,
                    prompt_tokens=response.usage.prompt_tokens if response.usage else None,
                    completion_tokens=response.usage.completion_tokens if response.usage else None,
                    total_tokens=response.usage.total_tokens if response.usage else None,
                    latency_ms=response.latency_ms,
                    status="success",
                    created_at=datetime.utcnow(),
                )
                db.add(log)
                await db.commit()
        except Exception as e:
            logger.error(f"Failed to log request: {e}")


analytics_service = AnalyticsService()
