"""
Security utilities for Facilitator Automation.
Handles API key authentication and authorization.
"""

from typing import Optional
from fastapi import HTTPException, Security, status
from fastapi.security import APIKeyHeader

from app.core.config import settings

# API key header scheme
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)


async def verify_api_key(api_key: Optional[str] = Security(api_key_header)) -> str:
    """
    Verify API key from request header.

    Args:
        api_key: API key from X-API-Key header

    Returns:
        Validated API key

    Raises:
        HTTPException: If API key is missing or invalid
    """
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API key is required",
            headers={"WWW-Authenticate": "ApiKey"},
        )

    # Get valid API keys from settings
    valid_keys = settings.facilitator_api_keys

    if not valid_keys:
        # If no keys configured, allow in dev mode only
        if settings.is_development():
            return api_key
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="API keys not configured",
        )

    if api_key not in valid_keys:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key",
            headers={"WWW-Authenticate": "ApiKey"},
        )

    return api_key


def is_valid_api_key(api_key: str) -> bool:
    """
    Check if an API key is valid (for non-FastAPI contexts).

    Args:
        api_key: API key to validate

    Returns:
        True if valid, False otherwise
    """
    valid_keys = settings.facilitator_api_keys

    if not valid_keys and settings.is_development():
        return True

    return api_key in valid_keys
