# Exit Builder Backend

Professional business valuation platform API built with FastAPI, supporting Quick Valuation (market multiples) and Full Valuation (DCF + weighted approaches).

## Features

### Quick Valuation Flow (Market Approach)
- Industry-specific multiple-based valuation
- SDE and EBITDA valuation methods
- Automatic valuation range generation

### Full Valuation Flow (Version 3)
- **Financial Recast/Normalization**: Adjust historical financials for non-recurring items
- **Multi-Year Projections**: Project future cash flows
- **DCF Valuation**: Discounted Cash Flow analysis with manually entered parameters
- **Weighted Valuation**: Combine Market, DCF, and Asset-based approaches
- **Professional Reports**: Generate comprehensive Markdown valuation reports

## Tech Stack

- **Framework**: FastAPI 0.109
- **Database**: SQLAlchemy 2.0 (async) with SQLite/PostgreSQL support
- **Migrations**: Alembic
- **Validation**: Pydantic v2

## Quick Start

### Installation

```bash
cd valuation_tool/backend

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run database migrations
alembic upgrade head

# Start server
uvicorn app.main:app --reload
```

The API will be available at `http://localhost:8000`
API documentation at `http://localhost:8000/docs`

### Configuration

Create a `.env` file in the backend directory:

```env
DATABASE_URL=sqlite+aiosqlite:///./exit_builder.db
# For PostgreSQL:
# DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/exit_builder

DEBUG=True
CORS_ORIGINS=http://localhost:5173,http://localhost:3000
```

## API Endpoints

### Projects
- `POST /api/v1/projects` - Create a new project
- `GET /api/v1/projects` - List all projects
- `GET /api/v1/projects/{id}` - Get project details
- `PATCH /api/v1/projects/{id}` - Update project
- `DELETE /api/v1/projects/{id}` - Delete project

### Financial Data
- `POST /api/v1/financial-inputs` - Add financial data for a year
- `GET /api/v1/projects/{id}/financial-inputs` - List financial inputs
- `POST /api/v1/normalization-entries` - Add recast adjustment
- `GET /api/v1/projects/{id}/normalization-entries` - List normalization entries
- `POST /api/v1/projects/{id}/compute-normalized-financials` - Compute normalized financials
- `GET /api/v1/projects/{id}/normalized-financials` - Get normalized financials

### Valuations
- `POST /api/v1/quick-valuation` - Run Quick Valuation (market approach)
- `GET /api/v1/projects/{id}/quick-valuation` - Get Quick Valuation results
- `POST /api/v1/full-valuation` - Run Full Valuation (weighted)
- `GET /api/v1/projects/{id}/full-valuation` - Get Full Valuation results

### DCF
- `POST /api/v1/dcf-parameters` - Set DCF parameters
- `GET /api/v1/projects/{id}/dcf-parameters` - Get DCF parameters
- `PATCH /api/v1/projects/{id}/dcf-parameters` - Update DCF parameters
- `POST /api/v1/dcf-cash-flows` - Add projected cash flow
- `GET /api/v1/projects/{id}/dcf-cash-flows` - List cash flows
- `POST /api/v1/compute-dcf` - Compute DCF valuation
- `GET /api/v1/projects/{id}/dcf-result` - Get DCF results

### Reports
- `GET /api/v1/projects/{id}/full-valuation-report` - Generate Full Valuation Report (Markdown)

## Workflow Examples

### Quick Valuation Workflow

```python
# 1. Create a project
POST /api/v1/projects
{
  "project_name": "Acme Corp Valuation",
  "business_name": "Acme Corp",
  "industry": "SaaS",
  "currency": "CAD"
}

# 2. Add financial data
POST /api/v1/financial-inputs
{
  "project_id": "...",
  "year": 2023,
  "revenue": 1000000,
  "ebitda": 300000,
  "sde": 400000
}

# 3. Run Quick Valuation
POST /api/v1/quick-valuation
{
  "project_id": "...",
  "method": "sde_multiple"
}

# Result: Valuation range based on industry multiples
```

### Full Valuation Workflow

```python
# 1-2. Same as Quick Valuation

# 3. Add normalization entries (recast)
POST /api/v1/normalization-entries
{
  "project_id": "...",
  "year": 2023,
  "category": "owner_salary",
  "description": "Excess owner compensation",
  "amount": 50000,
  "is_addback": true
}

# 4. Compute normalized financials
POST /api/v1/projects/{id}/compute-normalized-financials

# 5. Set DCF parameters (manually entered)
POST /api/v1/dcf-parameters
{
  "project_id": "...",
  "base_metric": "SDE",
  "base_year": 2023,
  "discount_rate": 0.18,
  "projection_years": 5,
  "terminal_method": "exit_multiple",
  "terminal_multiple": 4.0,
  "use_explicit_cash_flows": true
}

# 6. Add projected cash flows
POST /api/v1/dcf-cash-flows
{
  "project_id": "...",
  "year_index": 1,
  "year_label": "2024",
  "cash_flow": 420000
}
# Repeat for years 2-5...

# 7. Compute DCF valuation
POST /api/v1/compute-dcf
{
  "project_id": "..."
}

# 8. Run Full Valuation (weighted)
POST /api/v1/full-valuation
{
  "project_id": "...",
  "weight_market": 0.6,
  "weight_dcf": 0.3,
  "weight_asset": 0.1,
  "asset_value": 200000
}

# 9. Generate report
GET /api/v1/projects/{id}/full-valuation-report
```

## Database Models

### Core Models
- **Project**: Main project entity
- **FinancialInput**: Historical financial data
- **ValuationSummary**: Quick valuation results (market approach)

### Full Valuation Models
- **NormalizationEntry**: Recast adjustments
- **NormalizedFinancial**: Normalized earnings per year
- **DCFParameter**: DCF configuration (manually entered)
- **DCFCashFlow**: Projected cash flows
- **DCFResult**: DCF calculation output
- **FullValuationSummary**: Weighted final valuation

## Service Layer

### Engines
- **quick_valuation_engine.py**: Market-based valuation using industry multiples
- **recast_engine.py**: Financial normalization/recast calculations
- **dcf_engine.py**: Discounted Cash Flow valuation
- **full_valuation_engine.py**: Weighted valuation combining approaches
- **report_generator.py**: Markdown report generation

## Development

### Running Tests

```bash
pytest tests/
```

### Database Migrations

```bash
# Create a new migration
alembic revision --autogenerate -m "description"

# Apply migrations
alembic upgrade head

# Rollback
alembic downgrade -1
```

### Code Style

This project follows standard Python conventions:
- Type hints for all function signatures
- Docstrings for all public functions
- Async/await for all database operations

## Important Notes

### DCF Parameters
- All DCF parameters are **manually entered per project**
- No automatic estimation or inference
- Allows full control for professional appraisals

### Valuation Approaches
- **Market Approach**: Industry multiples × SDE/EBITDA
- **DCF Approach**: Present value of projected cash flows + terminal value
- **Asset Approach**: Manually entered asset-based value (optional)

### Weights
- Weights for Full Valuation must sum to 1.0 (±0.01 tolerance)
- Typical weights: 60% Market, 30% DCF, 10% Asset

## License

MIT

## Support

For issues or questions, please open an issue on GitHub.
