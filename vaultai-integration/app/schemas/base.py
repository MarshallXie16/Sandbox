"""
VaultAI Integration Layer - Base Schemas
Common Pydantic models used across all services.
"""

from typing import Optional
from pydantic import BaseModel, Field


class HealthCheckResponse(BaseModel):
    """Health check response."""

    status: str = Field(
        ...,
        description="Service status",
    )
    version: str = Field(
        ...,
        description="Service version",
    )
    providers_available: list[str] = Field(
        ...,
        description="List of available LLM providers",
    )


class ErrorResponse(BaseModel):
    """Error response."""

    error: str = Field(
        ...,
        description="Error type",
    )
    message: str = Field(
        ...,
        description="Error message",
    )
    detail: Optional[str] = Field(
        default=None,
        description="Additional error details",
    )


class SuccessResponse(BaseModel):
    """Generic success response."""

    success: bool = Field(
        default=True,
        description="Whether operation succeeded",
    )
    message: str = Field(
        ...,
        description="Success message",
    )
