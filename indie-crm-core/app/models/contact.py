"""Contact model with extensible details field"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import enum
from app.db.base import Base


class ContactCategory(str, enum.Enum):
    """Contact category enumeration"""
    SELLER = "seller"
    BUYER = "buyer"
    BANKER = "banker"
    LAWYER = "lawyer"
    ACCOUNTANT = "accountant"
    INVESTOR = "investor"
    OTHER = "other"


class Contact(Base):
    """
    Contact entity with flexible schema via JSONB details field.

    Core Fields:
        - Basic contact info (name, email, phone, social)
        - Category-specific fields (seller/buyer attributes)
        - Extensible details (JSONB) for custom fields

    Category-Specific Fields (in details JSON):
        Sellers:
            - timeline_to_sell: str
            - pain_points: str
            - expectation: str

        Buyers:
            - industry: str
            - budget: float
            - geographic_preference: str
            - passive_ownership: bool
            - timeline_to_buy: str
            - financial_capacity_verification: str
            - background_experience: str

    Relationships:
        - Many-to-many with Companies via ContactCompany
        - Many-to-many with Deals via ContactDeal
        - Many-to-many with Activities via ActivityContact
    """

    __tablename__ = "contacts"

    # Primary key
    id = Column(Integer, primary_key=True, index=True)

    # Basic information
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    primary_email = Column(String(255), unique=True, nullable=False, index=True)
    secondary_email = Column(String(255), nullable=True)
    phone = Column(String(50), nullable=True)

    # Social/Communication
    linkedin_url = Column(String(500), nullable=True)
    whatsapp = Column(String(50), nullable=True)
    wechat = Column(String(100), nullable=True)
    primary_language = Column(String(50), default="English")

    # Classification
    category = Column(
        SQLEnum(ContactCategory, name="contact_category_enum"),
        nullable=False,
        default=ContactCategory.OTHER,
        index=True,
    )
    is_active = Column(Boolean, default=True, nullable=False, index=True)

    # Extensible details field for custom attributes
    # Store category-specific fields and any future custom fields
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
    companies = relationship(
        "ContactCompany",
        back_populates="contact",
        cascade="all, delete-orphan",
    )
    deals = relationship(
        "ContactDeal",
        back_populates="contact",
        cascade="all, delete-orphan",
    )
    activities = relationship(
        "ActivityContact",
        back_populates="contact",
        cascade="all, delete-orphan",
    )

    def __repr__(self):
        return f"<Contact(id={self.id}, name='{self.first_name} {self.last_name}', email='{self.primary_email}')>"
