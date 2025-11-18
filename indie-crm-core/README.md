# IndieStack CRM

A production-ready, HubSpot-inspired CRM system built with FastAPI, SQLAlchemy, and PostgreSQL. Designed for flexibility and extensibility, supporting custom fields, configurable pipelines, and entity associations.

## Features

- **Contacts Management**: Track contacts with customizable categories (sellers, buyers, bankers, lawyers, etc.)
- **Companies Management**: Manage companies with business metrics and custom attributes
- **Deal Pipeline**: Customizable deal pipelines and stages stored in database (not hard-coded)
- **Activity Tracking**: Log all interactions (emails, calls, meetings, social media)
- **Entity Associations**: HubSpot-style associations to link contacts, companies, deals, and activities
- **Extensible Schema**: JSONB `details` field on all entities for custom fields without schema changes
- **RESTful API**: Full CRUD operations with filtering and pagination
- **Type Safety**: Pydantic schemas for request/response validation
- **Database Migrations**: Alembic for version-controlled schema changes
- **Production Ready**: Modular architecture, environment configuration, error handling

## Architecture

```
indie-crm-core/
├── app/
│   ├── api/                    # API layer
│   │   └── v1/
│   │       ├── endpoints/      # Route handlers
│   │       │   ├── contacts.py
│   │       │   ├── companies.py
│   │       │   ├── deals.py
│   │       │   ├── activities.py
│   │       │   ├── pipelines.py
│   │       │   └── associations.py
│   │       └── api.py          # Router aggregation
│   ├── core/                   # Core configuration
│   │   ├── config.py           # Settings management
│   │   └── deps.py             # Dependency injection
│   ├── db/                     # Database setup
│   │   ├── base.py             # Base model
│   │   ├── session.py          # Session factory
│   │   └── seed_data.py        # Pipeline seeding
│   ├── models/                 # SQLAlchemy ORM models
│   │   ├── contact.py
│   │   ├── company.py
│   │   ├── deal.py
│   │   ├── activity.py
│   │   ├── pipeline.py
│   │   └── associations.py
│   ├── repositories/           # Data access layer
│   │   ├── base.py             # Base repository
│   │   ├── contact.py
│   │   ├── company.py
│   │   ├── deal.py
│   │   ├── activity.py
│   │   ├── pipeline.py
│   │   └── association.py
│   ├── schemas/                # Pydantic schemas
│   │   ├── contact.py
│   │   ├── company.py
│   │   ├── deal.py
│   │   ├── activity.py
│   │   ├── pipeline.py
│   │   └── association.py
│   └── main.py                 # FastAPI app entry point
├── alembic/                    # Database migrations
├── docs/                       # Documentation
├── tests/                      # Test suite
├── requirements.txt            # Python dependencies
├── .env.example                # Environment template
└── README.md                   # This file
```

## Data Model

### Core Entities

#### Contacts
- Basic info: name, email, phone, social profiles
- Category: seller, buyer, banker, lawyer, accountant, investor, other
- Custom fields in `details` JSON:
  - Sellers: `timeline_to_sell`, `pain_points`, `expectation`
  - Buyers: `industry`, `budget`, `geographic_preference`, `timeline_to_buy`, etc.

#### Companies
- Basic info: name, location, website, LinkedIn
- Business metrics: revenue, employees, earnings, ARR
- Custom fields in `details` JSON

#### Deals
- Deal info: name, amount, currency, expected close date
- Pipeline tracking: pipeline_id, stage_id, status
- Owner assignment
- Custom fields in `details` JSON

#### Activities
- Type: email, call, meeting, LinkedIn, WhatsApp, WeChat, note
- Direction: incoming/outgoing
- Timeline: happened_at timestamp
- Custom fields in `details` JSON (e.g., call duration, meeting attendees)

#### Pipelines & Stages
**Stored in database** (not hard-coded enums):
- **Seller Pipeline**: Exit Ready → Facilitator → Broker → Marketing → LOI → Due Diligence → Closing → Won/Lost
- **Buyer Pipeline**: Buyer Access → Finder → Broker → Marketing → LOI → Due Diligence → Closing → Won/Lost

Pipelines and stages can be created, updated, or archived via API.

### Associations (Many-to-Many)

- **Contact-Company**: Links contacts to companies (with role, e.g., "CEO")
- **Contact-Deal**: Links contacts to deals (with role, e.g., "Decision Maker")
- **Company-Deal**: Links companies to deals (with role, e.g., "Seller")
- **Activity-Contact**: Links activities to contacts
- **Activity-Company**: Links activities to companies
- **Activity-Deal**: Links activities to deals

## Quick Start

### Prerequisites

- Python 3.10+
- PostgreSQL 12+
- pip

### Installation

1. **Clone and navigate to the project**:
   ```bash
   cd indie-crm-core
   ```

2. **Create virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**:
   ```bash
   cp .env.example .env
   # Edit .env with your database credentials
   ```

5. **Create PostgreSQL database**:
   ```bash
   createdb indie_crm
   # Or use your preferred PostgreSQL client
   ```

6. **Run database migrations**:
   ```bash
   alembic upgrade head
   ```

