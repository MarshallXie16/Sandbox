"""
Pydantic schemas for Facilitator Automation API.
"""

from app.schemas.base import (
    BaseSchema,
    TimestampMixin,
    PaginationParams,
    PaginatedResponse,
    SuccessResponse,
    ErrorResponse,
)
from app.schemas.engagement import (
    EngagementBase,
    EngagementCreate,
    EngagementUpdate,
    EngagementSetStatus,
    EngagementResponse,
    EngagementSummary,
)
from app.schemas.buyer_intro import (
    BuyerIntroBase,
    BuyerIntroCreate,
    BuyerIntroUpdate,
    BuyerIntroSetStatus,
    BuyerIntroResponse,
)
from app.schemas.offer import (
    OfferBase,
    OfferCreate,
    OfferUpdate,
    OfferSetStatus,
    OfferMarkFee,
    OfferResponse,
)
from app.schemas.closing import (
    ClosingBase,
    ClosingCreate,
    ClosingUpdate,
    ClosingMarkInvoiced,
    ClosingResponse,
)
from app.schemas.event import (
    EventBase,
    EventCreate,
    EventResponse,
    EventFilter,
)

__all__ = [
    # Base
    "BaseSchema",
    "TimestampMixin",
    "PaginationParams",
    "PaginatedResponse",
    "SuccessResponse",
    "ErrorResponse",
    # Engagement
    "EngagementBase",
    "EngagementCreate",
    "EngagementUpdate",
    "EngagementSetStatus",
    "EngagementResponse",
    "EngagementSummary",
    # BuyerIntro
    "BuyerIntroBase",
    "BuyerIntroCreate",
    "BuyerIntroUpdate",
    "BuyerIntroSetStatus",
    "BuyerIntroResponse",
    # Offer
    "OfferBase",
    "OfferCreate",
    "OfferUpdate",
    "OfferSetStatus",
    "OfferMarkFee",
    "OfferResponse",
    # Closing
    "ClosingBase",
    "ClosingCreate",
    "ClosingUpdate",
    "ClosingMarkInvoiced",
    "ClosingResponse",
    # Event
    "EventBase",
    "EventCreate",
    "EventResponse",
    "EventFilter",
]
