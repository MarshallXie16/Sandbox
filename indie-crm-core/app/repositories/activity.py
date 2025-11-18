"""Activity repository"""
from typing import Optional, List
from datetime import datetime
from sqlalchemy.orm import Session
from app.models.activity import Activity, ActivityType
from app.repositories.base import BaseRepository


class ActivityRepository(BaseRepository[Activity]):
    """Repository for Activity operations"""

    def __init__(self, db: Session):
        super().__init__(Activity, db)

    def get_by_type(
        self, activity_type: ActivityType, skip: int = 0, limit: int = 100
    ) -> List[Activity]:
        """Get activities by type"""
        return (
            self.db.query(Activity)
            .filter(Activity.type == activity_type)
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_by_date_range(
        self,
        start_date: datetime,
        end_date: datetime,
        skip: int = 0,
        limit: int = 100,
    ) -> List[Activity]:
        """Get activities within a date range"""
        return (
            self.db.query(Activity)
            .filter(Activity.happened_at >= start_date)
            .filter(Activity.happened_at <= end_date)
            .order_by(Activity.happened_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_by_owner(
        self, owner_id: int, skip: int = 0, limit: int = 100
    ) -> List[Activity]:
        """Get activities by owner"""
        return (
            self.db.query(Activity)
            .filter(Activity.owner_id == owner_id)
            .order_by(Activity.happened_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )
