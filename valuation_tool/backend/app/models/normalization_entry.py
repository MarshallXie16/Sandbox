"""NormalizationEntry model - recast adjustments for normalized financials."""
from sqlalchemy import Column, Integer, String, Numeric, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
from app.database import Base, GUID


class NormalizationEntry(Base):
    """Recast adjustments (addbacks/reductions) applied to historical financials."""

    __tablename__ = "normalization_entries"

    # Primary key
    id = Column(GUID, primary_key=True, default=uuid.uuid4)

    # Foreign key
    project_id = Column(GUID, ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True)

    # Year this adjustment applies to
    year = Column(Integer, nullable=False)

    # Adjustment details
    category = Column(String(100), nullable=False)  # e.g., 'owner_salary', 'one_time_expense', 'personal_expense'
    description = Column(Text, nullable=False)
    amount = Column(Numeric(precision=15, scale=2), nullable=False)  # Positive = addback, negative = reduction

    # Type of adjustment
    is_addback = Column(Boolean, nullable=False)  # True = addback to earnings, False = reduction

    # Timestamps
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    project = relationship("Project", back_populates="normalization_entries")

    def __repr__(self) -> str:
        return f"<NormalizationEntry(project_id={self.project_id}, year={self.year}, category={self.category}, amount={self.amount})>"
