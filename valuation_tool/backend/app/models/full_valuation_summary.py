"""FullValuationSummary model - weighted final valuation combining all approaches."""
from sqlalchemy import Column, Numeric, String, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
from app.database import Base, GUID


class FullValuationSummary(Base):
    """Weighted final valuation combining Market, DCF, and optionally Asset-based approaches."""

    __tablename__ = "full_valuation_summaries"

    # Primary key
    id = Column(GUID, primary_key=True, default=uuid.uuid4)

    # Foreign key (one-to-one with Project)
    project_id = Column(GUID, ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, unique=True, index=True)

    # Input values from different approaches
    market_value_mid = Column(Numeric(precision=15, scale=2))  # From valuation_summary
    dcf_value = Column(Numeric(precision=15, scale=2))  # From dcf_results.dcf_equity_value
    asset_value = Column(Numeric(precision=15, scale=2))  # Manually entered (optional)

    # Weights for each approach
    weight_market = Column(Numeric(precision=5, scale=4), nullable=False)  # e.g., 0.6 = 60%
    weight_dcf = Column(Numeric(precision=5, scale=4), nullable=False)  # e.g., 0.3 = 30%
    weight_asset = Column(Numeric(precision=5, scale=4), nullable=False)  # e.g., 0.1 = 10%

    # Final weighted valuation range
    final_value_low = Column(Numeric(precision=15, scale=2), nullable=False)
    final_value_mid = Column(Numeric(precision=15, scale=2), nullable=False)
    final_value_high = Column(Numeric(precision=15, scale=2), nullable=False)

    # Currency
    currency = Column(String(3), nullable=False, default="CAD")

    # Notes
    notes = Column(Text)

    # Timestamps
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    project = relationship("Project", back_populates="full_valuation_summary")

    def __repr__(self) -> str:
        return f"<FullValuationSummary(project_id={self.project_id}, final_value_mid={self.final_value_mid})>"
