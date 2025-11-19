"""
Score schemas
"""
from pydantic import BaseModel
from typing import List, Optional


class DimensionScore(BaseModel):
    """Schema for dimension score"""
    code: str
    name: str
    score: int
    weight: float
    comment: str


class ScoreResponse(BaseModel):
    """Schema for score result response"""
    total_score: int
    rating: str
    adjustment_factor: float
    dimensions: List[DimensionScore]


class StandardValuationResponse(BaseModel):
    """Schema for standard valuation response"""
    project_id: str
    baseline_valuation: dict
    score: dict
    adjusted_valuation: dict
    primary_method: Optional[str]
