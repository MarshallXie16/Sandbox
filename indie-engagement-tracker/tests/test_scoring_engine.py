"""Tests for the scoring engine."""
import pytest
from datetime import datetime, timedelta
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.models import Base, EngagementEntity, EngagementEvent, ScoringProfile, EntityType
from app.scoring import ScoringEngine


@pytest.fixture
def db_session():
    """Create in-memory SQLite database for testing."""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    SessionLocal = sessionmaker(bind=engine)
    session = SessionLocal()

    yield session

    session.close()


@pytest.fixture
def default_profile(db_session):
    """Create a default scoring profile."""
    profile = ScoringProfile(
        name="Test Profile",
        description="Test scoring profile",
        rules={
            "event_weights": {
                "email_sent": 1.0,
                "email_open": 3.0,
                "meeting": 15.0,
                "call": 8.0,
            },
            "time_decay": {"enabled": True, "decay_days": 90, "decay_factor": 0.5},
        },
        is_default=True,
    )
    db_session.add(profile)
    db_session.commit()
    return profile


@pytest.fixture
def test_entity(db_session):
    """Create a test engagement entity."""
    entity = EngagementEntity(
        external_id="test_contact_1",
        entity_type=EntityType.CONTACT,
        latest_score=0.0,
    )
    db_session.add(entity)
    db_session.commit()
    return entity


def test_calculate_score_simple(db_session, default_profile, test_entity):
    """Test basic score calculation without decay."""
    # Create events
    now = datetime.utcnow()

    events = [
        EngagementEvent(
            engagement_entity_id=test_entity.id,
            external_id=test_entity.external_id,
            entity_type="contact",
            source_system="test",
            event_type="email_sent",
            weight=1.0,
            occurred_at=now,
        ),
        EngagementEvent(
            engagement_entity_id=test_entity.id,
            external_id=test_entity.external_id,
            entity_type="contact",
            source_system="test",
            event_type="email_open",
            weight=3.0,
            occurred_at=now,
        ),
        EngagementEvent(
            engagement_entity_id=test_entity.id,
            external_id=test_entity.external_id,
            entity_type="contact",
            source_system="test",
            event_type="meeting",
            weight=15.0,
            occurred_at=now,
        ),
    ]

    for event in events:
        db_session.add(event)
    db_session.commit()

    # Calculate score
    engine = ScoringEngine(db_session, default_profile)
    score, breakdown = engine.calculate_score(events)

    # Verify
    expected_score = 1.0 + 3.0 + 15.0
    assert score == expected_score
    assert breakdown["total_events"] == 3
    assert breakdown["by_event_type"]["email_sent"] == 1.0
    assert breakdown["by_event_type"]["email_open"] == 3.0
    assert breakdown["by_event_type"]["meeting"] == 15.0


def test_calculate_score_with_decay(db_session, default_profile, test_entity):
    """Test score calculation with time decay."""
    now = datetime.utcnow()
    old_date = now - timedelta(days=100)  # Older than decay threshold

    events = [
        # Recent event - no decay
        EngagementEvent(
            engagement_entity_id=test_entity.id,
            external_id=test_entity.external_id,
            entity_type="contact",
            source_system="test",
            event_type="meeting",
            weight=15.0,
            occurred_at=now,
        ),
        # Old event - should decay
        EngagementEvent(
            engagement_entity_id=test_entity.id,
            external_id=test_entity.external_id,
            entity_type="contact",
            source_system="test",
            event_type="meeting",
            weight=15.0,
            occurred_at=old_date,
        ),
    ]

    for event in events:
        db_session.add(event)
    db_session.commit()

    engine = ScoringEngine(db_session, default_profile)
    score, breakdown = engine.calculate_score(events, reference_date=now)

    # Recent: 15.0, Old: 15.0 * 0.5 = 7.5, Total: 22.5
    expected_score = 15.0 + (15.0 * 0.5)
    assert score == expected_score
    assert breakdown["decayed_events"] == 1


def test_calculate_score_no_decay_when_disabled(db_session, test_entity):
    """Test that decay is not applied when disabled."""
    # Profile with decay disabled
    profile = ScoringProfile(
        name="No Decay",
        rules={
            "event_weights": {"meeting": 15.0},
            "time_decay": {"enabled": False},
        },
    )
    db_session.add(profile)
    db_session.commit()

    now = datetime.utcnow()
    old_date = now - timedelta(days=100)

    events = [
        EngagementEvent(
            engagement_entity_id=test_entity.id,
            external_id=test_entity.external_id,
            entity_type="contact",
            source_system="test",
            event_type="meeting",
            weight=15.0,
            occurred_at=old_date,
        ),
    ]

    for event in events:
        db_session.add(event)
    db_session.commit()

    engine = ScoringEngine(db_session, profile)
    score, breakdown = engine.calculate_score(events, reference_date=now)

    # Should be full weight even though event is old
    assert score == 15.0
    assert "decayed_events" not in breakdown


