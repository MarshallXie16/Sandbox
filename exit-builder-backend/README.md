# Exit Builder Backend

A comprehensive backend API for business valuation, supporting both **Quick Valuation** and **Standard Valuation (Exit Ready MPSP)** flows.

Built with FastAPI, SQLAlchemy, and PostgreSQL.

## Overview

Exit Builder provides two valuation products:

1. **Quick Valuation** - Fast financial-based valuation using industry multiples
2. **Standard Valuation (Exit Ready MPSP)** - Comprehensive $3,000 product with questionnaire, scorecard, and adjusted valuation

## Features

### Quick Valuation Flow
- Financial input collection (3 years optional)
- Multiple valuation methods:
  - Revenue Multiple
  - EBITDA Multiple
  - Asset-Based
- Industry-specific multipliers
- Quick valuation report generation

### Standard Valuation Flow
- All Quick Valuation features
- 20-question Exit Ready questionnaire
- 5-dimension scorecard:
  - Owner Dependency
  - Customer Concentration
  - Systems & Processes
  - Financial Quality
  - Growth & Market Position
- Valuation adjustment based on scorecard (0.80x - 1.10x)
- Comprehensive Exit Ready MPSP report

## Technology Stack

- **Framework**: FastAPI 0.104+
- **ORM**: SQLAlchemy 2.0+
- **Database**: PostgreSQL
- **Migrations**: Alembic
- **Testing**: pytest
- **Python**: 3.9+

## Quick Start

### Prerequisites

- Python 3.9+
- PostgreSQL 12+
- pip / virtualenv

### Installation

```bash
# Clone repository
cd exit-builder-backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your database credentials
```

### Database Setup

```bash
# Create PostgreSQL database
createdb exit_builder

# Run migrations
alembic upgrade head

# Seed initial data (questionnaire, score dimensions, rules)
python -m app.seeds.seed_data
```

### Run Application

```bash
# Development server
uvicorn app.main:app --reload

# Production
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

The API will be available at `http://localhost:8000`

API Documentation: `http://localhost:8000/docs`

## Project Structure

```
exit-builder-backend/
├── app/
│   ├── api/
│   │   └── v1/
│   │       └── routes/
│   │           ├── quick.py          # Quick Valuation endpoints
│   │           └── standard.py       # Standard Valuation endpoints
│   ├── core/
│   │   └── config.py                 # Application settings
│   ├── models/                       # SQLAlchemy models
│   │   ├── project.py
│   │   ├── financial_inputs.py
│   │   ├── valuation_results.py
│   │   ├── report.py
│   │   ├── questionnaire.py
│   │   ├── answer.py
│   │   └── score.py
│   ├── schemas/                      # Pydantic schemas
│   │   ├── project.py
│   │   ├── answer.py
│   │   ├── score.py
│   │   └── report.py
│   ├── services/                     # Business logic
│   │   ├── quick_valuation.py
│   │   ├── answer_service.py
│   │   ├── score_engine.py
│   │   ├── standard_valuation.py
│   │   └── report_builder.py
│   ├── seeds/
│   │   └── seed_data.py              # Seed questionnaire & scoring data
│   ├── database.py                   # Database configuration
│   └── main.py                       # FastAPI application
├── alembic/                          # Database migrations
│   └── versions/
│       └── 001_initial_schema.py
├── tests/                            # Test suite
│   ├── conftest.py
│   ├── test_quick_flow.py
│   └── test_standard_flow.py
├── requirements.txt
├── .env.example
└── README.md
```

## API Usage

### Quick Valuation Flow

#### 1. Create Quick Project

```bash
POST /api/v1/quick/projects
Content-Type: application/json

{
  "name": "My SaaS Business",
  "industry": "saas",
  "description": "Monthly subscription software",
  "financial_inputs": [
    {
      "year": 0,
      "revenue": 1000000,
      "ebitda": 250000,
      "net_profit": 180000,
      "total_assets": 400000,
      "total_liabilities": 100000
    }
  ]
}
```

#### 2. Run Quick Valuation

```bash
POST /api/v1/quick/projects/{project_id}/valuation
```

Response:
```json
{
  "project_id": "uuid",
  "value_low": 2500000,
  "value_mid": 5000000,
  "value_high": 7500000,
  "primary_method": "ebitda_multiple"
}
```

#### 3. Generate Quick Report

```bash
POST /api/v1/quick/projects/{project_id}/report
```

### Standard Valuation Flow

#### 1. Create Standard Project

```bash
POST /api/v1/standard/projects
Content-Type: application/json

{
  "name": "Exit Ready Business",
  "industry": "technology",
  "description": "Tech company seeking exit",
  "financial_inputs": [
    {
      "year": 0,
      "revenue": 2000000,
      "ebitda": 500000
    }
  ]
}
```

#### 2. Submit Questionnaire Answers

```bash
POST /api/v1/standard/projects/{project_id}/answers
Content-Type: application/json

{
  "answers": [
    {
      "question_code": "Q_OWNER_ROLE",
      "selected_option_values": ["FULLY_DELEGATED"]
    },
    {
      "question_code": "Q_TOP_CUSTOMER_PCT",
      "value_numeric": 12
    },
    ...
  ]
}
```

