"""
VaultAI Integration Layer - Authentication & Authorization
Simple API key-based authentication for internal services.
"""

from typing import Optional
from fastapi import HTTPException, Security, status
from fastapi.security import APIKeyHeader

from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)

# API Key header scheme
api_key_header = APIKeyHeader(name="X-VaultAI-API-Key", auto_error=False)


async def verify_api_key(api_key: Optional[str] = Security(api_key_header)) -> str:
    """
    Verify that the provided API key is valid.

    Args:
        api_key: API key from request header.

    Returns:
        The validated API key.

    Raises:
        HTTPException: If API key is missing or invalid.
    """
    if not api_key:
        logger.warning("API request without API key")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing API key. Provide X-VaultAI-API-Key header.",
        )

    valid_keys = settings.api_keys_list

    if not valid_keys:
        logger.error("No API keys configured in settings")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="API authentication not configured",
        )

    if api_key not in valid_keys:
        logger.warning(f"Invalid API key attempt: {api_key[:10]}...")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key",
        )

    logger.debug(f"API key validated: {api_key[:10]}...")
    return api_key


async def get_current_service(api_key: str = Security(verify_api_key)) -> str:
    """
    Get the name of the calling service based on API key.

    In a more sophisticated system, you could map API keys to service names
    or extract service identity from JWT tokens.

    Args:
        api_key: Validated API key.

    Returns:
        Service identifier (for logging/tracking purposes).
    """
    # Simple implementation: use API key prefix as service identifier
    # In production, use a proper mapping or JWT claims
    return f"service_{api_key[:8]}"
