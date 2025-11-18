# Extensibility Guide

This guide explains how to extend IndieStack CRM without modifying core domain logic.

## Architecture Principles

The system is designed with clear layer separation:

```
API Layer (FastAPI routes)
    ↓
Service Layer (future - business logic)
    ↓
Repository Layer (data access)
    ↓
Model Layer (SQLAlchemy ORM)
```

This architecture allows you to:
- Swap implementations without changing interfaces
- Add new entities without touching existing code
- Integrate with external systems via the details JSONB field
- Extend functionality through composition, not modification

## Adding Custom Fields (No Schema Changes)

All main entities include a `details` JSONB field for storing custom attributes.

### Example: Adding Fields to Contacts

```python
# Create contact with custom fields
contact_data = {
    "first_name": "John",
    "last_name": "Doe",
    "primary_email": "john@example.com",
    "category": "buyer",
    "details": {
        # Standard buyer fields
        "industry": "Healthcare",
        "budget": 5000000,

        # Custom fields (no migration needed!)
        "preferred_communication": "email",
        "timezone": "PST",
        "investment_thesis": "Roll-up strategy in healthcare IT",
        "risk_tolerance": "moderate",
        "decision_timeframe": "Q2 2025"
    }
}
```

### Querying Custom Fields

PostgreSQL JSONB supports powerful queries:

```python
from sqlalchemy import func

# Find buyers in healthcare industry
buyers = db.query(Contact).filter(
    Contact.category == "buyer",
    Contact.details["industry"].astext == "Healthcare"
).all()

# Find contacts with budget > 3M
wealthy_buyers = db.query(Contact).filter(
    Contact.category == "buyer",
    func.cast(Contact.details["budget"], Integer) > 3000000
).all()

# Find contacts by nested field
contacts = db.query(Contact).filter(
    Contact.details["preferences"]["communication"].astext == "phone"
).all()
```

## Adding Integration Metadata

Use the `details` field to store external system IDs:

### HubSpot Integration Example

```python
# Store HubSpot IDs when syncing
contact_data = {
    "first_name": "Jane",
    "last_name": "Smith",
    "primary_email": "jane@example.com",
    "details": {
        # Native CRM fields
        "industry": "SaaS",

        # Integration metadata
        "hubspot_contact_id": "12345678",
        "hubspot_last_sync": "2025-01-15T10:30:00Z",
        "sync_status": "active"
    }
}

# When syncing back to HubSpot
hubspot_id = contact.details.get("hubspot_contact_id")
if hubspot_id:
    hubspot_client.update_contact(hubspot_id, changes)
```

### Multiple Integration Support

```python
company_data = {
    "name": "Acme Corp",
    "details": {
        # Multiple external system IDs
        "hubspot_company_id": "hs-12345",
        "salesforce_account_id": "sf-67890",
        "zoho_company_id": "zoho-abc123",

        # Integration sync metadata
        "integrations": {
            "hubspot": {
                "id": "hs-12345",
                "last_sync": "2025-01-15T10:30:00Z",
                "sync_direction": "bidirectional"
            },
            "salesforce": {
                "id": "sf-67890",
                "last_sync": "2025-01-15T10:25:00Z",
                "sync_direction": "pull_only"
            }
        }
    }
}
```

## Adding a New Entity

Follow these steps to add a new entity (e.g., "Task"):

### 1. Create Model (`app/models/task.py`)

```python
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.sql import func
from app.db.base import Base

class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    due_date = Column(DateTime, nullable=True)
    status = Column(String(50), default="pending")
    owner_id = Column(Integer, nullable=True)

    # Link to deal
    deal_id = Column(Integer, ForeignKey("deals.id", ondelete="CASCADE"))

    # Extensible custom fields
    details = Column(JSONB, default=dict, server_default="{}")

    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
```

### 2. Create Repository (`app/repositories/task.py`)

```python
from app.repositories.base import BaseRepository
from app.models.task import Task

class TaskRepository(BaseRepository[Task]):
    def __init__(self, db: Session):
        super().__init__(Task, db)

    def get_by_deal(self, deal_id: int):
        return self.db.query(Task).filter(Task.deal_id == deal_id).all()

    def get_overdue(self):
        from datetime import datetime
        return self.db.query(Task).filter(
            Task.due_date < datetime.utcnow(),
            Task.status != "completed"
        ).all()
```

