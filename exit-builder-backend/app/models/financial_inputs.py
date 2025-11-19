"""
Financial Inputs model - Used for Quick Valuation
"""
from sqlalchemy import Column, String, Numeric, Integer, ForeignKey, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

from app.database import Base


class FinancialInputs(Base):
    """
    Financial inputs for Quick Valuation
    Stores 3 years of financial data (year0 = most recent)
    """
    __tablename__ = "financial_inputs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    year = Column(Integer, nullable=False)  # 0, 1, 2 (0 = most recent)
    revenue = Column(Numeric(15, 2), nullable=True)
    net_profit = Column(Numeric(15, 2), nullable=True)
    ebitda = Column(Numeric(15, 2), nullable=True)
    total_assets = Column(Numeric(15, 2), nullable=True)
    total_liabilities = Column(Numeric(15, 2), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    project = relationship("Project", back_populates="financial_inputs")

    def __repr__(self):
        return f"<FinancialInputs(project_id={self.project_id}, year={self.year}, revenue={self.revenue})>"
