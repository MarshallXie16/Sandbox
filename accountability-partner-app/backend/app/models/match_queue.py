"""Match Queue model."""
from sqlalchemy import Column, String, Float, Date, DateTime, ForeignKey
from sqlalchemy.sql import func
from datetime import datetime, timedelta
import uuid
from app.database import Base, GUID, JSONB


class MatchQueue(Base):
    """Match queue model for matching algorithm."""

    __tablename__ = "match_queue"

    # Primary key
    id = Column(GUID, primary_key=True, default=uuid.uuid4)
    user_id = Column(GUID, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    # Matching status
    status = Column(String(50), default="pending", index=True)  # 'pending', 'matched', 'expired'
    priority_score = Column(Float, default=0.5, index=True)  # Higher = prioritize matching

    # Match attempts (JSONB)
    proposed_matches = Column(JSONB, default=[])
    declined_user_ids = Column(JSONB, default=[])  # List of declined user IDs

    # Timestamps
    created_at = Column(DateTime, server_default=func.now())
    expires_at = Column(DateTime, default=lambda: datetime.utcnow() + timedelta(days=7))

    def __repr__(self) -> str:
        return f"<MatchQueue(user_id={self.user_id}, status={self.status})>"
