"""Project model - represents a valuation project."""
from sqlalchemy import Column, String, DateTime, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
from app.database import Base, GUID


class Project(Base):
    """Main project entity for business valuation."""

    __tablename__ = "projects"

    # Primary key
    id = Column(GUID, primary_key=True, default=uuid.uuid4)

    # Project info
    project_name = Column(String(255), nullable=False)
    business_name = Column(String(255), nullable=False)
    industry = Column(String(100), nullable=False)
    currency = Column(String(3), nullable=False, default="CAD")

    # Optional metadata
    description = Column(Text)
    advisor_notes = Column(Text)

    # Timestamps
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    financial_inputs = relationship(
        "FinancialInput",
        back_populates="project",
        cascade="all, delete-orphan"
    )
    valuation_summary = relationship(
        "ValuationSummary",
        back_populates="project",
        uselist=False,
        cascade="all, delete-orphan"
    )
    normalization_entries = relationship(
        "NormalizationEntry",
        back_populates="project",
        cascade="all, delete-orphan"
    )
    normalized_financials = relationship(
        "NormalizedFinancial",
        back_populates="project",
        cascade="all, delete-orphan"
    )
    dcf_parameters = relationship(
        "DCFParameter",
        back_populates="project",
        uselist=False,
        cascade="all, delete-orphan"
    )
    dcf_cash_flows = relationship(
        "DCFCashFlow",
        back_populates="project",
        cascade="all, delete-orphan"
    )
    dcf_result = relationship(
        "DCFResult",
        back_populates="project",
        uselist=False,
        cascade="all, delete-orphan"
    )
    full_valuation_summary = relationship(
        "FullValuationSummary",
        back_populates="project",
        uselist=False,
        cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Project(id={self.id}, name={self.project_name}, business={self.business_name})>"
