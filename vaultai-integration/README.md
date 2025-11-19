# VaultAI Integration Layer (Module 10)

**Centralized AI Gateway for the Capitalink Platform**

## Overview

The VaultAI Integration Layer is Module 10 of the Capitalink platform, providing a unified AI service gateway that connects to local private LLMs and/or cloud providers. It delivers domain-specific AI capabilities to all other modules while enforcing security, redaction, and role boundaries.

## Key Features

- **Provider-Agnostic Architecture**: Connect to any OpenAI-compatible API (local or cloud)
- **Multi-Provider Support**: Local private LLMs, OpenAI, Azure OpenAI, and custom endpoints
- **Domain-Specific Services**: Specialized AI endpoints for Exit Ready, Facilitator, CRM, and Analytics
- **Security & Privacy**: PII detection and redaction, API key authentication
- **Observability**: Comprehensive logging, usage tracking, and performance metrics
- **Scalability**: Async architecture with connection pooling
- **Vector Search**: pgvector integration for RAG workflows (optional)

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Capitalink Modules                         │
│  (Exit Ready, Facilitator, CRM, Analytics, etc.)            │
└────────────────────┬────────────────────────────────────────┘
                     │ HTTP + API Key
                     ▼
┌─────────────────────────────────────────────────────────────┐
│              VaultAI Integration Layer (This)               │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐        │
│  │  Exit Ready │  │ Facilitator │  │    CRM      │        │
│  │   Service   │  │   Service   │  │   Service   │  ...   │
│  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘        │
│         └─────────────────┴────────────────┘                │
│                         │                                    │
│                  ┌──────▼───────┐                           │
│                  │  LLM Router  │                           │
│                  └──────┬───────┘                           │
│         ┌───────────────┼───────────────┐                   │
│         │               │               │                    │
│    ┌────▼────┐    ┌────▼────┐    ┌────▼────┐              │
│    │  Local  │    │ OpenAI  │    │  Azure  │              │
│    │  Client │    │ Client  │    │ Client  │              │
│    └─────────┘    └─────────┘    └─────────┘              │
└─────────────────────────────────────────────────────────────┘
           │               │               │
           ▼               ▼               ▼
     ┌─────────┐     ┌─────────┐     ┌─────────┐
     │  Local  │     │ OpenAI  │     │  Azure  │
     │   LLM   │     │   API   │     │  OpenAI │
     └─────────┘     └─────────┘     └─────────┘
```

## Quick Start

### 1. Installation

```bash
cd vaultai-integration
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Configuration

Copy `.env.example` to `.env` and configure:

```bash
cp .env.example .env
# Edit .env with your settings
```

**Minimum Required Configuration:**

```env
# General
VAULTAI_API_KEYS=your_secure_api_key_here

# Database
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/vaultai_db

# LLM Provider (choose one or more)
LLM_DEFAULT_PROVIDER=local
LLM_LOCAL_BASE_URL=http://localhost:8009
LLM_LOCAL_MODEL=llama3-70b-instruct
```

### 3. Database Setup

```bash
# Create database
createdb vaultai_db

# Run migrations
alembic upgrade head
```

### 4. Run the Service

```bash
# Development
python main.py

# Production with Uvicorn
uvicorn main:app --host 0.0.0.0 --port 8010 --workers 4
```

### 5. Verify Installation

```bash
# Check health
curl http://localhost:8010/health

# List providers
curl http://localhost:8010/health/providers
```

## API Usage

### Authentication

All requests require an API key via header:

```bash
curl -H "X-VaultAI-API-Key: your_api_key_here" \
     http://localhost:8010/api/v1/vaultai/...
```

### Example: Generate Investment Teaser

```bash
curl -X POST http://localhost:8010/api/v1/vaultai/exit-ready/teaser \
  -H "X-VaultAI-API-Key: your_api_key" \
  -H "Content-Type: application/json" \
  -d '{
    "company_name": "Acme Corp",
    "industry": "SaaS",
    "revenue": 50,
    "ebitda": 15,
    "description": "Leading provider of cloud-based workflow automation",
    "unique_selling_points": [
      "98% customer retention",
      "Proprietary AI engine",
      "Recurring revenue model"
    ]
  }'
```

