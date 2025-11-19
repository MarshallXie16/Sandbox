"""
VaultAI Integration Layer - Database Configuration
Async SQLAlchemy 2.x setup with connection pooling.
"""

from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    create_async_engine,
    async_sessionmaker,
)
from sqlalchemy.orm import declarative_base
from sqlalchemy.pool import NullPool, QueuePool

from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)

# Declarative base for ORM models
Base = declarative_base()

# Create async engine
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.VAULTAI_DEBUG,
    future=True,
    poolclass=QueuePool if settings.VAULTAI_ENV == "prod" else NullPool,
    pool_size=20 if settings.VAULTAI_ENV == "prod" else 5,
    max_overflow=10 if settings.VAULTAI_ENV == "prod" else 0,
    pool_pre_ping=True,  # Verify connections before using
    pool_recycle=3600,  # Recycle connections after 1 hour
)

# Create async session factory
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency for FastAPI routes to get a database session.

    Yields:
        AsyncSession: Database session.

    Example:
        @app.get("/")
        async def root(db: AsyncSession = Depends(get_db)):
            result = await db.execute(select(PromptTemplate))
            return result.scalars().all()
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception as e:
            await session.rollback()
            logger.error(f"Database session error: {e}")
            raise
        finally:
            await session.close()


async def init_db() -> None:
    """
    Initialize database tables.
    This should only be used in development.
    In production, use Alembic migrations.
    """
    async with engine.begin() as conn:
        # Import all models to ensure they're registered
        from app.models import prompt_template, llm_log, document, embedding  # noqa

        if settings.VAULTAI_ENV == "dev":
            await conn.run_sync(Base.metadata.create_all)
            logger.info("Database tables created")
        else:
            logger.warning("init_db called in non-dev environment. Use Alembic migrations instead.")


async def close_db() -> None:
    """Close database connections on shutdown."""
    await engine.dispose()
    logger.info("Database connections closed")
