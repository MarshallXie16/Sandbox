"""Base class for event sources - pluggable architecture."""
from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from typing import Generator, Optional, Dict, Any


@dataclass
class StandardEvent:
    """
    Standardized event format for ingestion.

    All event sources must convert their data to this format.
    """

    external_id: str  # Contact/deal/company ID in the source system
    entity_type: str  # contact, company, deal
    source_system: str  # indie_crm, email_engine, hubspot, etc.
    event_type: str  # email_sent, email_open, call, meeting, etc.
    weight: float  # Base weight for this event
    occurred_at: datetime  # When the event happened
    metadata: Optional[Dict[str, Any]] = None  # Additional event data

    def __repr__(self) -> str:
        return (
            f"StandardEvent(external_id={self.external_id}, "
            f"type={self.event_type}, source={self.source_system}, "
            f"occurred_at={self.occurred_at})"
        )


class EventSource(ABC):
    """
    Abstract base class for event sources.

    Implement this class to add new event sources (HubSpot, Sendy, etc.).
    """

    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the event source.

        Args:
            config: Configuration dictionary (DSN, API keys, etc.)
        """
        self.config = config
        self.name = self.__class__.__name__

    @abstractmethod
    def fetch_new_events(
        self,
        since: Optional[datetime] = None,
        limit: Optional[int] = None,
    ) -> Generator[StandardEvent, None, None]:
        """
        Fetch new events from the source system.

        Args:
            since: Only fetch events after this datetime
            limit: Maximum number of events to fetch

        Yields:
            StandardEvent objects

        Example:
            for event in source.fetch_new_events(since=last_sync):
                # Process event
                pass
        """
        pass

    @abstractmethod
    def test_connection(self) -> bool:
        """
        Test the connection to the source system.

        Returns:
            True if connection is successful, False otherwise
        """
        pass

    def get_default_weight(self, event_type: str) -> float:
        """
        Get default weight for an event type.

        Can be overridden by subclasses for source-specific weights.

        Args:
            event_type: The event type

        Returns:
            Default weight value
        """
        # Default weights (can be overridden by scoring profile)
        weights = {
            # Email events
            "email_sent": 1.0,
            "email_open": 3.0,
            "email_click": 5.0,
            "email_reply": 10.0,
            "email_bounce": -2.0,
            # Communication events
            "call": 8.0,
            "meeting": 15.0,
            "message": 5.0,  # LinkedIn, WhatsApp, WeChat
            # CRM events
            "note_added": 3.0,
            "task_completed": 5.0,
            "deal_created": 20.0,
            "deal_stage_change": 15.0,
            "deal_won": 50.0,
            "deal_lost": -10.0,
            # Web events
            "form_submit": 12.0,
            "page_view": 1.0,
            "download": 7.0,
        }
        return weights.get(event_type, 1.0)
