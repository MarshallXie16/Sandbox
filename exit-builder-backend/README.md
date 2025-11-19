# Capital Link Exit Builder - Backend API

MVP backend for Capital Link Exit Builder, focusing on the **Quick Valuation** flow.

## Overview

This backend provides:
- Quick business valuation using industry multiples
- Database schema for clients, projects, financials, and valuations
- RESTful API endpoints for creating and retrieving valuations
- Automated Markdown report generation
- Seed data for industry multiples

## Tech Stack

- **Python 3.11**
- **FastAPI** - Modern web framework
- **SQLAlchemy** - ORM for database operations
- **Alembic** - Database migrations
- **PostgreSQL** - Primary database
- **Pydantic** - Request/response validation
- **Uvicorn** - ASGI server

## Project Structure

```
exit-builder-backend/
├── app/
│   ├── core/
│   │   ├── config.py          # Application settings
│   │   └── db.py              # Database configuration
│   ├── models/
│   │   ├── client.py          # Client model
│   │   ├── project.py         # Project model
│   │   ├── financial.py       # Financial inputs & industry multiples
│   │   ├── valuation.py       # Valuation models
│   │   └── report.py          # Report models
│   ├── services/
│   │   ├── quick_flow.py      # Quick valuation orchestration
│   │   ├── valuation_core.py  # Core valuation logic
│   │   └── report_builder.py  # Markdown report generation
│   ├── api/
│   │   └── v1/
│   │       └── routes/
│   │           └── quick.py   # Quick valuation endpoints
│   └── main.py                # FastAPI application
├── alembic/                   # Database migrations
├── tests/                     # Test files
├── requirements.txt           # Python dependencies
├── seed_data.py              # Database seed script
└── README.md                 # This file
```

## Installation

### 1. Prerequisites

- Python 3.11+
- PostgreSQL 12+
- pip or Poetry

### 2. Create Virtual Environment

```bash
cd exit-builder-backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment

Copy `.env.example` to `.env` and update with your settings:

```bash
cp .env.example .env
```

Edit `.env`:
```env
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/exit_builder
```

### 5. Create Database

```bash
# Create PostgreSQL database
psql -U postgres
CREATE DATABASE exit_builder;
\q
```

### 6. Run Migrations

```bash
alembic upgrade head
```

### 7. Seed Initial Data

```bash
python seed_data.py
```

This will populate:
- Valuation methods (SDE_MULTIPLE, EBITDA_MULTIPLE)
- Report templates (QUICK_SUMMARY)
- Sample industry multiples for HVAC, restaurants, professional services, and retail

## Running the Server

### Development Mode

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Or:

```bash
python -m app.main
```

The API will be available at:
- **API**: http://localhost:8000
- **Docs**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Production Mode

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

## API Endpoints

### Health Check

```bash
GET /health
```

Response:
```json
{
  "status": "healthy",
  "service": "Capital Link Exit Builder",
  "version": "1.0.0"
}
```

### Quick Valuation

Create a quick valuation project:

```bash
POST /api/v1/projects/quick
```

**Request Body:**
```json
{
  "client": {
    "id": null,
    "name": "ABC HVAC",
    "contact_name": "John Doe",
    "email": "john@example.com",
    "phone": "604-123-4567"
  },
  "project": {
    "business_name": "ABC HVAC",
    "industry_code": "238220",
    "location": "Vancouver, BC"
  },
  "financial": {
    "metric_type": "SDE",
    "metric_value": 270000,
    "revenue": 1350000
  }
}
```

**Response:**
```json
{
  "project_id": "uuid-here",
  "client_id": "uuid-here",
  "report_id": "uuid-here",
  "valuation_summary": {
    "recommended_value_low": 756000,
    "recommended_value_mid": 864000,
    "recommended_value_high": 972000,
    "currency": "CAD"
  }
}
```

### Get Project Details

```bash
GET /api/v1/projects/{project_id}
```

### Get Project Report

```bash
GET /api/v1/projects/{project_id}/report
```

Returns the Markdown report content.

## How Quick Valuation Works

### Algorithm

1. **Input Collection**: Receive business details, industry code, and either SDE or EBITDA
2. **Industry Lookup**: Find matching industry multiples based on NAICS code and metric type
3. **Calculation**:
   - `value_low = metric_value × multiple_low`
   - `value_mid = metric_value × multiple_mid`
   - `value_high = metric_value × multiple_high`
4. **Storage**: Save valuation inputs, results, and summary to database
5. **Report Generation**: Create formatted Markdown report

### Example Calculation

**Input:**
- Business: ABC HVAC
- Industry: 238220 (HVAC Services)
- SDE: $270,000
- Revenue: $1,350,000

**Industry Multiples (from seed data):**
- Low: 2.8x
- Mid: 3.2x
- High: 3.6x

**Valuation:**
- Low: $270,000 × 2.8 = **$756,000**
- Mid: $270,000 × 3.2 = **$864,000**
- High: $270,000 × 3.6 = **$972,000**

## Database Schema

### Key Tables

1. **clients** - Client information
2. **projects** - Valuation projects
3. **financial_inputs** - Revenue, SDE, EBITDA data
4. **industry_multiples** - Market multiples by industry
5. **valuation_methods** - Valuation approaches
6. **valuation_inputs** - Parameters used for valuation
7. **valuation_results** - Computed values
8. **valuation_summary** - Final recommended values
9. **report_templates** - Report types
10. **reports** - Generated reports

## Testing

### Run Tests

```bash
pytest
```

### Run with Coverage

```bash
pytest --cov=app --cov-report=html
```

### Test Quick Valuation with curl

```bash
curl -X POST "http://localhost:8000/api/v1/projects/quick" \
  -H "Content-Type: application/json" \
  -d '{
    "client": {
      "name": "Test Business Inc",
      "contact_name": "Jane Smith",
      "email": "jane@test.com"
    },
    "project": {
      "business_name": "Test Business",
      "industry_code": "238220",
      "location": "Toronto, ON"
    },
    "financial": {
      "metric_type": "SDE",
      "metric_value": 250000,
      "revenue": 1200000
    }
  }'