#### 3. Compute Scorecard

```bash
POST /api/v1/standard/projects/{project_id}/score
```

Response:
```json
{
  "total_score": 82,
  "rating": "A",
  "adjustment_factor": 1.10,
  "dimensions": [
    {
      "code": "OWNER_DEP",
      "name": "Owner Dependency",
      "score": 28,
      "weight": 0.25,
      "comment": "Strong performance in Owner Dependency"
    },
    ...
  ]
}
```

#### 4. Run Standard Valuation

```bash
POST /api/v1/standard/projects/{project_id}/valuation
```

Response:
```json
{
  "project_id": "uuid",
  "baseline_valuation": {
    "value_low": 8000000,
    "value_mid": 10000000,
    "value_high": 12000000
  },
  "score": {
    "total_score": 82,
    "rating": "A",
    "adjustment_factor": 1.10
  },
  "adjusted_valuation": {
    "value_low": 8800000,
    "value_mid": 11000000,
    "value_high": 13200000
  },
  "primary_method": "ebitda_multiple"
}
```

#### 5. Generate Standard Report

```bash
POST /api/v1/standard/projects/{project_id}/report
```

Returns comprehensive Exit Ready MPSP report in Markdown format.

## Scorecard Logic

### Score Dimensions (with weights)

1. **Owner Dependency (25%)** - How dependent is the business on the owner?
2. **Customer Concentration (20%)** - Revenue concentration risk
3. **Systems & Processes (20%)** - Operational maturity
4. **Financial Quality (20%)** - Financial strength and predictability
5. **Growth & Market Position (15%)** - Growth trajectory and competitive position

### Rating System

| Total Score | Rating | Valuation Adjustment |
|-------------|--------|---------------------|
| 80-100      | A      | 1.10x (10% premium) |
| 65-79       | B      | 1.00x (no adjustment) |
| 50-64       | C      | 0.90x (10% discount) |
| 0-49        | D      | 0.80x (20% discount) |

### How Scoring Works

1. Each question maps to one or more dimensions
2. Question responses match score rules
3. Matching rules contribute score deltas (e.g., +10, +5, -5)
4. Dimension scores are summed
5. Total score = weighted sum of dimension scores (normalized to 0-100)
6. Rating assigned based on total score
7. Valuation adjustment factor applied to baseline valuation

## Valuation Methodology

### Quick Valuation

Uses three standard methods:

1. **Revenue Multiple**: `Revenue × Industry Multiplier`
2. **EBITDA Multiple**: `EBITDA × Industry Multiplier`
3. **Asset-Based**: `(Assets - Liabilities) × Multiplier`

Industry multipliers:
- SaaS: 6.0x revenue, 12.0x EBITDA
- E-commerce: 2.5x revenue, 7.0x EBITDA
- Professional Services: 1.5x revenue, 5.0x EBITDA
- Technology: 5.0x revenue, 10.0x EBITDA
- (See `app/services/quick_valuation.py` for full list)

### Standard Valuation

1. Runs Quick Valuation to establish baseline
2. Computes Exit Readiness Score
3. Applies adjustment factor based on rating
4. Returns both baseline and adjusted valuations

## Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app tests/

# Run specific test file
pytest tests/test_standard_flow.py -v

# Run specific test
pytest tests/test_standard_flow.py::TestStandardFlow::test_end_to_end_standard_flow -v
```

## Database Schema

### Core Tables

- **projects** - Main project entity (QUICK or STANDARD)
- **financial_inputs** - Financial data (3 years)
- **valuation_results** - Individual method results
- **valuation_summary** - Final valuation summary

### Standard Flow Tables

- **questionnaire_templates** - Questionnaire definitions
- **questions** - Individual questions
- **question_options** - Choice options for questions
- **answers** - User responses
- **score_dimensions** - Scoring dimensions (5 total)
- **score_rules** - Rules mapping answers → scores
- **score_results** - Computed scorecard results
- **score_dimension_results** - Individual dimension scores

### Report Tables

- **report_templates** - Report template definitions
- **reports** - Generated reports

## Seed Data

The system includes comprehensive seed data:

- 20 Exit Ready questions across 5 sections
- 5 score dimensions with weights
- 60+ score rules mapping answers to scores
- 2 report templates (Quick & Standard)

Run seeds:
```bash
python -m app.seeds.seed_data
```

## Environment Variables

```bash
DATABASE_URL=postgresql://user:password@localhost:5432/exit_builder
SECRET_KEY=your-secret-key-here
ENVIRONMENT=development
DEBUG=True
```

## Deployment

### Docker (Optional)

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Production Considerations

- Use PostgreSQL in production (not SQLite)
- Set `DEBUG=False` in production
- Configure CORS origins properly
- Use environment variables for secrets
- Set up database connection pooling
- Implement authentication/authorization
- Add rate limiting
- Enable HTTPS

## Contributing

1. Follow existing code structure
2. Add tests for new features
3. Update documentation
4. Run tests before committing

## License

Proprietary - Capital Link / Exit Ready Program

## Support

For questions or issues, contact the development team.

---

**Built with ❤️ for entrepreneurs and business owners**

*Making businesses Exit Ready*
