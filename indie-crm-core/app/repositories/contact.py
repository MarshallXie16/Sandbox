"""Contact repository"""
from typing import Optional, List
from sqlalchemy.orm import Session
from app.models.contact import Contact, ContactCategory
from app.repositories.base import BaseRepository


class ContactRepository(BaseRepository[Contact]):
    """Repository for Contact operations"""

    def __init__(self, db: Session):
        super().__init__(Contact, db)

    def get_by_email(self, email: str) -> Optional[Contact]:
        """Get contact by primary email"""
        return self.db.query(Contact).filter(Contact.primary_email == email).first()

    def get_by_category(
        self, category: ContactCategory, skip: int = 0, limit: int = 100
    ) -> List[Contact]:
        """Get contacts by category"""
        return (
            self.db.query(Contact)
            .filter(Contact.category == category)
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_active(self, skip: int = 0, limit: int = 100) -> List[Contact]:
        """Get active contacts"""
        return (
            self.db.query(Contact)
            .filter(Contact.is_active == True)
            .offset(skip)
            .limit(limit)
            .all()
        )
