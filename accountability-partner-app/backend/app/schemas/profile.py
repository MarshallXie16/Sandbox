"""Profile schemas for request/response validation."""
from pydantic import BaseModel, Field, field_validator
from typing import Optional, List
from datetime import date
from uuid import UUID


class UserProfileBase(BaseModel):
    """Base profile schema with common fields."""
    strengths: Optional[List[str]] = Field(None, min_length=2, max_length=4)
    struggles: Optional[List[str]] = Field(None, min_length=2, max_length=4)
    communication_style: Optional[str] = None
    commitment_level: Optional[str] = None
    preferred_check_in_frequency: Optional[str] = None
    available_days_of_week: Optional[List[int]] = None
    preferred_check_in_time: Optional[str] = None

    @field_validator('communication_style')
    @classmethod
    def validate_communication_style(cls, v):
        if v is not None and v not in ['direct', 'supportive', 'motivational']:
            raise ValueError('communication_style must be one of: direct, supportive, motivational')
        return v

    @field_validator('commitment_level')
    @classmethod
    def validate_commitment_level(cls, v):
        if v is not None and v not in ['casual', 'moderate', 'intense']:
            raise ValueError('commitment_level must be one of: casual, moderate, intense')
        return v

    @field_validator('preferred_check_in_frequency')
    @classmethod
    def validate_check_in_frequency(cls, v):
        if v is not None and v not in ['daily', '3x_week', 'weekly']:
            raise ValueError('preferred_check_in_frequency must be one of: daily, 3x_week, weekly')
        return v

    @field_validator('available_days_of_week')
    @classmethod
    def validate_days(cls, v):
        if v is not None:
            if not all(1 <= day <= 7 for day in v):
                raise ValueError('Days must be between 1 (Monday) and 7 (Sunday)')
        return v

    @field_validator('preferred_check_in_time')
    @classmethod
    def validate_check_in_time(cls, v):
        if v is not None and v not in ['morning', 'afternoon', 'evening']:
            raise ValueError('preferred_check_in_time must be one of: morning, afternoon, evening')
        return v


class UserProfileCreate(UserProfileBase):
    """Schema for creating user profile (auto-created on registration)."""
    pass


class UserProfileUpdate(UserProfileBase):
    """Schema for updating user profile."""
    pass


class UserProfileResponse(BaseModel):
    """Schema for user profile response."""
    id: UUID
    user_id: UUID
    # Allow empty lists in response (validation only applies to updates)
    strengths: Optional[List[str]] = None
    struggles: Optional[List[str]] = None
    communication_style: Optional[str] = None
    commitment_level: Optional[str] = None
    preferred_check_in_frequency: Optional[str] = None
    available_days_of_week: Optional[List[int]] = None
    preferred_check_in_time: Optional[str] = None
    active_partnerships_count: int = 0
    max_partnerships: int = 3
    is_seeking_partner: bool = True
    ghosting_score: float = 0.0
    reciprocity_score: float = 0.5

    model_config = {
        "from_attributes": True,
        "json_schema_extra": {
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "user_id": "123e4567-e89b-12d3-a456-426614174001",
                "strengths": ["career", "fitness"],
                "struggles": ["fashion", "relationships"],
                "communication_style": "direct",
                "commitment_level": "moderate",
                "preferred_check_in_frequency": "3x_week",
                "available_days_of_week": [1, 3, 5],
                "preferred_check_in_time": "evening",
                "active_partnerships_count": 1,
                "max_partnerships": 3,
                "is_seeking_partner": True,
                "ghosting_score": 0.0,
                "reciprocity_score": 0.5
            }
        }
    }
