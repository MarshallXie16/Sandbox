"""Association tables for many-to-many relationships"""
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from app.db.base import Base


class ContactCompany(Base):
    """
    Association between Contact and Company.

    Attributes:
        role: The contact's role at the company (e.g., "CEO", "CFO", "Board Member")
        is_primary: Whether this is the contact's primary company affiliation
    """

    __tablename__ = "contact_companies"

    id = Column(Integer, primary_key=True, index=True)
    contact_id = Column(Integer, ForeignKey("contacts.id", ondelete="CASCADE"), nullable=False)
    company_id = Column(Integer, ForeignKey("companies.id", ondelete="CASCADE"), nullable=False)
    role = Column(String(100), nullable=True)
    is_primary = Column(Boolean, default=False, nullable=False)

    # Ensure unique contact-company pairs
    __table_args__ = (
        UniqueConstraint("contact_id", "company_id", name="uq_contact_company"),
    )

    # Relationships
    contact = relationship("Contact", back_populates="companies")
    company = relationship("Company", back_populates="contacts")

    def __repr__(self):
        return f"<ContactCompany(contact_id={self.contact_id}, company_id={self.company_id}, role='{self.role}')>"


class ContactDeal(Base):
    """
    Association between Contact and Deal.

    Attributes:
        role: The contact's role in the deal (e.g., "Decision Maker", "Influencer", "Champion")
    """

    __tablename__ = "contact_deals"

    id = Column(Integer, primary_key=True, index=True)
    contact_id = Column(Integer, ForeignKey("contacts.id", ondelete="CASCADE"), nullable=False)
    deal_id = Column(Integer, ForeignKey("deals.id", ondelete="CASCADE"), nullable=False)
    role = Column(String(100), nullable=True)

    # Ensure unique contact-deal pairs
    __table_args__ = (
        UniqueConstraint("contact_id", "deal_id", name="uq_contact_deal"),
    )

    # Relationships
    contact = relationship("Contact", back_populates="deals")
    deal = relationship("Deal", back_populates="contacts")

    def __repr__(self):
        return f"<ContactDeal(contact_id={self.contact_id}, deal_id={self.deal_id}, role='{self.role}')>"


class CompanyDeal(Base):
    """
    Association between Company and Deal.

    Attributes:
        role: The company's role in the deal (e.g., "Buyer", "Seller", "Advisor")
    """

    __tablename__ = "company_deals"

    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id", ondelete="CASCADE"), nullable=False)
    deal_id = Column(Integer, ForeignKey("deals.id", ondelete="CASCADE"), nullable=False)
    role = Column(String(100), nullable=True)

    # Ensure unique company-deal pairs
    __table_args__ = (
        UniqueConstraint("company_id", "deal_id", name="uq_company_deal"),
    )

    # Relationships
    company = relationship("Company", back_populates="deals")
    deal = relationship("Deal", back_populates="companies")

    def __repr__(self):
        return f"<CompanyDeal(company_id={self.company_id}, deal_id={self.deal_id}, role='{self.role}')>"


class ActivityContact(Base):
    """Association between Activity and Contact."""

    __tablename__ = "activity_contacts"

    id = Column(Integer, primary_key=True, index=True)
    activity_id = Column(Integer, ForeignKey("activities.id", ondelete="CASCADE"), nullable=False)
    contact_id = Column(Integer, ForeignKey("contacts.id", ondelete="CASCADE"), nullable=False)

    # Ensure unique activity-contact pairs
    __table_args__ = (
        UniqueConstraint("activity_id", "contact_id", name="uq_activity_contact"),
    )

    # Relationships
    activity = relationship("Activity", back_populates="contacts")
    contact = relationship("Contact", back_populates="activities")

    def __repr__(self):
        return f"<ActivityContact(activity_id={self.activity_id}, contact_id={self.contact_id})>"


class ActivityCompany(Base):
    """Association between Activity and Company."""

    __tablename__ = "activity_companies"

    id = Column(Integer, primary_key=True, index=True)
    activity_id = Column(Integer, ForeignKey("activities.id", ondelete="CASCADE"), nullable=False)
    company_id = Column(Integer, ForeignKey("companies.id", ondelete="CASCADE"), nullable=False)

    # Ensure unique activity-company pairs
    __table_args__ = (
        UniqueConstraint("activity_id", "company_id", name="uq_activity_company"),
    )

    # Relationships
    activity = relationship("Activity", back_populates="companies")
    company = relationship("Company", back_populates="activities")

    def __repr__(self):
        return f"<ActivityCompany(activity_id={self.activity_id}, company_id={self.company_id})>"


class ActivityDeal(Base):
    """Association between Activity and Deal."""

    __tablename__ = "activity_deals"

    id = Column(Integer, primary_key=True, index=True)
    activity_id = Column(Integer, ForeignKey("activities.id", ondelete="CASCADE"), nullable=False)
    deal_id = Column(Integer, ForeignKey("deals.id", ondelete="CASCADE"), nullable=False)

    # Ensure unique activity-deal pairs
    __table_args__ = (
        UniqueConstraint("activity_id", "deal_id", name="uq_activity_deal"),
    )

    # Relationships
    activity = relationship("Activity", back_populates="deals")
    deal = relationship("Deal", back_populates="activities")

    def __repr__(self):
        return f"<ActivityDeal(activity_id={self.activity_id}, deal_id={self.deal_id})>"
