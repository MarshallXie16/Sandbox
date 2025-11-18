"""
Database models for the email campaign engine.
"""
from .enums import (
    CampaignType,
    CampaignStatus,
    EmailBackend,
    RecipientSegment,
    RecipientStatus,
    SendStatus,
)
from .campaign import Campaign
from .recipient import Recipient
from .send_log import SendLog
from .rate_limit_profile import RateLimitProfile

__all__ = [
    # Enums
    "CampaignType",
    "CampaignStatus",
    "EmailBackend",
    "RecipientSegment",
    "RecipientStatus",
    "SendStatus",
    # Models
    "Campaign",
    "Recipient",
    "SendLog",
    "RateLimitProfile",
]
