"""
Project model
"""
import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.core.db import Base


class Project(Base):
    """Project entity - represents a valuation engagement"""

    __tablename__ = "projects"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    client_id = Column(UUID(as_uuid=True), ForeignKey("clients.id"), nullable=False)
    internal_code = Column(String, nullable=True)
    business_name = Column(String, nullable=False)
    industry_code = Column(String, nullable=False)
    location = Column(String, nullable=True)
    project_type = Column(String, nullable=False)  # 'quick', 'standard', 'full_valuation'
    status = Column(String, nullable=False, default='draft')  # 'draft', 'in_analysis', 'reported', 'closed'
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    client = relationship("Client", back_populates="projects")
    financial_inputs = relationship("FinancialInput", back_populates="project", cascade="all, delete-orphan")
    valuation_inputs = relationship("ValuationInput", back_populates="project", cascade="all, delete-orphan")
    valuation_results = relationship("ValuationResult", back_populates="project", cascade="all, delete-orphan")
    valuation_summary = relationship("ValuationSummary", back_populates="project", uselist=False, cascade="all, delete-orphan")
    reports = relationship("Report", back_populates="project", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Project(id={self.id}, business_name='{self.business_name}', type='{self.project_type}')>"
