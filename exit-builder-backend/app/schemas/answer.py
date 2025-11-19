"""
Answer schemas
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Any


class AnswerCreate(BaseModel):
    """Schema for creating/updating an answer"""
    question_code: str = Field(..., description="Question code (e.g., Q_OWNER_ROLE)")
    value_text: Optional[str] = None
    value_numeric: Optional[float] = None
    selected_option_values: Optional[List[str]] = None


class AnswersSubmit(BaseModel):
    """Schema for submitting multiple answers"""
    answers: List[AnswerCreate]


class AnswerResponse(BaseModel):
    """Schema for answer response"""
    id: str
    question_id: str
    question_code: str
    question_text: str
    question_section: str
    input_type: str
    value_text: Optional[str]
    value_numeric: Optional[float]
    selected_option_values: Optional[List[str]]
    created_at: str
    updated_at: str
