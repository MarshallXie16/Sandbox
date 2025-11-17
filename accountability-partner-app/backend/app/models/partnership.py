"""Partnership model."""
from sqlalchemy import Column, String, Integer, Float, Date, ForeignKey, ARRAY, Text, CheckConstraint
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime, timedelta
import uuid
from app.database import Base


class Partnership(Base):
    """Partnership model for accountability relationships."""

    __tablename__ = "partnerships"

    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Partners
    user1_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    user2_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)

    # Partnership metadata
    status = Column(String(50), default="active", index=True)  # 'pending', 'active', 'completed', 'cancelled'
    season_number = Column(Integer, default=1)
    current_season_start_date = Column(Date, default=func.current_date())
    current_season_end_date = Column(Date, default=lambda: datetime.utcnow().date() + timedelta(weeks=4))

    # Shared goals (JSONB)
    mutual_goals = Column(JSONB, default=[])

    # Partnership settings
    check_in_frequency = Column(String(50), default="weekly")
    check_in_days = Column(ARRAY(Integer), default=[1, 3, 5])  # Mon, Wed, Fri
    communication_methods = Column(ARRAY(Text), default=["text"])  # text, voice, photo

    # Health metrics
    balance_score = Column(Float, default=0.5)  # 0 (user1 gives more) to 1 (user2 gives more)
    engagement_score = Column(Float, default=0.0)  # 0 (inactive) to 1 (highly engaged)
    last_interaction_at = Column(Date)

    # Anti-ghosting
    user1_last_active_at = Column(Date, server_default=func.now())
    user2_last_active_at = Column(Date, server_default=func.now())
    nudge_count = Column(Integer, default=0)

    # Timestamps
    created_at = Column(Date, server_default=func.now())
    updated_at = Column(Date, server_default=func.now(), onupdate=func.now())

    # Constraints
    __table_args__ = (
        CheckConstraint("user1_id != user2_id", name="check_different_users"),
    )

    # Relationships
    user1 = relationship("User", foreign_keys=[user1_id], back_populates="partnerships_as_user1")
    user2 = relationship("User", foreign_keys=[user2_id], back_populates="partnerships_as_user2")
    goals = relationship("Goal", back_populates="partnership", cascade="all, delete-orphan")
    check_ins = relationship("CheckIn", back_populates="partnership", cascade="all, delete-orphan")
    tasks = relationship("Task", back_populates="partnership", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<Partnership(id={self.id}, user1_id={self.user1_id}, user2_id={self.user2_id}, status={self.status})>"
