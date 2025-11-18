"""
API dependencies including authentication.
"""

from typing import AsyncGenerator

from fastapi import Depends, HTTPException, Security, status
from fastapi.security import APIKeyHeader
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.core.matching_engine import MatchingEngine
from app.database import get_db

# API Key authentication
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=True)


async def verify_api_key(api_key: str = Security(api_key_header)) -> str:
    """
    Verify API key from request header.

    Args:
        api_key: API key from X-API-Key header

    Returns:
        Validated API key

    Raises:
        HTTPException: If API key is invalid
    """
    settings = get_settings()

    if api_key != settings.api_key:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid API key",
        )

    return api_key


async def get_matching_engine(
    db: AsyncSession = Depends(get_db),
) -> MatchingEngine:
    """
    Get MatchingEngine instance with database session.

    Args:
        db: Database session dependency

    Returns:
        MatchingEngine instance
    """
    return MatchingEngine(db=db)
