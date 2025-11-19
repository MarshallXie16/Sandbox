"""
Scoring models - For Standard Valuation Flow
"""
from sqlalchemy import Column, String, Text, Integer, Numeric, ForeignKey, DateTime, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
import enum

from app.database import Base


class MatchType(str, enum.Enum):
    """Score rule match type enumeration"""
    OPTION_VALUE = "option_value"
    NUMERIC_RANGE = "numeric_range"
    YES_NO = "yes_no"
    TEXT_CONTAINS = "text_contains"


class ScoreDimension(Base):
    """
    Scoring dimensions (e.g., Owner Dependency, Customer Concentration)
    """
    __tablename__ = "score_dimensions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    code = Column(String, unique=True, nullable=False)  # OWNER_DEP, CUSTOMER_CONC, etc.
    name = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    weight = Column(Numeric(3, 2), nullable=False)  # 0.10 - 0.30
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    score_rules = relationship("ScoreRule", back_populates="dimension", cascade="all, delete-orphan")
    dimension_results = relationship("ScoreDimensionResult", back_populates="dimension", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<ScoreDimension(code={self.code}, name={self.name}, weight={self.weight})>"


class ScoreRule(Base):
    """
    Rules mapping question responses to score deltas
    """
    __tablename__ = "score_rules"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    dimension_id = Column(UUID(as_uuid=True), ForeignKey("score_dimensions.id", ondelete="CASCADE"), nullable=False)
    question_id = Column(UUID(as_uuid=True), ForeignKey("questions.id", ondelete="CASCADE"), nullable=False)
    match_type = Column(SQLEnum(MatchType), nullable=False)
    match_value = Column(String, nullable=False)  # e.g., 'HIGH', '>=3', 'YES'
    score_delta = Column(Integer, nullable=False)  # Points to add/subtract
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    dimension = relationship("ScoreDimension", back_populates="score_rules")
    question = relationship("Question", back_populates="score_rules")

    def __repr__(self):
        return f"<ScoreRule(dimension={self.dimension.code if self.dimension else None}, delta={self.score_delta})>"


class ScoreResult(Base):
    """
    Overall score result for a project
    """
    __tablename__ = "score_results"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    total_score = Column(Integer, nullable=False)
    rating = Column(String, nullable=False)  # A, B, C, D
    valuation_adjustment_factor = Column(Numeric(5, 2), nullable=False)  # 1.10, 1.00, 0.90, 0.80
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    project = relationship("Project", back_populates="score_results")
    dimension_results = relationship("ScoreDimensionResult", back_populates="score_result", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<ScoreResult(total_score={self.total_score}, rating={self.rating}, adjustment={self.valuation_adjustment_factor})>"


class ScoreDimensionResult(Base):
    """
    Individual dimension scores within a score result
    """
    __tablename__ = "score_dimension_results"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    score_result_id = Column(UUID(as_uuid=True), ForeignKey("score_results.id", ondelete="CASCADE"), nullable=False)
    dimension_id = Column(UUID(as_uuid=True), ForeignKey("score_dimensions.id", ondelete="CASCADE"), nullable=False)
    score = Column(Integer, nullable=False)
    comment = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    score_result = relationship("ScoreResult", back_populates="dimension_results")
    dimension = relationship("ScoreDimension", back_populates="dimension_results")

    def __repr__(self):
        return f"<ScoreDimensionResult(dimension={self.dimension.code if self.dimension else None}, score={self.score})>"
