"""Matching schemas for request/response validation."""
from pydantic import BaseModel, Field
from typing import List, Optional, Dict
from datetime import datetime
from uuid import UUID


class MatchExplanation(BaseModel):
    """Explanation of why two users matched."""
    you_help_with: List[str] = Field(description="Areas where you can help your partner")
    they_help_with: List[str] = Field(description="Areas where they can help you")


class MatchSuggestion(BaseModel):
    """A suggested match for a user."""
    user_id: UUID
    username: str
    profile_picture_url: Optional[str] = None
    compatibility_score: float = Field(ge=0.0, le=1.0, description="Match compatibility (0-1)")
    strengths: List[str]
    struggles: List[str]
    communication_style: Optional[str] = None
    commitment_level: Optional[str] = None
    why_matched: MatchExplanation


class QueueStatusResponse(BaseModel):
    """Response for queue status check."""
    in_queue: bool
    status: str  # 'pending', 'matched', 'expired'
    queue_position: Optional[int] = None
    entered_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None
    has_suggestions: bool = False
    suggestions_count: int = 0


class MatchSuggestionsResponse(BaseModel):
    """Response containing match suggestions."""
    suggestions: List[MatchSuggestion]
    queue_position: Optional[int] = None
    total_in_queue: int


class AcceptMatchRequest(BaseModel):
    """Request to accept a match."""
    match_id: UUID = Field(description="User ID of the person to match with")


class DeclineMatchRequest(BaseModel):
    """Request to decline a match."""
    match_id: UUID = Field(description="User ID of the person to decline")
    reason: Optional[str] = Field(None, max_length=500, description="Optional decline reason")


class PartnerInfo(BaseModel):
    """Public partner information."""
    id: UUID
    username: str
    full_name: Optional[str] = None
    profile_picture_url: Optional[str] = None
    strengths: List[str]
    struggles: List[str]


class PartnershipCreatedResponse(BaseModel):
    """Response after successfully creating a partnership."""
    partnership_id: UUID
    partner: PartnerInfo
    season_number: int
    season_start_date: datetime
    season_end_date: datetime
    status: str
    message: str = "Partnership created successfully!"

    model_config = {"from_attributes": True}
