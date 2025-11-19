"""
VaultAI Integration Layer - LLM Schemas
Pydantic models for LLM requests and responses.
"""

from typing import List, Literal, Optional, Dict, Any
from pydantic import BaseModel, Field


class ChatMessage(BaseModel):
    """Single message in a chat conversation."""

    role: Literal["system", "user", "assistant"] = Field(
        ...,
        description="Role of the message sender",
    )
    content: str = Field(
        ...,
        description="Message content",
        min_length=1,
    )


class LLMRequest(BaseModel):
    """Request to LLM for chat completion."""

    messages: List[ChatMessage] = Field(
        ...,
        description="List of chat messages",
        min_length=1,
    )
    model: Optional[str] = Field(
        default=None,
        description="Model to use (overrides provider default)",
    )
    temperature: Optional[float] = Field(
        default=None,
        ge=0.0,
        le=2.0,
        description="Sampling temperature",
    )
    max_tokens: Optional[int] = Field(
        default=None,
        ge=1,
        le=32000,
        description="Maximum tokens to generate",
    )
    top_p: Optional[float] = Field(
        default=None,
        ge=0.0,
        le=1.0,
        description="Nucleus sampling parameter",
    )
    frequency_penalty: Optional[float] = Field(
        default=None,
        ge=-2.0,
        le=2.0,
        description="Frequency penalty",
    )
    presence_penalty: Optional[float] = Field(
        default=None,
        ge=-2.0,
        le=2.0,
        description="Presence penalty",
    )
    stop: Optional[List[str]] = Field(
        default=None,
        description="Stop sequences",
    )
    stream: bool = Field(
        default=False,
        description="Whether to stream responses",
    )


class LLMUsage(BaseModel):
    """Token usage statistics."""

    prompt_tokens: int = Field(
        ...,
        description="Tokens in the prompt",
    )
    completion_tokens: int = Field(
        ...,
        description="Tokens in the completion",
    )
    total_tokens: int = Field(
        ...,
        description="Total tokens used",
    )


class LLMResponse(BaseModel):
    """Response from LLM."""

    content: str = Field(
        ...,
        description="Generated content",
    )
    model: str = Field(
        ...,
        description="Model that generated the response",
    )
    provider: str = Field(
        ...,
        description="Provider used (local, openai_compatible, etc.)",
    )
    usage: Optional[LLMUsage] = Field(
        default=None,
        description="Token usage statistics",
    )
    finish_reason: Optional[str] = Field(
        default=None,
        description="Reason for completion (stop, length, etc.)",
    )
    latency_ms: Optional[float] = Field(
        default=None,
        description="Response latency in milliseconds",
    )


class EmbeddingRequest(BaseModel):
    """Request to generate embeddings."""

    texts: List[str] = Field(
        ...,
        description="Texts to embed",
        min_length=1,
    )
    model: Optional[str] = Field(
        default=None,
        description="Embedding model to use",
    )


class EmbeddingResponse(BaseModel):
    """Response with generated embeddings."""

    embeddings: List[List[float]] = Field(
        ...,
        description="List of embedding vectors",
    )
    model: str = Field(
        ...,
        description="Model used for embeddings",
    )
    dimension: int = Field(
        ...,
        description="Dimension of each embedding vector",
    )
    usage: Optional[LLMUsage] = Field(
        default=None,
        description="Token usage statistics",
    )


class ProviderConfig(BaseModel):
    """Configuration for an LLM provider."""

    provider: str = Field(
        ...,
        description="Provider identifier",
    )
    base_url: str = Field(
        ...,
        description="Base URL for API",
    )
    model: str = Field(
        ...,
        description="Default model",
    )
    api_key: Optional[str] = Field(
        default=None,
        description="API key (if required)",
    )
    timeout: int = Field(
        default=60,
        description="Request timeout in seconds",
    )
    max_retries: int = Field(
        default=3,
        description="Maximum number of retries",
    )
    extra: Dict[str, Any] = Field(
        default_factory=dict,
        description="Provider-specific configuration",
    )
