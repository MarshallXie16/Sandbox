"""Company model with extensible details field"""
from sqlalchemy import Column, Integer, String, Float, DateTime
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.db.base import Base


class Company(Base):
    """
    Company entity with flexible schema via JSONB details field.

    Core Fields:
        - Basic company info (name, location, website)
        - Business metrics (revenue, employees, earnings)
        - Extensible details (JSONB) for custom fields

    Details Field Can Include:
        - Custom tags, labels, or categories
        - Additional financial metrics
        - Industry-specific attributes
        - Integration metadata (e.g., HubSpot company ID)

    Relationships:
        - Many-to-many with Contacts via ContactCompany
        - Many-to-many with Deals via CompanyDeal
        - Many-to-many with Activities via ActivityCompany
    """

    __tablename__ = "companies"

    # Primary key
    id = Column(Integer, primary_key=True, index=True)

    # Basic information
    name = Column(String(255), nullable=False, index=True)
    location = Column(String(255), nullable=True)
    website = Column(String(500), nullable=True)
    linkedin_url = Column(String(500), nullable=True)

    # Business information
    industry = Column(String(100), nullable=True, index=True)
    revenue = Column(Float, nullable=True)  # Annual revenue
    employees = Column(Integer, nullable=True)
    earnings = Column(Float, nullable=True)  # EBITDA or net earnings
    fiscal_year_end = Column(String(10), nullable=True)  # e.g., "12-31"
    founded_year = Column(Integer, nullable=True)
    recurring_arr = Column(Float, nullable=True)  # Annual Recurring Revenue

    # Extensible details field for custom attributes
    details = Column(JSONB, nullable=False, default=dict, server_default="{}")

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    # Relationships (via association tables)
    contacts = relationship(
        "ContactCompany",
        back_populates="company",
        cascade="all, delete-orphan",
    )
    deals = relationship(
        "CompanyDeal",
        back_populates="company",
        cascade="all, delete-orphan",
    )
    activities = relationship(
        "ActivityCompany",
        back_populates="company",
        cascade="all, delete-orphan",
    )

    def __repr__(self):
        return f"<Company(id={self.id}, name='{self.name}')>"
