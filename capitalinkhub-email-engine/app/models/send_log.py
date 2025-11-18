"""
SendLog model for tracking email sending attempts and results.
"""
from datetime import datetime
from typing import Optional, Dict, Any
import json

from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Enum as SQLEnum, Text
from sqlalchemy.orm import relationship

from app.core.database import Base
from .enums import EmailBackend, SendStatus


class SendLog(Base):
    """
    Email send log entry.

    Tracks individual email sending attempts, results, and metadata.
    Used for debugging, analytics, and audit trails.
    """
    __tablename__ = "send_logs"

    id = Column(Integer, primary_key=True, index=True)
    campaign_id = Column(Integer, ForeignKey("campaigns.id", ondelete="CASCADE"), nullable=False, index=True)
    recipient_id = Column(Integer, ForeignKey("recipients.id", ondelete="CASCADE"), nullable=False, index=True)
    backend = Column(SQLEnum(EmailBackend), nullable=False)
    sent_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    status = Column(SQLEnum(SendStatus), nullable=False)
    message_id = Column(String(255), nullable=True)  # External message ID from email provider
    error_message = Column(Text, nullable=True)
    details = Column(Text, nullable=True)  # JSON field for additional metadata

    # Relationships
    campaign = relationship("Campaign", back_populates="send_logs")
    recipient = relationship("Recipient", back_populates="send_logs")

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
        return f"<SendLog(id={self.id}, recipient_id={self.recipient_id}, status={self.status}, sent_at={self.sent_at})>"
