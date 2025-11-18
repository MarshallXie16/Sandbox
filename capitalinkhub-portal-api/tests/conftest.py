"""
Pytest configuration and fixtures.
"""

import pytest
from typing import AsyncGenerator
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.pool import NullPool

from app.core.database import Base, get_db
from app.core.config import settings
from main import app


@pytest.fixture
def api_key() -> str:
    """Return a valid API key for testing."""
    return settings.PORTAL_API_KEY


@pytest.fixture
def client(api_key: str) -> TestClient:
    """
    Create a test client with API key authentication.
    """
    return TestClient(app)


@pytest.fixture
def auth_headers(api_key: str) -> dict:
    """
    Return headers with valid API key for authenticated requests.
    """
    return {"X-API-Key": api_key}


@pytest.fixture
async def test_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Create a test database session.

    Note: In a real test environment, you'd use a separate test database.
    This is a placeholder showing the structure.
    """
    # In production tests, use a test database URL
    # TEST_DB_DSN = "postgresql+asyncpg://user:pass@localhost:5432/test_db"

    # For now, use the configured database (not recommended for real tests)
    engine = create_async_engine(
        settings.INDIE_DB_DSN,
        poolclass=NullPool,
    )

    # Create tables
    async with engine.begin() as conn:
        # In real tests, you'd create all tables here
        # await conn.run_sync(Base.metadata.create_all)
        pass

    # Create session
    async_session = async_sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )

    async with async_session() as session:
        yield session

    # Cleanup
    # In real tests, you'd drop tables or rollback transactions
    await engine.dispose()
