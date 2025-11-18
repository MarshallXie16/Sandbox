"""Goal schemas for request/response validation."""
from pydantic import BaseModel, Field, ConfigDict, field_validator
from typing import Optional, List
from datetime import date, datetime
from uuid import UUID


class SubtaskBase(BaseModel):
    """Subtask schema."""
    task: str = Field(..., min_length=1, max_length=200)
    completed: bool = False


class GoalBase(BaseModel):
    """Base goal schema with common fields."""
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    category: Optional[str] = None
    target_date: Optional[date] = None


class GoalCreate(GoalBase):
    """Schema for creating a goal."""
    is_mutual: bool = False
    subtasks: Optional[List[SubtaskBase]] = []

    @field_validator('category')
    @classmethod
    def validate_category(cls, v):
        if v is not None:
            valid_categories = [
                'career', 'fitness', 'relationships', 'finance',
                'fashion', 'public_speaking', 'creativity', 'health', 'social_skills'
            ]
            if v not in valid_categories:
                raise ValueError(f'category must be one of: {valid_categories}')
        return v

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "title": "Get promoted to Senior Engineer",
                "description": "Focus on leadership and communication skills",
                "category": "career",
                "is_mutual": False,
                "target_date": "2026-06-01",
                "subtasks": [
                    {"task": "Complete leadership course", "completed": False},
                    {"task": "Lead 2 team meetings", "completed": False}
                ]
            }
        }
    )


class GoalUpdate(BaseModel):
    """Schema for updating a goal."""
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    category: Optional[str] = None
    target_date: Optional[date] = None
    status: Optional[str] = None
    subtasks: Optional[List[SubtaskBase]] = None

    @field_validator('status')
    @classmethod
    def validate_status(cls, v):
        if v is not None and v not in ['not_started', 'in_progress', 'completed', 'abandoned']:
            raise ValueError('status must be one of: not_started, in_progress, completed, abandoned')
        return v

    @field_validator('category')
    @classmethod
    def validate_category(cls, v):
        if v is not None:
            valid_categories = [
                'career', 'fitness', 'relationships', 'finance',
                'fashion', 'public_speaking', 'creativity', 'health', 'social_skills'
            ]
            if v not in valid_categories:
                raise ValueError(f'category must be one of: {valid_categories}')
        return v


class GoalResponse(GoalBase):
    """Schema for goal response."""
    id: UUID
    partnership_id: UUID
    owner_id: Optional[UUID] = None  # NULL if mutual goal
    is_mutual: bool
    status: str
    completed_at: Optional[datetime] = None
    subtasks: List[dict] = []
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": "goal-uuid",
                "partnership_id": "partnership-uuid",
                "owner_id": "user-uuid",
                "title": "Get promoted to Senior Engineer",
                "description": "Focus on leadership and communication skills",
                "category": "career",
                "is_mutual": False,
                "status": "in_progress",
                "target_date": "2026-06-01",
                "completed_at": None,
                "subtasks": [
                    {"task": "Complete leadership course", "completed": False},
                    {"task": "Lead 2 team meetings", "completed": True}
                ],
                "created_at": "2025-11-18T10:30:00Z",
                "updated_at": "2025-11-18T10:30:00Z"
            }
        }
    )


class GoalListResponse(BaseModel):
    """Schema for listing goals."""
    goals: List[GoalResponse]
    total: int

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "goals": [],
                "total": 0
            }
        }
    )


class CompleteGoalRequest(BaseModel):
    """Schema for completing a goal."""
    confirm: bool = True  # For mutual goals, both partners must confirm

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "confirm": True
            }
        }
    )
