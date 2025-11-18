"""Partnership schemas for request/response validation."""
from pydantic import BaseModel, Field, ConfigDict, field_validator
from typing import Optional, List
from datetime import date, datetime
from uuid import UUID


class PartnerInfo(BaseModel):
    """Public partner information (no private data)."""
    id: UUID
    username: str
    full_name: Optional[str] = None
    profile_picture_url: Optional[str] = None
    strengths: Optional[List[str]] = None
    struggles: Optional[List[str]] = None

    model_config = ConfigDict(from_attributes=True)


class PartnershipResponse(BaseModel):
    """Schema for partnership response."""
    id: UUID
    partner: PartnerInfo
    status: str
    season_number: int
    current_season_start_date: date
    current_season_end_date: date
    mutual_goals: List[dict] = []
    check_in_frequency: str
    check_in_days: List[int]
    communication_methods: List[str]
    balance_score: float
    engagement_score: float
    last_interaction_at: Optional[datetime] = None
    created_at: datetime

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": "partnership-uuid",
                "partner": {
                    "id": "partner-uuid",
                    "username": "mike_fitness",
                    "full_name": "Mike Johnson",
                    "profile_picture_url": "https://...",
                    "strengths": ["fashion", "relationships"],
                    "struggles": ["career", "fitness"]
                },
                "status": "active",
                "season_number": 1,
                "current_season_start_date": "2025-11-18",
                "current_season_end_date": "2025-12-16",
                "mutual_goals": [],
                "check_in_frequency": "3x_week",
                "check_in_days": [1, 3, 5],
                "communication_methods": ["text"],
                "balance_score": 0.5,
                "engagement_score": 1.0,
                "last_interaction_at": "2025-11-18T10:30:00Z",
                "created_at": "2025-11-18T10:30:00Z"
            }
        }
    )


class PartnershipListResponse(BaseModel):
    """Schema for listing partnerships."""
    partnerships: List[PartnershipResponse]
    total: int

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "partnerships": [],
                "total": 0
            }
        }
    )


class PartnershipUpdateSettings(BaseModel):
    """Schema for updating partnership settings."""
    check_in_frequency: Optional[str] = None
    check_in_days: Optional[List[int]] = None
    communication_methods: Optional[List[str]] = None

    @field_validator('check_in_frequency')
    @classmethod
    def validate_frequency(cls, v):
        if v is not None and v not in ['daily', '3x_week', 'weekly']:
            raise ValueError('check_in_frequency must be one of: daily, 3x_week, weekly')
        return v

    @field_validator('check_in_days')
    @classmethod
    def validate_days(cls, v):
        if v is not None:
            if not all(1 <= day <= 7 for day in v):
                raise ValueError('check_in_days must be integers 1-7 (Monday=1, Sunday=7)')
            if len(v) < 1 or len(v) > 7:
                raise ValueError('check_in_days must have 1-7 items')
        return v

    @field_validator('communication_methods')
    @classmethod
    def validate_methods(cls, v):
        if v is not None:
            valid_methods = ['text', 'voice', 'photo']
            if not all(method in valid_methods for method in v):
                raise ValueError(f'communication_methods must be subset of: {valid_methods}')
        return v

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "check_in_frequency": "3x_week",
                "check_in_days": [1, 3, 5],
                "communication_methods": ["text", "voice"]
            }
        }
    )


class EndPartnershipRequest(BaseModel):
    """Schema for ending a partnership."""
    reason: Optional[str] = Field(None, max_length=500)
    give_feedback: bool = False

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "reason": "Completed our goals together!",
                "give_feedback": True
            }
        }
    )


class PartnershipStats(BaseModel):
    """Schema for partnership analytics."""
    partnership_id: UUID
    season_number: int
    days_active: int
    total_check_ins: int
    user_check_ins: int
    partner_check_ins: int
    total_goals: int
    completed_goals: int
    balance_score: float
    engagement_score: float
    current_streak: int
    longest_streak: int
    last_interaction_at: Optional[datetime] = None

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "partnership_id": "partnership-uuid",
                "season_number": 1,
                "days_active": 14,
                "total_check_ins": 12,
                "user_check_ins": 6,
                "partner_check_ins": 6,
                "total_goals": 4,
                "completed_goals": 2,
                "balance_score": 0.5,
                "engagement_score": 0.85,
                "current_streak": 5,
                "longest_streak": 5,
                "last_interaction_at": "2025-11-18T10:30:00Z"
            }
        }
    )
