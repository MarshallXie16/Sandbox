"""Pipeline and Stage models for deal management"""
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship
import enum
from app.db.base import Base


class PipelineType(str, enum.Enum):
    """Pipeline type enumeration"""
    SELLER = "seller"
    BUYER = "buyer"


class DealPipeline(Base):
    """
    Deal pipeline definition.

    Pipelines are stored in the database (not hard-coded) and can be
    created, updated, or archived via API. Each pipeline has a type
    (seller or buyer) and contains multiple stages.

    Default Pipelines:
        - Seller Pipeline: Exit Ready → Facilitator → Broker → Marketing
                          → LOI → Due Diligence → Closing → Won/Lost
        - Buyer Pipeline: Buyer Access → Finder → Broker → Marketing
                         → LOI → Due Diligence → Closing → Won/Lost

    Relationships:
        - One-to-many with DealStage
        - One-to-many with Deal
    """

    __tablename__ = "deal_pipelines"

    # Primary key
    id = Column(Integer, primary_key=True, index=True)

    # Pipeline details
    name = Column(String(100), nullable=False, unique=True)
    type = Column(
        SQLEnum(PipelineType, name="pipeline_type_enum"),
        nullable=False,
        index=True,
    )
    is_active = Column(Boolean, default=True, nullable=False)

    # Relationships
    stages = relationship(
        "DealStage",
        back_populates="pipeline",
        cascade="all, delete-orphan",
        order_by="DealStage.order_index",
    )
    deals = relationship("Deal", back_populates="pipeline")

    def __repr__(self):
        return f"<DealPipeline(id={self.id}, name='{self.name}', type='{self.type}')>"


class DealStage(Base):
    """
    Deal stage within a pipeline.

    Stages define the progression steps within a pipeline. Each stage
    has an order index for positioning and flags to indicate terminal
    states (won/lost).

    Key Attributes:
        - order_index: Determines stage order in pipeline (lower = earlier)
        - is_closed_won: True if this stage represents a successful close
        - is_closed_lost: True if this stage represents a failed close

    Relationships:
        - Many-to-one with DealPipeline
        - One-to-many with Deal
    """

    __tablename__ = "deal_stages"

    # Primary key
    id = Column(Integer, primary_key=True, index=True)

    # Foreign key
    pipeline_id = Column(Integer, ForeignKey("deal_pipelines.id"), nullable=False)

    # Stage details
    name = Column(String(100), nullable=False)
    order_index = Column(Integer, nullable=False)  # Lower values come first
    is_closed_won = Column(Boolean, default=False, nullable=False)
    is_closed_lost = Column(Boolean, default=False, nullable=False)

    # Relationships
    pipeline = relationship("DealPipeline", back_populates="stages")
    deals = relationship("Deal", back_populates="stage")

    def __repr__(self):
        return f"<DealStage(id={self.id}, name='{self.name}', order={self.order_index})>"
