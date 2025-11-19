"""
VaultAI Integration Layer - Facilitator Schemas
Pydantic models for Facilitator module AI services.
"""

from typing import Optional, List
from pydantic import BaseModel, Field


class DraftMessageRequest(BaseModel):
    """Request to draft facilitation message."""

    context: str = Field(
        ...,
        description="Context of the negotiation/facilitation",
        min_length=10,
    )
    message_type: str = Field(
        ...,
        description="Type of message (introduction, update, clarification, proposal)",
    )
    recipient_role: str = Field(
        ...,
        description="Role of recipient (buyer, seller, broker)",
    )
    key_points: List[str] = Field(
        ...,
        description="Key points to include in message",
        min_length=1,
    )
    tone: Optional[str] = Field(
        default="professional",
        description="Desired tone (professional, friendly, formal)",
    )


class DraftMessageResponse(BaseModel):
    """Response with drafted message."""

    message: str = Field(
        ...,
        description="Drafted message",
    )
    word_count: int = Field(
        ...,
        description="Word count",
    )
    pii_detected: dict = Field(
        default_factory=dict,
        description="Detected PII",
    )


class SummarizeNegotiationRequest(BaseModel):
    """Request to summarize negotiation progress."""

    deal_id: Optional[str] = Field(
        default=None,
        description="Deal identifier",
    )
    conversation_history: List[dict] = Field(
        ...,
        description="List of messages with role and content",
        min_length=1,
    )
    focus: Optional[str] = Field(
        default=None,
        description="Specific aspect to focus on",
    )


class SummarizeNegotiationResponse(BaseModel):
    """Response with negotiation summary."""

    summary: str = Field(
        ...,
        description="Negotiation summary",
    )
    key_points: List[str] = Field(
        default_factory=list,
        description="Key discussion points",
    )
    action_items: List[str] = Field(
        default_factory=list,
        description="Identified action items",
    )
    sentiment: Optional[str] = Field(
        default=None,
        description="Overall sentiment (positive, neutral, negative)",
    )
