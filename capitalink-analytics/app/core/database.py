"""Database connection and session management."""

from typing import AsyncGenerator, Optional

from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool

from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)


class DatabaseManager:
    """Manages database connections for analytics and upstream sources."""

    def __init__(self):
        """Initialize database manager with connection pools."""
        # Analytics database (read-write for this module's tables)
        self.analytics_engine: Optional[AsyncEngine] = None
        self.analytics_session_maker: Optional[sessionmaker] = None

        # Upstream databases (read-only)
        self.crm_engine: Optional[AsyncEngine] = None
        self.exit_ready_engine: Optional[AsyncEngine] = None
        self.facilitator_engine: Optional[AsyncEngine] = None
        self.match_engine_engine: Optional[AsyncEngine] = None
        self.engagement_engine: Optional[AsyncEngine] = None
        self.portal_engine: Optional[AsyncEngine] = None

    def _create_engine(self, database_url: str, pool_size: int = 10) -> AsyncEngine:
        """Create async engine with connection pooling."""
        return create_async_engine(
            database_url,
            echo=settings.analytics_debug,
            pool_pre_ping=True,
            pool_size=pool_size,
            max_overflow=20,
        )

    def _create_readonly_engine(self, database_url: str) -> AsyncEngine:
        """Create read-only async engine with smaller pool."""
        return create_async_engine(
            database_url,
            echo=settings.analytics_debug,
            pool_pre_ping=True,
            pool_size=5,
            max_overflow=10,
        )

    async def initialize(self) -> None:
        """Initialize all database connections."""
        logger.info("Initializing database connections...")

        # Analytics database (primary)
        self.analytics_engine = self._create_engine(settings.analytics_database_url)
        self.analytics_session_maker = sessionmaker(
            self.analytics_engine,
            class_=AsyncSession,
            expire_on_commit=False,
        )
        logger.info("Analytics database connected")

        # Upstream databases (read-only, optional)
        if settings.crm_database_url:
            self.crm_engine = self._create_readonly_engine(settings.crm_database_url)
            logger.info("CRM database connected (read-only)")

        if settings.exit_ready_database_url:
            self.exit_ready_engine = self._create_readonly_engine(
                settings.exit_ready_database_url
            )
            logger.info("Exit Ready database connected (read-only)")

        if settings.facilitator_database_url:
            self.facilitator_engine = self._create_readonly_engine(
                settings.facilitator_database_url
            )
            logger.info("Facilitator database connected (read-only)")

        if settings.match_engine_database_url:
            self.match_engine_engine = self._create_readonly_engine(
                settings.match_engine_database_url
            )
            logger.info("Match Engine database connected (read-only)")

        if settings.engagement_database_url:
            self.engagement_engine = self._create_readonly_engine(
                settings.engagement_database_url
            )
            logger.info("Engagement Tracker database connected (read-only)")

        if settings.portal_database_url:
            self.portal_engine = self._create_readonly_engine(
                settings.portal_database_url
            )
            logger.info("Portal API database connected (read-only)")

    async def close(self) -> None:
        """Close all database connections."""
        logger.info("Closing database connections...")

        engines = [
            self.analytics_engine,
            self.crm_engine,
            self.exit_ready_engine,
            self.facilitator_engine,
            self.match_engine_engine,
            self.engagement_engine,
            self.portal_engine,
        ]

        for engine in engines:
            if engine:
                await engine.dispose()

        logger.info("All database connections closed")

    async def get_analytics_session(self) -> AsyncGenerator[AsyncSession, None]:
        """Get analytics database session."""
        if not self.analytics_session_maker:
            raise RuntimeError("Database not initialized. Call initialize() first.")

        async with self.analytics_session_maker() as session:
            try:
                yield session
            except Exception:
                await session.rollback()
                raise
            finally:
                await session.close()


# Global database manager instance
db_manager = DatabaseManager()


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Dependency for getting database session."""
    async for session in db_manager.get_analytics_session():
        yield session
