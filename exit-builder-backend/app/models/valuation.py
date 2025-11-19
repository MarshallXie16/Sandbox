"""
Valuation models
"""
import uuid
from datetime import datetime
from sqlalchemy import Column, String, Numeric, Text, Boolean, ForeignKey, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.core.db import Base


class ValuationMethod(Base):
    """Valuation methods - defines approaches to valuing a business"""

    __tablename__ = "valuation_methods"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    code = Column(String, unique=True, nullable=False)  # 'SDE_MULTIPLE', 'EBITDA_MULTIPLE'
    name = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)

    # Relationships
    valuation_inputs = relationship("ValuationInput", back_populates="valuation_method")
    valuation_results = relationship("ValuationResult", back_populates="valuation_method")

    def __repr__(self):
        return f"<ValuationMethod(code='{self.code}', name='{self.name}')>"


class ValuationInput(Base):
    """Valuation inputs - stores the parameters used for a specific valuation method"""

    __tablename__ = "valuation_inputs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id"), nullable=False)
    valuation_method_id = Column(UUID(as_uuid=True), ForeignKey("valuation_methods.id"), nullable=False)
    base_metric = Column(String, nullable=False)  # 'SDE' or 'EBITDA'
    base_metric_value = Column(Numeric(15, 2), nullable=False)
    base_multiple = Column(Numeric(5, 2), nullable=False)
    adjusted_multiple = Column(Numeric(5, 2), nullable=False)  # Same as base_multiple for Quick MVP
    notes = Column(Text, nullable=True)

    # Relationships
    project = relationship("Project", back_populates="valuation_inputs")
    valuation_method = relationship("ValuationMethod", back_populates="valuation_inputs")

    def __repr__(self):
        return f"<ValuationInput(project_id={self.project_id}, metric={self.base_metric}, value={self.base_metric_value})>"


class ValuationResult(Base):
    """Valuation results - stores computed valuation ranges"""

    __tablename__ = "valuation_results"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id"), nullable=False)
    valuation_method_id = Column(UUID(as_uuid=True), ForeignKey("valuation_methods.id"), nullable=False)
    scenario = Column(String, nullable=False, default='base')  # Always 'base' for Quick MVP
    value_low = Column(Numeric(15, 2), nullable=False)
    value_mid = Column(Numeric(15, 2), nullable=False)
    value_high = Column(Numeric(15, 2), nullable=False)
    currency = Column(String, nullable=False, default='CAD')
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    project = relationship("Project", back_populates="valuation_results")
    valuation_method = relationship("ValuationMethod", back_populates="valuation_results")

    def __repr__(self):
        return f"<ValuationResult(project_id={self.project_id}, mid={self.value_mid}, currency={self.currency})>"


class ValuationSummary(Base):
    """Valuation summary - final recommended value range for a project"""

    __tablename__ = "valuation_summary"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id"), nullable=False, unique=True)
    recommended_value_low = Column(Numeric(15, 2), nullable=False)
    recommended_value_mid = Column(Numeric(15, 2), nullable=False)
    recommended_value_high = Column(Numeric(15, 2), nullable=False)
    currency = Column(String, nullable=False, default='CAD')
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    project = relationship("Project", back_populates="valuation_summary")

    def __repr__(self):
        return f"<ValuationSummary(project_id={self.project_id}, mid={self.recommended_value_mid})>"
