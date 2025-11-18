"""Association repositories for managing relationships between entities"""
from typing import List, Optional
from sqlalchemy.orm import Session
from app.models.associations import (
    ContactCompany,
    ContactDeal,
    CompanyDeal,
    ActivityContact,
    ActivityCompany,
    ActivityDeal,
)
from app.repositories.base import BaseRepository


class ContactCompanyRepository(BaseRepository[ContactCompany]):
    """Repository for Contact-Company associations"""

    def __init__(self, db: Session):
        super().__init__(ContactCompany, db)

    def get_by_contact(self, contact_id: int) -> List[ContactCompany]:
        """Get all companies for a contact"""
        return (
            self.db.query(ContactCompany)
            .filter(ContactCompany.contact_id == contact_id)
            .all()
        )

    def get_by_company(self, company_id: int) -> List[ContactCompany]:
        """Get all contacts for a company"""
        return (
            self.db.query(ContactCompany)
            .filter(ContactCompany.company_id == company_id)
            .all()
        )

    def get_association(
        self, contact_id: int, company_id: int
    ) -> Optional[ContactCompany]:
        """Get specific contact-company association"""
        return (
            self.db.query(ContactCompany)
            .filter(
                ContactCompany.contact_id == contact_id,
                ContactCompany.company_id == company_id,
            )
            .first()
        )

    def delete_association(self, contact_id: int, company_id: int) -> bool:
        """Delete contact-company association"""
        assoc = self.get_association(contact_id, company_id)
        if assoc:
            self.db.delete(assoc)
            self.db.commit()
            return True
        return False


class ContactDealRepository(BaseRepository[ContactDeal]):
    """Repository for Contact-Deal associations"""

    def __init__(self, db: Session):
        super().__init__(ContactDeal, db)

    def get_by_contact(self, contact_id: int) -> List[ContactDeal]:
        """Get all deals for a contact"""
        return (
            self.db.query(ContactDeal).filter(ContactDeal.contact_id == contact_id).all()
        )

    def get_by_deal(self, deal_id: int) -> List[ContactDeal]:
        """Get all contacts for a deal"""
        return self.db.query(ContactDeal).filter(ContactDeal.deal_id == deal_id).all()

    def get_association(self, contact_id: int, deal_id: int) -> Optional[ContactDeal]:
        """Get specific contact-deal association"""
        return (
            self.db.query(ContactDeal)
            .filter(
                ContactDeal.contact_id == contact_id,
                ContactDeal.deal_id == deal_id,
            )
            .first()
        )

    def delete_association(self, contact_id: int, deal_id: int) -> bool:
        """Delete contact-deal association"""
        assoc = self.get_association(contact_id, deal_id)
        if assoc:
            self.db.delete(assoc)
            self.db.commit()
            return True
        return False


class CompanyDealRepository(BaseRepository[CompanyDeal]):
    """Repository for Company-Deal associations"""

    def __init__(self, db: Session):
        super().__init__(CompanyDeal, db)

    def get_by_company(self, company_id: int) -> List[CompanyDeal]:
        """Get all deals for a company"""
        return (
            self.db.query(CompanyDeal).filter(CompanyDeal.company_id == company_id).all()
        )

    def get_by_deal(self, deal_id: int) -> List[CompanyDeal]:
        """Get all companies for a deal"""
        return self.db.query(CompanyDeal).filter(CompanyDeal.deal_id == deal_id).all()

    def get_association(self, company_id: int, deal_id: int) -> Optional[CompanyDeal]:
        """Get specific company-deal association"""
        return (
            self.db.query(CompanyDeal)
            .filter(
                CompanyDeal.company_id == company_id,
                CompanyDeal.deal_id == deal_id,
            )
            .first()
        )

    def delete_association(self, company_id: int, deal_id: int) -> bool:
        """Delete company-deal association"""
        assoc = self.get_association(company_id, deal_id)
        if assoc:
            self.db.delete(assoc)
            self.db.commit()
            return True
        return False


class ActivityContactRepository(BaseRepository[ActivityContact]):
    """Repository for Activity-Contact associations"""

    def __init__(self, db: Session):
        super().__init__(ActivityContact, db)

    def get_by_activity(self, activity_id: int) -> List[ActivityContact]:
        """Get all contacts for an activity"""
        return (
            self.db.query(ActivityContact)
            .filter(ActivityContact.activity_id == activity_id)
            .all()
        )

    def get_by_contact(self, contact_id: int) -> List[ActivityContact]:
        """Get all activities for a contact"""
        return (
            self.db.query(ActivityContact)
            .filter(ActivityContact.contact_id == contact_id)
            .all()
        )

    def delete_association(self, activity_id: int, contact_id: int) -> bool:
        """Delete activity-contact association"""
        assoc = (
            self.db.query(ActivityContact)
            .filter(
                ActivityContact.activity_id == activity_id,
                ActivityContact.contact_id == contact_id,
            )
            .first()
        )
        if assoc:
            self.db.delete(assoc)
            self.db.commit()
            return True
        return False


class ActivityCompanyRepository(BaseRepository[ActivityCompany]):
    """Repository for Activity-Company associations"""

    def __init__(self, db: Session):
        super().__init__(ActivityCompany, db)

    def get_by_activity(self, activity_id: int) -> List[ActivityCompany]:
        """Get all companies for an activity"""
        return (
            self.db.query(ActivityCompany)
            .filter(ActivityCompany.activity_id == activity_id)
            .all()
        )

    def get_by_company(self, company_id: int) -> List[ActivityCompany]:
        """Get all activities for a company"""
        return (
            self.db.query(ActivityCompany)
            .filter(ActivityCompany.company_id == company_id)
            .all()
        )

    def delete_association(self, activity_id: int, company_id: int) -> bool:
        """Delete activity-company association"""
        assoc = (
            self.db.query(ActivityCompany)
            .filter(
                ActivityCompany.activity_id == activity_id,
                ActivityCompany.company_id == company_id,
            )
            .first()
        )
        if assoc:
            self.db.delete(assoc)
            self.db.commit()
            return True
        return False


class ActivityDealRepository(BaseRepository[ActivityDeal]):
    """Repository for Activity-Deal associations"""

    def __init__(self, db: Session):
        super().__init__(ActivityDeal, db)

    def get_by_activity(self, activity_id: int) -> List[ActivityDeal]:
        """Get all deals for an activity"""
        return (
            self.db.query(ActivityDeal)
            .filter(ActivityDeal.activity_id == activity_id)
            .all()
        )

    def get_by_deal(self, deal_id: int) -> List[ActivityDeal]:
        """Get all activities for a deal"""
        return (
            self.db.query(ActivityDeal).filter(ActivityDeal.deal_id == deal_id).all()
        )

    def delete_association(self, activity_id: int, deal_id: int) -> bool:
        """Delete activity-deal association"""
        assoc = (
            self.db.query(ActivityDeal)
            .filter(
                ActivityDeal.activity_id == activity_id,
                ActivityDeal.deal_id == deal_id,
            )
            .first()
        )
        if assoc:
            self.db.delete(assoc)
            self.db.commit()
            return True
        return False
