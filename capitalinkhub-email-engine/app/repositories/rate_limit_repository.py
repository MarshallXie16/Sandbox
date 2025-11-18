"""
Repository for RateLimitProfile model operations.
"""
from typing import Optional
from sqlalchemy.orm import Session

from app.models import RateLimitProfile
from .base import BaseRepository


class RateLimitRepository(BaseRepository[RateLimitProfile]):
    """RateLimitProfile-specific repository with custom query methods."""

    def __init__(self, db: Session):
        super().__init__(RateLimitProfile, db)

    def get_by_name(self, name: str) -> Optional[RateLimitProfile]:
        """Get a rate limit profile by name."""
        return self.db.query(RateLimitProfile).filter(RateLimitProfile.name == name).first()

    def get_or_create_default(self, settings) -> RateLimitProfile:
        """
        Get or create a default rate limit profile.
        Uses settings from configuration.
        """
        profile = self.get_by_name("default")
        if not profile:
            profile = RateLimitProfile(
                name="default",
                max_per_hour=settings.default_max_per_hour,
                max_per_day=settings.default_max_per_day,
                min_delay_seconds=settings.default_min_delay_seconds,
                max_delay_seconds=settings.default_max_delay_seconds
            )
            self.db.add(profile)
            self.db.flush()
        return profile
