"""Pipeline and Stage repositories"""
from typing import Optional, List
from sqlalchemy.orm import Session
from app.models.pipeline import DealPipeline, DealStage, PipelineType
from app.repositories.base import BaseRepository


class PipelineRepository(BaseRepository[DealPipeline]):
    """Repository for DealPipeline operations"""

    def __init__(self, db: Session):
        super().__init__(DealPipeline, db)

    def get_by_type(
        self, pipeline_type: PipelineType, skip: int = 0, limit: int = 100
    ) -> List[DealPipeline]:
        """Get pipelines by type"""
        return (
            self.db.query(DealPipeline)
            .filter(DealPipeline.type == pipeline_type)
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_active(self, skip: int = 0, limit: int = 100) -> List[DealPipeline]:
        """Get active pipelines"""
        return (
            self.db.query(DealPipeline)
            .filter(DealPipeline.is_active == True)
            .offset(skip)
            .limit(limit)
            .all()
        )


class StageRepository(BaseRepository[DealStage]):
    """Repository for DealStage operations"""

    def __init__(self, db: Session):
        super().__init__(DealStage, db)

    def get_by_pipeline(self, pipeline_id: int) -> List[DealStage]:
        """Get all stages for a pipeline, ordered by order_index"""
        return (
            self.db.query(DealStage)
            .filter(DealStage.pipeline_id == pipeline_id)
            .order_by(DealStage.order_index)
            .all()
        )

    def get_won_stages(self) -> List[DealStage]:
        """Get all 'won' stages"""
        return self.db.query(DealStage).filter(DealStage.is_closed_won == True).all()

    def get_lost_stages(self) -> List[DealStage]:
        """Get all 'lost' stages"""
        return self.db.query(DealStage).filter(DealStage.is_closed_lost == True).all()
