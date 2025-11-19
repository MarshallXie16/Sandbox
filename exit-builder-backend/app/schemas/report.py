"""
Report schemas
"""
from pydantic import BaseModel
from datetime import datetime
from uuid import UUID


class ReportResponse(BaseModel):
    """Schema for report response"""
    id: UUID
    project_id: UUID
    template_code: str
    content: str
    format: str
    created_at: datetime

    class Config:
        from_attributes = True
