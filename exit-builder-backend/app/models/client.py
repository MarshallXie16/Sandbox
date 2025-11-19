"""
Client model
"""
import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.core.db import Base


class Client(Base):
    """Client entity - represents a business owner or stakeholder"""

    __tablename__ = "clients"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    contact_name = Column(String, nullable=True)
    email = Column(String, nullable=True)
    phone = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    projects = relationship("Project", back_populates="client", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Client(id={self.id}, name='{self.name}')>"
