"""
Campaign model representing an email campaign.
"""
from datetime import datetime
from typing import Optional, Dict, Any
import json

from sqlalchemy import Column, Integer, String, DateTime, Enum as SQLEnum, Text, ForeignKey
from sqlalchemy.orm import relationship

from app.core.database import Base
from .enums import CampaignType, CampaignStatus, EmailBackend


class Campaign(Base):
    """
    Email campaign entity.

    A campaign represents a planned or ongoing email outreach effort.
    It contains configuration, templates, and tracks overall status.
    """
    __tablename__ = "campaigns"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, unique=True)
    type = Column(SQLEnum(CampaignType), nullable=False)
    subject_template = Column(String(500), nullable=False)
    body_template_path = Column(String(500), nullable=False)
    sender_name = Column(String(255), nullable=False)
    sender_email = Column(String(255), nullable=False)
    backend = Column(SQLEnum(EmailBackend), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    scheduled_at = Column(DateTime, nullable=True)
    status = Column(SQLEnum(CampaignStatus), default=CampaignStatus.DRAFT, nullable=False)
    details = Column(Text, nullable=True)  # JSON field for additional metadata

    # Foreign key to rate limit profile
    rate_limit_profile_id = Column(Integer, ForeignKey("rate_limit_profiles.id"), nullable=True)

    # Relationships
    recipients = relationship("Recipient", back_populates="campaign", cascade="all, delete-orphan")
    send_logs = relationship("SendLog", back_populates="campaign", cascade="all, delete-orphan")
    rate_limit_profile = relationship("RateLimitProfile", back_populates="campaigns")

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
        return f"<Campaign(id={self.id}, name='{self.name}', type={self.type}, status={self.status})>"