7. **Seed default pipelines** (optional but recommended):
   ```bash
   python -m app.db.seed_data
   ```

8. **Start the server**:
   ```bash
   uvicorn app.main:app --reload
   ```

9. **Access the API**:
   - API: http://localhost:8000
   - Interactive docs: http://localhost:8000/docs
   - ReDoc: http://localhost:8000/redoc

## Database Migrations

### Create a new migration after model changes:
```bash
alembic revision --autogenerate -m "description of changes"
```

### Apply migrations:
```bash
alembic upgrade head
```

### Rollback one migration:
```bash
alembic downgrade -1
```

### View migration history:
```bash
alembic history
```

## API Usage Examples

See `docs/API_EXAMPLES.md` for comprehensive HTTP request examples.

### Create a Contact
```bash
curl -X POST "http://localhost:8000/api/v1/contacts" \
  -H "Content-Type: application/json" \
  -d '{
    "first_name": "Jane",
    "last_name": "Smith",
    "primary_email": "jane.smith@example.com",
    "category": "buyer",
    "details": {
      "industry": "SaaS",
      "budget": 3000000,
      "geographic_preference": "West Coast"
    }
  }'
```

### Create a Company
```bash
curl -X POST "http://localhost:8000/api/v1/companies" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "TechCorp Inc",
    "industry": "Technology",
    "revenue": 5000000,
    "employees": 25
  }'
```

### Link Contact to Company
```bash
curl -X POST "http://localhost:8000/api/v1/associations/contact-company" \
  -H "Content-Type: application/json" \
  -d '{
    "contact_id": 1,
    "company_id": 1,
    "role": "CEO",
    "is_primary": true
  }'
```

### Create a Deal
```bash
curl -X POST "http://localhost:8000/api/v1/deals" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "TechCorp Acquisition",
    "pipeline_type": "buyer",
    "pipeline_id": 2,
    "stage_id": 5,
    "amount": 3000000,
    "status": "open"
  }'
```

### List Deals by Pipeline
```bash
curl "http://localhost:8000/api/v1/deals?pipeline_id=2&status=open"
```

## Extensibility via Details Field

All main entities (Contact, Company, Deal, Activity) include a `details` JSONB field for storing custom attributes:

### Adding Custom Fields (No Schema Changes Required)

**Seller Contact Example**:
```json
{
  "first_name": "John",
  "last_name": "Doe",
  "category": "seller",
  "details": {
    "timeline_to_sell": "6-12 months",
    "pain_points": "Looking to retire",
    "expectation": "$5M valuation",
    "custom_tag": "high_priority"
  }
}
```

**Company with Integration Metadata**:
```json
{
  "name": "Acme Corp",
  "details": {
    "hubspot_company_id": "12345678",
    "zoho_company_id": "ABC-123",
    "custom_score": 85
  }
}
```

The `details` field supports any valid JSON structure, making the system highly extensible without requiring database migrations.

## Future Extensions

The codebase is designed to support future integrations:

1. **HubSpot Integration**: Use `details` field to store external IDs
2. **Zoho Integration**: Similar pattern with external system IDs
3. **User Management**: Add User model and FK relationships to owner_id fields
4. **Email Integration**: Link email activities via Activity model
5. **Webhooks**: Add webhook endpoints for external system notifications
6. **Analytics**: Query JSONB fields for custom reporting

All integrations can be added **without modifying core domain logic** thanks to:
- Repository pattern (swap implementations)
- JSONB extensibility (store integration metadata)
- Clear layer separation (API → Service → Repository → Model)

## Development Guidelines

### Adding a New Entity

1. Create model in `app/models/`
2. Create repository in `app/repositories/`
3. Create schemas in `app/schemas/`
4. Create endpoints in `app/api/v1/endpoints/`
5. Register router in `app/api/v1/api.py`
6. Create migration: `alembic revision --autogenerate -m "add entity"`
7. Apply migration: `alembic upgrade head`

### Adding Custom Fields

Use the `details` JSONB field - no migration needed!

```python
# Create with custom fields
contact = {
    "first_name": "John",
    "last_name": "Doe",
    "details": {
        "custom_field_1": "value1",
        "custom_field_2": 123,
        "nested": {"key": "value"}
    }
}
```

### Code Quality

- Follow PEP 8 style guidelines
- Use type hints throughout
- Write docstrings for all classes and functions
- Keep repository methods focused and single-purpose
- Validate input with Pydantic schemas
- Handle errors with appropriate HTTP status codes

## Testing

```bash
# Run tests (coming soon)
pytest

# Run with coverage
pytest --cov=app tests/
```

## Production Deployment

1. Set `DEBUG=False` in `.env`
2. Use strong `SECRET_KEY`
3. Configure proper CORS origins
4. Use production-grade PostgreSQL (AWS RDS, etc.)
5. Deploy with gunicorn:
   ```bash
   gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker
   ```
6. Use reverse proxy (Nginx) for SSL/TLS
7. Set up database backups
8. Monitor logs and performance

## License

MIT

## Support

For issues or questions, please open an issue on the project repository.
