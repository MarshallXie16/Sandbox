# Project Structure

```
indie-hubspot-sync/
│
├── app/                          # Main application package
│   ├── __init__.py
│   │
│   ├── core/                     # Core functionality
│   │   ├── __init__.py
│   │   ├── config.py            # Settings and environment variables
│   │   ├── database.py          # Database connection and session management
│   │   └── logging.py           # Structured logging configuration
│   │
│   ├── models/                   # Database models
│   │   ├── __init__.py
│   │   └── tracking.py          # Sync tracking models (SyncObject, SyncRun, SyncError)
│   │
│   ├── hubspot/                  # HubSpot integration
│   │   ├── __init__.py
│   │   └── client.py            # HubSpot API client (CRM v3)
│   │
│   ├── indie/                    # IndieStack integration
│   │   ├── __init__.py
│   │   ├── models.py            # IndieStack CRM models (Contact, Company, Deal)
│   │   └── repository.py        # Data access layer (database & API)
│   │
│   ├── mappings/                 # Field mapping engine
│   │   ├── __init__.py
│   │   └── engine.py            # YAML-based field mapper with transformations
│   │
│   ├── services/                 # Business logic
│   │   ├── __init__.py
│   │   └── sync_service.py      # Core sync orchestration and conflict resolution
│   │
│   ├── api/                      # FastAPI REST API
│   │   ├── __init__.py
│   │   ├── main.py              # FastAPI app initialization
│   │   └── routes.py            # API endpoints
│   │
│   └── cli/                      # Command-line interface
│       ├── __init__.py
│       └── main.py              # Typer CLI commands
│
├── config/                       # Configuration files
│   └── field_mappings.yaml      # Field mapping definitions
│
├── docs/                         # Documentation
│   ├── architecture.md          # System architecture and design
│   ├── configuration.md         # Configuration guide
│   └── usage_examples.md        # Usage examples and tutorials
│
├── tests/                        # Unit tests
│   ├── __init__.py
│   ├── conftest.py              # Pytest fixtures
│   └── test_mapping_engine.py   # Mapping engine tests
│
├── .env.example                  # Example environment variables
├── .gitignore                    # Git ignore patterns
├── CHANGELOG.md                  # Version history
├── Makefile                      # Common commands
├── README.md                     # Main documentation
├── requirements.txt              # Python dependencies
├── setup.py                      # Package setup
└── sync_cli.py                   # CLI entry point

```

## File Descriptions

### Root Files

| File | Purpose |
|------|---------|
| `.env.example` | Template for environment configuration |
| `.gitignore` | Files/directories excluded from git |
| `CHANGELOG.md` | Version history and release notes |
| `Makefile` | Common development commands |
| `README.md` | Main project documentation |
| `requirements.txt` | Python package dependencies |
| `setup.py` | Package installation configuration |
| `sync_cli.py` | CLI entry point script |

### Core Application (`app/core/`)

| File | Purpose |
|------|---------|
| `config.py` | Pydantic settings, environment variable loading |
| `database.py` | SQLAlchemy engine, session factory, DB initialization |
| `logging.py` | Structured logging with structlog (JSON/text) |

### Models (`app/models/`)

| File | Purpose |
|------|---------|
| `tracking.py` | SyncObject (mappings), SyncRun (operations), SyncError (failures) |

### HubSpot Integration (`app/hubspot/`)

| File | Purpose |
|------|---------|
| `client.py` | HTTP client for HubSpot CRM v3 API (contacts, companies, deals) |

### IndieStack Integration (`app/indie/`)

| File | Purpose |
|------|---------|
| `models.py` | SQLAlchemy models for IndieStack CRM schema |
| `repository.py` | Repository pattern for database/API access |

### Mapping Engine (`app/mappings/`)

| File | Purpose |
|------|---------|
| `engine.py` | YAML-based field mapping with transformations |

### Services (`app/services/`)

| File | Purpose |
|------|---------|
| `sync_service.py` | Core sync logic, conflict resolution, orchestration |

### API (`app/api/`)

| File | Purpose |
|------|---------|
| `main.py` | FastAPI app setup, CORS, startup/shutdown |
| `routes.py` | REST endpoints for sync control and monitoring |

### CLI (`app/cli/`)

| File | Purpose |
|------|---------|
| `main.py` | Typer commands for sync operations and utilities |

### Configuration (`config/`)

| File | Purpose |
|------|---------|
| `field_mappings.yaml` | Field mapping definitions for all entity types |

### Documentation (`docs/`)

| File | Purpose |
|------|---------|
| `architecture.md` | System design, data flow, extensibility |
| `configuration.md` | Detailed configuration guide |
| `usage_examples.md` | Tutorials and common scenarios |

### Tests (`tests/`)

| File | Purpose |
|------|---------|
| `conftest.py` | Pytest fixtures and test configuration |
| `test_mapping_engine.py` | Unit tests for field mapping logic |

## Key Components

### 1. Sync Service (`app/services/sync_service.py`)

The heart of the application:
- Orchestrates bidirectional sync
- Implements conflict resolution
- Manages sync runs and error tracking
- Handles pagination and batching

### 2. Mapping Engine (`app/mappings/engine.py`)

Flexible field transformation:
- Reads YAML configuration
- Transforms IndieStack ↔ HubSpot data
- Supports nested JSON fields
- Applies custom transformations

### 3. Repository Pattern (`app/indie/repository.py`)

Abstraction for data access:
- Currently supports database integration
- Designed for future API integration
- Swappable implementation

### 4. Tracking Database (`app/models/tracking.py`)

Maintains sync state:
- `sync_objects`: IndieStack ↔ HubSpot mappings
- `sync_runs`: Operation history
- `sync_errors`: Error logging

## Data Flow

```
┌─────────────┐
│   CLI/API   │
└──────┬──────┘
       │
       ▼
┌─────────────────┐
│  Sync Service   │
└─────┬─────┬─────┘
      │     │
      ▼     ▼
┌──────┐ ┌───────┐
│HubSpot│ │Indie  │
│Client │ │Repo   │
└───┬───┘ └───┬───┘
    │         │
    ▼         ▼
┌─────────────────┐
│ Mapping Engine  │
└─────────────────┘
```

## Extension Points

1. **Add new entity types**: Extend models, repository, and mappings
2. **Custom transformations**: Add to `MappingEngine`
3. **New conflict strategies**: Extend `SyncService._should_update_indie()`
4. **API integration**: Implement `IndieAPIRepository`
5. **New sync triggers**: Add endpoints or CLI commands

## Development Workflow

1. **Setup**: `make dev-setup`
2. **Code**: Edit files in `app/`
3. **Test**: `make test`
4. **Format**: `make format`
5. **Lint**: `make lint`
6. **Run**: `make run-api` or `python sync_cli.py`

## Deployment Files

Generated at runtime:
- `sync_tracking.db` - SQLite tracking database (if using SQLite)
- `*.log` - Log files (if configured)
- `.env` - Environment variables (never commit!)

## Dependencies

Main libraries:
- **FastAPI** - REST API framework
- **Typer** - CLI framework
- **SQLAlchemy** - ORM and database toolkit
- **httpx** - HTTP client for HubSpot API
- **Pydantic** - Data validation and settings
- **structlog** - Structured logging
- **PyYAML** - YAML configuration parsing
- **Rich** - Beautiful CLI output
