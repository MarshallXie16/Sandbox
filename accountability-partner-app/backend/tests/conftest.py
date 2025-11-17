"""Test configuration and fixtures."""
import pytest
import pytest_asyncio
from typing import AsyncGenerator
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.pool import NullPool

from app.main import app
from app.database import Base, get_db
from app.models.user import User, UserProfile
from app.models.partnership import Partnership
from app.models.goal import Goal
from app.models.checkin import CheckIn
from app.models.task import Task
from app.models.match_queue import MatchQueue
from app.models.report import Report
from app.core.security import get_password_hash
from app.core.auth import create_access_token

# Test database URL (in-memory SQLite for testing)
# Use file-based database to avoid connection isolation issues with :memory:
TEST_DATABASE_URL = "sqlite+aiosqlite:///./test.db"


@pytest_asyncio.fixture(scope="function")
async def async_engine():
    """Create test database engine."""
    # Import all models to register them with Base before creating engine
    from app.models import user, partnership, goal, checkin, task, match_queue, report  # noqa

    engine = create_async_engine(
        TEST_DATABASE_URL,
        echo=False,
        poolclass=NullPool
    )

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield engine

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    await engine.dispose()

    # Clean up test database file
    import os
    if os.path.exists("./test.db"):
        os.remove("./test.db")


@pytest_asyncio.fixture(scope="function")
async def db_session(async_engine) -> AsyncGenerator[AsyncSession, None]:
    """Create a fresh database session for each test."""
    async_session = async_sessionmaker(
        async_engine,
        class_=AsyncSession,
        expire_on_commit=False
    )

    async with async_session() as session:
        yield session
        # Rollback any uncommitted changes
        await session.rollback()


@pytest_asyncio.fixture(scope="function")
async def client(db_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    """Create test client with database override."""
    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac

    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def test_user(db_session: AsyncSession) -> User:
    """Create a test user with profile."""
    user = User(
        email="test@example.com",
        username="testuser",
        full_name="Test User",
        password_hash=get_password_hash("TestPass123")
    )
    db_session.add(user)
    await db_session.flush()

    # Create associated user profile
    user_profile = UserProfile(user_id=user.id)
    db_session.add(user_profile)

    await db_session.commit()
    await db_session.refresh(user)

    return user


@pytest_asyncio.fixture
async def auth_headers(test_user: User) -> dict:
    """Generate auth headers for authenticated requests."""
    token = create_access_token(data={"sub": str(test_user.id)})
    return {"Authorization": f"Bearer {token}"}
