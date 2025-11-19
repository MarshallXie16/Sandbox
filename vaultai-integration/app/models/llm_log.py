"""
VaultAI Integration Layer - LLM Log Model
Tracks all LLM requests and responses for auditing and analysis.
"""

from datetime import datetime
from typing import Optional
from sqlalchemy import String, Text, Integer, Float, DateTime, JSON, Index
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class LLMLog(Base):
    """
    Log of all LLM interactions.

    Stores request/response pairs for:
    - Debugging
    - Cost tracking
    - Performance monitoring
    - Audit trails
    """

    __tablename__ = "llm_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    # Request metadata
    request_id: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        nullable=False,
        index=True,
        comment="Unique request identifier (UUID)",
    )

    domain: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
        index=True,
        comment="Domain/module that made the request",
    )

    task_type: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
        index=True,
        comment="Type of task performed",
    )

    service_identifier: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True,
        index=True,
        comment="Service that made the request (from API key)",
    )

    # LLM provider info
    provider: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        index=True,
        comment="LLM provider used (local, openai_compatible, azure)",
    )

    model: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        comment="Model name",
    )

    # Request details
    messages: Mapped[dict] = mapped_column(
        JSON,
        nullable=False,
        comment="Request messages (array of {role, content})",
    )

    request_params: Mapped[Optional[dict]] = mapped_column(
        JSON,
        nullable=True,
        comment="Additional request parameters (temperature, max_tokens, etc.)",
    )

    # Response details
    response_content: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="Generated response content",
    )

    finish_reason: Mapped[Optional[str]] = mapped_column(
        String(50),
        nullable=True,
        comment="Completion finish reason (stop, length, etc.)",
    )

    # Usage tracking
    prompt_tokens: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True,
        comment="Tokens in prompt",
    )

    completion_tokens: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True,
        comment="Tokens in completion",
    )

    total_tokens: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True,
        index=True,
        comment="Total tokens used",
    )

    # Performance metrics
    latency_ms: Mapped[Optional[float]] = mapped_column(
        Float,
        nullable=True,
        comment="Response latency in milliseconds",
    )

    # Status
    status: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="success",
        index=True,
        comment="Request status (success, error, timeout)",
    )

    error_message: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="Error message if request failed",
    )

    # PII detection
    pii_detected: Mapped[Optional[dict]] = mapped_column(
        JSON,
        nullable=True,
        comment="Detected PII types and counts",
    )

    # Timestamp
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
        index=True,
    )

    def __repr__(self) -> str:
        return (
            f"<LLMLog(id={self.id}, request_id='{self.request_id}', "
            f"provider='{self.provider}', status='{self.status}')>"
        )


# Composite indexes for common queries
Index(
    "idx_llm_logs_domain_task_created",
    LLMLog.domain,
    LLMLog.task_type,
    LLMLog.created_at,
)

Index(
    "idx_llm_logs_provider_status_created",
    LLMLog.provider,
    LLMLog.status,
    LLMLog.created_at,
)