### Example: Draft Facilitation Message

```bash
curl -X POST http://localhost:8010/api/v1/vaultai/facilitator/draft-message \
  -H "X-VaultAI-API-Key: your_api_key" \
  -H "Content-Type: application/json" \
  -d '{
    "context": "Negotiating purchase price for software company",
    "message_type": "update",
    "recipient_role": "buyer",
    "key_points": [
      "Seller has provided updated financials",
      "Due diligence timeline extended by 2 weeks",
      "Next meeting scheduled for Friday"
    ],
    "tone": "professional"
  }'
```

## CLI Usage

The VaultAI CLI provides administrative tools:

```bash
# Show status
python cli.py status

# Database operations
python cli.py db init
python cli.py db stats
python cli.py db reset  # WARNING: Deletes all data

# Provider management
python cli.py provider list
python cli.py provider test local

# Template management
python cli.py template list
python cli.py template show exit_ready_teaser_v1

# Log analysis
python cli.py logs recent --limit 20
python cli.py logs stats --days 7
```

## Configuration Reference

See [docs/configuration.md](docs/configuration.md) for detailed configuration options.

### Key Settings

| Setting | Description | Default |
|---------|-------------|---------|
| `VAULTAI_ENV` | Environment (dev/prod) | `dev` |
| `VAULTAI_API_KEYS` | Comma-separated API keys | (required) |
| `DATABASE_URL` | PostgreSQL connection string | (required) |
| `LLM_DEFAULT_PROVIDER` | Default LLM provider | `local` |
| `LLM_LOCAL_BASE_URL` | Local LLM endpoint | `http://localhost:8009` |
| `LLM_OPENAI_API_KEY` | OpenAI API key | (optional) |
| `ENABLE_PII_REDACTION` | Enable PII redaction | `true` |

## Provider Configuration

### Local Private LLM

```env
LLM_DEFAULT_PROVIDER=local
LLM_LOCAL_BASE_URL=http://localhost:8009
LLM_LOCAL_MODEL=llama3-70b-instruct
```

Supports any local LLM server with OpenAI-compatible API:
- vLLM
- Ollama
- LM Studio
- text-generation-webui

### OpenAI

```env
LLM_DEFAULT_PROVIDER=openai_compatible
LLM_OPENAI_BASE_URL=https://api.openai.com/v1
LLM_OPENAI_API_KEY=sk-...
LLM_OPENAI_MODEL=gpt-4-turbo-preview
```

### Azure OpenAI

```env
LLM_DEFAULT_PROVIDER=azure
LLM_AZURE_BASE_URL=https://your-resource.openai.azure.com
LLM_AZURE_API_KEY=...
LLM_AZURE_MODEL=gpt-4
LLM_AZURE_API_VERSION=2024-02-01
```

## Domain Services

### Exit Ready (Module 7)

- **Investment Teasers**: Generate compelling investment summaries
- **Checklists**: Create exit readiness checklists
- **Summaries**: Summarize exit readiness data

**API Endpoints:**
- `POST /api/v1/vaultai/exit-ready/teaser`
- `POST /api/v1/vaultai/exit-ready/checklist`
- `POST /api/v1/vaultai/exit-ready/summary`

### Facilitator (Module 9)

- **Message Drafting**: Draft professional facilitation messages
- **Negotiation Summaries**: Summarize negotiation progress

**API Endpoints:**
- `POST /api/v1/vaultai/facilitator/draft-message`
- `POST /api/v1/vaultai/facilitator/summarize`

### CRM (Modules 1, 6)

- **Partner Matching**: AI-powered buyer-seller matching
- **Profile Enrichment**: Enhance entity profiles with insights

**API Endpoints:**
- `POST /api/v1/vaultai/crm/match`
- `POST /api/v1/vaultai/crm/enrich`

### Analytics (Module 8)

- **Insights Generation**: Extract insights from analytics data
- **Report Creation**: Generate comprehensive reports
- **Metric Explanation**: Explain metrics in plain language

**API Endpoints:**
- `POST /api/v1/vaultai/analytics/insights`
- `POST /api/v1/vaultai/analytics/report`
- `POST /api/v1/vaultai/analytics/explain`

