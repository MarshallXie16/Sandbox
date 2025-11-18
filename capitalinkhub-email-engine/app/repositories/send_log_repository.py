"""
Repository for SendLog model operations.
"""
from typing import Optional, List
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.models import SendLog, SendStatus, EmailBackend
from .base import BaseRepository


class SendLogRepository(BaseRepository[SendLog]):
    """SendLog-specific repository with custom query methods."""

    def __init__(self, db: Session):
        super().__init__(SendLog, db)

    def get_by_campaign(self, campaign_id: int, skip: int = 0, limit: int = 100) -> List[SendLog]:
        """Get all send logs for a specific campaign."""
        return (
            self.db.query(SendLog)
            .filter(SendLog.campaign_id == campaign_id)
            .order_by(SendLog.sent_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_by_recipient(self, recipient_id: int) -> List[SendLog]:
        """Get all send logs for a specific recipient."""
        return (
            self.db.query(SendLog)
            .filter(SendLog.recipient_id == recipient_id)
            .order_by(SendLog.sent_at.desc())
            .all()
        )

    def get_by_status(self, status: SendStatus) -> List[SendLog]:
        """Get all send logs with a specific status."""
        return self.db.query(SendLog).filter(SendLog.status == status).all()

    def count_sent_in_timeframe(
        self, campaign_id: int, start_time: datetime, end_time: Optional[datetime] = None
    ) -> int:
        """
        Count emails sent for a campaign within a timeframe.
        Used for rate limiting.
        """
        if end_time is None:
            end_time = datetime.utcnow()

        return (
            self.db.query(SendLog)
            .filter(
                SendLog.campaign_id == campaign_id,
                SendLog.sent_at >= start_time,
                SendLog.sent_at <= end_time,
                SendLog.status == SendStatus.SUCCESS
            )
            .count()
        )

    def count_sent_last_hour(self, campaign_id: int) -> int:
        """Count successful sends in the last hour for a campaign."""
        one_hour_ago = datetime.utcnow() - timedelta(hours=1)
        return self.count_sent_in_timeframe(campaign_id, one_hour_ago)

    def count_sent_today(self, campaign_id: int) -> int:
        """Count successful sends today for a campaign."""
        today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        return self.count_sent_in_timeframe(campaign_id, today_start)

    def get_last_send_time(self, campaign_id: int) -> Optional[datetime]:
        """Get the timestamp of the last successful send for a campaign."""
        result = (
            self.db.query(func.max(SendLog.sent_at))
            .filter(
                SendLog.campaign_id == campaign_id,
                SendLog.status == SendStatus.SUCCESS
            )
            .scalar()
        )
        return result

    def create_log(
        self,
        campaign_id: int,
        recipient_id: int,
        backend: EmailBackend,
        status: SendStatus,
        message_id: Optional[str] = None,
        error_message: Optional[str] = None,
        details: Optional[dict] = None
    ) -> SendLog:
        """Create a new send log entry."""
        log = SendLog(
            campaign_id=campaign_id,
            recipient_id=recipient_id,
            backend=backend,
            status=status,
            message_id=message_id,
            error_message=error_message
        )
        if details:
            log.set_details(details)
        self.db.add(log)
        self.db.flush()
        return log
