"""Activity model for tracking interactions"""
from sqlalchemy import Column, Integer, String, Text, DateTime, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import enum
from app.db.base import Base


class ActivityType(str, enum.Enum):
    """Activity type enumeration"""
    EMAIL = "email"
    CALL = "call"
    MEETING = "meeting"
    LINKEDIN = "linkedin"
    WHATSAPP = "whatsapp"
    WECHAT = "wechat"
    NOTE = "note"


class ActivityDirection(str, enum.Enum):
    """Activity direction enumeration"""
    INCOMING = "incoming"
    OUTGOING = "outgoing"


class Activity(Base):
    """
    Activity entity for tracking all interactions.

    Core Fields:
        - Type (email, call, meeting, social, note)
        - Subject and content
        - Direction (incoming/outgoing)
        - Timestamp
        - Owner assignment
        - Extensible details (JSONB) for custom fields

    Details Field Can Include:
        - Email metadata (thread_id, message_id, cc, bcc)
        - Call metadata (duration, recording_url)
        - Meeting metadata (location, attendees, video_url)
        - Social media metadata (post_url, engagement_metrics)
        - Integration metadata

    Relationships:
        - Many-to-many with Contacts via ActivityContact
        - Many-to-many with Companies via ActivityCompany
        - Many-to-many with Deals via ActivityDeal
    """

    __tablename__ = "activities"

    # Primary key
    id = Column(Integer, primary_key=True, index=True)

    # Activity details
    type = Column(
        SQLEnum(ActivityType, name="activity_type_enum"),
        nullable=False,
        index=True,
    )
    subject = Column(String(500), nullable=True)
    content = Column(Text, nullable=True)

    # Direction
    direction = Column(
        SQLEnum(ActivityDirection, name="activity_direction_enum"),
        nullable=True,
    )

    # Timeline
    happened_at = Column(
        DateTime(timezone=True),
        nullable=False,
        index=True,
        server_default=func.now(),
    )

    # Ownership (could be FK to User model in future)
    owner_id = Column(Integer, nullable=True)  # Reference to user who created activity

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
        "ActivityContact",
        back_populates="activity",
        cascade="all, delete-orphan",
    )
    companies = relationship(
        "ActivityCompany",
        back_populates="activity",
        cascade="all, delete-orphan",
    )
    deals = relationship(
        "ActivityDeal",
        back_populates="activity",
        cascade="all, delete-orphan",
    )

    def __repr__(self):
        return f"<Activity(id={self.id}, type='{self.type}', subject='{self.subject}')>"
