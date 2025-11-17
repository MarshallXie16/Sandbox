"""Match Queue model."""
from sqlalchemy import Column, String, Float, Date, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import func
from datetime import datetime, timedelta
import uuid
from app.database import Base


class MatchQueue(Base):
    """Match queue model for matching algorithm."""

    __tablename__ = "match_queue"

    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    # Matching status
    status = Column(String(50), default="pending", index=True)  # 'pending', 'matched', 'expired'
    priority_score = Column(Float, default=0.5, index=True)  # Higher = prioritize matching

    # Match attempts (JSONB)
    proposed_matches = Column(JSONB, default=[])

    # Timestamps
    created_at = Column(Date, server_default=func.now())
    expires_at = Column(Date, default=lambda: datetime.utcnow().date() + timedelta(days=7))

    def __repr__(self) -> str:
        return f"<MatchQueue(user_id={self.user_id}, status={self.status})>"
