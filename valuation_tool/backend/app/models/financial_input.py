"""FinancialInput model - historical financial data for Quick Valuation."""
from sqlalchemy import Column, Integer, Numeric, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
from app.database import Base, GUID


class FinancialInput(Base):
    """Historical financial data for a project year."""

    __tablename__ = "financial_inputs"

    # Primary key
    id = Column(GUID, primary_key=True, default=uuid.uuid4)

    # Foreign key
    project_id = Column(GUID, ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True)

    # Year
    year = Column(Integer, nullable=False)

    # Financial metrics
    revenue = Column(Numeric(precision=15, scale=2), nullable=False)
    cogs = Column(Numeric(precision=15, scale=2))  # Cost of Goods Sold
    gross_profit = Column(Numeric(precision=15, scale=2))
    operating_expenses = Column(Numeric(precision=15, scale=2))
    ebitda = Column(Numeric(precision=15, scale=2))  # Earnings Before Interest, Taxes, Depreciation, Amortization
    sde = Column(Numeric(precision=15, scale=2))  # Seller's Discretionary Earnings
    net_income = Column(Numeric(precision=15, scale=2))

    # Timestamps
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    project = relationship("Project", back_populates="financial_inputs")

    def __repr__(self) -> str:
        return f"<FinancialInput(project_id={self.project_id}, year={self.year}, revenue={self.revenue})>"
