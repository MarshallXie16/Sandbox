# Capitalink Analytics

**Module 8** – Read-only analytics and reporting service that aggregates data across all Capitalink modules.

## Overview

Capitalink Analytics is the command center for the entire Capitalink platform, providing:

- **Aggregated Metrics** across all modules (CRM, Exit Ready, Facilitator, etc.)
- **Funnel Statistics** for buyer progression and deal flow
- **Pipeline Analytics** for tracking cases and engagements
- **Revenue Analytics** for financial reporting and forecasting
- **Buyer Activity Analytics** for engagement tracking

### Key Features

- **REST API** for programmatic access to analytics data
- **Dashboard UI** for visual analytics exploration
- **CLI Tools** for terminal-based reporting and operations
- **Read-Only Architecture** – never mutates upstream module data
- **Snapshot System** for historical trend analysis

## Architecture

This module operates as a **read-only aggregator**:

- Queries upstream databases directly (CRM, Exit Ready, Facilitator)
- Maintains its own analytics-specific tables for caching and aggregations
- Provides multiple interfaces: API, Dashboard, CLI

```
┌─────────────────────────────────────────────────┐
│         Capitalink Analytics (Module 8)         │
├─────────────────────────────────────────────────┤
│  ┌─────────┐  ┌───────────┐  ┌──────────────┐  │
│  │   API   │  │ Dashboard │  │     CLI      │  │
│  └────┬────┘  └─────┬─────┘  └──────┬───────┘  │
│       │             │                │          │
│  ┌────┴─────────────┴────────────────┴────┐    │
│  │      Analytics Services Layer         │    │
│  └───────────────┬───────────────────────┘    │
│                  │                             │
│  ┌───────────────┴───────────────────────┐    │
│  │   Read-Only Repositories Layer        │    │
│  └───────────────┬───────────────────────┘    │
└──────────────────┼─────────────────────────────┘
                   │
    ┌──────────────┼──────────────┐
    │              │              │
┌───▼────┐  ┌──────▼──────┐  ┌───▼──────┐
│  CRM   │  │ Exit Ready  │  │Facilitator│
│   DB   │  │     DB      │  │    DB     │
└────────┘  └─────────────┘  └───────────┘
```

## Quick Start

### 1. Installation

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configuration

Copy `.env.example` to `.env` and configure:

```bash
cp .env.example .env
```

Edit `.env` with your database connections:

```env
# Analytics database (this module's own schema)
ANALYTICS_DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/capitalink_analytics

# Upstream databases (read-only)
CRM_DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/indie_crm_core
EXIT_READY_DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/exit_ready_automation
FACILITATOR_DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/facilitator_automation

# API Security
ANALYTICS_API_KEYS=your-secret-key-here
```

### 3. Database Setup

Run migrations to create analytics tables:

```bash
alembic upgrade head
```

### 4. Run the Service

**Development Server:**

```bash
make dev
# or
uvicorn main:app --reload --host 0.0.0.0 --port 8008
```

**Production Server:**

```bash
uvicorn main:app --host 0.0.0.0 --port 8008 --workers 4
```

### 5. Access the Dashboard

Open your browser to:

```
http://localhost:8008/dashboard
```

## API Usage

All API endpoints require authentication via `X-API-Key` header.

### Health Check

```bash
curl http://localhost:8008/api/v1/health
```

### Exit Ready Analytics

```bash
# Pipeline summary
curl -H "X-API-Key: your-key" \
  http://localhost:8008/api/v1/analytics/exit-ready/pipeline

# Stage durations
curl -H "X-API-Key: your-key" \
  http://localhost:8008/api/v1/analytics/exit-ready/durations

# Volume over time
curl -H "X-API-Key: your-key" \
  "http://localhost:8008/api/v1/analytics/exit-ready/volume?period=month"
```

### Facilitator Analytics

```bash
# Engagement summary
curl -H "X-API-Key: your-key" \
  http://localhost:8008/api/v1/analytics/facilitator/engagements

# Revenue summary
curl -H "X-API-Key: your-key" \
  "http://localhost:8008/api/v1/analytics/facilitator/revenue?from=2025-01-01&to=2025-01-31"

# Buyer funnel
curl -H "X-API-Key: your-key" \
  http://localhost:8008/api/v1/analytics/facilitator/funnel
```

### CRM Analytics

```bash
# CRM overview
curl -H "X-API-Key: your-key" \
  http://localhost:8008/api/v1/analytics/crm/overview
```

