# Capitalink Analytics - Architecture

## System Overview

Capitalink Analytics is a **read-only analytics and reporting service** that aggregates data across all Capitalink modules (1-9) to provide comprehensive insights into the platform's performance.

## Design Principles

### 1. Read-Only by Design

**Critical Principle:** This module MUST NOT mutate any upstream module's core data.

- All upstream database connections are read-only
- Repository pattern enforces read-only access
- Analytics-specific tables are maintained separately

### 2. Multi-Database Architecture

The system connects to multiple databases:

```
┌─────────────────────────────────────────────┐
│        Capitalink Analytics Module          │
│                                             │
│  ┌────────────────────────────────────┐    │
│  │    Analytics Database (RW)         │    │
│  │  - Snapshots                       │    │
│  │  - Summaries                       │    │
│  │  - Jobs                            │    │
│  └────────────────────────────────────┘    │
│                                             │
│  ┌────────────────────────────────────┐    │
│  │   Upstream Databases (Read-Only)   │    │
│  │  - CRM (Module 1)                  │    │
│  │  - Exit Ready (Module 7)           │    │
│  │  - Facilitator (Module 9)          │    │
│  │  - Engagement Tracker (Module 3)   │    │
│  │  - Portal (Module 5)               │    │
│  │  - Matching Engine (Module 6)      │    │
│  └────────────────────────────────────┘    │
└─────────────────────────────────────────────┘
```

### 3. Layered Architecture

```
┌─────────────────────────────────────────┐
│     Presentation Layer                  │
│  ┌──────┐  ┌──────┐  ┌──────────────┐  │
│  │ API  │  │  UI  │  │     CLI      │  │
│  └──┬───┘  └──┬───┘  └──────┬───────┘  │
└─────┼─────────┼──────────────┼──────────┘
      │         │              │
┌─────┼─────────┼──────────────┼──────────┐
│     │    Service Layer        │         │
│  ┌──▼─────────▼──────────────▼───────┐  │
│  │  Analytics Services              │  │
│  │  - ExitReadyAnalyticsService     │  │
│  │  - FacilitatorAnalyticsService   │  │
│  │  - CrmAnalyticsService           │  │
│  └──────────────┬───────────────────┘  │
└─────────────────┼──────────────────────┘
                  │
┌─────────────────┼──────────────────────┐
│    Repository Layer    │               │
│  ┌──────────────┴───────────────────┐  │
│  │  Data Access Repositories        │  │
│  │  - ExitReadyReadRepository       │  │
│  │  - FacilitatorReadRepository     │  │
│  │  - CrmReadRepository             │  │
│  │  - AnalyticsRepository           │  │
│  └──────────────┬───────────────────┘  │
└─────────────────┼──────────────────────┘
                  │
┌─────────────────┼──────────────────────┐
│     Data Layer           │             │
│  ┌──────────────┴───────────────────┐  │
│  │  PostgreSQL Databases            │  │
│  └──────────────────────────────────┘  │
└─────────────────────────────────────────┘
```

## Components

### 1. Core Layer (`app/core/`)

**Purpose:** Foundation services and configuration

- `config.py` – Settings management with Pydantic
- `database.py` – Database connection management
- `logging.py` – Logging configuration
- `auth.py` – API key authentication

### 2. Models Layer (`app/models/`)

**Purpose:** Database schema definitions

- `analytics.py` – Analytics-specific tables:
  - `AnalyticsSnapshot` – Daily metric snapshots
  - `AnalyticsExitReadySummary` – Exit Ready case summaries
  - `AnalyticsFacilitatorSummary` – Facilitator engagement summaries
  - `AnalyticsJob` – Job execution tracking

### 3. Schemas Layer (`app/schemas/`)

**Purpose:** API request/response validation

- Pydantic models for type-safe API contracts
- Response schemas for each analytics domain

### 4. Repository Layer (`app/repositories/`)

**Purpose:** Data access abstraction

**Read-Only Repositories:**
- `CrmReadRepository` – Query CRM data
- `ExitReadyReadRepository` – Query Exit Ready data
- `FacilitatorReadRepository` – Query Facilitator data

**Analytics Repository:**
- `AnalyticsRepository` – Manage analytics-specific tables

### 5. Service Layer (`app/services/`)

**Purpose:** Business logic and analytics calculations

- `ExitReadyAnalyticsService` – Exit Ready metrics
- `FacilitatorAnalyticsService` – Facilitator metrics
- `CrmAnalyticsService` – CRM metrics

### 6. API Layer (`app/api/`)

**Purpose:** REST API endpoints

FastAPI routers for:
- Health checks
- Exit Ready analytics
- Facilitator analytics
- CRM analytics

### 7. UI Layer (`app/ui/`)

**Purpose:** Web dashboard

- Jinja2 templates
- Dashboard routes
- Simple HTML/CSS interface

### 8. CLI Layer (`app/cli/`)

**Purpose:** Command-line interface

- Typer-based CLI
- Rich terminal output
- Snapshot management
- Quick reporting

## Data Flow

### Query Flow (Read Operations)

