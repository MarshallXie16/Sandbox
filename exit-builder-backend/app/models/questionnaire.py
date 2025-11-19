"""
Questionnaire models - For Standard Valuation Flow
"""
from sqlalchemy import Column, String, Text, Integer, ForeignKey, DateTime, Boolean, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
import enum

from app.database import Base


class InputType(str, enum.Enum):
    """Question input type enumeration"""
    SINGLE_CHOICE = "single_choice"
    MULTI_CHOICE = "multi_choice"
    NUMBER = "number"
    TEXT = "text"
    YES_NO = "yes_no"


class QuestionnaireTemplate(Base):
    """
    Questionnaire template (e.g., Exit Ready Standard)
    """
    __tablename__ = "questionnaire_templates"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    version = Column(Integer, nullable=False, default=1)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    questions = relationship("Question", back_populates="questionnaire_template", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<QuestionnaireTemplate(name={self.name}, version={self.version})>"


class Question(Base):
    """
    Individual questions in a questionnaire
    """
    __tablename__ = "questions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    questionnaire_template_id = Column(UUID(as_uuid=True), ForeignKey("questionnaire_templates.id", ondelete="CASCADE"), nullable=False)
    section = Column(String, nullable=False)  # e.g., "Owner Dependency"
    order_index = Column(Integer, nullable=False)
    code = Column(String, unique=True, nullable=False)  # e.g., Q_OWNER_ROLE
    text = Column(Text, nullable=False)
    input_type = Column(SQLEnum(InputType), nullable=False)
    is_required = Column(Boolean, default=True, nullable=False)
    help_text = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    questionnaire_template = relationship("QuestionnaireTemplate", back_populates="questions")
    options = relationship("QuestionOption", back_populates="question", cascade="all, delete-orphan")
    answers = relationship("Answer", back_populates="question", cascade="all, delete-orphan")
    score_rules = relationship("ScoreRule", back_populates="question", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Question(code={self.code}, section={self.section})>"


class QuestionOption(Base):
    """
    Options for choice-based questions
    """
    __tablename__ = "question_options"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    question_id = Column(UUID(as_uuid=True), ForeignKey("questions.id", ondelete="CASCADE"), nullable=False)
    value = Column(String, nullable=False)  # Internal code (e.g., HIGH, LOW)
    label = Column(String, nullable=False)  # User-facing text
    order_index = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    question = relationship("Question", back_populates="options")

    def __repr__(self):
        return f"<QuestionOption(value={self.value}, label={self.label})>"
