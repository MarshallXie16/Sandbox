"""
Database configuration and session management.
"""
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    AsyncEngine,
    create_async_engine,
    async_sessionmaker,
)
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.pool import NullPool

from app.core.config import settings


class Base(DeclarativeBase):
    """Base class for all SQLAlchemy models."""
    pass


# Exit Ready database engine
engine: AsyncEngine = create_async_engine(
    settings.database_url,
    echo=settings.debug,
    pool_size=settings.db_pool_size,
    max_overflow=settings.db_max_overflow,
    pool_timeout=settings.db_pool_timeout,
    pool_recycle=settings.db_pool_recycle,
    pool_pre_ping=True,  # Verify connections before using
)

# CRM database engine (read-only)
crm_engine: AsyncEngine = create_async_engine(
    settings.crm_database_url,
    echo=settings.debug,
    pool_size=5,
    max_overflow=5,
    pool_timeout=settings.db_pool_timeout,
    pool_recycle=settings.db_pool_recycle,
    pool_pre_ping=True,
)

# Session factories
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)

CrmAsyncSessionLocal = async_sessionmaker(
    crm_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency for getting async database sessions.

    Usage in FastAPI:
        @app.get("/items")
        async def read_items(db: AsyncSession = Depends(get_db)):
            ...
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def get_crm_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency for getting CRM database sessions (read-only).

    Usage in FastAPI:
        @app.get("/crm-data")
        async def read_crm_data(crm_db: AsyncSession = Depends(get_crm_db)):
            ...
    """
    async with CrmAsyncSessionLocal() as session:
        try:
            yield session
        except Exception:
            raise
        finally:
            await session.close()


async def init_db() -> None:
    """
    Initialize database by creating all tables.
    Only use in development. In production, use Alembic migrations.
    """
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def close_db() -> None:
    """Close database connections."""
    await engine.dispose()
    await crm_engine.dispose()


# Testing database setup
def get_test_engine(database_url: str) -> AsyncEngine:
    """
    Create a test database engine with NullPool.
    Used for isolated test databases.
    """
    return create_async_engine(
        database_url,
        echo=False,
        poolclass=NullPool,
    )


def get_test_session_factory(engine: AsyncEngine) -> async_sessionmaker:
    """Create a session factory for testing."""
    return async_sessionmaker(
        engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autocommit=False,
        autoflush=False,
    )
