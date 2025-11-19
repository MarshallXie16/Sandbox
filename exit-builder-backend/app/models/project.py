"""
Project model - Core entity for both Quick and Standard valuations
"""
from sqlalchemy import Column, String, DateTime, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
import enum

from app.database import Base


class ProjectType(str, enum.Enum):
    """Project type enumeration"""
    QUICK = "quick"
    STANDARD = "standard"


class Project(Base):
    """
    Main project entity
    Represents a business valuation project (Quick or Standard)
    """
    __tablename__ = "projects"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    project_type = Column(SQLEnum(ProjectType), nullable=False)
    industry = Column(String, nullable=True)
    description = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    financial_inputs = relationship("FinancialInputs", back_populates="project", cascade="all, delete-orphan")
    valuation_results = relationship("ValuationResults", back_populates="project", cascade="all, delete-orphan")
    valuation_summary = relationship("ValuationSummary", back_populates="project", uselist=False, cascade="all, delete-orphan")
    reports = relationship("Report", back_populates="project", cascade="all, delete-orphan")
    answers = relationship("Answer", back_populates="project", cascade="all, delete-orphan")
    score_results = relationship("ScoreResult", back_populates="project", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Project(id={self.id}, name={self.name}, type={self.project_type})>"