```

## Development

### Create New Migration

```bash
alembic revision --autogenerate -m "description of changes"
```

### Apply Migrations

```bash
alembic upgrade head
```

### Rollback Migration

```bash
alembic downgrade -1
```

### Format Code

```bash
black app/
```

### Lint Code

```bash
flake8 app/
```

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `DATABASE_URL` | `postgresql://...` | PostgreSQL connection string |
| `API_V1_PREFIX` | `/api/v1` | API version prefix |
| `PROJECT_NAME` | `Capital Link Exit Builder` | Project name |
| `VERSION` | `1.0.0` | API version |
| `ENVIRONMENT` | `development` | Environment (development/production) |
| `DEBUG` | `True` | Debug mode |
| `BACKEND_CORS_ORIGINS` | `http://localhost:3000,...` | Allowed CORS origins |

## Future Enhancements

This MVP focuses on Quick Valuation. Future versions will include:

- **Standard Valuation**: Adjusted multiples, comparables analysis
- **Full Valuation**: DCF (Discounted Cash Flow) modeling
- **Asset-Based Valuation**: Balance sheet approach
- **Market Comparables**: Real-time market data integration
- **PDF Report Generation**: Professional PDF reports
- **User Authentication**: Multi-tenant support
- **Advanced Analytics**: Historical trends, industry benchmarks

## Troubleshooting

### Database Connection Errors

- Verify PostgreSQL is running: `pg_isready`
- Check DATABASE_URL in `.env`
- Ensure database exists: `psql -U postgres -l`

### Migration Errors

- Reset migrations: `alembic downgrade base && alembic upgrade head`
- Check alembic/versions directory for conflicts

### Import Errors

- Activate virtual environment: `source venv/bin/activate`
- Reinstall dependencies: `pip install -r requirements.txt`

## Support

For issues or questions:
- Check the `/docs` endpoint for API documentation
- Review error logs in console output
- Verify all environment variables are set correctly

## License

Proprietary - Capital Link Exit Builder

---

**Built with FastAPI** 🚀
