"""
SQLAlchemy models for IndieStack CRM entities.

These are minimal models that map to existing tables in the IndieStack CRM database.
They are used for read-only operations and basic updates.
"""

from datetime import datetime
from typing import Optional
from sqlalchemy import String, Integer, DateTime, Text, Numeric, TIMESTAMP, JSON
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class Contact(Base):
    """
    Contact model - maps to IndieStack CRM contacts table.
    """

    __tablename__ = "contacts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    first_name: Mapped[Optional[str]] = mapped_column(String(100))
    last_name: Mapped[Optional[str]] = mapped_column(String(100))
    primary_email: Mapped[Optional[str]] = mapped_column(String(255), index=True)
    phone: Mapped[Optional[str]] = mapped_column(String(50))
    category: Mapped[Optional[str]] = mapped_column(String(50))  # buyer, seller, both
    title: Mapped[Optional[str]] = mapped_column(String(100))
    company_id: Mapped[Optional[int]] = mapped_column(Integer)
    details: Mapped[Optional[dict]] = mapped_column(JSON)  # JSONB field for flexible data
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP, default=datetime.utcnow, nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        TIMESTAMP, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    def __repr__(self) -> str:
        return f"<Contact(id={self.id}, email={self.primary_email}, category={self.category})>"


class Company(Base):
    """
    Company model - maps to IndieStack CRM companies table.
    """

    __tablename__ = "companies"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    website: Mapped[Optional[str]] = mapped_column(String(255))
    industry: Mapped[Optional[str]] = mapped_column(String(100), index=True)
    region: Mapped[Optional[str]] = mapped_column(String(100), index=True)
    revenue: Mapped[Optional[float]] = mapped_column(Numeric(15, 2))
    ebitda: Mapped[Optional[float]] = mapped_column(Numeric(15, 2))
    size: Mapped[Optional[str]] = mapped_column(String(50))  # e.g., "1-10", "11-50"
    description: Mapped[Optional[str]] = mapped_column(Text)
    details: Mapped[Optional[dict]] = mapped_column(JSON)  # JSONB field
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP, default=datetime.utcnow, nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        TIMESTAMP, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    def __repr__(self) -> str:
        return f"<Company(id={self.id}, name={self.name}, industry={self.industry})>"


class Deal(Base):
    """
    Deal model - maps to IndieStack CRM deals table.
    Represents a business listing or sales opportunity.
    """

    __tablename__ = "deals"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    amount: Mapped[Optional[float]] = mapped_column(Numeric(15, 2))  # Asking price
    stage_id: Mapped[Optional[int]] = mapped_column(Integer)
    status: Mapped[Optional[str]] = mapped_column(String(50), index=True)  # Active, Closed, etc.
    company_id: Mapped[Optional[int]] = mapped_column(Integer, index=True)
    owner_contact_id: Mapped[Optional[int]] = mapped_column(Integer)  # Seller contact
    expected_close_date: Mapped[Optional[datetime]] = mapped_column(DateTime)
    details: Mapped[Optional[dict]] = mapped_column(JSON)  # JSONB field
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP, default=datetime.utcnow, nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        TIMESTAMP, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    def __repr__(self) -> str:
        return f"<Deal(id={self.id}, name={self.name}, status={self.status})>"


class Activity(Base):
    """
    Activity model - maps to IndieStack CRM activities table.
    Represents timeline events, notes, and interactions.
    """

    __tablename__ = "activities"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    activity_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    subject: Mapped[Optional[str]] = mapped_column(String(255))
    description: Mapped[Optional[str]] = mapped_column(Text)
    contact_id: Mapped[Optional[int]] = mapped_column(Integer, index=True)
    company_id: Mapped[Optional[int]] = mapped_column(Integer, index=True)
    deal_id: Mapped[Optional[int]] = mapped_column(Integer, index=True)
    occurred_at: Mapped[datetime] = mapped_column(
        TIMESTAMP, default=datetime.utcnow, nullable=False
    )
    metadata: Mapped[Optional[dict]] = mapped_column(JSON)  # JSONB field
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP, default=datetime.utcnow, nullable=False
    )

    def __repr__(self) -> str:
        return f"<Activity(id={self.id}, type={self.activity_type}, contact_id={self.contact_id})>"