See [docs/api_usage.md](docs/api_usage.md) for full API documentation.

## CLI Usage

The analytics CLI provides terminal-based reporting:

```bash
# Make CLI executable
chmod +x cli.py

# Run snapshot (collect daily metrics)
python cli.py snapshot --date 2025-01-15

# Exit Ready summary
python cli.py exit-ready

# Facilitator revenue report
python cli.py facilitator revenue --from 2025-01-01 --to 2025-01-31

# Facilitator funnel
python cli.py facilitator funnel

# CRM overview
python cli.py crm
```

See [docs/cli_usage.md](docs/cli_usage.md) for full CLI documentation.

## Dashboard

The web dashboard provides visual analytics at:

- `/dashboard` – Main overview
- `/dashboard/exit-ready` – Exit Ready detailed analytics
- `/dashboard/facilitator` – Facilitator detailed analytics

Features:
- Real-time metrics
- KPI cards
- Status distributions
- Funnel visualizations
- Revenue breakdowns

## Development

### Running Tests

```bash
make test
# or
pytest -v --cov=app
```

### Code Formatting

```bash
make format
# or
black app tests
isort app tests
```

### Linting

```bash
make lint
# or
flake8 app tests
```

### Creating Migrations

```bash
make migrate message="add new analytics table"
# or
alembic revision --autogenerate -m "add new analytics table"
```

## Project Structure

```
capitalink-analytics/
├── app/
│   ├── api/              # FastAPI routers
│   ├── cli/              # CLI command implementations
│   ├── core/             # Config, database, logging, auth
│   ├── models/           # SQLAlchemy models
│   ├── repositories/     # Data access layer
│   ├── schemas/          # Pydantic schemas
│   ├── services/         # Business logic
│   └── ui/               # Dashboard templates
├── alembic/              # Database migrations
├── config/               # Configuration files
├── docs/                 # Documentation
├── tests/                # Tests
├── cli.py                # CLI entry point
├── main.py               # FastAPI app entry point
├── requirements.txt      # Python dependencies
├── Makefile              # Common commands
└── README.md             # This file
```

## Analytics Domains

### 1. Exit Ready Analytics

Tracks the Exit Ready assessment pipeline:

- Case counts by status
- Stage duration metrics
- Volume trends over time
- Conversion to Facilitator engagements

### 2. Facilitator Analytics

Monitors M&A advisory engagements:

- Engagement status distribution
- Revenue metrics (offer fees, success fees)
- Buyer introduction funnel
- Offer-to-close conversion rates

### 3. CRM Analytics

Basic CRM statistics:

- Contact counts (sellers, buyers)
- Company counts
- Listing pipeline
- Deal status distribution

### 4. Buyer Activity Analytics

Engagement tracking:

- Top engaged buyers
- Portal usage metrics
- Match quality analysis
- Activity trends

## Important Notes

### Read-Only Architecture

**CRITICAL:** This module must NEVER mutate data in upstream databases:

- All repository methods are read-only
- No `INSERT`, `UPDATE`, or `DELETE` operations on upstream tables
- Only query operations (`SELECT`) are permitted
- Analytics-specific tables (snapshots, summaries) are maintained locally

### Database Connections

This module connects to multiple databases:

- **Analytics DB:** Read-write for this module's tables
- **Upstream DBs:** Read-only for querying source data

Ensure proper connection pooling and read-only user permissions on upstream databases.

## Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `ANALYTICS_DATABASE_URL` | Analytics database connection | Yes |
| `CRM_DATABASE_URL` | CRM database (read-only) | Optional |
| `EXIT_READY_DATABASE_URL` | Exit Ready database (read-only) | Optional |
| `FACILITATOR_DATABASE_URL` | Facilitator database (read-only) | Optional |
| `ANALYTICS_API_KEYS` | Comma-separated API keys | Yes |
| `ANALYTICS_ENV` | Environment (dev/prod) | No |
| `LOG_LEVEL` | Logging level | No |

## Documentation

- [Architecture](docs/architecture.md) – System design and data flows
- [API Usage](docs/api_usage.md) – API reference and examples
- [CLI Usage](docs/cli_usage.md) – CLI command reference
- [Dashboard](docs/dashboard.md) – Dashboard user guide

## Support

For issues or questions:

1. Check the documentation in `docs/`
2. Review error logs
3. Contact the development team

## License

Proprietary - Capitalink Platform
