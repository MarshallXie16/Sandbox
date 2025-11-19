"""
Answer model - User responses to questionnaire
"""
from sqlalchemy import Column, Numeric, Text, ForeignKey, DateTime
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

from app.database import Base


class Answer(Base):
    """
    User answers to questionnaire questions
    """
    __tablename__ = "answers"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    question_id = Column(UUID(as_uuid=True), ForeignKey("questions.id", ondelete="CASCADE"), nullable=False)
    value_text = Column(Text, nullable=True)
    value_numeric = Column(Numeric(15, 2), nullable=True)
    selected_option_values = Column(JSONB, nullable=True)  # For multi-choice: ["VALUE1", "VALUE2"]
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    project = relationship("Project", back_populates="answers")
    question = relationship("Question", back_populates="answers")

    def __repr__(self):
        return f"<Answer(project_id={self.project_id}, question_id={self.question_id})>"
