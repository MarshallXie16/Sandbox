"""
Repository for Recipient model operations.
"""
from typing import Optional, List
from sqlalchemy.orm import Session

from app.models import Recipient, RecipientStatus, RecipientSegment
from .base import BaseRepository


class RecipientRepository(BaseRepository[Recipient]):
    """Recipient-specific repository with custom query methods."""

    def __init__(self, db: Session):
        super().__init__(Recipient, db)

    def get_by_campaign(self, campaign_id: int, skip: int = 0, limit: int = 100) -> List[Recipient]:
        """Get all recipients for a specific campaign."""
        return (
            self.db.query(Recipient)
            .filter(Recipient.campaign_id == campaign_id)
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_by_campaign_and_status(
        self, campaign_id: int, status: RecipientStatus, limit: Optional[int] = None
    ) -> List[Recipient]:
        """Get recipients for a campaign with a specific status."""
        query = self.db.query(Recipient).filter(
            Recipient.campaign_id == campaign_id,
            Recipient.status == status
        )
        if limit:
            query = query.limit(limit)
        return query.all()

    def get_pending_recipients(self, campaign_id: int, limit: Optional[int] = None) -> List[Recipient]:
        """Get all pending recipients for a campaign."""
        return self.get_by_campaign_and_status(campaign_id, RecipientStatus.PENDING, limit)

    def get_by_email(self, email: str) -> List[Recipient]:
        """Get all recipient records with a specific email."""
        return self.db.query(Recipient).filter(Recipient.email == email).all()

    def get_by_segment(self, segment: RecipientSegment) -> List[Recipient]:
        """Get all recipients in a specific segment."""
        return self.db.query(Recipient).filter(Recipient.segment == segment).all()

    def update_status(
        self, recipient: Recipient, new_status: RecipientStatus, error: Optional[str] = None
    ) -> Recipient:
        """Update recipient status and optionally set error message."""
        recipient.status = new_status
        if error:
            recipient.last_error = error
        self.db.flush()
        return recipient

    def count_by_campaign(self, campaign_id: int) -> int:
        """Count total recipients for a campaign."""
        return self.db.query(Recipient).filter(Recipient.campaign_id == campaign_id).count()

    def count_by_campaign_and_status(self, campaign_id: int, status: RecipientStatus) -> int:
        """Count recipients for a campaign with a specific status."""
        return (
            self.db.query(Recipient)
            .filter(Recipient.campaign_id == campaign_id, Recipient.status == status)
            .count()
        )

    def bulk_create(self, recipients_data: List[dict]) -> List[Recipient]:
        """Bulk create recipients."""
        recipients = [Recipient(**data) for data in recipients_data]
        self.db.bulk_save_objects(recipients, return_defaults=True)
        self.db.flush()
        return recipients
