"""
Pydantic schemas for Exit Ready documents.
"""
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field


class DocBase(BaseModel):
    """Base schema for Exit Ready document."""
    doc_type: str = Field(..., min_length=1, max_length=100)
    label: str = Field(..., min_length=1, max_length=255)
    required: bool = True
    notes: Optional[str] = None


class DocCreate(DocBase):
    """Schema for creating a new document entry."""
    case_id: int


class DocUpdate(BaseModel):
    """Schema for updating a document."""
    label: Optional[str] = Field(None, min_length=1, max_length=255)
    required: Optional[bool] = None
    status: Optional[str] = Field(None, pattern="^(pending|received|waived)$")
    file_url: Optional[str] = None
    notes: Optional[str] = None


class DocStatusUpdate(BaseModel):
    """Schema for updating document status."""
    status: str = Field(..., pattern="^(pending|received|waived)$")
    file_url: Optional[str] = None
    notes: Optional[str] = None


class DocResponse(DocBase):
    """Schema for document response."""
    id: int
    case_id: int
    status: str
    received_at: Optional[datetime]
    file_url: Optional[str]
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class DocChecklist(BaseModel):
    """Schema for document checklist summary."""
    case_id: int
    total_docs: int
    required_docs: int
    received_docs: int
    pending_docs: int
    waived_docs: int
    completion_percentage: float
    documents: List[DocResponse]


class BulkDocCreate(BaseModel):
    """Schema for creating multiple document entries."""
    case_id: int
    documents: List[DocBase]