## Security

### PII Protection

Automatic detection and optional redaction of:
- Social Security Numbers
- Email addresses
- Phone numbers
- Credit card numbers

Configure via:
```env
ENABLE_PII_REDACTION=true
REDACTION_PATTERNS=ssn,email,phone,credit_card
```

### API Authentication

All endpoints require API key authentication:

```python
headers = {
    "X-VaultAI-API-Key": "your_api_key_here"
}
```

### Data Boundaries

VaultAI is **stateless in business data**:
- Does NOT mutate upstream databases
- Does NOT store business transaction data
- Only logs LLM requests/responses for audit

## Logging & Observability

All LLM requests are logged to the `llm_logs` table:

```python
{
    "request_id": "uuid",
    "domain": "exit_ready",
    "task_type": "teaser",
    "provider": "local",
    "model": "llama3-70b-instruct",
    "prompt_tokens": 250,
    "completion_tokens": 180,
    "total_tokens": 430,
    "latency_ms": 1250,
    "status": "success"
}
```

View logs via CLI:
```bash
python cli.py logs recent --limit 50
python cli.py logs stats --days 30
```

## Testing

```bash
# Run tests
pytest

# With coverage
pytest --cov=app --cov-report=html

# Run specific test
pytest tests/unit/test_llm_client.py
```

## Development

### Project Structure

```
vaultai-integration/
├── app/
│   ├── api/              # FastAPI routers
│   ├── cli/              # CLI commands
│   ├── core/             # Config, DB, auth, logging
│   ├── llm/              # LLM client & router
│   ├── models/           # SQLAlchemy models
│   ├── schemas/          # Pydantic schemas
│   └── services/         # Domain services
├── alembic/              # Database migrations
├── config/               # Prompt templates
├── docs/                 # Documentation
├── tests/                # Test suite
├── main.py               # FastAPI app
├── cli.py                # CLI entry point
└── requirements.txt      # Dependencies
```

### Adding a New Service

1. Create schema in `app/schemas/your_domain.py`
2. Create service in `app/services/your_domain.py`
3. Create router in `app/api/your_domain_router.py`
4. Register router in `main.py`

See [docs/development.md](docs/development.md) for details.

## Deployment

### Docker (Recommended)

```bash
# Build image
docker build -t vaultai-integration .

# Run container
docker run -p 8010:8010 --env-file .env vaultai-integration
```

### Systemd Service

See [docs/deployment.md](docs/deployment.md) for systemd configuration.

## Performance

- **Async Architecture**: Non-blocking I/O for concurrent requests
- **Connection Pooling**: Optimized database connections
- **Provider Fallback**: Automatic retry with exponential backoff
- **Horizontal Scaling**: Stateless design for easy scaling

Typical performance (local LLM):
- Latency: 500-2000ms (depends on model size)
- Throughput: 100+ requests/minute per instance

## Troubleshooting

### Common Issues

**1. Database Connection Errors**
```bash
# Check PostgreSQL is running
pg_isready

# Verify DATABASE_URL in .env
echo $DATABASE_URL
```

**2. LLM Provider Not Available**
```bash
# Test provider connection
python cli.py provider test local

# Check provider URL
curl http://localhost:8009/v1/models
```

**3. API Authentication Failures**
```bash
# Verify API key is set
echo $VAULTAI_API_KEYS

# Test with curl
curl -H "X-VaultAI-API-Key: your_key" http://localhost:8010/health
```

See [docs/troubleshooting.md](docs/troubleshooting.md) for more.

## Contributing

1. Follow PEP 8 style guide
2. Add tests for new features
3. Update documentation
4. Run linting: `black app/ && flake8 app/`

## License

Proprietary - Capitalink Platform

## Support

For issues or questions:
- Documentation: `/docs`
- API Docs: `http://localhost:8010/docs`
- Logs: `python cli.py logs recent`

---

**Built with:**
- FastAPI (API framework)
- SQLAlchemy 2.x (ORM)
- Pydantic v2 (validation)
- httpx (async HTTP)
- pgvector (vector search)
- Typer (CLI)
