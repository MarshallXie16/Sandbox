"""
Recipient model representing email recipients in campaigns.
"""
from datetime import datetime
from typing import Optional, Dict, Any
import json

from sqlalchemy import Column, Integer, String, ForeignKey, Enum as SQLEnum, Text, DateTime
from sqlalchemy.orm import relationship

from app.core.database import Base
from .enums import RecipientSegment, RecipientStatus


class Recipient(Base):
    """
    Email recipient entity.

    Represents an individual recipient within a campaign.
    Tracks delivery status and stores personalization data.
    """
    __tablename__ = "recipients"

    id = Column(Integer, primary_key=True, index=True)
    campaign_id = Column(Integer, ForeignKey("campaigns.id", ondelete="CASCADE"), nullable=False, index=True)
    email = Column(String(255), nullable=False, index=True)
    name = Column(String(255), nullable=True)
    segment = Column(SQLEnum(RecipientSegment), nullable=False, default=RecipientSegment.OTHER)
    status = Column(SQLEnum(RecipientStatus), nullable=False, default=RecipientStatus.PENDING, index=True)
    last_error = Column(Text, nullable=True)
    details = Column(Text, nullable=True)  # JSON field for merge fields
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    campaign = relationship("Campaign", back_populates="recipients")
    send_logs = relationship("SendLog", back_populates="recipient", cascade="all, delete-orphan")

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

    def get_merge_fields(self) -> Dict[str, Any]:
        """
        Get all merge fields for template rendering.
        Combines standard fields with custom details.
        """
        fields = {
            "email": self.email,
            "name": self.name or "",
            "first_name": self.name.split()[0] if self.name else "",
            "segment": self.segment.value if self.segment else "",
        }
        # Add custom fields from details
        fields.update(self.get_details())
        return fields

    def __repr__(self) -> str:
        return f"<Recipient(id={self.id}, email='{self.email}', campaign_id={self.campaign_id}, status={self.status})>"
