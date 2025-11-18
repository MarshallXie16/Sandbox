"""
SQLAlchemy models representing IndieStack CRM schema.

These models reflect the expected schema of indie-crm-core database.
They are used for database integration mode.
"""

from datetime import datetime
from typing import Optional

from sqlalchemy import Column, Integer, String, DateTime, Float, ForeignKey, Text, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

IndieBase = declarative_base()


class IndieContact(IndieBase):
    """Contact entity in IndieStack CRM."""

    __tablename__ = "contacts"

    id = Column(Integer, primary_key=True, index=True)

    # Basic fields
    first_name = Column(String, nullable=True)
    last_name = Column(String, nullable=True)
    primary_email = Column(String, nullable=True, index=True)
    phone = Column(String, nullable=True)
    job_title = Column(String, nullable=True)

    # Custom fields
    category = Column(String, nullable=True)
    lifecycle_stage = Column(String, nullable=True)
    source = Column(String, nullable=True)

    # Relationships
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=True)

    # JSON/metadata fields (stored as TEXT, parsed as JSON)
    details = Column(Text, nullable=True)  # JSON: {engagement_score, etc.}

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    def __repr__(self) -> str:
        return f"<IndieContact(id={self.id}, email={self.primary_email})>"


class IndieCompany(IndieBase):
    """Company entity in IndieStack CRM."""

    __tablename__ = "companies"

    id = Column(Integer, primary_key=True, index=True)

    # Basic fields
    name = Column(String, nullable=False)
    website = Column(String, nullable=True)
    phone = Column(String, nullable=True)
    industry = Column(String, nullable=True)

    # Address fields
    address = Column(String, nullable=True)
    city = Column(String, nullable=True)
    state = Column(String, nullable=True)
    country = Column(String, nullable=True)
    postal_code = Column(String, nullable=True)

    # Custom fields
    revenue = Column(Float, nullable=True)
    employee_count = Column(Integer, nullable=True)
    company_type = Column(String, nullable=True)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    contacts = relationship("IndieContact", backref="company")

    def __repr__(self) -> str:
        return f"<IndieCompany(id={self.id}, name={self.name})>"


class IndieDeal(IndieBase):
    """Deal entity in IndieStack CRM."""

    __tablename__ = "deals"

    id = Column(Integer, primary_key=True, index=True)

    # Basic fields
    name = Column(String, nullable=False)
    amount = Column(Float, nullable=True)
    close_date = Column(DateTime, nullable=True)
    description = Column(Text, nullable=True)

    # Pipeline/stage
    pipeline_id = Column(Integer, nullable=True)
    stage_id = Column(Integer, nullable=True)

    # Custom fields
    deal_type = Column(String, nullable=True)
    priority = Column(String, nullable=True)
    probability = Column(Float, nullable=True)

    # Relationships
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=True)

    # JSON fields for associated contacts
    contacts = Column(Text, nullable=True)  # JSON array of contact IDs

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    def __repr__(self) -> str:
        return f"<IndieDeal(id={self.id}, name={self.name}, amount={self.amount})>"
