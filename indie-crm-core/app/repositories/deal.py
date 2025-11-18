"""Deal repository"""
from typing import Optional, List
from sqlalchemy.orm import Session
from app.models.deal import Deal, DealStatus
from app.models.pipeline import PipelineType
from app.repositories.base import BaseRepository


class DealRepository(BaseRepository[Deal]):
    """Repository for Deal operations"""

    def __init__(self, db: Session):
        super().__init__(Deal, db)

    def get_by_pipeline(
        self, pipeline_id: int, skip: int = 0, limit: int = 100
    ) -> List[Deal]:
        """Get deals by pipeline"""
        return (
            self.db.query(Deal)
            .filter(Deal.pipeline_id == pipeline_id)
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_by_stage(self, stage_id: int, skip: int = 0, limit: int = 100) -> List[Deal]:
        """Get deals by stage"""
        return (
            self.db.query(Deal)
            .filter(Deal.stage_id == stage_id)
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_by_status(
        self, status: DealStatus, skip: int = 0, limit: int = 100
    ) -> List[Deal]:
        """Get deals by status"""
        return (
            self.db.query(Deal)
            .filter(Deal.status == status)
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_by_pipeline_type(
        self, pipeline_type: PipelineType, skip: int = 0, limit: int = 100
    ) -> List[Deal]:
        """Get deals by pipeline type (seller/buyer)"""
        return (
            self.db.query(Deal)
            .filter(Deal.pipeline_type == pipeline_type)
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_by_owner(self, owner_id: int, skip: int = 0, limit: int = 100) -> List[Deal]:
        """Get deals by owner"""
        return (
            self.db.query(Deal)
            .filter(Deal.owner_id == owner_id)
            .offset(skip)
            .limit(limit)
            .all()
        )
