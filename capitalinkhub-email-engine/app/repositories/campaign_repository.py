"""
Repository for Campaign model operations.
"""
from typing import Optional, List
from datetime import datetime
from sqlalchemy.orm import Session

from app.models import Campaign, CampaignStatus, CampaignType
from .base import BaseRepository


class CampaignRepository(BaseRepository[Campaign]):
    """Campaign-specific repository with custom query methods."""

    def __init__(self, db: Session):
        super().__init__(Campaign, db)

    def get_by_name(self, name: str) -> Optional[Campaign]:
        """Get a campaign by name."""
        return self.db.query(Campaign).filter(Campaign.name == name).first()

    def get_by_status(self, status: CampaignStatus) -> List[Campaign]:
        """Get all campaigns with a specific status."""
        return self.db.query(Campaign).filter(Campaign.status == status).all()

    def get_by_type(self, campaign_type: CampaignType) -> List[Campaign]:
        """Get all campaigns of a specific type."""
        return self.db.query(Campaign).filter(Campaign.type == campaign_type).all()

    def get_scheduled_campaigns(self, current_time: Optional[datetime] = None) -> List[Campaign]:
        """
        Get campaigns that are scheduled to run.
        Returns campaigns with status 'scheduled' or 'sending' and scheduled_at <= current_time.
        """
        if current_time is None:
            current_time = datetime.utcnow()

        return (
            self.db.query(Campaign)
            .filter(
                Campaign.status.in_([CampaignStatus.SCHEDULED, CampaignStatus.SENDING]),
                Campaign.scheduled_at <= current_time
            )
            .all()
        )

    def get_active_campaigns(self) -> List[Campaign]:
        """Get all active campaigns (scheduled or sending)."""
        return (
            self.db.query(Campaign)
            .filter(Campaign.status.in_([CampaignStatus.SCHEDULED, CampaignStatus.SENDING]))
            .all()
        )

    def update_status(self, campaign: Campaign, new_status: CampaignStatus) -> Campaign:
        """Update campaign status."""
        campaign.status = new_status
        self.db.flush()
        return campaign

    def schedule_campaign(self, campaign: Campaign, scheduled_at: datetime) -> Campaign:
        """Schedule a campaign for sending."""
        campaign.scheduled_at = scheduled_at
        campaign.status = CampaignStatus.SCHEDULED
        self.db.flush()
        return campaign
