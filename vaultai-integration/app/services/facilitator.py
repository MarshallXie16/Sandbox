"""
VaultAI Integration Layer - Facilitator Service
AI services for Facilitator module (Module 9).
"""

import uuid
from datetime import datetime

from app.llm.router import llm_router
from app.schemas.llm import ChatMessage, LLMRequest
from app.schemas.facilitator import (
    DraftMessageRequest,
    DraftMessageResponse,
    SummarizeNegotiationRequest,
    SummarizeNegotiationResponse,
)
from app.core.security import detect_pii
from app.core.logging import get_logger
from app.core.database import AsyncSessionLocal
from app.models.llm_log import LLMLog

logger = get_logger(__name__)


class FacilitatorService:
    """AI services for Facilitator module."""

    def __init__(self):
        self.domain = "facilitator"

    async def draft_message(
        self,
        request: DraftMessageRequest,
        service_id: str = "unknown",
    ) -> DraftMessageResponse:
        """Draft facilitation message."""
        logger.info(f"Drafting {request.message_type} message")

        system_prompt = f"""You are a professional deal facilitator drafting a {request.message_type} message.

Tone: {request.tone}
Recipient: {request.recipient_role}

Your message should:
- Be clear and professional
- Build trust and rapport
- Avoid regulatory/legal advice
- Focus on facilitation, not negotiation"""

        key_points_str = "\n".join(f"- {point}" for point in request.key_points)

        user_prompt = f"""Context: {request.context}

Key points to cover:
{key_points_str}

Draft the message."""

        llm_request = LLMRequest(
            messages=[
                ChatMessage(role="system", content=system_prompt),
                ChatMessage(role="user", content=user_prompt),
            ],
            temperature=0.7,
            max_tokens=600,
        )

        request_id = str(uuid.uuid4())
        response = await llm_router.chat(
            request=llm_request,
            task_type="facilitator_draft_message",
        )

        pii_detected = detect_pii(response.content)
        word_count = len(response.content.split())

        # Log to database (simplified)
        await self._log_request(request_id, "draft_message", service_id, llm_request.messages, response, pii_detected)

        return DraftMessageResponse(
            message=response.content,
            word_count=word_count,
            pii_detected=pii_detected,
        )

    async def summarize_negotiation(
        self,
        request: SummarizeNegotiationRequest,
        service_id: str = "unknown",
    ) -> SummarizeNegotiationResponse:
        """Summarize negotiation progress."""
        logger.info(f"Summarizing negotiation for deal {request.deal_id}")

        system_prompt = """You are a deal facilitator summarizing negotiation progress.

Provide:
- Concise summary
- Key discussion points
- Action items
- Overall sentiment

Respond in JSON:
{
  "summary": "Overall summary",
  "key_points": ["Point 1", "Point 2"],
  "action_items": ["Action 1", "Action 2"],
  "sentiment": "positive|neutral|negative"
}"""

        conversation_str = "\n".join(
            f"{msg['role']}: {msg['content']}"
            for msg in request.conversation_history
        )

        user_prompt = f"""Summarize this negotiation:

{conversation_str}

{f'Focus on: {request.focus}' if request.focus else ''}"""

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
            task_type="facilitator_summarize",
        )

        # Parse JSON
        import json
        try:
            data = json.loads(response.content)
            summary = data.get("summary", response.content)
            key_points = data.get("key_points", [])
            action_items = data.get("action_items", [])
            sentiment = data.get("sentiment")
        except json.JSONDecodeError:
            summary = response.content
            key_points = []
            action_items = []
            sentiment = None

        await self._log_request(request_id, "summarize", service_id, llm_request.messages, response)

        return SummarizeNegotiationResponse(
            summary=summary,
            key_points=key_points,
            action_items=action_items,
            sentiment=sentiment,
        )

    async def _log_request(self, request_id, task_type, service_id, messages, response, pii_detected=None):
        """Log request to database."""
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


facilitator_service = FacilitatorService()
