"""DCFParameter model - manually entered DCF configuration per project."""
from sqlalchemy import Column, Integer, String, Numeric, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
from app.database import Base, GUID


class DCFParameter(Base):
    """DCF parameters manually entered per project (no auto-inference)."""

    __tablename__ = "dcf_parameters"

    # Primary key
    id = Column(GUID, primary_key=True, default=uuid.uuid4)

    # Foreign key (one-to-one with Project)
    project_id = Column(GUID, ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, unique=True, index=True)

    # Base configuration
    base_metric = Column(String(50), nullable=False)  # 'EBITDA', 'SDE', or 'FCF'
    base_year = Column(Integer, nullable=False)  # Year from normalized_financials used as starting point

    # DCF parameters
    discount_rate = Column(Numeric(precision=10, scale=6), nullable=False)  # e.g., 0.18 = 18%
    projection_years = Column(Integer, nullable=False)  # e.g., 3, 5

    # Terminal value calculation
    terminal_method = Column(String(50), nullable=False)  # 'terminal_growth' or 'exit_multiple'
    terminal_growth_rate = Column(Numeric(precision=10, scale=6))  # Used if terminal_method='terminal_growth'
    terminal_multiple = Column(Numeric(precision=10, scale=2))  # Used if terminal_method='exit_multiple'

    # Cash flow approach
    use_explicit_cash_flows = Column(Boolean, nullable=False, default=False)  # If true, use manually entered cash flows

    # Notes
    notes = Column(Text)

    # Timestamps
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    project = relationship("Project", back_populates="dcf_parameters")

    def __repr__(self) -> str:
        return f"<DCFParameter(project_id={self.project_id}, base_metric={self.base_metric}, discount_rate={self.discount_rate})>"
