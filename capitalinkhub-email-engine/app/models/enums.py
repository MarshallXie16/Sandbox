"""
Enumerations used throughout the application.
"""
import enum


class CampaignType(str, enum.Enum):
    """Types of email campaigns."""
    COLD = "cold"
    MEMBER = "member"
    WARM = "warm"


class CampaignStatus(str, enum.Enum):
    """Campaign execution status."""
    DRAFT = "draft"
    SCHEDULED = "scheduled"
    SENDING = "sending"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"


class EmailBackend(str, enum.Enum):
    """Available email sending backends."""
    SENDY = "sendy"
    SMTP = "smtp"


class RecipientSegment(str, enum.Enum):
    """Recipient segmentation categories."""
    BUYER = "buyer"
    SELLER = "seller"
    INVESTOR = "investor"
    ADVISOR = "advisor"
    MEMBER = "member"
    COLD_LEAD = "cold_lead"
    OTHER = "other"


class RecipientStatus(str, enum.Enum):
    """Status of individual recipients."""
    PENDING = "pending"
    SENT = "sent"
    FAILED = "failed"
    BOUNCED = "bounced"
    UNSUBSCRIBED = "unsubscribed"


class SendStatus(str, enum.Enum):
    """Status of individual send attempts."""
    SUCCESS = "success"
    FAILED = "failed"
    BOUNCED = "bounced"
