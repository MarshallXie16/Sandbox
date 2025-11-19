"""NormalizedFinancial model - normalized earnings per year after adjustments."""
from sqlalchemy import Column, Integer, Numeric, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
from app.database import Base, GUID


class NormalizedFinancial(Base):
    """Normalized financials per year after applying recast adjustments."""

    __tablename__ = "normalized_financials"

    # Primary key
    id = Column(GUID, primary_key=True, default=uuid.uuid4)

    # Foreign key
    project_id = Column(GUID, ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True)

    # Year
    year = Column(Integer, nullable=False)

    # Normalized metrics
    normalized_revenue = Column(Numeric(precision=15, scale=2), nullable=False)
    normalized_ebitda = Column(Numeric(precision=15, scale=2))
    normalized_sde = Column(Numeric(precision=15, scale=2))
    normalized_net_income = Column(Numeric(precision=15, scale=2))

    # Notes
    notes = Column(Text)

    # Timestamps
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    project = relationship("Project", back_populates="normalized_financials")

    def __repr__(self) -> str:
        return f"<NormalizedFinancial(project_id={self.project_id}, year={self.year}, normalized_sde={self.normalized_sde})>"