### 3. Create Schemas (`app/schemas/task.py`)

```python
from pydantic import BaseModel
from datetime import datetime

class TaskBase(BaseModel):
    title: str
    description: str | None = None
    due_date: datetime | None = None
    status: str = "pending"
    owner_id: int | None = None
    deal_id: int | None = None
    details: dict = {}

class TaskCreate(TaskBase):
    pass

class TaskUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    due_date: datetime | None = None
    status: str | None = None
    details: dict | None = None

class TaskResponse(TaskBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
```

### 4. Create Endpoints (`app/api/v1/endpoints/tasks.py`)

```python
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.deps import get_db
from app.repositories.task import TaskRepository
from app.schemas.task import TaskCreate, TaskUpdate, TaskResponse

router = APIRouter()

@router.get("/", response_model=list[TaskResponse])
def list_tasks(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    repo = TaskRepository(db)
    return repo.get_multi(skip=skip, limit=limit)

@router.post("/", response_model=TaskResponse, status_code=201)
def create_task(task_in: TaskCreate, db: Session = Depends(get_db)):
    repo = TaskRepository(db)
    return repo.create(task_in.model_dump())

# ... other endpoints
```

### 5. Register Router (`app/api/v1/api.py`)

```python
from app.api.v1.endpoints import tasks

api_router.include_router(
    tasks.router,
    prefix="/tasks",
    tags=["Tasks"],
)
```

### 6. Create Migration

```bash
alembic revision --autogenerate -m "add tasks table"
alembic upgrade head
```

## Adding External Integrations

### Example: HubSpot Sync Service

Create a service layer for integration logic:

```python
# app/services/hubspot_sync.py
from typing import Dict, Any
import httpx
from app.repositories.contact import ContactRepository
from app.repositories.company import CompanyRepository

class HubSpotSyncService:
    def __init__(self, api_key: str, db):
        self.api_key = api_key
        self.db = db
        self.base_url = "https://api.hubapi.com"

    async def sync_contact_to_hubspot(self, contact_id: int):
        """Push contact to HubSpot"""
        repo = ContactRepository(self.db)
        contact = repo.get(contact_id)

        # Check if already synced
        hubspot_id = contact.details.get("hubspot_contact_id")

        # Prepare HubSpot payload
        hs_data = {
            "properties": {
                "firstname": contact.first_name,
                "lastname": contact.last_name,
                "email": contact.primary_email,
                # Custom properties
                "category": contact.category,
                "timeline_to_sell": contact.details.get("timeline_to_sell"),
            }
        }

        async with httpx.AsyncClient() as client:
            if hubspot_id:
                # Update existing
                response = await client.patch(
                    f"{self.base_url}/crm/v3/objects/contacts/{hubspot_id}",
                    headers={"Authorization": f"Bearer {self.api_key}"},
                    json=hs_data
                )
            else:
                # Create new
                response = await client.post(
                    f"{self.base_url}/crm/v3/objects/contacts",
                    headers={"Authorization": f"Bearer {self.api_key}"},
                    json=hs_data
                )

                # Store HubSpot ID
                hs_contact = response.json()
                contact.details["hubspot_contact_id"] = hs_contact["id"]
                contact.details["hubspot_last_sync"] = datetime.utcnow().isoformat()
                self.db.commit()

        return response.json()

    async def pull_contact_from_hubspot(self, hubspot_id: str):
        """Pull contact from HubSpot to our CRM"""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/crm/v3/objects/contacts/{hubspot_id}",
                headers={"Authorization": f"Bearer {self.api_key}"}
            )
            hs_contact = response.json()

        # Map to our schema
        contact_data = {
            "first_name": hs_contact["properties"]["firstname"],
            "last_name": hs_contact["properties"]["lastname"],
            "primary_email": hs_contact["properties"]["email"],
            "details": {
                "hubspot_contact_id": hubspot_id,
                "hubspot_last_sync": datetime.utcnow().isoformat(),
                # Store any custom HubSpot properties
                **{k: v for k, v in hs_contact["properties"].items()
                   if k not in ["firstname", "lastname", "email"]}
            }
        }

        repo = ContactRepository(self.db)
        return repo.create(contact_data)
```

### Adding Sync Endpoints

