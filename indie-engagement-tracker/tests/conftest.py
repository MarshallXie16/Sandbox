"""Pytest configuration and shared fixtures."""
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.models import Base


@pytest.fixture(scope="function")
def test_db():
    """Create a fresh in-memory database for each test."""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)

    SessionLocal = sessionmaker(bind=engine)
    db = SessionLocal()

    yield db

    db.close()
    Base.metadata.drop_all(engine)


@pytest.fixture
def sample_event_weights():
    """Sample event weights for testing."""
    return {
        "email_sent": 1.0,
        "email_open": 3.0,
        "email_click": 5.0,
        "call": 8.0,
        "meeting": 15.0,
        "deal_created": 20.0,
        "deal_won": 50.0,
    }


@pytest.fixture
def sample_scoring_rules(sample_event_weights):
    """Sample scoring profile rules."""
    return {
        "event_weights": sample_event_weights,
        "time_decay": {
            "enabled": True,
            "decay_days": 90,
            "decay_factor": 0.5,
        },
    }
