"""Tests for event sources."""
import pytest
from datetime import datetime
from app.sources.base import EventSource, StandardEvent


class MockEventSource(EventSource):
    """Mock event source for testing."""

    def __init__(self, config, events=None):
        super().__init__(config)
        self.mock_events = events or []
        self.connection_ok = True

    def fetch_new_events(self, since=None, limit=None):
        """Return mock events."""
        events = self.mock_events

        if since:
            events = [e for e in events if e.occurred_at > since]

        if limit:
            events = events[:limit]

        for event in events:
            yield event

    def test_connection(self):
        """Return mock connection status."""
        return self.connection_ok


def test_standard_event_creation():
    """Test creating a StandardEvent."""
    event = StandardEvent(
        external_id="contact_123",
        entity_type="contact",
        source_system="test",
        event_type="email_sent",
        weight=1.0,
        occurred_at=datetime.utcnow(),
        metadata={"subject": "Test"},
    )

    assert event.external_id == "contact_123"
    assert event.entity_type == "contact"
    assert event.source_system == "test"
    assert event.event_type == "email_sent"
    assert event.weight == 1.0
    assert event.metadata["subject"] == "Test"


def test_mock_source_fetch_all():
    """Test fetching all events from mock source."""
    mock_events = [
        StandardEvent(
            external_id="contact_1",
            entity_type="contact",
            source_system="mock",
            event_type="email_sent",
            weight=1.0,
            occurred_at=datetime.utcnow(),
        ),
        StandardEvent(
            external_id="contact_2",
            entity_type="contact",
            source_system="mock",
            event_type="meeting",
            weight=15.0,
            occurred_at=datetime.utcnow(),
        ),
    ]

    source = MockEventSource(config={}, events=mock_events)
    fetched = list(source.fetch_new_events())

    assert len(fetched) == 2
    assert fetched[0].external_id == "contact_1"
    assert fetched[1].external_id == "contact_2"


def test_mock_source_fetch_with_limit():
    """Test fetching events with limit."""
    mock_events = [
        StandardEvent(
            external_id=f"contact_{i}",
            entity_type="contact",
            source_system="mock",
            event_type="email_sent",
            weight=1.0,
            occurred_at=datetime.utcnow(),
        )
        for i in range(10)
    ]

    source = MockEventSource(config={}, events=mock_events)
    fetched = list(source.fetch_new_events(limit=5))

    assert len(fetched) == 5


def test_mock_source_fetch_with_since():
    """Test fetching events with since filter."""
    now = datetime.utcnow()
    from datetime import timedelta

    old_event = StandardEvent(
        external_id="contact_old",
        entity_type="contact",
        source_system="mock",
        event_type="email_sent",
        weight=1.0,
        occurred_at=now - timedelta(days=10),
    )

    new_event = StandardEvent(
        external_id="contact_new",
        entity_type="contact",
        source_system="mock",
        event_type="email_sent",
        weight=1.0,
        occurred_at=now,
    )

    source = MockEventSource(config={}, events=[old_event, new_event])
    since_date = now - timedelta(days=5)
    fetched = list(source.fetch_new_events(since=since_date))

    assert len(fetched) == 1
    assert fetched[0].external_id == "contact_new"


def test_mock_source_connection_test():
    """Test connection testing."""
    source = MockEventSource(config={})
    assert source.test_connection() is True

    source.connection_ok = False
    assert source.test_connection() is False


def test_default_event_weights():
    """Test default weight getter."""
    source = MockEventSource(config={})

    assert source.get_default_weight("email_sent") == 1.0
    assert source.get_default_weight("email_open") == 3.0
    assert source.get_default_weight("meeting") == 15.0
    assert source.get_default_weight("deal_won") == 50.0
    assert source.get_default_weight("unknown_event") == 1.0  # Default fallback
