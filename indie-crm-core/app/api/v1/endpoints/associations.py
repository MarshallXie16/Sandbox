"""Association API endpoints for linking entities"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.deps import get_db
from app.repositories.association import (
    ContactCompanyRepository,
    ContactDealRepository,
    CompanyDealRepository,
    ActivityContactRepository,
    ActivityCompanyRepository,
    ActivityDealRepository,
)
from app.schemas.association import (
    ContactCompanyCreate,
    ContactCompanyResponse,
    ContactDealCreate,
    ContactDealResponse,
    CompanyDealCreate,
    CompanyDealResponse,
    ActivityContactCreate,
    ActivityContactResponse,
    ActivityCompanyCreate,
    ActivityCompanyResponse,
    ActivityDealCreate,
    ActivityDealResponse,
)

router = APIRouter()


# Contact-Company Associations
@router.post("/contact-company", response_model=ContactCompanyResponse, status_code=201)
def create_contact_company_association(
    assoc_in: ContactCompanyCreate,
    db: Session = Depends(get_db),
):
    """
    Link a contact to a company.

    Example:
    ```json
    {
        "contact_id": 1,
        "company_id": 5,
        "role": "CEO",
        "is_primary": true
    }
    ```
    """
    repo = ContactCompanyRepository(db)

    # Check if association already exists
    existing = repo.get_association(assoc_in.contact_id, assoc_in.company_id)
    if existing:
        raise HTTPException(
            status_code=400,
            detail="Association already exists",
        )

    assoc = repo.create(assoc_in.model_dump())
    return assoc


@router.get("/contact/{contact_id}/companies", response_model=List[ContactCompanyResponse])
def get_companies_for_contact(contact_id: int, db: Session = Depends(get_db)):
    """Get all companies associated with a contact"""
    repo = ContactCompanyRepository(db)
    associations = repo.get_by_contact(contact_id)
    return associations


@router.get("/company/{company_id}/contacts", response_model=List[ContactCompanyResponse])
def get_contacts_for_company(company_id: int, db: Session = Depends(get_db)):
    """Get all contacts associated with a company"""
    repo = ContactCompanyRepository(db)
    associations = repo.get_by_company(company_id)
    return associations


@router.delete("/contact-company/{contact_id}/{company_id}", status_code=204)
def delete_contact_company_association(
    contact_id: int,
    company_id: int,
    db: Session = Depends(get_db),
):
    """Unlink a contact from a company"""
    repo = ContactCompanyRepository(db)
    deleted = repo.delete_association(contact_id, company_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Association not found")
    return None


# Contact-Deal Associations
@router.post("/contact-deal", response_model=ContactDealResponse, status_code=201)
def create_contact_deal_association(
    assoc_in: ContactDealCreate,
    db: Session = Depends(get_db),
):
    """
    Link a contact to a deal.

    Example:
    ```json
    {
        "contact_id": 1,
        "deal_id": 3,
        "role": "Decision Maker"
    }
    ```
    """
    repo = ContactDealRepository(db)

    existing = repo.get_association(assoc_in.contact_id, assoc_in.deal_id)
    if existing:
        raise HTTPException(status_code=400, detail="Association already exists")

    assoc = repo.create(assoc_in.model_dump())
    return assoc


@router.get("/contact/{contact_id}/deals", response_model=List[ContactDealResponse])
def get_deals_for_contact(contact_id: int, db: Session = Depends(get_db)):
    """Get all deals associated with a contact"""
    repo = ContactDealRepository(db)
    associations = repo.get_by_contact(contact_id)
    return associations


@router.get("/deal/{deal_id}/contacts", response_model=List[ContactDealResponse])
def get_contacts_for_deal(deal_id: int, db: Session = Depends(get_db)):
    """Get all contacts associated with a deal"""
    repo = ContactDealRepository(db)
    associations = repo.get_by_deal(deal_id)
    return associations


@router.delete("/contact-deal/{contact_id}/{deal_id}", status_code=204)
def delete_contact_deal_association(
    contact_id: int,
    deal_id: int,
    db: Session = Depends(get_db),
):
    """Unlink a contact from a deal"""
    repo = ContactDealRepository(db)
    deleted = repo.delete_association(contact_id, deal_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Association not found")
    return None


# Company-Deal Associations
@router.post("/company-deal", response_model=CompanyDealResponse, status_code=201)
def create_company_deal_association(
    assoc_in: CompanyDealCreate,
    db: Session = Depends(get_db),
):
    """
    Link a company to a deal.

    Example:
    ```json
    {
        "company_id": 5,
        "deal_id": 3,
        "role": "Seller"
    }
    ```
    """
    repo = CompanyDealRepository(db)

    existing = repo.get_association(assoc_in.company_id, assoc_in.deal_id)
    if existing:
        raise HTTPException(status_code=400, detail="Association already exists")

    assoc = repo.create(assoc_in.model_dump())
    return assoc


@router.get("/company/{company_id}/deals", response_model=List[CompanyDealResponse])
def get_deals_for_company(company_id: int, db: Session = Depends(get_db)):
    """Get all deals associated with a company"""
    repo = CompanyDealRepository(db)
    associations = repo.get_by_company(company_id)
    return associations


@router.get("/deal/{deal_id}/companies", response_model=List[CompanyDealResponse])
def get_companies_for_deal(deal_id: int, db: Session = Depends(get_db)):
    """Get all companies associated with a deal"""
    repo = CompanyDealRepository(db)
    associations = repo.get_by_deal(deal_id)
    return associations


@router.delete("/company-deal/{company_id}/{deal_id}", status_code=204)
def delete_company_deal_association(
    company_id: int,
    deal_id: int,
    db: Session = Depends(get_db),
):
    """Unlink a company from a deal"""
    repo = CompanyDealRepository(db)
    deleted = repo.delete_association(company_id, deal_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Association not found")
    return None


# Activity-Contact Associations
@router.post("/activity-contact", response_model=ActivityContactResponse, status_code=201)
def create_activity_contact_association(
    assoc_in: ActivityContactCreate,
    db: Session = Depends(get_db),
):
    """Link an activity to a contact"""
    repo = ActivityContactRepository(db)
    assoc = repo.create(assoc_in.model_dump())
    return assoc


@router.get("/activity/{activity_id}/contacts", response_model=List[ActivityContactResponse])
def get_contacts_for_activity(activity_id: int, db: Session = Depends(get_db)):
    """Get all contacts associated with an activity"""
    repo = ActivityContactRepository(db)
    associations = repo.get_by_activity(activity_id)
    return associations


@router.delete("/activity-contact/{activity_id}/{contact_id}", status_code=204)
def delete_activity_contact_association(
    activity_id: int,
    contact_id: int,
    db: Session = Depends(get_db),
):
    """Unlink an activity from a contact"""
    repo = ActivityContactRepository(db)
    deleted = repo.delete_association(activity_id, contact_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Association not found")
    return None


# Activity-Company Associations
@router.post("/activity-company", response_model=ActivityCompanyResponse, status_code=201)
def create_activity_company_association(
    assoc_in: ActivityCompanyCreate,
    db: Session = Depends(get_db),
):
    """Link an activity to a company"""
    repo = ActivityCompanyRepository(db)
    assoc = repo.create(assoc_in.model_dump())
    return assoc


@router.get("/activity/{activity_id}/companies", response_model=List[ActivityCompanyResponse])
def get_companies_for_activity(activity_id: int, db: Session = Depends(get_db)):
    """Get all companies associated with an activity"""
    repo = ActivityCompanyRepository(db)
    associations = repo.get_by_activity(activity_id)
    return associations


@router.delete("/activity-company/{activity_id}/{company_id}", status_code=204)
def delete_activity_company_association(
    activity_id: int,
    company_id: int,
    db: Session = Depends(get_db),
):
    """Unlink an activity from a company"""
    repo = ActivityCompanyRepository(db)
    deleted = repo.delete_association(activity_id, company_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Association not found")
    return None


# Activity-Deal Associations
@router.post("/activity-deal", response_model=ActivityDealResponse, status_code=201)
def create_activity_deal_association(
    assoc_in: ActivityDealCreate,
    db: Session = Depends(get_db),
):
    """Link an activity to a deal"""
    repo = ActivityDealRepository(db)
    assoc = repo.create(assoc_in.model_dump())
    return assoc


@router.get("/activity/{activity_id}/deals", response_model=List[ActivityDealResponse])
def get_deals_for_activity(activity_id: int, db: Session = Depends(get_db)):
    """Get all deals associated with an activity"""
    repo = ActivityDealRepository(db)
    associations = repo.get_by_activity(activity_id)
    return associations


@router.delete("/activity-deal/{activity_id}/{deal_id}", status_code=204)
def delete_activity_deal_association(
    activity_id: int,
    deal_id: int,
    db: Session = Depends(get_db),
):
    """Unlink an activity from a deal"""
    repo = ActivityDealRepository(db)
    deleted = repo.delete_association(activity_id, deal_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Association not found")
    return None
