"""DCFResult model - DCF valuation output."""
from sqlalchemy import Column, String, Numeric, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
from app.database import Base, GUID


class DCFResult(Base):
    """DCF valuation results for a project."""

    __tablename__ = "dcf_results"

    # Primary key
    id = Column(GUID, primary_key=True, default=uuid.uuid4)

    # Foreign key (one-to-one with Project)
    project_id = Column(GUID, ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, unique=True, index=True)

    # DCF calculation results
    present_value_of_cash_flows = Column(Numeric(precision=15, scale=2), nullable=False)
    terminal_value = Column(Numeric(precision=15, scale=2), nullable=False)
    present_value_of_terminal_value = Column(Numeric(precision=15, scale=2), nullable=False)
    dcf_equity_value = Column(Numeric(precision=15, scale=2), nullable=False)  # Main DCF conclusion

    # Currency
    currency = Column(String(3), nullable=False, default="CAD")

    # Timestamps
    created_at = Column(DateTime, server_default=func.now(), nullable=False)

    # Relationships
    project = relationship("Project", back_populates="dcf_result")

    def __repr__(self) -> str:
        return f"<DCFResult(project_id={self.project_id}, dcf_equity_value={self.dcf_equity_value})>"
