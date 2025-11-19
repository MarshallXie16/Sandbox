"""
Pydantic schemas for Introduced Buyers.
"""

from datetime import datetime
from typing import Optional
from pydantic import Field

from app.schemas.base import BaseSchema, TimestampMixin
from app.models.enums import BuyerIntroStatus, IntroductionChannel


class BuyerIntroBase(BaseSchema):
    """Base buyer intro schema with common fields."""

    buyer_contact_id: int = Field(..., description="CRM contact ID for the buyer")
    introduction_channel: IntroductionChannel = Field(
        default=IntroductionChannel.EMAIL,
        description="Channel through which buyer was introduced"
    )
    notes: Optional[str] = Field(None, description="Notes about the introduction")


class BuyerIntroCreate(BuyerIntroBase):
    """Schema for creating a new buyer introduction."""

    pass


class BuyerIntroUpdate(BaseSchema):
    """Schema for updating a buyer introduction."""

    status: Optional[BuyerIntroStatus] = None
    introduction_channel: Optional[IntroductionChannel] = None
    notes: Optional[str] = None


class BuyerIntroSetStatus(BaseSchema):
    """Schema for setting buyer intro status."""

    status: BuyerIntroStatus = Field(..., description="New status")
    notes: Optional[str] = Field(None, description="Notes about the status change")


class BuyerIntroResponse(BuyerIntroBase, TimestampMixin):
    """Schema for buyer intro response."""

    id: int
    engagement_id: int
    status: BuyerIntroStatus
    introduced_at: datetime = Field(..., description="When buyer was introduced")
    nda_sent_at: Optional[datetime] = None
    nda_signed_at: Optional[datetime] = None
    teaser_sent_at: Optional[datetime] = None
    info_access_granted_at: Optional[datetime] = None
    last_contact_at: Optional[datetime] = None

    # Counts (populated by service layer if needed)
    offer_count: Optional[int] = Field(None, description="Number of offers from this buyer")
