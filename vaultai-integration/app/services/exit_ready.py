"""
VaultAI Integration Layer - Exit Ready Service
AI services for Exit Ready module (Module 7).
"""

import uuid
from typing import Dict, Any
from datetime import datetime

from app.llm.router import llm_router
from app.schemas.llm import ChatMessage, LLMRequest
from app.schemas.exit_ready import (
    TeaserRequest,
    TeaserResponse,
    ChecklistRequest,
    ChecklistResponse,
    ChecklistItem,
    SummaryRequest,
    SummaryResponse,
)
from app.core.security import detect_pii, redact_pii
from app.core.logging import get_logger
from app.core.database import AsyncSessionLocal
from app.models.llm_log import LLMLog
from sqlalchemy import insert

logger = get_logger(__name__)


class ExitReadyService:
    """
    AI services for Exit Ready module.

    Provides:
    - Investment teaser generation
    - Exit readiness checklist creation
    - Data summarization
    """

    def __init__(self):
        """Initialize Exit Ready service."""
        self.domain = "exit_ready"

    async def generate_teaser(
        self,
        request: TeaserRequest,
        service_id: str = "unknown",
    ) -> TeaserResponse:
        """
        Generate investment teaser for a company.

        Args:
            request: Teaser request with company data.
            service_id: Calling service identifier.

        Returns:
            Generated teaser.
        """
        logger.info(f"Generating teaser for {request.company_name}")

        # Build prompt
        system_prompt = """You are an expert investment banker creating professional investment teasers.

Your teasers should:
- Be concise (200-300 words)
- Highlight key financial metrics
- Emphasize unique selling points
- Maintain professional tone
- Be compelling but factual

DO NOT include:
- Specific deal terms or pricing
- Confidential information
- Exaggerated claims
- Legal or financial advice"""

        # Build user prompt
        company_info = f"""Company: {request.company_name}
Industry: {request.industry}
Description: {request.description}"""

        if request.revenue is not None:
            company_info += f"\nRevenue: ${request.revenue}M"
        if request.ebitda is not None:
            company_info += f"\nEBITDA: ${request.ebitda}M"
        if request.year_founded is not None:
            company_info += f"\nFounded: {request.year_founded}"
        if request.employees is not None:
            company_info += f"\nEmployees: {request.employees}"
        if request.unique_selling_points:
            company_info += "\n\nKey Strengths:\n" + "\n".join(
                f"- {usp}" for usp in request.unique_selling_points
            )
        if request.additional_context:
            company_info += f"\n\nAdditional Context:\n{request.additional_context}"

        user_prompt = f"""Create an investment teaser for the following company:

{company_info}

Generate a professional, compelling teaser that would interest potential buyers or investors."""

        # Create LLM request
        llm_request = LLMRequest(
            messages=[
                ChatMessage(role="system", content=system_prompt),
                ChatMessage(role="user", content=user_prompt),
            ],
            temperature=0.7,
            max_tokens=800,
        )

        # Call LLM
        request_id = str(uuid.uuid4())
        try:
            response = await llm_router.chat(
                request=llm_request,
                task_type="exit_ready_teaser",
            )

            # Detect PII in response
            pii_detected = detect_pii(response.content)

            # Log request (in background)
            await self._log_request(
                request_id=request_id,
                task_type="teaser",
                service_id=service_id,
                messages=llm_request.messages,
                response=response,
                pii_detected=pii_detected,
            )

            # Count words
            word_count = len(response.content.split())

            return TeaserResponse(
                teaser=response.content,
                word_count=word_count,
                pii_detected=pii_detected,
            )

        except Exception as e:
            logger.error(f"Teaser generation failed: {e}")
            # Log error
            await self._log_error(
                request_id=request_id,
                task_type="teaser",
                service_id=service_id,
                messages=llm_request.messages,
                error=str(e),
            )
            raise

    async def generate_checklist(
        self,
        request: ChecklistRequest,
        service_id: str = "unknown",
    ) -> ChecklistResponse:
        """
        Generate exit readiness checklist.

        Args:
            request: Checklist request with company data.
            service_id: Calling service identifier.

        Returns:
            Exit readiness checklist.
        """
        logger.info(f"Generating checklist for {request.company_name}")

        system_prompt = """You are an expert M&A advisor creating exit readiness checklists.

Your checklists should:
- Cover key areas: Financial, Legal, Operational, Strategic
- Prioritize items by importance
- Provide actionable steps
- Be realistic and practical

Respond in JSON format:
{
  "summary": "Overall assessment",
  "items": [
    {"category": "Financial", "item": "Description", "priority": "High|Medium|Low", "estimated_time": "X weeks"}
  ]
}"""

        company_info = f"""Company: {request.company_name}
Industry: {request.industry}"""

        if request.revenue is not None:
            company_info += f"\nRevenue: ${request.revenue}M"
        if request.exit_timeline_months is not None:
            company_info += f"\nExit Timeline: {request.exit_timeline_months} months"
        if request.current_challenges:
            company_info += "\n\nKnown Challenges:\n" + "\n".join(
                f"- {challenge}" for challenge in request.current_challenges
            )

        user_prompt = f"""Create an exit readiness checklist for:

{company_info}

Provide a comprehensive checklist covering all key areas."""

        llm_request = LLMRequest(
            messages=[
                ChatMessage(role="system", content=system_prompt),
                ChatMessage(role="user", content=user_prompt),
            ],
            temperature=0.5,
            max_tokens=1500,
        )

        request_id = str(uuid.uuid4())
        try:
            response = await llm_router.chat(
                request=llm_request,
                task_type="exit_ready_checklist",
            )

            # Parse JSON response
            import json
            try:
                data = json.loads(response.content)
                items = [
                    ChecklistItem(**item)
                    for item in data.get("items", [])
                ]
                summary = data.get("summary", "Exit readiness checklist generated")
            except json.JSONDecodeError:
                # Fallback if LLM doesn't return valid JSON
                logger.warning("LLM response not valid JSON, using fallback")
                items = []
                summary = response.content

            # Log request
            await self._log_request(
                request_id=request_id,
                task_type="checklist",
                service_id=service_id,
                messages=llm_request.messages,
                response=response,
            )

            return ChecklistResponse(
                checklist=items,
                summary=summary,
            )

        except Exception as e:
            logger.error(f"Checklist generation failed: {e}")
            await self._log_error(
                request_id=request_id,
                task_type="checklist",
                service_id=service_id,
                messages=llm_request.messages,
                error=str(e),
            )
            raise

    async def summarize_data(
        self,
        request: SummaryRequest,
        service_id: str = "unknown",
    ) -> SummaryResponse:
        """
        Summarize exit readiness data.

        Args:
            request: Summary request with data.
            service_id: Calling service identifier.

        Returns:
            Summary and insights.
        """
        logger.info(f"Summarizing data for {request.company_name}")

        system_prompt = """You are an expert analyst summarizing exit readiness data.

Provide:
- Clear, concise summary
- Key findings
- Actionable recommendations

Respond in JSON format:
{
  "summary": "Overall summary",
  "key_findings": ["Finding 1", "Finding 2"],
  "recommendations": ["Recommendation 1", "Recommendation 2"]
}"""

        data_str = str(request.data)
        focus_str = ""
        if request.focus_areas:
            focus_str = "\n\nFocus Areas:\n" + "\n".join(
                f"- {area}" for area in request.focus_areas
            )

        user_prompt = f"""Summarize the following exit readiness data for {request.company_name}:

{data_str}{focus_str}"""

        llm_request = LLMRequest(
            messages=[
                ChatMessage(role="system", content=system_prompt),
                ChatMessage(role="user", content=user_prompt),
            ],
            temperature=0.5,
            max_tokens=1000,
        )

        request_id = str(uuid.uuid4())
        try:
            response = await llm_router.chat(
                request=llm_request,
                task_type="exit_ready_summary",
            )

            # Parse JSON
            import json
            try:
                data = json.loads(response.content)
                summary = data.get("summary", response.content)
                key_findings = data.get("key_findings", [])
                recommendations = data.get("recommendations", [])
            except json.JSONDecodeError:
                summary = response.content
                key_findings = []
                recommendations = []

            await self._log_request(
                request_id=request_id,
                task_type="summary",
                service_id=service_id,
                messages=llm_request.messages,
                response=response,
            )

            return SummaryResponse(
                summary=summary,
                key_findings=key_findings,
                recommendations=recommendations,
            )

        except Exception as e:
            logger.error(f"Summary generation failed: {e}")
            await self._log_error(
                request_id=request_id,
                task_type="summary",
                service_id=service_id,
                messages=llm_request.messages,
                error=str(e),
            )
            raise

    async def _log_request(
        self,
        request_id: str,
        task_type: str,
        service_id: str,
        messages: list,
        response: Any,
        pii_detected: Dict[str, int] = None,
    ) -> None:
        """Log LLM request to database."""
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
                    pii_detected=pii_detected,
                    created_at=datetime.utcnow(),
                )
                db.add(log)
                await db.commit()
        except Exception as e:
            logger.error(f"Failed to log request: {e}")

    async def _log_error(
        self,
        request_id: str,
        task_type: str,
        service_id: str,
        messages: list,
        error: str,
    ) -> None:
        """Log failed LLM request."""
        try:
            async with AsyncSessionLocal() as db:
                log = LLMLog(
                    request_id=request_id,
                    domain=self.domain,
                    task_type=task_type,
                    service_identifier=service_id,
                    provider="unknown",
                    model="unknown",
                    messages=[msg.model_dump() for msg in messages],
                    status="error",
                    error_message=error,
                    created_at=datetime.utcnow(),
                )
                db.add(log)
                await db.commit()
        except Exception as e:
            logger.error(f"Failed to log error: {e}")


# Global service instance
exit_ready_service = ExitReadyService()
