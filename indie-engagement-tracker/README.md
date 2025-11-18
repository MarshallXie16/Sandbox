# Indie Engagement Tracker

A sophisticated client engagement tracking service designed to work with **IndieStack CRM Core** and **Capital Ink Hub Email Engine**, with extensibility for additional sources like HubSpot and Sendy.

## Overview

The Engagement Tracker maintains engagement scores for contacts, companies, and deals based on their activities and interactions across multiple systems. It provides:

- **Pluggable event ingestion** from multiple sources
- **Flexible scoring engine** with customizable profiles
- **Time decay** for aging events
- **REST API** for integration
- **CLI tools** for operations
- **Historical tracking** for trend analysis

## Features

- ✅ Multi-source event ingestion (CRM, Email Engine, extensible)
- ✅ Configurable scoring profiles with event weights
- ✅ Time-based score decay
- ✅ REST API with comprehensive endpoints
- ✅ CLI tools for common operations
- ✅ Score history tracking
- ✅ Support for PostgreSQL and SQLite
- ✅ Type-safe with Pydantic schemas
- ✅ Production-ready logging

## Quick Start

### Installation

1. **Clone and navigate to the project:**
   ```bash
   cd indie-engagement-tracker
   ```

2. **Create and activate virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment:**
   ```bash
   cp .env.example .env
   # Edit .env with your database connections and settings
   ```

5. **Initialize the database:**
   ```bash
   python -m app.cli.main init
   ```

### Configuration

Edit `.env` with your settings:

```env
# Engagement Tracker Database
DATABASE_URL=postgresql://user:password@localhost:5432/engagement_tracker
# Or for development:
# DATABASE_URL=sqlite:///./engagement_tracker.db

# IndieStack CRM Core (database access)
INDIE_CRM_DB_URL=postgresql://user:password@localhost:5432/indie_crm_core

# Capital Ink Hub Email Engine
EMAIL_ENGINE_DB_URL=postgresql://user:password@localhost:5432/capitalinkhub_email

# Scoring Configuration
DEFAULT_SCORING_PROFILE_ID=1
SCORE_DECAY_ENABLED=true
SCORE_DECAY_DAYS=90
SCORE_DECAY_FACTOR=0.5
```

## Usage

### CLI Commands

The tracker provides a command-line interface for common operations:

```bash
# Initialize database
python -m app.cli.main init

# Test source connections
python -m app.cli.main test-sources

# Ingest events from all sources
python -m app.cli.main ingest-all

# Ingest with filters
python -m app.cli.main ingest-all --since "2024-01-01T00:00:00" --limit 1000

# Dry run (don't save to database)
python -m app.cli.main ingest-all --dry-run

# Recalculate all scores
python -m app.cli.main recalc-all

# Recalculate with filters
python -m app.cli.main recalc-all --entity-type contact --min-events 5

# Show top engaged contacts
python -m app.cli.main top-contacts --limit 50

# Show statistics
python -m app.cli.main stats
```

### API Server

Start the API server:

```bash
# Using the main module
python -m app.main

# Or using uvicorn directly
uvicorn app.main:app --host 0.0.0.0 --port 8001 --reload
```

The API will be available at:
- API Root: http://localhost:8001/
- API Docs (Swagger): http://localhost:8001/docs
- API Docs (ReDoc): http://localhost:8001/redoc
- Health Check: http://localhost:8001/api/v1/health

### API Examples

See [docs/api_examples.md](docs/api_examples.md) for detailed API usage examples.

#### Quick Examples

**Get top engaged contacts:**
```bash
curl "http://localhost:8001/api/v1/scores/top-contacts?limit=10"
```

**Trigger event ingestion:**
```bash
curl -X POST "http://localhost:8001/api/v1/ingest/run" \
  -H "Content-Type: application/json" \
  -d '{"dry_run": false}'
```

**Recalculate scores:**
```bash
curl -X POST "http://localhost:8001/api/v1/scores/recalculate" \
  -H "Content-Type: application/json" \
  -d '{}'
```

## Architecture

### System Design

```
┌─────────────────────────────────────────────────────────┐
│                  Engagement Tracker                     │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐ │
│  │ Event Sources│  │Scoring Engine│  │  REST API    │ │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘ │
│         │                 │                 │          │
│         └─────────────────┴─────────────────┘          │
│                          │                             │
│                   ┌──────▼──────┐                      │
│                   │  Database   │                      │
│                   └─────────────┘                      │
└─────────────────────────────────────────────────────────┘
         ▲              ▲              ▲
         │              │              │
    ┌────┴────┐    ┌────┴────┐   ┌────┴────┐
    │ IndieStack│    │  Email  │   │  Future │
    │    CRM    │    │  Engine │   │ Sources │
    └──────────┘    └─────────┘   └─────────┘
```

### Data Model

- **engagement_entities**: Contacts, companies, and deals being tracked
- **engagement_events**: Individual activity events (emails, calls, meetings, etc.)
- **scoring_profiles**: Configurable scoring rules and weights
- **score_history**: Historical scores for trend analysis

