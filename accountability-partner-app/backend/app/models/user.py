"""User and UserProfile models."""
from sqlalchemy import Column, String, Boolean, Date, DateTime, Integer, Float, Text, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
import uuid
from app.database import Base, GUID, ARRAY, JSONB


class User(Base):
    """User model for authentication and core user data."""

    __tablename__ = "users"

    # Primary key
    id = Column(GUID, primary_key=True, default=uuid.uuid4)

    # Authentication
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    username = Column(String(50), unique=True, nullable=False, index=True)

    # Profile
    full_name = Column(String(100))
    profile_picture_url = Column(Text)
    bio = Column(Text)
    date_of_birth = Column(Date)
    timezone = Column(String(50), default="UTC")

    # Verification & safety
    is_verified = Column(Boolean, default=False)
    verification_tier = Column(String(20), default="basic")  # basic, phone, id
    is_active = Column(Boolean, default=True)
    is_banned = Column(Boolean, default=False)

    # Gamification
    total_points = Column(Integer, default=0)
    streak_count = Column(Integer, default=0)

    # Timestamps
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    last_login_at = Column(DateTime)

    # Relationships
    profile = relationship("UserProfile", back_populates="user", uselist=False, cascade="all, delete-orphan")
    partnerships_as_user1 = relationship("Partnership", foreign_keys="Partnership.user1_id", back_populates="user1")
    partnerships_as_user2 = relationship("Partnership", foreign_keys="Partnership.user2_id", back_populates="user2")
    check_ins = relationship("CheckIn", back_populates="author", cascade="all, delete-orphan")
    assigned_tasks = relationship("Task", foreign_keys="Task.assigned_by_user_id", back_populates="assigned_by")
    received_tasks = relationship("Task", foreign_keys="Task.assigned_to_user_id", back_populates="assigned_to")

    def __repr__(self) -> str:
        return f"<User(id={self.id}, email={self.email}, username={self.username})>"


class UserProfile(Base):
    """User profile model for matching data and preferences."""

    __tablename__ = "user_profiles"

    # Primary key
    id = Column(GUID, primary_key=True, default=uuid.uuid4)
    user_id = Column(GUID, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    # Strengths & Struggles (arrays)
    strengths = Column(ARRAY(Text), default=[])
    struggles = Column(ARRAY(Text), default=[])

    # Matching preferences
    communication_style = Column(String(50))  # 'direct', 'supportive', 'motivational'
    commitment_level = Column(String(50))  # 'casual', 'moderate', 'intense'
    preferred_check_in_frequency = Column(String(50))  # 'daily', '3x_week', 'weekly'

    # Availability
    available_days_of_week = Column(ARRAY(Integer), default=[])  # [1,2,3,4,5] (Mon-Fri)
    preferred_check_in_time = Column(String(20))  # 'morning', 'afternoon', 'evening'

    # Goals (JSONB for flexibility)
    current_goals = Column(JSONB, default=[])

    # Matching metadata
    active_partnerships_count = Column(Integer, default=0)
    max_partnerships = Column(Integer, default=3)
    is_seeking_partner = Column(Boolean, default=True)

    # Behavioral metrics
    ghosting_score = Column(Float, default=0.0)  # 0 (never ghosts) to 1 (frequent ghoster)
    reciprocity_score = Column(Float, default=0.5)  # 0 (takes) to 1 (gives)

    # Timestamps
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    # Relationships
    user = relationship("User", back_populates="profile")

    def __repr__(self) -> str:
        return f"<UserProfile(user_id={self.user_id}, strengths={self.strengths}, struggles={self.struggles})>"
