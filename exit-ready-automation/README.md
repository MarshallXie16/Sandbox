# Exit Ready Automation

**Module 7: Exit Ready Automation Service**

A FastAPI-based service that implements the Phase 1 Exit Ready pipeline for Capital Link's IndieStack platform. This module provides semi-automated workflows for business exit preparation, including intake, document collection, financial normalization, valuation, and report generation.

## Overview

Exit Ready Automation manages the complete lifecycle of Exit Ready cases through a well-defined state machine:

1. **Create Case** → Send intake form
2. **Collect Documents** → Generate checklist, track document submissions
3. **Normalize Financials** → Prepare data for valuation
4. **Run Valuation** → Call external valuation engine (with stub mode)
5. **Generate Drafts** → Create teaser, summary, and CIM content
6. **Export Report** → Generate PDF deliverables
7. **Deliver** → Send to seller via email
8. **Close Case** → Track next steps

## Features

✅ **State Machine Workflow** - Enforced transitions between case statuses
✅ **Document Checklist** - Standard and custom document tracking
✅ **External Integrations** - Valuation and email engines (with stub modes)
✅ **Audit Logging** - Complete event history for all actions
✅ **REST API** - Full FastAPI implementation with Swagger docs
✅ **CLI** - Typer-based command-line interface for operators
✅ **Async Architecture** - SQLAlchemy 2.x with asyncpg
✅ **Type Safety** - Pydantic v2 schemas throughout

## Tech Stack

- **Framework**: FastAPI 0.109+
- **Database**: PostgreSQL with SQLAlchemy 2.x (async)
- **Migrations**: Alembic
- **CLI**: Typer + Rich
- **HTTP Client**: httpx
- **Validation**: Pydantic v2
- **Testing**: pytest + pytest-asyncio

## Quick Start

### 1. Installation

```bash
# Clone or navigate to the module
cd exit-ready-automation

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configuration

```bash
# Copy example environment file
cp .env.example .env

# Edit .env with your settings
nano .env
```

Key settings to configure:
- `DATABASE_URL` - PostgreSQL connection string
- `VALUATION_ENGINE_STUB_MODE=true` - Enable stub mode for development
- `EMAIL_ENGINE_STUB_MODE=true` - Enable stub mode for development

### 3. Database Setup

```bash
# Run migrations
alembic upgrade head
```

### 4. Run API Server

```bash
# Development mode with auto-reload
python main.py

# Or with uvicorn
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

API will be available at:
- **API Base**: http://localhost:8000/api/v1
- **Swagger Docs**: http://localhost:8000/api/v1/docs
- **ReDoc**: http://localhost:8000/api/v1/redoc

### 5. Use CLI

```bash
# Create a new case
python cli.py create-case

# List all cases
python cli.py list-cases

# Get case details
python cli.py get-case 1

# Send intake link
python cli.py send-intake 1

# Generate document checklist
python cli.py generate-checklist 1

# Run valuation
python cli.py run-valuation 1

# Generate drafts
python cli.py generate-drafts 1

# Export report
python cli.py export-report 1

# Deliver report
python cli.py deliver-report 1

# Close case
python cli.py close-case 1 --next-step optimize_business

# Show statistics
python cli.py stats

# Show version
python cli.py version
```

## Project Structure

```
exit-ready-automation/
├── app/
│   ├── core/              # Configuration, DB, logging, workflow
│   ├── models/            # SQLAlchemy models
│   ├── schemas/           # Pydantic request/response models
│   ├── repositories/      # Data access layer
│   ├── services/          # Business logic
│   ├── integrations/      # External API clients
│   └── api/               # FastAPI routers
├── alembic/               # Database migrations
├── config/                # Templates and config files
├── docs/                  # Documentation
├── tests/                 # Test suite
├── main.py                # FastAPI entrypoint
├── cli.py                 # CLI entrypoint
├── requirements.txt       # Python dependencies
├── alembic.ini            # Alembic configuration
├── .env.example           # Environment variables template
└── README.md              # This file
```

## Case Lifecycle

### Status Flow

```
created
  ↓
intake_pending  (intake link sent)
  ↓
intake_done  (intake data received)
  ↓
docs_collecting  (document checklist generated)
  ↓
financials_ready  (all required docs received/waived)
  ↓
valuation_done  (valuation completed)
  ↓
drafts_generated  (teaser, summary, CIM created)
  ↓
under_review  (human review in progress)
  ↓
report_ready  (PDF exported)
  ↓
delivered  (sent to seller)
  ↓
closed  (case completed)
```

### Workflow Commands

Each status transition has corresponding CLI and API commands:

