"""ValuationSummary model - Quick Valuation results (market-based)."""
from sqlalchemy import Column, Numeric, String, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
from app.database import Base, GUID


class ValuationSummary(Base):
    """Quick Valuation results using market multiples (industry × SDE/EBITDA)."""

    __tablename__ = "valuation_summaries"

    # Primary key
    id = Column(GUID, primary_key=True, default=uuid.uuid4)

    # Foreign key (one-to-one with Project)
    project_id = Column(GUID, ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, unique=True, index=True)

    # Valuation ranges
    value_low = Column(Numeric(precision=15, scale=2), nullable=False)
    value_mid = Column(Numeric(precision=15, scale=2), nullable=False)
    value_high = Column(Numeric(precision=15, scale=2), nullable=False)

    # Methodology used
    method = Column(String(50), nullable=False)  # e.g., 'sde_multiple', 'ebitda_multiple', 'revenue_multiple'

    # Multiple used
    multiple_low = Column(Numeric(precision=10, scale=2))
    multiple_mid = Column(Numeric(precision=10, scale=2))
    multiple_high = Column(Numeric(precision=10, scale=2))

    # Base metric used
    base_metric_value = Column(Numeric(precision=15, scale=2))  # The SDE/EBITDA/Revenue value used
    base_metric_type = Column(String(50))  # 'SDE', 'EBITDA', 'Revenue'

    # Currency
    currency = Column(String(3), nullable=False, default="CAD")

    # Notes
    notes = Column(Text)

    # Timestamps
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    project = relationship("Project", back_populates="valuation_summary")

    def __repr__(self) -> str:
        return f"<ValuationSummary(project_id={self.project_id}, value_mid={self.value_mid}, method={self.method})>"
