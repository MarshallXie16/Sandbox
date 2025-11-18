"""Company repository"""
from typing import Optional, List
from sqlalchemy.orm import Session
from app.models.company import Company
from app.repositories.base import BaseRepository


class CompanyRepository(BaseRepository[Company]):
    """Repository for Company operations"""

    def __init__(self, db: Session):
        super().__init__(Company, db)

    def get_by_name(self, name: str) -> Optional[Company]:
        """Get company by name (exact match)"""
        return self.db.query(Company).filter(Company.name == name).first()

    def search_by_name(self, name: str, skip: int = 0, limit: int = 100) -> List[Company]:
        """Search companies by name (partial match, case-insensitive)"""
        return (
            self.db.query(Company)
            .filter(Company.name.ilike(f"%{name}%"))
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_by_industry(
        self, industry: str, skip: int = 0, limit: int = 100
    ) -> List[Company]:
        """Get companies by industry"""
        return (
            self.db.query(Company)
            .filter(Company.industry == industry)
            .offset(skip)
            .limit(limit)
            .all()
        )