def test_calculate_entity_score(db_session, default_profile, test_entity):
    """Test calculating score for a specific entity."""
    now = datetime.utcnow()

    events = [
        EngagementEvent(
            engagement_entity_id=test_entity.id,
            external_id=test_entity.external_id,
            entity_type="contact",
            source_system="test",
            event_type="call",
            weight=8.0,
            occurred_at=now,
        ),
        EngagementEvent(
            engagement_entity_id=test_entity.id,
            external_id=test_entity.external_id,
            entity_type="contact",
            source_system="test",
            event_type="meeting",
            weight=15.0,
            occurred_at=now,
        ),
    ]

    for event in events:
        db_session.add(event)
    db_session.commit()

    engine = ScoringEngine(db_session, default_profile)
    score, breakdown = engine.calculate_entity_score(test_entity, save_history=False)

    # Verify entity was updated
    assert test_entity.latest_score == 23.0  # 8 + 15
    assert test_entity.score_breakdown is not None
    assert test_entity.last_activity_at is not None


def test_calculate_score_empty_events(db_session, default_profile):
    """Test score calculation with no events."""
    engine = ScoringEngine(db_session, default_profile)
    score, breakdown = engine.calculate_score([])

    assert score == 0.0
    assert breakdown == {}


def test_score_breakdown_by_source(db_session, default_profile, test_entity):
    """Test that breakdown includes per-source aggregation."""
    now = datetime.utcnow()

    events = [
        EngagementEvent(
            engagement_entity_id=test_entity.id,
            external_id=test_entity.external_id,
            entity_type="contact",
            source_system="crm",
            event_type="call",
            weight=8.0,
            occurred_at=now,
        ),
        EngagementEvent(
            engagement_entity_id=test_entity.id,
            external_id=test_entity.external_id,
            entity_type="contact",
            source_system="email",
            event_type="email_sent",
            weight=1.0,
            occurred_at=now,
        ),
    ]

    for event in events:
        db_session.add(event)
    db_session.commit()

    engine = ScoringEngine(db_session, default_profile)
    score, breakdown = engine.calculate_score(events)

    assert breakdown["by_source"]["crm"] == 8.0
    assert breakdown["by_source"]["email"] == 1.0


def test_recalculate_all_scores(db_session, default_profile):
    """Test recalculating scores for multiple entities."""
    # Create multiple entities with events
    entities = []
    for i in range(3):
        entity = EngagementEntity(
            external_id=f"contact_{i}",
            entity_type=EntityType.CONTACT,
            latest_score=0.0,
        )
        db_session.add(entity)
        db_session.flush()

        # Add events
        event = EngagementEvent(
            engagement_entity_id=entity.id,
            external_id=entity.external_id,
            entity_type="contact",
            source_system="test",
            event_type="meeting",
            weight=15.0,
            occurred_at=datetime.utcnow(),
        )
        db_session.add(event)
        entities.append(entity)

    db_session.commit()

    engine = ScoringEngine(db_session, default_profile)
    stats = engine.recalculate_all_scores()

    assert stats["total_entities"] == 3
    assert stats["recalculated"] == 3
    assert stats["skipped"] == 0
    assert stats["errors"] == 0

    # Verify all entities were updated
    for entity in entities:
        db_session.refresh(entity)
        assert entity.latest_score == 15.0


def test_recalculate_with_min_events_filter(db_session, default_profile):
    """Test recalculation with minimum events filter."""
    # Entity with 1 event
    entity1 = EngagementEntity(
        external_id="contact_1", entity_type=EntityType.CONTACT, latest_score=0.0
    )
    db_session.add(entity1)
    db_session.flush()

    event1 = EngagementEvent(
        engagement_entity_id=entity1.id,
        external_id=entity1.external_id,
        entity_type="contact",
        source_system="test",
        event_type="meeting",
        weight=15.0,
        occurred_at=datetime.utcnow(),
    )
    db_session.add(event1)

    # Entity with 2 events
    entity2 = EngagementEntity(
        external_id="contact_2", entity_type=EntityType.CONTACT, latest_score=0.0
    )
    db_session.add(entity2)
    db_session.flush()

    for _ in range(2):
        event = EngagementEvent(
            engagement_entity_id=entity2.id,
            external_id=entity2.external_id,
            entity_type="contact",
            source_system="test",
            event_type="call",
            weight=8.0,
            occurred_at=datetime.utcnow(),
        )
        db_session.add(event)

    db_session.commit()

    engine = ScoringEngine(db_session, default_profile)
    stats = engine.recalculate_all_scores(min_events=2)

    # Only entity2 should be recalculated
    assert stats["recalculated"] == 1
    assert stats["skipped"] == 1
