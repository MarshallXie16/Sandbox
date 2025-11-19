"""
Financial input models
"""
import uuid
from sqlalchemy import Column, String, Integer, Numeric, Text, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.core.db import Base


class FinancialInput(Base):
    """Financial inputs for a project - stores SDE, EBITDA, Revenue"""

    __tablename__ = "financial_inputs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id"), nullable=False)
    year = Column(Integer, nullable=False, default=0)  # 0 = TTM (Trailing Twelve Months)
    revenue = Column(Numeric(15, 2), nullable=False)
    sde = Column(Numeric(15, 2), nullable=True)  # Seller's Discretionary Earnings
    ebitda = Column(Numeric(15, 2), nullable=True)  # Earnings Before Interest, Taxes, Depreciation, Amortization
    notes = Column(Text, nullable=True)

    # Relationships
    project = relationship("Project", back_populates="financial_inputs")

    def __repr__(self):
        return f"<FinancialInput(id={self.id}, project_id={self.project_id}, revenue={self.revenue})>"


class IndustryMultiple(Base):
    """Industry multiples for valuation - market data for different industries"""

    __tablename__ = "industry_multiples"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    industry_code = Column(String, nullable=False)  # NAICS code
    metric_type = Column(String, nullable=False)  # 'SDE' or 'EBITDA'
    size_min_revenue = Column(Numeric(15, 2), nullable=True)
    size_max_revenue = Column(Numeric(15, 2), nullable=True)
    multiple_low = Column(Numeric(5, 2), nullable=False)
    multiple_mid = Column(Numeric(5, 2), nullable=False)
    multiple_high = Column(Numeric(5, 2), nullable=False)
    source = Column(String, nullable=True)
    effective_date = Column(String, nullable=True)  # Using string for simplicity in MVP

    def __repr__(self):
        return f"<IndustryMultiple(industry={self.industry_code}, type={self.metric_type}, mid={self.multiple_mid})>"
