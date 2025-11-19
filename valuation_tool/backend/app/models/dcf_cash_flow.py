"""DCFCashFlow model - projected cash flows per year for DCF calculation."""
from sqlalchemy import Column, Integer, String, Numeric, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
from app.database import Base, GUID


class DCFCashFlow(Base):
    """Projected cash flows per year for DCF valuation."""

    __tablename__ = "dcf_cash_flows"

    # Primary key
    id = Column(GUID, primary_key=True, default=uuid.uuid4)

    # Foreign key
    project_id = Column(GUID, ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True)

    # Year identification
    year_index = Column(Integer, nullable=False)  # 1, 2, 3, ... up to projection_years
    year_label = Column(String(50), nullable=False)  # e.g., 'Y1', 'Y2', 'Y3', or '2026', '2027'

    # Cash flow projections
    cash_flow = Column(Numeric(precision=15, scale=2), nullable=False)  # Projected free cash flow (or SDE/EBITDA proxy)
    discounted_cash_flow = Column(Numeric(precision=15, scale=2))  # Filled by DCF engine

    # Timestamps
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    project = relationship("Project", back_populates="dcf_cash_flows")

    def __repr__(self) -> str:
        return f"<DCFCashFlow(project_id={self.project_id}, year_label={self.year_label}, cash_flow={self.cash_flow})>"
