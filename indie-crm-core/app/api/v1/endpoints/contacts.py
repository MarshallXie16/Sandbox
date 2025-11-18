"""Contact API endpoints"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.core.deps import get_db
from app.repositories.contact import ContactRepository
from app.schemas.contact import ContactCreate, ContactUpdate, ContactResponse
from app.models.contact import ContactCategory

router = APIRouter()


@router.get("/", response_model=List[ContactResponse])
def list_contacts(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    category: Optional[ContactCategory] = None,
    is_active: Optional[bool] = None,
    db: Session = Depends(get_db),
):
    """
    List contacts with optional filtering.

    - **skip**: Number of records to skip (pagination)
    - **limit**: Maximum number of records to return
    - **category**: Filter by contact category
    - **is_active**: Filter by active status
    """
    repo = ContactRepository(db)

    filters = {}
    if category:
        filters["category"] = category
    if is_active is not None:
        filters["is_active"] = is_active

    contacts = repo.get_multi(skip=skip, limit=limit, filters=filters)
    return contacts


@router.get("/{contact_id}", response_model=ContactResponse)
def get_contact(contact_id: int, db: Session = Depends(get_db)):
    """Get a specific contact by ID"""
    repo = ContactRepository(db)
    contact = repo.get(contact_id)
    if not contact:
        raise HTTPException(status_code=404, detail="Contact not found")
    return contact


@router.post("/", response_model=ContactResponse, status_code=201)
def create_contact(contact_in: ContactCreate, db: Session = Depends(get_db)):
    """
    Create a new contact.

    Example request body:
    ```json
    {
        "first_name": "John",
        "last_name": "Doe",
        "primary_email": "john.doe@example.com",
        "category": "buyer",
        "details": {
            "industry": "Technology",
            "budget": 5000000,
            "geographic_preference": "North America"
        }
    }
    ```
    """
    repo = ContactRepository(db)

    # Check if email already exists
    existing = repo.get_by_email(contact_in.primary_email)
    if existing:
        raise HTTPException(
            status_code=400,
            detail=f"Contact with email {contact_in.primary_email} already exists",
        )

    contact = repo.create(contact_in.model_dump())
    return contact


@router.put("/{contact_id}", response_model=ContactResponse)
def update_contact(
    contact_id: int,
    contact_in: ContactUpdate,
    db: Session = Depends(get_db),
):
    """Update an existing contact"""
    repo = ContactRepository(db)

    # Check if contact exists
    if not repo.get(contact_id):
        raise HTTPException(status_code=404, detail="Contact not found")

    # If updating email, check for duplicates
    if contact_in.primary_email:
        existing = repo.get_by_email(contact_in.primary_email)
        if existing and existing.id != contact_id:
            raise HTTPException(
                status_code=400,
                detail=f"Contact with email {contact_in.primary_email} already exists",
            )

    # Only include non-None values in update
    update_data = contact_in.model_dump(exclude_unset=True)
    contact = repo.update(contact_id, update_data)
    return contact


@router.delete("/{contact_id}", status_code=204)
def delete_contact(contact_id: int, db: Session = Depends(get_db)):
    """Delete a contact"""
    repo = ContactRepository(db)
    deleted = repo.delete(contact_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Contact not found")
    return None