```
1. User Request
   ↓
2. API/Dashboard/CLI Handler
   ↓
3. Analytics Service
   - Apply business logic
   - Calculate metrics
   ↓
4. Repository Layer
   - Execute SQL queries
   - Read from upstream DBs
   ↓
5. Database Connection Pool
   - Async connection management
   ↓
6. Upstream Databases (Read-Only)
   - Return raw data
   ↓
7. Service Layer
   - Aggregate results
   - Calculate derived metrics
   ↓
8. Response
   - Return formatted data
```

### Snapshot Flow (Write Operations)

```
1. CLI: snapshot --date 2025-01-15
   ↓
2. Snapshot Command
   ↓
3. Analytics Service
   - Query upstream databases
   - Calculate aggregates
   ↓
4. Analytics Repository
   - Write to analytics_snapshots
   - Store in analytics DB
   ↓
5. Job Tracking
   - Log job start/completion
   - Track errors
```

## Database Schema

### Analytics Tables (Local to Module)

#### analytics_snapshots

```sql
CREATE TABLE analytics_snapshots (
    id UUID PRIMARY KEY,
    snapshot_date DATE NOT NULL,
    domain VARCHAR(100) NOT NULL,
    data JSONB NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE,
    updated_at TIMESTAMP WITH TIME ZONE,
    UNIQUE(snapshot_date, domain)
);
```

Purpose: Store daily metrics snapshots for historical analysis.

#### analytics_exit_ready_summary

```sql
CREATE TABLE analytics_exit_ready_summary (
    id UUID PRIMARY KEY,
    case_id UUID UNIQUE NOT NULL,
    status VARCHAR(50) NOT NULL,
    seller_contact_id UUID,
    company_id UUID,
    -- Timestamps
    case_created_at TIMESTAMP NOT NULL,
    intake_completed_at TIMESTAMP,
    -- ... other timestamps
    -- Duration metrics
    total_duration_days INTEGER,
    duration_intake_to_docs INTEGER,
    -- ...
    linked_facilitator_engagement_id UUID,
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);
```

Purpose: Denormalized case metrics for performance.

#### analytics_facilitator_summary

```sql
CREATE TABLE analytics_facilitator_summary (
    id UUID PRIMARY KEY,
    engagement_id UUID UNIQUE NOT NULL,
    status VARCHAR(50) NOT NULL,
    -- Metrics
    num_introduced_buyers INTEGER,
    num_offers INTEGER,
    closed_with_introduced_buyer BOOLEAN,
    -- Financial
    final_price DECIMAL,
    success_fee_gross_amount DECIMAL,
    success_fee_net_amount DECIMAL,
    offer_fee_collected DECIMAL,
    total_revenue DECIMAL,
    -- Timestamps
    engagement_created_at TIMESTAMP,
    engagement_closed_at TIMESTAMP,
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);
```

Purpose: Per-engagement revenue and metrics tracking.

#### analytics_jobs

```sql
CREATE TABLE analytics_jobs (
    id UUID PRIMARY KEY,
    job_type VARCHAR(100) NOT NULL,
    status VARCHAR(50) NOT NULL,
    domain VARCHAR(100),
    started_at TIMESTAMP NOT NULL,
    completed_at TIMESTAMP,
    error_message TEXT,
    metadata JSONB,
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);
```

Purpose: Track analytics job executions for monitoring.

## Security

### Authentication

- API key-based authentication
- Keys configured via environment variables
- Header: `X-API-Key`

### Database Security

- Read-only credentials for upstream databases
- Separate connection pools
- No write operations on upstream data

### Data Privacy

- No PII exposure in logs
- Aggregated metrics only in snapshots
- Secure credential management

## Performance Considerations

### Connection Pooling

```python
# Analytics DB: Larger pool (read-write)
analytics_engine = create_async_engine(
    url, pool_size=10, max_overflow=20
)

# Upstream DBs: Smaller pools (read-only)
upstream_engine = create_async_engine(
    url, pool_size=5, max_overflow=10
)
```

### Caching Strategy

- Daily snapshots reduce load on upstream DBs
- Summary tables for frequently accessed metrics
- Async queries for concurrent operations

### Query Optimization

- Direct SQL for complex aggregations
- Indexed columns in analytics tables
- Efficient date range queries

## Monitoring

### Logging

- Structured logs with context
- Separate loggers per component
- Error tracking with stack traces

### Job Tracking

- All snapshot runs logged in `analytics_jobs`
- Status tracking: running, completed, failed
- Error messages captured for debugging

### Health Checks

- `/api/v1/health` endpoint
- Database connectivity checks
- Service availability monitoring

## Extensibility

### Adding New Analytics

1. Create repository methods in appropriate read repository
2. Add service methods for business logic
3. Create API endpoints
4. Update dashboard templates
5. Add CLI commands

### Adding New Upstream Sources

1. Add database URL to configuration
2. Create new read repository
3. Initialize engine in `database.py`
4. Create analytics service
5. Expose via API/Dashboard/CLI

## Deployment

### Environment Setup

1. Configure environment variables
2. Run database migrations
3. Start FastAPI server
4. Configure reverse proxy (nginx)
5. Set up monitoring

### Scaling

- Horizontal scaling via multiple workers
- Database read replicas for upstream sources
- CDN for dashboard static assets
- Load balancer for API endpoints

## Future Enhancements

- Email/Slack notifications for metrics
- Scheduled snapshot jobs (cron)
- Advanced visualizations (charts.js)
- Export to Excel/CSV
- GraphQL API
- Real-time dashboards (WebSocket)
