"""API dependencies for dependency injection."""

from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import db_manager
from app.repositories.crm_read import CrmReadRepository
from app.repositories.exit_ready_read import ExitReadyReadRepository
from app.repositories.facilitator_read import FacilitatorReadRepository
from app.services.crm_analytics import CrmAnalyticsService
from app.services.exit_ready_analytics import ExitReadyAnalyticsService
from app.services.facilitator_analytics import FacilitatorAnalyticsService


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Get analytics database session."""
    async for session in db_manager.get_analytics_session():
        yield session


def get_exit_ready_service() -> ExitReadyAnalyticsService:
    """Get Exit Ready analytics service."""
    repository = ExitReadyReadRepository(db_manager.exit_ready_engine)
    return ExitReadyAnalyticsService(repository)


def get_facilitator_service() -> FacilitatorAnalyticsService:
    """Get Facilitator analytics service."""
    repository = FacilitatorReadRepository(db_manager.facilitator_engine)
    return FacilitatorAnalyticsService(repository)


def get_crm_service() -> CrmAnalyticsService:
    """Get CRM analytics service."""
    repository = CrmReadRepository(db_manager.crm_engine)
    return CrmAnalyticsService(repository)
