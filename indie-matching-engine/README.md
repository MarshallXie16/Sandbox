# Indie Matching Engine

**Intelligent Buyer-Seller Matching Service for IndieStack CRM**

A production-ready FastAPI service that provides configurable, rule-based matching between buyers (contacts) and listings (deals) from the IndieStack CRM database. Designed for seamless integration with `capitalinkhub-portal-api`, `indie-engagement-tracker`, and `capitalinkhub-email-engine`.

---

## 🎯 Features

- **Configuration-Driven Scoring**: YAML-based scoring rules (no hard-coded weights)
- **Multi-Factor Matching**: Industry, region, deal size, experience, and engagement scoring
- **High-Performance Caching**: Pre-computed match scores for fast recommendation retrieval
- **RESTful API**: FastAPI endpoints with automatic OpenAPI documentation
- **CLI Tools**: Batch processing and management commands via Typer
- **Async Architecture**: Built on SQLAlchemy 2.x async for scalability
- **API Key Authentication**: Secure internal-service-only access
- **Extensible Design**: Ready for ML-based scoring models in the future

---

## 📋 Table of Contents

- [Quick Start](#-quick-start)
- [Architecture](#-architecture)
- [Configuration](#-configuration)
- [API Endpoints](#-api-endpoints)
- [CLI Commands](#-cli-commands)
- [Database Schema](#-database-schema)
- [Integration Guide](#-integration-guide)
- [Deployment](#-deployment)
- [Development](#-development)
- [Testing](#-testing)

---

## 🚀 Quick Start

### Prerequisites

- Python 3.10+
- PostgreSQL database (access to `indie-crm-core` database)
- Virtual environment tool (venv, conda, etc.)

### Installation

```bash
# Clone and navigate to the project
cd indie-matching-engine

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy environment template
cp .env.example .env

# Edit .env with your database credentials
# DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/indie_crm_core
# API_KEY=your-secret-api-key
```

### Database Setup

```bash
# Run Alembic migrations to create matching engine tables
alembic upgrade head
```

### Running the Service

**Option 1: Using CLI (recommended)**
```bash
python cli.py serve --reload
```

**Option 2: Direct uvicorn**
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8003 --reload
```

**Option 3: Python module**
```bash
python -m app.main
```

The API will be available at:
- **API Base**: `http://localhost:8003`
- **Interactive Docs**: `http://localhost:8003/docs`
- **ReDoc**: `http://localhost:8003/redoc`

---

## 🏗 Architecture

### System Design

```
┌─────────────────────────────────────────────────────────────┐
│                    Indie Matching Engine                     │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌────────────┐      ┌─────────────────┐                   │
│  │  FastAPI   │──────│  Matching       │                   │
│  │  Endpoints │      │  Engine         │                   │
│  └────────────┘      └─────────────────┘                   │
│        │                      │                             │
│        │                      ├──► RuleBasedScorer         │
│        │                      │    (YAML Config)            │
│        │                      │                             │
│        │                      ├──► DataLoader              │
│        │                      │    (CRM Access)             │
│        │                      │                             │
│        │                      └──► Match Caching            │
│        │                           (PostgreSQL)             │
│        │                                                     │
│  ┌────────────┐                                             │
│  │    CLI     │──────────────────────────────────►          │
│  │  Commands  │      Batch Processing                       │
│  └────────────┘                                             │
│                                                              │
└─────────────────────────────────────────────────────────────┘
         │                              │
         │                              │
         ▼                              ▼
┌──────────────────┐          ┌──────────────────┐
│  indie-crm-core  │          │  Engagement      │
│  (PostgreSQL)    │          │  Tracker API     │
└──────────────────┘          └──────────────────┘
```

### Component Overview

#### 1. **Matching Engine** (`app/core/matching_engine.py`)
   - Orchestrates scoring and recommendations
   - Manages match score caching
   - Handles batch computations

#### 2. **Scoring System** (`app/core/scoring/`)
   - **RuleBasedScorer**: Main scoring implementation
   - **Component Scorers**: Industry, Region, DealSize, Experience, Engagement
   - **Config Loader**: Reads YAML scoring rules

#### 3. **Data Loader** (`app/core/data_loader.py`)
   - Fetches buyers and listings from CRM database
   - Transforms CRM data into internal schemas

#### 4. **API Layer** (`app/api/`)
   - RESTful endpoints for recommendations
   - Batch match computation triggers
   - API key authentication

#### 5. **Database Models** (`app/models/`)
   - `BuyerListingMatch`: Cached match scores
   - `MatchingRun`: Batch processing tracking

---

## ⚙️ Configuration

### Environment Variables

Create a `.env` file with the following:

```bash
# Database
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/indie_crm_core

# API Settings
API_HOST=0.0.0.0
API_PORT=8003
API_KEY=your-secret-api-key-here

# Scoring
SCORING_CONFIG_PATH=config/scoring_rules.yaml
MIN_RECOMMENDATION_SCORE=40
MAX_RECOMMENDATIONS=20

# Caching
ENABLE_MATCH_CACHING=true
CACHE_TTL_SECONDS=3600

# External Services
ENABLE_ENGAGEMENT_INTEGRATION=false
ENGAGEMENT_TRACKER_URL=http://localhost:8002
ENGAGEMENT_TRACKER_API_KEY=your-engagement-api-key

# Logging
LOG_LEVEL=INFO
```

### Scoring Rules Configuration

Edit `config/scoring_rules.yaml` to customize matching weights:

```yaml
weights:
  industry_exact: 30
  industry_related: 15
  region_exact: 20
  deal_size_perfect: 25
  experience_strong: 10
  engagement_high: 10

thresholds:
  min_recommendation_score: 40
  high_quality_match: 70
  perfect_match: 85

industry_relations:
  software:
    - it_services
    - saas
    - technology

  manufacturing:
    - distribution
    - logistics

region_relations:
  BC:
    - Western Canada
    - Alberta
```

---

## 📡 API Endpoints

All authenticated endpoints require `X-API-Key` header.

### Public Endpoints

#### `GET /`
Root endpoint with service information.

#### `GET /health`
Health check (no authentication required).

### Recommendation Endpoints

#### `GET /api/v1/recommendations/buyer/{buyer_id}`
Get listing recommendations for a buyer.

**Query Parameters:**
- `min_score` (optional): Minimum match score (0-100)
- `limit` (optional): Max recommendations (default: 10)
- `use_cached` (optional): Use cached scores (default: true)

**Response:**
```json
{
  "buyer_id": 123,
  "recommendations": [
    {
      "listing": {
        "id": 456,
        "name": "Tech SaaS Company",
        "industry": "software",
        "region": "BC",
        "amount": 1000000
      },
      "match_score": {
        "score": 85.5,
        "components": {
          "industry_score": 30,
          "region_score": 20,
          "deal_size_score": 25,
          "experience_score": 10,
          "engagement_score": 0.5
        },
        "reason_codes": [
          "Exact industry match: software",
          "Same region: BC",
          "Deal size within budget"
        ]
      }
    }
  ],
  "total_candidates": 50,
  "recommendations_count": 10,
  "min_score_used": 40.0,
  "cached": true
}
```

#### `GET /api/v1/recommendations/listing/{listing_id}`
Get buyer recommendations for a listing.

**Query Parameters:** Same as buyer recommendations.

### Match Computation Endpoints

#### `POST /api/v1/matches/compute`
Trigger batch match computation and caching.

**Request Body:**
```json
{
  "buyer_ids": [1, 2, 3],  // Optional: specific buyers
  "listing_ids": [101, 102],  // Optional: specific listings
  "force_recompute": false
}
```

**Response:**
```json
{
  "matching_run_id": 42,
  "status": "completed",
  "matches_computed": 150,
  "buyers_processed": 50,
  "listings_processed": 30
}
```

#### `GET /api/v1/matches/health`
Service health check (authenticated).

---

## 💻 CLI Commands

### View Configuration

```bash
python cli.py info
```

Displays current configuration and scoring weights.

### Compute Matches

```bash
# Compute all matches
python cli.py compute-matches

# Compute for specific buyer
python cli.py compute-matches --buyer-id 123

# Force recomputation
python cli.py compute-matches --force

# Multiple buyers
python cli.py compute-matches --buyer-id 1 --buyer-id 2 --buyer-id 3
```

### Get Recommendations

```bash
# Get recommendations for buyer
python cli.py recommend-for-buyer 123 --limit 5

# With minimum score
python cli.py recommend-for-buyer 123 --min-score 50

# Without cache
python cli.py recommend-for-buyer 123 --no-cache

# Get recommendations for listing
python cli.py recommend-for-listing 456 --limit 10
```

### Start Server

```bash
python cli.py serve --port 8003 --reload
```

---

## 🗄 Database Schema

### `buyer_listing_matches`

Stores pre-computed match scores.

| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER | Primary key |
| buyer_id | INTEGER | Contact ID from CRM |
| listing_id | INTEGER | Deal ID from CRM |
| score | FLOAT | Match score (0-100) |
| components | JSONB | Score breakdown |
| reason_codes | JSONB | Match explanations |
| matching_run_id | INTEGER | Associated run ID |
| created_at | TIMESTAMP | Created timestamp |
| updated_at | TIMESTAMP | Last updated |

**Indexes:**
- `(buyer_id, listing_id)` - Unique constraint
- `buyer_id` - Fast buyer lookups
- `listing_id` - Fast listing lookups
- `score` - Sorting by score
- `updated_at` - Cache staleness checks

### `matching_runs`

Tracks batch computation runs.

| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER | Primary key |
| run_type | VARCHAR | full/partial/incremental |
| status | VARCHAR | pending/running/completed/failed |
| scope | JSONB | Run parameters |
| matches_computed | INTEGER | Match count |
| buyers_processed | INTEGER | Buyers processed |
| listings_processed | INTEGER | Listings processed |
| started_at | TIMESTAMP | Start time |
| completed_at | TIMESTAMP | End time |
| stats | JSONB | Run statistics |

---

## 🔌 Integration Guide

### Integrating with Portal API

```python
import httpx

async def get_buyer_recommendations(buyer_id: int):
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"http://matching-engine:8003/api/v1/recommendations/buyer/{buyer_id}",
            headers={"X-API-Key": "your-api-key"},
            params={"limit": 10, "min_score": 50}
        )
        return response.json()
```

### Integrating with Email Engine

```python
# Trigger match computation after new listing is created
async def on_listing_created(listing_id: int):
    await client.post(
        "http://matching-engine:8003/api/v1/matches/compute",
        headers={"X-API-Key": "your-api-key"},
        json={"listing_ids": [listing_id]}
    )

    # Get top buyer matches for email campaign
    response = await client.get(
        f"http://matching-engine:8003/api/v1/recommendations/listing/{listing_id}",
        headers={"X-API-Key": "your-api-key"},
        params={"limit": 50, "min_score": 60}
    )

    return response.json()["recommendations"]
```

---

## 🚢 Deployment

### Docker Deployment

```dockerfile
FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Run migrations
RUN alembic upgrade head

# Start server
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8003"]
```

### Docker Compose

```yaml
services:
  matching-engine:
    build: ./indie-matching-engine
    ports:
      - "8003:8003"
    environment:
      - DATABASE_URL=postgresql+asyncpg://user:pass@db:5432/indie_crm_core
      - API_KEY=${MATCHING_ENGINE_API_KEY}
    depends_on:
      - db
```

### Production Checklist

- [ ] Change `API_KEY` from default
- [ ] Set `LOG_LEVEL=WARNING` or `ERROR`
- [ ] Configure CORS for specific origins
- [ ] Set up monitoring and alerting
- [ ] Run Alembic migrations on deployment
- [ ] Configure cache TTL based on data freshness needs
- [ ] Set up scheduled batch computations (cron/Airflow)

---

## 🛠 Development

### Setup Development Environment

```bash
# Install dev dependencies
pip install -r requirements.txt
pip install pytest pytest-asyncio pytest-cov black flake8 mypy

# Set up pre-commit hooks (optional)
# pip install pre-commit
# pre-commit install
```

### Code Style

```bash
# Format code
black .

# Lint
flake8 app/ tests/

# Type checking
mypy app/
```

### Project Structure

```
indie-matching-engine/
├── app/
│   ├── api/              # API routes
│   ├── core/             # Business logic
│   │   └── scoring/      # Scoring system
│   ├── models/           # Database models
│   ├── schemas/          # Pydantic schemas
│   ├── integrations/     # External services
│   ├── cli/              # CLI commands
│   ├── config.py         # Configuration
│   ├── database.py       # DB setup
│   └── main.py           # FastAPI app
├── alembic/              # Migrations
├── config/               # YAML configs
├── tests/                # Test suite
├── cli.py                # CLI entry point
└── requirements.txt
```

---

## 🧪 Testing

### Run All Tests

```bash
pytest
```

### Run Specific Test File

```bash
pytest tests/test_scoring.py
```

### Run with Coverage

```bash
pytest --cov=app --cov-report=html
```

### Test Categories

- **Unit Tests** (`test_scoring.py`): Scoring logic and components
- **API Tests** (`test_api.py`): Endpoint behavior and authentication
- **Integration Tests**: Database operations (add as needed)

---

## 📚 Additional Resources

- **FastAPI Documentation**: https://fastapi.tiangolo.com
- **SQLAlchemy 2.0**: https://docs.sqlalchemy.org/en/20/
- **Alembic Migrations**: https://alembic.sqlalchemy.org
- **Pydantic V2**: https://docs.pydantic.dev/latest/

---

## 📝 License

Internal use for IndieStack/CapitalInkHub platform.

---

## 🤝 Support

For issues or questions:
1. Check the logs: `LOG_LEVEL=DEBUG`
2. Review API docs: `http://localhost:8003/docs`
3. Contact the development team

---

**Built with ❤️ for IndieStack CRM**
