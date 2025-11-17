"""Goal model."""
from sqlalchemy import Column, String, Boolean, Date, Text, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
from app.database import Base


class Goal(Base):
    """Goal model for individual and mutual goals."""

    __tablename__ = "goals"

    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    partnership_id = Column(UUID(as_uuid=True), ForeignKey("partnerships.id", ondelete="CASCADE"), nullable=False, index=True)
    owner_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), index=True)  # NULL if mutual

    # Goal details
    title = Column(String(200), nullable=False)
    description = Column(Text)
    category = Column(String(50))  # 'career', 'fitness', 'relationships', etc.
    is_mutual = Column(Boolean, default=False)

    # Tracking
    status = Column(String(50), default="in_progress", index=True)  # 'not_started', 'in_progress', 'completed', 'abandoned'
    target_date = Column(Date)
    completed_at = Column(Date)

    # Subtasks (JSONB)
    subtasks = Column(JSONB, default=[])

    # Timestamps
    created_at = Column(Date, server_default=func.now())
    updated_at = Column(Date, server_default=func.now(), onupdate=func.now())

    # Relationships
    partnership = relationship("Partnership", back_populates="goals")

    def __repr__(self) -> str:
        return f"<Goal(id={self.id}, title={self.title}, status={self.status})>"