| Status | CLI Command | API Endpoint |
|--------|-------------|--------------|
| created → intake_pending | `send-intake` | `POST /cases/{id}/intake/send` |
| intake_done → docs_collecting | `generate-checklist` | `POST /cases/{id}/checklist` |
| financials_ready → valuation_done | `run-valuation` | `POST /cases/{id}/valuation` |
| valuation_done → drafts_generated | `generate-drafts` | `POST /cases/{id}/drafts` |
| drafts_generated → report_ready | `export-report` | `POST /cases/{id}/export` |
| report_ready → delivered | `deliver-report` | `POST /cases/{id}/deliver` |
| delivered → closed | `close-case` | `POST /cases/{id}/close` |

## API Examples

### Create a Case

```bash
curl -X POST "http://localhost:8000/api/v1/exit-ready/cases" \
  -H "Content-Type: application/json" \
  -d '{
    "owner_name": "John Doe",
    "owner_email": "john@example.com",
    "company_name": "Acme Corp",
    "industry": "SaaS",
    "region": "US-West"
  }'
```

### Run Full Pipeline

```bash
# 1. Create case
CASE_ID=$(curl -X POST ... | jq -r '.id')

# 2. Send intake
curl -X POST "http://localhost:8000/api/v1/exit-ready/cases/$CASE_ID/intake/send"

# 3. Import intake data (simulated)
curl -X POST "http://localhost:8000/api/v1/exit-ready/cases/$CASE_ID/intake/import" \
  -H "Content-Type: application/json" \
  -d '{"annual_revenue": 500000, "profit_margin": 0.25}'

# 4. Generate checklist
curl -X POST "http://localhost:8000/api/v1/exit-ready/cases/$CASE_ID/checklist"

# 5. Mark documents received (repeat for each doc)
curl -X POST "http://localhost:8000/api/v1/exit-ready/documents/1/received?file_url=https://..."

# 6. Run valuation
curl -X POST "http://localhost:8000/api/v1/exit-ready/cases/$CASE_ID/valuation"

# 7. Generate drafts
curl -X POST "http://localhost:8000/api/v1/exit-ready/cases/$CASE_ID/drafts"

# 8. Export report
curl -X POST "http://localhost:8000/api/v1/exit-ready/cases/$CASE_ID/export"

# 9. Deliver report
curl -X POST "http://localhost:8000/api/v1/exit-ready/cases/$CASE_ID/deliver"

# 10. Close case
curl -X POST "http://localhost:8000/api/v1/exit-ready/cases/$CASE_ID/close?next_step=none"
```

## Development

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific test file
pytest tests/test_services.py
```

### Code Quality

```bash
# Format code
black app/

# Lint
ruff check app/

# Type checking
mypy app/
```

### Database Migrations

```bash
# Create a new migration
alembic revision --autogenerate -m "Description"

# Apply migrations
alembic upgrade head

# Rollback one migration
alembic downgrade -1

# Show current version
alembic current
```

## Integration Modes

### Stub Mode (Development)

In `.env`:
```
VALUATION_ENGINE_STUB_MODE=true
EMAIL_ENGINE_STUB_MODE=true
```

- Valuation engine returns fake but realistic valuations
- Email engine logs emails instead of sending
- Perfect for development and testing

### Production Mode

In `.env`:
```
VALUATION_ENGINE_STUB_MODE=false
VALUATION_ENGINE_BASE_URL=https://api.capitallink.com/valuation/v1
VALUATION_ENGINE_API_KEY=your_key_here

EMAIL_ENGINE_STUB_MODE=false
EMAIL_ENGINE_BASE_URL=https://api.capitallink.com/email/v1
EMAIL_ENGINE_API_KEY=your_key_here
```

## Deployment

### Using Docker (Recommended)

```bash
# Build image
docker build -t exit-ready-automation:latest .

# Run container
docker run -d \
  -p 8000:8000 \
  --env-file .env \
  exit-ready-automation:latest
```

### Using systemd

```bash
# Create service file
sudo nano /etc/systemd/system/exit-ready.service

# Enable and start
sudo systemctl enable exit-ready
sudo systemctl start exit-ready
```

## Environment Variables

See `.env.example` for all available configuration options.

Key variables:
- `DATABASE_URL` - PostgreSQL connection string
- `CRM_DATABASE_URL` - CRM database (if separate)
- `VALUATION_ENGINE_*` - Valuation engine settings
- `EMAIL_ENGINE_*` - Email engine settings
- `STORAGE_TYPE` - File storage (local/s3)
- `SECRET_KEY` - Application secret

## Troubleshooting

### Database Connection Issues

```bash
# Test connection
python -c "from app.core.db import engine; import asyncio; asyncio.run(engine.connect())"
```

### Migration Issues

```bash
# Reset migrations (WARNING: drops all data)
alembic downgrade base
alembic upgrade head
```

### API Not Starting

```bash
# Check logs
python main.py

# Verify dependencies
pip list | grep fastapi
```

## Support

For issues and questions:
- Check `/docs/architecture.md` for design details
- Review API docs at `/api/v1/docs`
- See `/docs/cli_usage.md` for CLI reference

## License

Proprietary - Capital Link / IndieStack Platform

## Version

**1.0.0** - Initial release with Phase 1 Exit Ready automation
