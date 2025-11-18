"""
SQLAlchemy models for sync tracking database.
"""

from datetime import datetime
from typing import Optional

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, Enum
from sqlalchemy.orm import relationship
import enum

from app.core.database import Base


class EntityType(str, enum.Enum):
    """Supported entity types for synchronization."""

    CONTACT = "contact"
    COMPANY = "company"
    DEAL = "deal"


class SyncDirection(str, enum.Enum):
    """Direction of sync operation."""

    INDIE_TO_HUBSPOT = "indie_to_hubspot"
    HUBSPOT_TO_INDIE = "hubspot_to_indie"
    BIDIRECTIONAL = "bidirectional"


class SyncStatus(str, enum.Enum):
    """Status of sync run."""

    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    PARTIAL = "partial"


class SyncObject(Base):
    """
    Tracks mapping between IndieStack and HubSpot objects.

    This table maintains the relationship between entities in both systems,
    enabling efficient lookups and tracking of sync state.
    """

    __tablename__ = "sync_objects"

    id = Column(Integer, primary_key=True, index=True)
    entity_type = Column(Enum(EntityType), nullable=False, index=True)

    # Primary keys in respective systems
    indie_id = Column(String, nullable=False, index=True)
    hubspot_id = Column(String, nullable=True, index=True)

    # Sync metadata
    last_synced_at = Column(DateTime, nullable=True)
    last_direction = Column(Enum(SyncDirection), nullable=True)

    # JSON field for additional metadata
    details = Column(Text, nullable=True)  # Store as JSON string

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    errors = relationship("SyncError", back_populates="sync_object", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return (
            f"<SyncObject(entity_type={self.entity_type}, "
            f"indie_id={self.indie_id}, hubspot_id={self.hubspot_id})>"
        )


class SyncRun(Base):
    """
    Tracks individual sync run executions.

    Each sync operation (manual or scheduled) creates a SyncRun record
    to track progress, status, and results.
    """

    __tablename__ = "sync_runs"

    id = Column(Integer, primary_key=True, index=True)

    # Run metadata
    started_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    finished_at = Column(DateTime, nullable=True)
    status = Column(Enum(SyncStatus), default=SyncStatus.RUNNING, nullable=False)
    direction = Column(Enum(SyncDirection), nullable=False)

    # Summary statistics (stored as JSON string)
    summary = Column(Text, nullable=True)

    # Relationships
    errors = relationship("SyncError", back_populates="sync_run", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<SyncRun(id={self.id}, status={self.status}, direction={self.direction})>"


class SyncError(Base):
    """
    Tracks errors that occur during sync operations.

    Enables debugging and monitoring of sync failures.
    """

    __tablename__ = "sync_errors"

    id = Column(Integer, primary_key=True, index=True)

    # Foreign keys
    sync_run_id = Column(Integer, ForeignKey("sync_runs.id"), nullable=False, index=True)
    sync_object_id = Column(Integer, ForeignKey("sync_objects.id"), nullable=True, index=True)

    # Error details
    entity_type = Column(Enum(EntityType), nullable=False)
    indie_id = Column(String, nullable=True)
    hubspot_id = Column(String, nullable=True)
    error_message = Column(Text, nullable=False)

    # Additional context (stored as JSON string)
    payload = Column(Text, nullable=True)

    # Timestamp
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    sync_run = relationship("SyncRun", back_populates="errors")
    sync_object = relationship("SyncObject", back_populates="errors")

    def __repr__(self) -> str:
        return (
            f"<SyncError(entity_type={self.entity_type}, "
            f"indie_id={self.indie_id}, error={self.error_message[:50]})>"
        )
