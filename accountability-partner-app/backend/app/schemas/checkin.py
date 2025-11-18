"""Check-in schemas for request/response validation."""
from pydantic import BaseModel, Field, ConfigDict, field_validator
from typing import Optional
from datetime import datetime
from uuid import UUID


class CheckInBase(BaseModel):
    """Base check-in schema with common fields."""
    content_type: str = "text"
    text_content: Optional[str] = None


class CheckInCreate(BaseModel):
    """Schema for creating a check-in."""
    what_i_did: str = Field(..., min_length=1, max_length=2000)
    what_i_struggled_with: Optional[str] = Field(None, max_length=2000)
    what_i_need: Optional[str] = Field(None, max_length=2000)
    content_type: str = "text"
    media_url: Optional[str] = None

    @field_validator('content_type')
    @classmethod
    def validate_content_type(cls, v):
        if v not in ['text', 'voice', 'photo']:
            raise ValueError('content_type must be one of: text, voice, photo')
        return v

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "what_i_did": "Applied to 5 senior roles, had 2 phone screens this week",
                "what_i_struggled_with": "Imposter syndrome during technical interviews",
                "what_i_need": "Help practicing answers to leadership questions",
                "content_type": "text"
            }
        }
    )


class CheckInUpdate(BaseModel):
    """Schema for updating a check-in."""
    is_read: Optional[bool] = None


class AuthorInfo(BaseModel):
    """Author information for check-in."""
    id: UUID
    username: str
    full_name: Optional[str] = None
    profile_picture_url: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class CheckInResponse(BaseModel):
    """Schema for check-in response."""
    id: UUID
    partnership_id: UUID
    author: AuthorInfo
    what_i_did: Optional[str] = None
    what_i_struggled_with: Optional[str] = None
    what_i_need: Optional[str] = None
    content_type: str
    text_content: Optional[str] = None
    media_url: Optional[str] = None
    is_read: bool
    response_id: Optional[UUID] = None
    created_at: datetime

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": "checkin-uuid",
                "partnership_id": "partnership-uuid",
                "author": {
                    "id": "author-uuid",
                    "username": "marcus_design",
                    "full_name": "Marcus Design",
                    "profile_picture_url": None
                },
                "what_i_did": "Applied to 5 senior roles, had 2 phone screens this week",
                "what_i_struggled_with": "Imposter syndrome during technical interviews",
                "what_i_need": "Help practicing answers to leadership questions",
                "content_type": "text",
                "text_content": None,
                "media_url": None,
                "is_read": False,
                "response_id": None,
                "created_at": "2025-11-18T14:30:00Z"
            }
        }
    )


class CheckInListResponse(BaseModel):
    """Schema for listing check-ins."""
    check_ins: list[CheckInResponse]
    total: int
    has_more: bool

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "check_ins": [],
                "total": 0,
                "has_more": False
            }
        }
    )