```python
# app/api/v1/endpoints/integrations.py
from fastapi import APIRouter, Depends
from app.services.hubspot_sync import HubSpotSyncService
from app.core.deps import get_db

router = APIRouter()

@router.post("/hubspot/sync/contact/{contact_id}")
async def sync_contact_to_hubspot(contact_id: int, db = Depends(get_db)):
    """Push contact to HubSpot"""
    service = HubSpotSyncService(api_key="your-key", db=db)
    result = await service.sync_contact_to_hubspot(contact_id)
    return {"status": "synced", "hubspot_contact": result}

@router.post("/hubspot/pull/contact/{hubspot_id}")
async def pull_contact_from_hubspot(hubspot_id: str, db = Depends(get_db)):
    """Pull contact from HubSpot"""
    service = HubSpotSyncService(api_key="your-key", db=db)
    contact = await service.pull_contact_from_hubspot(hubspot_id)
    return contact
```

## Adding Authentication & User Management

The system currently uses `owner_id` as a simple integer. To add proper user management:

### 1. Create User Model

```python
from sqlalchemy import Column, Integer, String, Boolean
from app.db.base import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    email = Column(String, unique=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String)
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)
```

### 2. Add Foreign Keys

```python
# In deals model
owner_id = Column(Integer, ForeignKey("users.id"), nullable=True)
owner = relationship("User")
```

### 3. Add Authentication

```python
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    # Get user from database
    user = user_repo.get(int(user_id))
    if user is None:
        raise credentials_exception
    return user

# Use in endpoints
@router.post("/deals")
def create_deal(
    deal_in: DealCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Auto-assign owner
    deal_data = deal_in.model_dump()
    deal_data["owner_id"] = current_user.id

    repo = DealRepository(db)
    return repo.create(deal_data)
```

## Adding Webhooks

To notify external systems of changes:

```python
# app/services/webhooks.py
import httpx
from typing import List

class WebhookService:
    def __init__(self, webhook_urls: List[str]):
        self.webhook_urls = webhook_urls

    async def notify(self, event_type: str, data: dict):
        """Send webhook notifications"""
        payload = {
            "event": event_type,
            "timestamp": datetime.utcnow().isoformat(),
            "data": data
        }

        async with httpx.AsyncClient() as client:
            tasks = [
                client.post(url, json=payload)
                for url in self.webhook_urls
            ]
            await asyncio.gather(*tasks)

# Use in endpoints
@router.post("/deals", response_model=DealResponse)
async def create_deal(deal_in: DealCreate, db: Session = Depends(get_db)):
    repo = DealRepository(db)
    deal = repo.create(deal_in.model_dump())

    # Send webhook notification
    webhook_service = WebhookService(["https://your-webhook.com/endpoint"])
    await webhook_service.notify("deal.created", {
        "deal_id": deal.id,
        "name": deal.name,
        "amount": deal.amount
    })

    return deal
```

## Performance Optimization

### Add Caching

```python
from functools import lru_cache
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from fastapi_cache.decorator import cache

# In main.py
from redis import asyncio as aioredis

@app.on_event("startup")
async def startup():
    redis = aioredis.from_url("redis://localhost")
    FastAPICache.init(RedisBackend(redis), prefix="crm-cache")

# In endpoints
@router.get("/pipelines/{pipeline_id}")
@cache(expire=300)  # Cache for 5 minutes
async def get_pipeline(pipeline_id: int, db: Session = Depends(get_db)):
    repo = PipelineRepository(db)
    return repo.get(pipeline_id)
```

### Add Database Indexes

```python
# In models
class Contact(Base):
    __tablename__ = "contacts"

    # Add composite index for common queries
    __table_args__ = (
        Index('idx_contact_category_active', 'category', 'is_active'),
        Index('idx_contact_details_industry',
              func.jsonb_extract_path_text('details', 'industry')),
    )
```

## Summary

The IndieStack CRM is designed for extensibility through:

1. **JSONB Details Field**: Add custom fields without migrations
2. **Repository Pattern**: Swap implementations easily
3. **Clear Layers**: Separate concerns for maintainability
4. **Integration Metadata**: Store external IDs in details field
5. **Service Layer**: Add business logic without touching core

This architecture allows you to build integrations, add features, and scale the system without rewriting core functionality.
