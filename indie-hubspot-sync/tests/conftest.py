"""
Pytest configuration and shared fixtures.
"""

import os
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.database import Base
from app.models.tracking import SyncObject, SyncRun, SyncError


@pytest.fixture(scope="function")
def test_db():
    """Create a test database for each test."""
    # Use in-memory SQLite for tests
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)

    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()

    yield db

    db.close()
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="session", autouse=True)
def setup_test_env():
    """Set up test environment variables."""
    os.environ["HUBSPOT_PRIVATE_APP_TOKEN"] = "test_token_12345"
    os.environ["INDIE_DB_HOST"] = "localhost"
    os.environ["INDIE_DB_NAME"] = "test_db"
    os.environ["INDIE_DB_USER"] = "test_user"
    os.environ["INDIE_DB_PASSWORD"] = "test_pass"
    os.environ["SYNC_DB_URL"] = "sqlite:///:memory:"
    os.environ["LOG_LEVEL"] = "ERROR"  # Reduce logging noise in tests
