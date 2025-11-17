"""Task model."""
from sqlalchemy import Column, String, Date, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
from app.database import Base, GUID


class Task(Base):
    """Task model for micro-coaching assignments."""

    __tablename__ = "tasks"

    # Primary key
    id = Column(GUID, primary_key=True, default=uuid.uuid4)
    partnership_id = Column(GUID, ForeignKey("partnerships.id", ondelete="CASCADE"), nullable=False, index=True)
    assigned_by_user_id = Column(GUID, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    assigned_to_user_id = Column(GUID, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)

    # Task details
    title = Column(String(200), nullable=False)
    description = Column(Text)
    task_type = Column(String(50))  # 'action', 'reflection', 'submission'

    # Completion
    status = Column(String(50), default="pending")  # 'pending', 'completed', 'skipped'
    completed_at = Column(DateTime)
    completion_proof_url = Column(Text)  # S3 URL for photo/voice proof

    # Metadata
    due_date = Column(Date)
    created_at = Column(DateTime, server_default=func.now())

    # Relationships
    partnership = relationship("Partnership", back_populates="tasks")
    assigned_by = relationship("User", foreign_keys=[assigned_by_user_id], back_populates="assigned_tasks")
    assigned_to = relationship("User", foreign_keys=[assigned_to_user_id], back_populates="received_tasks")

    def __repr__(self) -> str:
        return f"<Task(id={self.id}, title={self.title}, status={self.status})>"
