# Facilitator Automation - Phase 2 Facilitator Service

**Version:** 1.0.0
**Status:** Production-ready

## Overview

Facilitator Automation is a **Phase 2 facilitator service** that implements a structured, compliant, non-broker, non-fiduciary coordination layer for tracking buyer introductions and calculating facilitator fees.

### Legal Context

**IMPORTANT**: This is a **facilitator/finder** workflow system, **NOT a brokerage system**.

- **No fiduciary duty** - Capital Link acts as a facilitator, not an agent
- **No agency role** - No representation of seller in a licensed broker capacity
- **Introduced Buyer semantics** - Success fees ONLY apply to buyers explicitly introduced through this system
- **Transparent fee structure** - Fixed $5k offer fee + 5% success fee with credit

## Core Functionality

### 1. Facilitator Engagements
- Track Phase 2 engagements between Capital Link (facilitator) and sellers/listings
- Manage engagement lifecycle (draft → active → offers → closing)
- Store commercial terms (offer fee, success fee rate, currency)

### 2. Introduced Buyers
- **Source of truth** for which buyers have been introduced
- Track buyer lifecycle (invited → NDA → teaser → info access → offer)
- Critical for success fee eligibility determination

### 3. Offers & Closings
- Record offers from introduced buyers
- Calculate facilitator fees:
  - **Offer fee**: $5,000 (default) when buyer makes an offer
  - **Success fee**: 5% (default) of final price on closing
  - **Credit**: Offer fees paid are credited against success fee

## Tech Stack

- **Python 3.10+**
- **FastAPI** - Modern async API framework
- **SQLAlchemy 2.x + asyncpg** - Async ORM with PostgreSQL
- **Alembic** - Database migrations
- **Pydantic v2** - Data validation and serialization
- **Typer** - CLI interface with rich formatting
- **pytest** - Testing framework

## Quick Start

### 1. Installation

```bash
cd facilitator-automation

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy and configure environment
cp .env.example .env
# Edit .env with your database URL and configuration
```

### 2. Database Setup

```bash
# Run migrations
alembic upgrade head
```

### 3. Run API Server

```bash
# Development mode
uvicorn main:app --reload --port 8080

# Production mode
uvicorn main:app --host 0.0.0.0 --port 8080 --workers 4
```

API will be available at:
- API: http://localhost:8080
- Interactive docs: http://localhost:8080/docs
- Health check: http://localhost:8080/api/v1/health

### 4. Use CLI

```bash
# List engagements
python cli.py engagements list

# Create engagement
python cli.py engagements create --seller-contact-id 123 --company-id 456

# Activate engagement
python cli.py engagements activate 1

# Introduce a buyer
python cli.py buyers add --engagement-id 1 --buyer-contact-id 321 --channel email

# Record an offer
python cli.py offers add --engagement-id 1 --buyer-intro-id 1 --headline-price 2500000

# Record closing (calculates fees)
python cli.py closings record --engagement-id 1 --buyer-intro-id 1 --final-price 2500000

# View closing details
python cli.py closings show 1
```

## Project Structure

```
facilitator-automation/
├── app/
│   ├── core/              # Core utilities (config, database, logging, security)
│   ├── models/            # SQLAlchemy models (engagements, buyers, offers, closings)
│   ├── schemas/           # Pydantic schemas for API
│   ├── repositories/      # Data access layer
│   ├── services/          # Business logic (fee calculator, workflow, etc.)
│   ├── integrations/      # External service clients (Matching Engine, Email Engine, CRM)
│   ├── api/               # FastAPI routers
│   └── cli/               # CLI commands
├── alembic/               # Database migrations
├── tests/                 # Test suite
├── docs/                  # Documentation
├── main.py                # FastAPI entrypoint
├── cli.py                 # CLI entrypoint
├── requirements.txt       # Python dependencies
└── .env.example           # Environment template
```

## Configuration

All configuration is done via environment variables (see `.env.example`):

### Required
- `DATABASE_URL` - PostgreSQL connection string
- `FACILITATOR_API_KEYS` - Comma-separated API keys for authentication

### Optional
- `DEFAULT_OFFER_FEE_FIXED` - Default offer fee (default: 5000)
- `DEFAULT_SUCCESS_FEE_RATE` - Default success fee rate (default: 0.05)
- `MATCH_ENGINE_BASE_URL` - Matching Engine API URL
- `EMAIL_ENGINE_BASE_URL` - Email Engine API URL
- `CRM_API_BASE_URL` - CRM API URL

### Stub Modes
For development/testing without external services:
- `MATCH_ENGINE_STUB_MODE=true`
- `EMAIL_ENGINE_STUB_MODE=true`

## API Examples

### Create Engagement
```bash
curl -X POST http://localhost:8080/api/v1/facilitator/engagements \
  -H "X-API-Key: your-api-key" \
  -H "Content-Type: application/json" \
  -d '{
    "seller_contact_id": 123,
    "company_id": 456,
    "listing_id": 789,
    "offer_fee_fixed": 5000,
    "success_fee_rate": 0.05,
    "currency": "CAD"
  }'
```

### Introduce Buyer
```bash
curl -X POST http://localhost:8080/api/v1/facilitator/engagements/1/buyers \
  -H "X-API-Key: your-api-key" \
  -H "Content-Type: application/json" \
  -d '{
    "buyer_contact_id": 321,
    "introduction_channel": "email"
  }'
```

### Record Closing
```bash
curl -X POST http://localhost:8080/api/v1/facilitator/engagements/1/closings \
  -H "X-API-Key: your-api-key" \
  -H "Content-Type: application/json" \
  -d '{
    "buyer_intro_id": 1,
    "closing_date": "2025-04-01T00:00:00",
    "final_price": 2500000,
    "currency": "CAD"
  }'
```

## Fee Calculation Example

Given:
- Final price: $2,000,000
- Success fee rate: 5%
- Offer fee paid: $5,000

Calculation:
```
Gross success fee = $2,000,000 × 0.05 = $100,000
Offer fee credit  = min($5,000, $100,000) = $5,000
Net success fee   = $100,000 - $5,000 = $95,000

Total facilitator revenue = $5,000 + $95,000 = $100,000
```

## Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific test file
pytest tests/test_fee_calculator.py
```

## Documentation

- [Architecture](docs/architecture.md) - System architecture and design decisions
- [API Usage](docs/api_usage.md) - Detailed API documentation with examples
- [CLI Usage](docs/cli_usage.md) - CLI command reference and workflows

## Integration

### With Other Modules
- **indie-crm-core**: Source of contact and company data
- **indie-matching-engine**: Suggests candidate buyers for listings
- **capitalinkhub-email-engine**: Sends introduction and notification emails
- **exit-ready-automation (Module 7)**: Feeds listings ready for Phase 2

### External API Configuration
Configure integration endpoints in `.env`:
```
CRM_API_BASE_URL=http://localhost:8001/api/v1
MATCH_ENGINE_BASE_URL=http://localhost:8002/api/v1
EMAIL_ENGINE_BASE_URL=http://localhost:8003/api/v1
```

## License

Proprietary - Capital Link

---

For detailed information about the architecture, workflow, and API endpoints, see the `docs/` directory.
