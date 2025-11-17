"""User schemas for request/response validation."""
from pydantic import BaseModel, EmailStr, Field, ConfigDict
from typing import Optional
from datetime import date, datetime
from uuid import UUID


class UserBase(BaseModel):
    """Base user schema with common fields."""
    email: EmailStr
    username: str = Field(..., min_length=3, max_length=50)
    full_name: Optional[str] = Field(None, max_length=100)


class UserCreate(UserBase):
    """Schema for user registration."""
    password: str = Field(..., min_length=8, max_length=100)

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "email": "sarah@example.com",
                "username": "sarah_career",
                "full_name": "Sarah Johnson",
                "password": "SecurePass123"
            }
        }
    )


class UserLogin(BaseModel):
    """Schema for user login."""
    email: EmailStr
    password: str


class UserResponse(UserBase):
    """Schema for user response."""
    id: UUID
    profile_picture_url: Optional[str] = None
    bio: Optional[str] = None
    timezone: str = "UTC"
    is_verified: bool = False
    total_points: int = 0
    streak_count: int = 0
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class UserUpdate(BaseModel):
    """Schema for updating user profile."""
    full_name: Optional[str] = Field(None, max_length=100)
    bio: Optional[str] = Field(None, max_length=500)
    date_of_birth: Optional[date] = None
    timezone: Optional[str] = None


class TokenResponse(BaseModel):
    """Schema for token response."""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RefreshTokenRequest(BaseModel):
    """Schema for token refresh request."""
    refresh_token: str
