"""Event source for Capital Ink Hub Email Engine."""
from datetime import datetime
from typing import Generator, Optional, Dict, Any

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

from app.core.logging import logger
from app.sources.base import EventSource, StandardEvent


class EmailEngineSource(EventSource):
    """
    Event source for Capital Ink Hub Email Engine.

    Fetches email sending events from the email engine database.
    """

    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the email engine source.

        Args:
            config: Must contain 'db_url' key with database connection string
        """
        super().__init__(config)

        if "db_url" not in config:
            raise ValueError("EmailEngineSource requires 'db_url' in config")

        self.db_url = config["db_url"]
        self._engine = None
        self._session_maker = None

    def _get_session(self) -> any:
        """Get or create database session."""
        if not self._engine:
            self._engine = create_engine(self.db_url)
            self._session_maker = sessionmaker(bind=self._engine)

        return self._session_maker()

    def test_connection(self) -> bool:
        """Test connection to email engine database."""
        try:
            session = self._get_session()
            # Try a simple query
            result = session.execute(text("SELECT 1"))
            result.fetchone()
            session.close()
            logger.info(f"{self.name}: Connection successful")
            return True
        except Exception as e:
            logger.error(f"{self.name}: Connection failed: {str(e)}")
            return False

    def fetch_new_events(
        self,
        since: Optional[datetime] = None,
        limit: Optional[int] = None,
    ) -> Generator[StandardEvent, None, None]:
        """
        Fetch email events from the email engine database.

        Reads from SendLogs and Recipients tables to extract:
        - Email sent events
        - Email bounce/failure events

        Args:
            since: Only fetch events after this datetime
            limit: Maximum number of events to fetch

        Yields:
            StandardEvent objects
        """
        session = self._get_session()

        try:
            # Build query to fetch send logs with recipients
            query = """
            SELECT
                sl.id as send_log_id,
                sl.sent_at,
                sl.status,
                sl.campaign_id,
                r.email,
                r.contact_id,
                r.status as recipient_status,
                r.metadata
            FROM send_logs sl
            JOIN recipients r ON sl.id = r.send_log_id
            WHERE 1=1
            """

            params = {}

            if since:
                query += " AND sl.sent_at > :since"
                params["since"] = since

            query += " ORDER BY sl.sent_at DESC"

            if limit:
                query += " LIMIT :limit"
                params["limit"] = limit

            result = session.execute(text(query), params)

            for row in result:
                contact_id = row.contact_id or row.email
                sent_at = row.sent_at

                # Determine event type based on status
                if row.status == "sent" or row.recipient_status == "sent":
                    event_type = "email_sent"
                    weight = self.get_default_weight("email_sent")
                elif row.status in ("failed", "bounced") or row.recipient_status in (
                    "failed",
                    "bounced",
                ):
                    event_type = "email_bounce"
                    weight = self.get_default_weight("email_bounce")
                else:
                    # Skip unknown statuses
                    continue

                yield StandardEvent(
                    external_id=str(contact_id),
                    entity_type="contact",
                    source_system="email_engine",
                    event_type=event_type,
                    weight=weight,
                    occurred_at=sent_at,
                    metadata={
                        "send_log_id": row.send_log_id,
                        "campaign_id": row.campaign_id,
                        "email": row.email,
                        "status": row.status,
                        "recipient_status": row.recipient_status,
                    },
                )

        except Exception as e:
            logger.error(f"{self.name}: Error fetching events: {str(e)}")
            raise
        finally:
            session.close()

    def fetch_opens_and_clicks(
        self, since: Optional[datetime] = None
    ) -> Generator[StandardEvent, None, None]:
        """
        Fetch email open and click events (if tracked).

        This is a placeholder for future Sendy integration or
        if the email engine adds tracking.

        Args:
            since: Only fetch events after this datetime

        Yields:
            StandardEvent objects
        """
        # TODO: Implement when tracking is available
        # For now, this could integrate with Sendy webhooks
        logger.warning(f"{self.name}: Open/click tracking not yet implemented")
        return
        yield  # Make this a generator
