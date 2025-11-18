"""
Database configuration and session management.
"""

from contextlib import contextmanager
from typing import Generator

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session

from app.core.config import settings

# Create engine for tracking database
engine = create_engine(
    settings.sync_db_url,
    connect_args={"check_same_thread": False} if "sqlite" in settings.sync_db_url else {},
    echo=settings.log_level == "DEBUG",
)

# Session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for tracking models
Base = declarative_base()


def init_db() -> None:
    """Initialize the tracking database, creating all tables."""
    Base.metadata.create_all(bind=engine)


def get_db() -> Generator[Session, None, None]:
    """
    Dependency function for FastAPI to get database sessions.

    Yields:
        Database session
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@contextmanager
def get_db_context() -> Generator[Session, None, None]:
    """
    Context manager for getting database sessions in non-FastAPI contexts.

    Usage:
        with get_db_context() as db:
            # use db
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
