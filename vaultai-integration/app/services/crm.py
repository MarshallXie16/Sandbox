"""
VaultAI Integration Layer - CRM Service
AI services for CRM and matching.
"""

import uuid
import json
from datetime import datetime

from app.llm.router import llm_router
from app.schemas.llm import ChatMessage, LLMRequest
from app.schemas.crm import (
    MatchingRequest,
    MatchingResponse,
    MatchResult,
    EnrichProfileRequest,
    EnrichProfileResponse,
)
from app.core.logging import get_logger
from app.core.database import AsyncSessionLocal
from app.models.llm_log import LLMLog

logger = get_logger(__name__)


class CRMService:
    """AI services for CRM and matching."""

    def __init__(self):
        self.domain = "crm"

    async def find_matches(
        self,
        request: MatchingRequest,
        service_id: str = "unknown",
    ) -> MatchingResponse:
        """Find matching partners using AI."""
        logger.info(f"Finding matches for {request.entity_type}")

        system_prompt = """You are an expert matchmaker for M&A transactions.

Analyze the entity and candidates to find the best matches.

Respond in JSON:
{
  "matches": [
    {
      "entity_id": "id",
      "score": 0.85,
      "reasoning": "Why this is a good match",
      "strengths": ["Strength 1", "Strength 2"],
      "concerns": ["Concern 1"]
    }
  ]
}"""

        candidates_str = json.dumps(request.candidate_pool, indent=2)
        entity_str = json.dumps(request.entity_data, indent=2)

        user_prompt = f"""Entity to match:
{entity_str}

Candidates:
{candidates_str}

Find and rank the top matches."""

        llm_request = LLMRequest(
            messages=[
                ChatMessage(role="system", content=system_prompt),
                ChatMessage(role="user", content=user_prompt),
            ],
            temperature=0.3,
            max_tokens=2000,
        )

        request_id = str(uuid.uuid4())
        response = await llm_router.chat(
            request=llm_request,
            task_type="crm_matching",
        )

        # Parse response
        try:
            data = json.loads(response.content)
            matches = [MatchResult(**m) for m in data.get("matches", [])]
        except (json.JSONDecodeError, Exception) as e:
            logger.warning(f"Failed to parse matches: {e}")
            matches = []

        await self._log_request(request_id, "matching", service_id, llm_request.messages, response)

        return MatchingResponse(
            matches=matches,
            total_evaluated=len(request.candidate_pool),
        )

    async def enrich_profile(
        self,
        request: EnrichProfileRequest,
        service_id: str = "unknown",
    ) -> EnrichProfileResponse:
        """Enrich entity profile with AI insights."""
        logger.info(f"Enriching profile for {request.entity_id}")

        system_prompt = f"""You are an analyst enriching entity profiles with insights.

Enrichment type: {request.enrichment_type}

Provide insights and recommendations in JSON:
{{
  "enriched_data": {{}},
  "insights": ["Insight 1", "Insight 2"],
  "recommendations": ["Recommendation 1", "Recommendation 2"]
}}"""

        entity_str = json.dumps(request.entity_data, indent=2)

        user_prompt = f"""Entity data:
{entity_str}

Provide enrichment and insights."""

        llm_request = LLMRequest(
            messages=[
                ChatMessage(role="system", content=system_prompt),
                ChatMessage(role="user", content=user_prompt),
            ],
            temperature=0.5,
            max_tokens=1200,
        )

        request_id = str(uuid.uuid4())
        response = await llm_router.chat(
            request=llm_request,
            task_type="crm_enrich",
        )

        try:
            data = json.loads(response.content)
            enriched_data = data.get("enriched_data", {})
            insights = data.get("insights", [])
            recommendations = data.get("recommendations", [])
        except json.JSONDecodeError:
            enriched_data = {}
            insights = []
            recommendations = []

        await self._log_request(request_id, "enrich", service_id, llm_request.messages, response)

        return EnrichProfileResponse(
            enriched_data=enriched_data,
            insights=insights,
            recommendations=recommendations,
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


crm_service = CRMService()
