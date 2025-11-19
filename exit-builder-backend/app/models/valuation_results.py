"""
Valuation Results models
"""
from sqlalchemy import Column, String, Numeric, ForeignKey, DateTime, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

from app.database import Base


class ValuationResults(Base):
    """
    Individual valuation method results
    E.g., revenue_multiple, ebitda_multiple, asset_based
    """
    __tablename__ = "valuation_results"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    method = Column(String, nullable=False)  # revenue_multiple, ebitda_multiple, asset_based
    value = Column(Numeric(15, 2), nullable=False)
    confidence = Column(String, nullable=True)  # low, medium, high
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    project = relationship("Project", back_populates="valuation_results")

    def __repr__(self):
        return f"<ValuationResults(method={self.method}, value={self.value})>"


class ValuationSummary(Base):
    """
    Summary valuation for a project
    Includes low, mid, high estimates
    """
    __tablename__ = "valuation_summary"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, unique=True)
    value_low = Column(Numeric(15, 2), nullable=False)
    value_mid = Column(Numeric(15, 2), nullable=False)
    value_high = Column(Numeric(15, 2), nullable=False)
    primary_method = Column(String, nullable=True)
    adjustment_factor = Column(Numeric(5, 2), nullable=True, default=1.0)  # For Standard flow
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    project = relationship("Project", back_populates="valuation_summary")

    def __repr__(self):
        return f"<ValuationSummary(value_mid={self.value_mid}, adjustment={self.adjustment_factor})>"
