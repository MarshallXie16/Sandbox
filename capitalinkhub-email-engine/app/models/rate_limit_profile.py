"""
RateLimitProfile model for managing sending rate limits.
"""
from datetime import datetime
from typing import Optional, Dict, Any
import json

from sqlalchemy import Column, Integer, String, DateTime, Text
from sqlalchemy.orm import relationship

from app.core.database import Base


class RateLimitProfile(Base):
    """
    Rate limiting profile.

    Defines sending rate limits for campaigns.
    Multiple campaigns can share the same rate limit profile.
    """
    __tablename__ = "rate_limit_profiles"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, unique=True)
    max_per_hour = Column(Integer, nullable=False)
    max_per_day = Column(Integer, nullable=False)
    min_delay_seconds = Column(Integer, nullable=False, default=2)
    max_delay_seconds = Column(Integer, nullable=False, default=7)
    details = Column(Text, nullable=True)  # JSON field for additional configuration
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    campaigns = relationship("Campaign", back_populates="rate_limit_profile")

    def get_details(self) -> Dict[str, Any]:
        """Parse and return details as dictionary."""
        if self.details:
            try:
                return json.loads(self.details)
            except json.JSONDecodeError:
                return {}
        return {}

    def set_details(self, details_dict: Dict[str, Any]) -> None:
        """Set details from dictionary."""
        self.details = json.dumps(details_dict)

    def __repr__(self) -> str:
        return f"<RateLimitProfile(id={self.id}, name='{self.name}', max_per_hour={self.max_per_hour}, max_per_day={self.max_per_day})>"
