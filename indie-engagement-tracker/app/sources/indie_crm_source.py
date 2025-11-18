"""Event source for IndieStack CRM Core."""
from datetime import datetime
from typing import Generator, Optional, Dict, Any

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

from app.core.logging import logger
from app.sources.base import EventSource, StandardEvent


class IndieCrmActivitySource(EventSource):
    """
    Event source for IndieStack CRM Core.

    Fetches activities (calls, meetings, emails, etc.) and deal changes.
    """

    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the CRM source.

        Args:
            config: Must contain either 'db_url' or 'api_url' + 'api_key'
        """
        super().__init__(config)

        self.use_api = "api_url" in config
        if self.use_api:
            self.api_url = config["api_url"]
            self.api_key = config.get("api_key")
        else:
            if "db_url" not in config:
                raise ValueError(
                    "IndieCrmActivitySource requires either 'db_url' or 'api_url'"
                )
            self.db_url = config["db_url"]
            self._engine = None
            self._session_maker = None

    def _get_session(self) -> any:
        """Get or create database session."""
        if self.use_api:
            raise NotImplementedError("API access not yet implemented")

        if not self._engine:
            self._engine = create_engine(self.db_url)
            self._session_maker = sessionmaker(bind=self._engine)

        return self._session_maker()

    def test_connection(self) -> bool:
        """Test connection to CRM."""
        try:
            if self.use_api:
                # TODO: Implement API health check
                logger.warning(f"{self.name}: API connection test not implemented")
                return False

            session = self._get_session()
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
        Fetch activity events from IndieStack CRM.

        Fetches:
        - Activities (calls, meetings, emails, messages)
        - Deal stage changes

        Args:
            since: Only fetch events after this datetime
            limit: Maximum number of events to fetch

        Yields:
            StandardEvent objects
        """
        # Fetch activities first
        yield from self._fetch_activities(since, limit)

        # Then fetch deal stage changes
        yield from self._fetch_deal_changes(since, limit)

    def _fetch_activities(
        self,
        since: Optional[datetime] = None,
        limit: Optional[int] = None,
    ) -> Generator[StandardEvent, None, None]:
        """Fetch activity events."""
        session = self._get_session()

        try:
            # Query activities
            query = """
            SELECT
                a.id,
                a.contact_id,
                a.type,
                a.created_at,
                a.details,
                c.id as contact_external_id
            FROM activities a
            LEFT JOIN contacts c ON a.contact_id = c.id
            WHERE 1=1
            """

            params = {}

            if since:
                query += " AND a.created_at > :since"
                params["since"] = since

            query += " ORDER BY a.created_at DESC"

            if limit:
                query += " LIMIT :limit"
                params["limit"] = limit

            result = session.execute(text(query), params)

            for row in result:
                if not row.contact_external_id:
                    continue  # Skip activities without contacts

                # Map CRM activity type to event type
                activity_type = row.type.lower()
                event_type_map = {
                    "email": "email_sent",
                    "call": "call",
                    "meeting": "meeting",
                    "linkedin": "message",
                    "whatsapp": "message",
                    "wechat": "message",
                    "note": "note_added",
                    "task": "task_completed",
                }

                event_type = event_type_map.get(activity_type, activity_type)
                weight = self.get_default_weight(event_type)

                yield StandardEvent(
                    external_id=str(row.contact_external_id),
                    entity_type="contact",
                    source_system="indie_crm",
                    event_type=event_type,
                    weight=weight,
                    occurred_at=row.created_at,
                    metadata={
                        "activity_id": row.id,
                        "activity_type": row.type,
                        "details": row.details,
                    },
                )

        except Exception as e:
            logger.error(f"{self.name}: Error fetching activities: {str(e)}")
            raise
        finally:
            session.close()

    def _fetch_deal_changes(
        self,
        since: Optional[datetime] = None,
        limit: Optional[int] = None,
    ) -> Generator[StandardEvent, None, None]:
        """Fetch deal stage change events."""
        session = self._get_session()

        try:
            # Query deal history for stage changes
            query = """
            SELECT
                d.id as deal_id,
                d.contact_id,
                d.company_id,
                d.stage_id,
                d.status,
                d.updated_at,
                d.value,
                p.name as pipeline_name,
                s.name as stage_name
            FROM deals d
            LEFT JOIN pipelines p ON d.pipeline_id = p.id
            LEFT JOIN stages s ON d.stage_id = s.id
            WHERE 1=1
            """

            params = {}

            if since:
                query += " AND d.updated_at > :since"
                params["since"] = since

            query += " ORDER BY d.updated_at DESC"

            if limit:
                query += " LIMIT :limit"
                params["limit"] = limit

            result = session.execute(text(query), params)

            for row in result:
                # Determine event type based on deal status
                if row.status == "won":
                    event_type = "deal_won"
                elif row.status == "lost":
                    event_type = "deal_lost"
                else:
                    event_type = "deal_stage_change"

                weight = self.get_default_weight(event_type)

                # Create event for contact if present
                if row.contact_id:
                    yield StandardEvent(
                        external_id=str(row.contact_id),
                        entity_type="contact",
                        source_system="indie_crm",
                        event_type=event_type,
                        weight=weight,
                        occurred_at=row.updated_at,
                        metadata={
                            "deal_id": row.deal_id,
                            "pipeline": row.pipeline_name,
                            "stage": row.stage_name,
                            "status": row.status,
                            "value": float(row.value) if row.value else None,
                        },
                    )

                # Also create event for the deal itself
                yield StandardEvent(
                    external_id=str(row.deal_id),
                    entity_type="deal",
                    source_system="indie_crm",
                    event_type=event_type,
                    weight=weight,
                    occurred_at=row.updated_at,
                    metadata={
                        "pipeline": row.pipeline_name,
                        "stage": row.stage_name,
                        "status": row.status,
                        "value": float(row.value) if row.value else None,
                    },
                )

        except Exception as e:
            logger.error(f"{self.name}: Error fetching deal changes: {str(e)}")
            raise
        finally:
            session.close()
