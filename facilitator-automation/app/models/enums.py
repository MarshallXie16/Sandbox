"""
Enums for Facilitator Automation domain models.
Defines valid states and types for various entities.
"""

import enum


class EngagementStatus(str, enum.Enum):
    """
    Valid states for a Facilitator Engagement.

    State machine flow:
    draft → active → (shortlisting/outreach_in_progress/offers_in_play/under_agreement) →
    (closed_success/closed_no_deal/terminated)
    """
    DRAFT = "draft"
    ACTIVE = "active"
    SHORTLISTING = "shortlisting"
    OUTREACH_IN_PROGRESS = "outreach_in_progress"
    OFFERS_IN_PLAY = "offers_in_play"
    UNDER_AGREEMENT = "under_agreement"
    CLOSED_SUCCESS = "closed_success"
    CLOSED_NO_DEAL = "closed_no_deal"
    TERMINATED = "terminated"


class BuyerIntroStatus(str, enum.Enum):
    """Valid states for an Introduced Buyer."""
    INVITED = "invited"
    NDA_PENDING = "nda_pending"
    NDA_SIGNED = "nda_signed"
    TEASER_SENT = "teaser_sent"
    INFO_ACCESS = "info_access"
    OFFER_MADE = "offer_made"
    INACTIVE = "inactive"
    NOT_INTERESTED = "not_interested"
    DROPPED = "dropped"


class OfferStatus(str, enum.Enum):
    """Valid states for an Offer."""
    RECEIVED = "received"
    UNDER_REVIEW = "under_review"
    ACCEPTED = "accepted"
    DECLINED = "declined"
    WITHDRAWN = "withdrawn"
    SUPERSEDED = "superseded"


class IntroductionChannel(str, enum.Enum):
    """Channels through which buyers can be introduced."""
    EMAIL = "email"
    PHONE = "phone"
    EVENT = "event"
    REFERRAL = "referral"
    DIRECT = "direct"
    OTHER = "other"


class EventType(str, enum.Enum):
    """Types of events for audit trail."""
    ENGAGEMENT_CREATED = "engagement_created"
    ENGAGEMENT_ACTIVATED = "engagement_activated"
    ENGAGEMENT_STATUS_CHANGED = "engagement_status_changed"
    BUYER_INTRODUCED = "buyer_introduced"
    BUYER_STATUS_CHANGED = "buyer_status_changed"
    NDA_SENT = "nda_sent"
    NDA_SIGNED = "nda_signed"
    TEASER_SENT = "teaser_sent"
    INFO_ACCESS_GRANTED = "info_access_granted"
    OFFER_RECEIVED = "offer_received"
    OFFER_STATUS_CHANGED = "offer_status_changed"
    OFFER_FEE_INVOICED = "offer_fee_invoiced"
    OFFER_FEE_PAID = "offer_fee_paid"
    CLOSING_RECORDED = "closing_recorded"
    SUCCESS_FEE_INVOICED = "success_fee_invoiced"
    SUCCESS_FEE_PAID = "success_fee_paid"
    ENGAGEMENT_TERMINATED = "engagement_terminated"
