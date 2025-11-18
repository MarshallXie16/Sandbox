"""Deal model with extensible details field"""
from sqlalchemy import Column, Integer, String, Float, Date, DateTime, ForeignKey, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import enum
from app.db.base import Base
from app.models.pipeline import PipelineType


class DealStatus(str, enum.Enum):
    """Deal status enumeration"""
    OPEN = "open"
    WON = "won"
    LOST = "lost"


class Deal(Base):
    """
    Deal entity representing a sales opportunity.

    Core Fields:
        - Deal identification (name, amount, currency)
        - Pipeline and stage tracking
        - Owner assignment
        - Status and timeline
        - Extensible details (JSONB) for custom fields

    Details Field Can Include:
        - Loss reason (for lost deals)
        - Win notes
        - Custom deal attributes
        - Integration metadata

    Relationships:
        - Many-to-one with DealPipeline
        - Many-to-one with DealStage
        - Many-to-many with Contacts via ContactDeal
        - Many-to-many with Companies via CompanyDeal
        - Many-to-many with Activities via ActivityDeal
    """

    __tablename__ = "deals"

    # Primary key
    id = Column(Integer, primary_key=True, index=True)

    # Deal information
    name = Column(String(255), nullable=False, index=True)

    # Pipeline tracking
    pipeline_type = Column(
        SQLEnum(PipelineType, name="pipeline_type_enum"),
        nullable=False,
        index=True,
    )
    pipeline_id = Column(Integer, ForeignKey("deal_pipelines.id"), nullable=False)
    stage_id = Column(Integer, ForeignKey("deal_stages.id"), nullable=False)

    # Financial
    amount = Column(Float, nullable=True)
    currency = Column(String(3), default="USD", nullable=False)  # ISO 4217 code

    # Timeline
    expected_close_date = Column(Date, nullable=True)

    # Ownership (could be FK to User model in future)
    owner_id = Column(Integer, nullable=True)  # Reference to user who owns deal

    # Status
    status = Column(
        SQLEnum(DealStatus, name="deal_status_enum"),
        nullable=False,
        default=DealStatus.OPEN,
        index=True,
    )

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

    # Relationships
    pipeline = relationship("DealPipeline", back_populates="deals")
    stage = relationship("DealStage", back_populates="deals")

    contacts = relationship(
        "ContactDeal",
        back_populates="deal",
        cascade="all, delete-orphan",
    )
    companies = relationship(
        "CompanyDeal",
        back_populates="deal",
        cascade="all, delete-orphan",
    )
    activities = relationship(
        "ActivityDeal",
        back_populates="deal",
        cascade="all, delete-orphan",
    )

    def __repr__(self):
        return f"<Deal(id={self.id}, name='{self.name}', status='{self.status}')>"
