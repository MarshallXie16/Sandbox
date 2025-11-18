# Capital Ink Hub Portal API

Backend API service for the WordPress member portal, providing integration between Ultimate Member and IndieStack CRM.

## Overview

The Portal API serves as a secure backend intermediary that:

- Maps WordPress/Ultimate Member users to IndieStack CRM contacts
- Exposes anonymized business listings for buyers
- Tracks buyer interests and engagement
- Provides personalized recommendations
- Manages downloadable resources

**Key Design Principles:**
- Backend-to-backend communication only (WordPress → Portal API → IndieStack CRM)
- API key authentication (no direct browser access)
- Anonymized listing data to protect seller privacy
- Future-compatible with matching engine and engagement tracker

## Architecture

```
WordPress + Ultimate Member
          ↓ (HTTP + API Key)
   Portal API (this service)
          ↓
    IndieStack CRM (PostgreSQL)
```

See [docs/architecture.md](docs/architecture.md) for detailed architecture documentation.

## Tech Stack

- **Framework:** FastAPI
- **Server:** Uvicorn (ASGI)
- **Database:** PostgreSQL (via asyncpg)
- **ORM:** SQLAlchemy 2.0 (async)
- **Migrations:** Alembic
- **CLI:** Typer
- **Validation:** Pydantic v2

## Quick Start

### 1. Installation

```bash
# Clone repository
cd capitalinkhub-portal-api

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configuration

```bash
# Copy example environment file
cp .env.example .env

# Edit .env with your configuration
# IMPORTANT: Set INDIE_DB_DSN to your IndieStack CRM database
# IMPORTANT: Generate and set PORTAL_API_KEY
```

Generate API key:
```bash
python portal_cli.py portal create-api-key
```

### 3. Database Setup

```bash
# Initialize portal-specific tables
python portal_cli.py portal init-db

# Or use Alembic for migrations
alembic upgrade head
```

### 4. Run Server

```bash
# Development mode (with auto-reload)
make dev

# Or directly with uvicorn
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Server will be available at `http://localhost:8000`

API documentation: `http://localhost:8000/docs` (dev mode only)

## API Endpoints

All endpoints require `X-API-Key` header for authentication.

### Health Check
- `GET /api/v1/health` - Health check (no auth required)

### Members
- `POST /api/v1/members/resolve` - Resolve/create member mapping
- `GET /api/v1/members/{member_id}/profile` - Get member profile
- `GET /api/v1/members/{member_id}/engagement` - Get engagement summary

### Listings
- `GET /api/v1/listings` - Browse listings with filters
- `GET /api/v1/listings/{listing_id}` - Get listing detail
- `POST /api/v1/listings/{listing_id}/interest` - Express interest

### Interests
- `GET /api/v1/members/{member_id}/interests` - Get member's interests

### Recommendations
- `GET /api/v1/members/{member_id}/recommendations` - Get personalized recommendations

### Resources
- `GET /api/v1/resources` - List downloadable resources
- `GET /api/v1/resources/{slug}` - Get resource by slug

See [docs/api_usage.md](docs/api_usage.md) for detailed API documentation with examples.

## CLI Tools

The Portal API includes a CLI tool for management tasks:

```bash
# Initialize database
python portal_cli.py portal init-db

# Generate API key
python portal_cli.py portal create-api-key

# List portal members
python portal_cli.py members list

# Find member by UM user ID or email
python portal_cli.py members find --um-user-id 123
python portal_cli.py members find --email user@example.com
```

## WordPress Integration

The WordPress site (using Ultimate Member) should call this API from the backend (PHP code), not from the browser.

**Required headers:**
```
X-API-Key: your-api-key-here
Content-Type: application/json
```

**Recommended WordPress hooks for integration:**
- `um_after_user_is_approved` → Call `/members/resolve`
- `um_user_login` → Call `/members/resolve` (if needed)
- Profile page load → Call `/members/{id}/profile`, `/engagement`, `/interests`
- Listing browse → Call `/listings`
- Interest button → Call `/listings/{id}/interest`

See [docs/integration_ultimate_member.md](docs/integration_ultimate_member.md) for detailed WordPress integration guide.

## Development

### Running Tests

```bash
# Run all tests
make test

# Run with coverage
make test-cov
```

### Code Quality

```bash
# Format code
make format

# Lint code
make lint
```

### Database Migrations

```bash
# Create new migration
make create-migration msg="add new field"

# Run migrations
make migrate
```

## Project Structure

```
capitalinkhub-portal-api/
├── app/
│   ├── api/              # FastAPI routers
│   ├── core/             # Config, logging, database, auth
│   ├── models/           # SQLAlchemy models
│   ├── repositories/     # Data access layer
│   ├── schemas/          # Pydantic models
│   ├── services/         # Business logic
│   └── integrations/     # External service clients
├── alembic/              # Database migrations
├── config/               # Configuration files
├── docs/                 # Documentation
├── tests/                # Test suite
├── main.py               # FastAPI app entrypoint
├── portal_cli.py         # CLI tool
├── requirements.txt      # Python dependencies
├── Makefile              # Convenience commands
└── .env.example          # Example environment config
```

## Environment Variables

Key environment variables (see `.env.example` for complete list):

- `PORTAL_ENV` - Environment (dev/staging/prod)
- `PORTAL_API_KEY` - Primary API key for authentication
- `INDIE_DB_DSN` - PostgreSQL connection string for IndieStack CRM
- `ENGAGEMENT_TRACKER_BASE_URL` - URL for engagement tracker API (optional)
- `MATCHING_ENGINE_BASE_URL` - URL for matching engine API (optional)

## Security

- **API Key Authentication:** All endpoints (except health check) require valid API key
- **Anonymized Data:** Listings expose only non-sensitive information
- **Backend-Only:** Not designed for direct browser access
- **Database Isolation:** Portal tables separate from CRM core tables

## Future Enhancements

- [ ] Integration with `indie-engagement-tracker` for real-time engagement scoring
- [ ] Integration with `indie-matching-engine` for ML-based recommendations
- [ ] Signed URL generation for resource downloads
- [ ] Webhook support for real-time CRM updates
- [ ] Rate limiting and request throttling
- [ ] Enhanced caching layer

## License

Proprietary - Capital Ink Hub

## Support

For questions or issues, contact the IndieStack development team.
