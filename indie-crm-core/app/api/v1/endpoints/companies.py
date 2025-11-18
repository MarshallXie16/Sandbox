"""Company API endpoints"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.core.deps import get_db
from app.repositories.company import CompanyRepository
from app.schemas.company import CompanyCreate, CompanyUpdate, CompanyResponse

router = APIRouter()


@router.get("/", response_model=List[CompanyResponse])
def list_companies(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    industry: Optional[str] = None,
    db: Session = Depends(get_db),
):
    """
    List companies with optional filtering.

    - **skip**: Number of records to skip (pagination)
    - **limit**: Maximum number of records to return
    - **industry**: Filter by industry
    """
    repo = CompanyRepository(db)

    filters = {}
    if industry:
        filters["industry"] = industry

    companies = repo.get_multi(skip=skip, limit=limit, filters=filters)
    return companies


@router.get("/search", response_model=List[CompanyResponse])
def search_companies(
    name: str = Query(..., min_length=1),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db),
):
    """Search companies by name (partial match, case-insensitive)"""
    repo = CompanyRepository(db)
    companies = repo.search_by_name(name, skip=skip, limit=limit)
    return companies


@router.get("/{company_id}", response_model=CompanyResponse)
def get_company(company_id: int, db: Session = Depends(get_db)):
    """Get a specific company by ID"""
    repo = CompanyRepository(db)
    company = repo.get(company_id)
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    return company


@router.post("/", response_model=CompanyResponse, status_code=201)
def create_company(company_in: CompanyCreate, db: Session = Depends(get_db)):
    """
    Create a new company.

    Example request body:
    ```json
    {
        "name": "Acme Corporation",
        "location": "San Francisco, CA",
        "website": "https://acme.com",
        "industry": "Technology",
        "revenue": 10000000,
        "employees": 50,
        "details": {
            "parent_company": "Acme Holdings",
            "subsidiaries": ["Acme Labs", "Acme Consulting"]
        }
    }
    ```
    """
    repo = CompanyRepository(db)
    company = repo.create(company_in.model_dump())
    return company


@router.put("/{company_id}", response_model=CompanyResponse)
def update_company(
    company_id: int,
    company_in: CompanyUpdate,
    db: Session = Depends(get_db),
):
    """Update an existing company"""
    repo = CompanyRepository(db)

    # Check if company exists
    if not repo.get(company_id):
        raise HTTPException(status_code=404, detail="Company not found")

    # Only include non-None values in update
    update_data = company_in.model_dump(exclude_unset=True)
    company = repo.update(company_id, update_data)
    return company


@router.delete("/{company_id}", status_code=204)
def delete_company(company_id: int, db: Session = Depends(get_db)):
    """Delete a company"""
    repo = CompanyRepository(db)
    deleted = repo.delete(company_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Company not found")
    return None