See [docs/architecture.md](docs/architecture.md) for detailed architecture documentation.

## Scoring System

### Default Event Weights

| Event Type         | Weight | Description                    |
|--------------------|--------|--------------------------------|
| email_sent         | 1.0    | Email sent to contact          |
| email_open         | 3.0    | Contact opened email           |
| email_click        | 5.0    | Contact clicked link in email  |
| email_reply        | 10.0   | Contact replied to email       |
| email_bounce       | -2.0   | Email bounced                  |
| call               | 8.0    | Phone call                     |
| meeting            | 15.0   | Meeting held                   |
| message            | 5.0    | LinkedIn/WhatsApp/WeChat       |
| note_added         | 3.0    | Note added to contact          |
| deal_created       | 20.0   | New deal created               |
| deal_stage_change  | 15.0   | Deal moved to new stage        |
| deal_won           | 50.0   | Deal closed-won                |
| deal_lost          | -10.0  | Deal closed-lost               |

### Time Decay

Events older than 90 days (configurable) receive 50% weight by default. This ensures recent engagement is weighted more heavily.

### Custom Scoring Profiles

Create custom scoring profiles via API or database:

```json
{
  "name": "Sales-Focused",
  "description": "Emphasizes deal activities",
  "rules": {
    "event_weights": {
      "meeting": 25.0,
      "deal_stage_change": 30.0,
      "deal_won": 100.0
    },
    "time_decay": {
      "enabled": true,
      "decay_days": 60,
      "decay_factor": 0.3
    }
  }
}
```

See [docs/scoring_profiles.md](docs/scoring_profiles.md) for more examples.

## Event Sources

### Current Sources

1. **IndieStack CRM Core**
   - Activities (calls, meetings, emails, messages)
   - Deal stage changes
   - Connects via direct database access

2. **Capital Ink Hub Email Engine**
   - Email sends
   - Email bounces/failures
   - Connects via direct database access

### Adding New Sources

Create a new class extending `EventSource`:

```python
from app.sources.base import EventSource, StandardEvent

class HubSpotSource(EventSource):
    def fetch_new_events(self, since=None, limit=None):
        # Fetch from HubSpot API
        # Convert to StandardEvent
        # Yield events
        pass

    def test_connection(self):
        # Test HubSpot connection
        pass
```

Register in `app/sources/manager.py`.

## Testing

Run tests:

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific test file
pytest tests/test_scoring_engine.py
```

See [tests/](tests/) directory for test examples.

## Development

### Project Structure

```
indie-engagement-tracker/
├── app/
│   ├── core/           # Configuration, database, logging
│   ├── models/         # SQLAlchemy models
│   ├── repositories/   # Data access layer
│   ├── scoring/        # Scoring engine
│   ├── sources/        # Event sources
│   ├── api/            # FastAPI routes and schemas
│   ├── cli/            # CLI commands
│   └── main.py         # FastAPI app
├── docs/               # Documentation
├── tests/              # Unit tests
├── .env.example        # Environment template
├── requirements.txt    # Python dependencies
└── README.md          # This file
```

### Code Quality

```bash
# Format code
black app tests

# Lint code
flake8 app tests

# Type checking
mypy app
```

## Deployment

### Using Docker (TODO)

```bash
docker build -t engagement-tracker .
docker run -p 8001:8001 --env-file .env engagement-tracker
```

### Production Checklist

- [ ] Use PostgreSQL (not SQLite)
- [ ] Set strong `API_SECRET_KEY`
- [ ] Configure proper CORS origins
- [ ] Set `APP_ENV=production`
- [ ] Use environment-specific logging
- [ ] Set up database backups
- [ ] Configure monitoring and alerts
- [ ] Use reverse proxy (nginx)
- [ ] Enable HTTPS

## Troubleshooting

### Database Connection Issues

**PostgreSQL connection failed:**
- Check DATABASE_URL format: `postgresql://user:pass@host:port/dbname`
- Verify database exists: `psql -l`
- Check firewall/network access

**SQLite permissions:**
- Ensure write permissions in directory
- Check file path is absolute

### Source Connection Issues

**IndieStack CRM not connecting:**
- Verify INDIE_CRM_DB_URL is correct
- Check database user permissions
- Ensure tables exist (contacts, activities, deals)

**Email Engine not connecting:**
- Verify EMAIL_ENGINE_DB_URL is correct
- Ensure send_logs and recipients tables exist

### Scoring Issues

**Scores not updating:**
- Run `tracker recalc-all` to force recalculation
- Check event ingestion: `tracker stats`
- Verify scoring profile is configured

**No events ingested:**
- Test sources: `tracker test-sources`
- Check source database connections
- Verify event tables have data

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Run tests and linting
6. Submit a pull request

## License

MIT License - see LICENSE file for details

## Support

For issues and questions:
- Check [docs/](docs/) directory
- Review API documentation at `/docs` endpoint
- Open an issue on GitHub

---

**Built with:** FastAPI, SQLAlchemy, Typer, and Pydantic
