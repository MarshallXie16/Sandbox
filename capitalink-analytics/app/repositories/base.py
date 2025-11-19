"""Base repository class."""

from typing import Optional

from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession
from sqlalchemy.orm import sessionmaker


class BaseReadRepository:
    """
    Base class for read-only repositories that query upstream databases.

    These repositories should NEVER perform write operations on upstream data.
    """

    def __init__(self, engine: Optional[AsyncEngine] = None):
        """
        Initialize repository with database engine.

        Args:
            engine: SQLAlchemy async engine for the upstream database
        """
        self.engine = engine
        self.session_maker: Optional[sessionmaker] = None

        if engine:
            self.session_maker = sessionmaker(
                engine,
                class_=AsyncSession,
                expire_on_commit=False,
            )

    def is_available(self) -> bool:
        """Check if this repository's database is available."""
        return self.engine is not None

    async def get_session(self) -> AsyncSession:
        """
        Get a database session.

        Returns:
            AsyncSession instance

        Raises:
            RuntimeError: If engine is not configured
        """
        if not self.session_maker:
            raise RuntimeError(
                f"{self.__class__.__name__} database is not configured. "
                "Check your environment variables."
            )

        return self.session_maker()
