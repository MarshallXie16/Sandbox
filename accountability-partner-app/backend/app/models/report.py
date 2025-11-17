"""Report model for safety and moderation."""
from sqlalchemy import Column, String, Date, DateTime, Text, ForeignKey
from sqlalchemy.sql import func
import uuid
from app.database import Base, GUID, ARRAY


class Report(Base):
    """Report model for user safety reports."""

    __tablename__ = "reports"

    # Primary key
    id = Column(GUID, primary_key=True, default=uuid.uuid4)
    reporter_id = Column(GUID, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    reported_user_id = Column(GUID, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    partnership_id = Column(GUID, ForeignKey("partnerships.id", ondelete="SET NULL"))

    # Report details
    reason = Column(String(50), nullable=False)  # 'harassment', 'inappropriate', 'ghosting', 'spam'
    description = Column(Text)
    evidence_urls = Column(ARRAY(Text))  # Screenshots, etc.

    # Resolution
    status = Column(String(50), default="pending", index=True)  # 'pending', 'investigating', 'resolved', 'dismissed'
    admin_notes = Column(Text)
    action_taken = Column(String(100))  # 'warning', 'temp_ban', 'permanent_ban', 'no_action'

    # Timestamps
    created_at = Column(DateTime, server_default=func.now())
    resolved_at = Column(DateTime)

    def __repr__(self) -> str:
        return f"<Report(id={self.id}, reason={self.reason}, status={self.status})>"
