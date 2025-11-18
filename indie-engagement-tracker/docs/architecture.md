# Architecture Documentation

## Overview

The Indie Engagement Tracker is designed as a modular, extensible service for tracking and scoring client engagement across multiple systems. It follows clean architecture principles with clear separation of concerns.

## System Architecture

```
┌──────────────────────────────────────────────────────────────┐
│                    External Systems                          │
│  ┌─────────────┐  ┌──────────────┐  ┌──────────────────┐   │
│  │ IndieStack  │  │ Capital Ink  │  │ Future Sources   │   │
│  │    CRM      │  │  Hub Email   │  │ (HubSpot/Sendy)  │   │
│  └──────┬──────┘  └──────┬───────┘  └────────┬─────────┘   │
└─────────┼─────────────────┼───────────────────┼─────────────┘
          │                 │                   │
          │                 │                   │
┌─────────▼─────────────────▼───────────────────▼─────────────┐
│                  Event Source Layer                          │
│  ┌─────────────────────────────────────────────────────┐    │
│  │           EventSource (Abstract Base)               │    │
│  │  • fetch_new_events() → StandardEvent              │    │
│  │  • test_connection() → bool                        │    │
│  └────────────────────┬────────────────────────────────┘    │
│           ┌───────────┼───────────┐                          │
│  ┌────────▼──────┐ ┌──▼───────────┐ ┌────────────────┐     │
│  │EmailEngine    │ │ IndieCRM     │ │  Future        │     │
│  │Source         │ │ ActivitySrc  │ │  Sources       │     │
│  └───────────────┘ └──────────────┘ └────────────────┘     │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐   │
│  │           SourceManager                              │   │
│  │  • Coordinates all sources                          │   │
│  │  • Handles deduplication                            │   │
│  │  • Manages ingestion workflow                       │   │
│  └──────────────────────────────────────────────────────┘   │
└──────────────────────┬───────────────────────────────────────┘
                       │
                       │ StandardEvent
                       │
┌──────────────────────▼───────────────────────────────────────┐
│                  Application Core                            │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐   │
│  │              Repositories                            │   │
│  │  • ScoringProfileRepository                         │   │
│  │  • EngagementRepository                             │   │
│  │  Data access abstraction layer                      │   │
│  └──────────────────┬───────────────────────────────────┘   │
│                     │                                         │
│  ┌──────────────────▼───────────────────────────────────┐   │
│  │              Models (SQLAlchemy)                     │   │
│  │  • EngagementEntity                                 │   │
│  │  • EngagementEvent                                  │   │
│  │  • ScoringProfile                                   │   │
│  │  • ScoreHistory                                     │   │
│  └──────────────────┬───────────────────────────────────┘   │
│                     │                                         │
│  ┌──────────────────▼───────────────────────────────────┐   │
│  │              Database                                │   │
│  │  PostgreSQL (production) or SQLite (dev)            │   │
│  └──────────────────────────────────────────────────────┘   │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐   │
│  │              Scoring Engine                          │   │
│  │  • ScoringEngine                                    │   │
│  │  • Applies weights and decay                        │   │
│  │  • Generates score breakdowns                       │   │
│  └──────────────────────────────────────────────────────┘   │
└──────────────────────┬───────────────────────────────────────┘
                       │
                       │
┌──────────────────────┴───────────────────────────────────────┐
│                  Interface Layer                             │
│                                                              │
│  ┌─────────────────────┐  ┌──────────────────────────┐     │
│  │    REST API         │  │    CLI Tools             │     │
│  │  (FastAPI)          │  │    (Typer)               │     │
│  │                     │  │                          │     │
│  │  • Health           │  │  • init                  │     │
│  │  • Profiles CRUD    │  │  • ingest-all            │     │
│  │  • Ingest trigger   │  │  • recalc-all            │     │
│  │  • Score queries    │  │  • top-contacts          │     │
│  │  • Statistics       │  │  • stats                 │     │
│  └─────────────────────┘  └──────────────────────────┘     │
└──────────────────────────────────────────────────────────────┘
```

## Layer Descriptions

### 1. External Systems Layer

**Purpose:** Source systems that generate engagement data.

**Components:**
- IndieStack CRM Core (contacts, activities, deals)
- Capital Ink Hub Email Engine (email sends, bounces)
- Future integrations (HubSpot, Sendy, webhooks)

**Interaction:** Read-only access via database connections or APIs.

### 2. Event Source Layer

**Purpose:** Abstract and normalize event data from various sources.

**Key Components:**

#### EventSource (Abstract Base Class)
- Defines interface for all event sources
- `fetch_new_events()`: Yields standardized events
- `test_connection()`: Validates source connectivity

#### StandardEvent (Data Class)
```python
@dataclass
class StandardEvent:
    external_id: str        # Contact/deal ID
    entity_type: str        # contact, company, deal
    source_system: str      # Source identifier
    event_type: str         # Normalized event type
    weight: float           # Base weight
    occurred_at: datetime   # Event timestamp
    metadata: Optional[Dict]# Additional data
```

#### SourceManager
- Coordinates multiple sources
- Handles deduplication
- Manages ingestion workflow
- Provides connection testing

**Design Patterns:**
- Strategy Pattern: Pluggable event sources
- Factory Pattern: Source instantiation
- Iterator Pattern: Event streaming

### 3. Application Core Layer

**Purpose:** Business logic, data persistence, and scoring.

**Key Components:**

#### Repositories
Abstraction layer for data access:

```python
class ScoringProfileRepository:
    def get_by_id(profile_id)
    def get_default()
    def create(name, rules)
    def update(profile_id, **kwargs)
    def delete(profile_id)

class EngagementRepository:
    def get_entity_by_external_id(external_id, type)
    def get_top_contacts(limit, filters)
    def get_entity_events(entity_id)
    def get_statistics()
```

#### Models (SQLAlchemy)

**EngagementEntity:**
- Represents tracked entities (contacts, companies, deals)
- Stores latest score and breakdown
- Tracks last activity timestamp

**EngagementEvent:**
- Immutable event records
- Links to entity
- Contains metadata for debugging

**ScoringProfile:**
- Defines scoring rules
- Configurable event weights
- Time decay settings

**ScoreHistory:**
- Historical score snapshots
- Enables trend analysis
- Debugging and auditing

#### Scoring Engine

```python
class ScoringEngine:
    def __init__(db, profile)

    def calculate_score(events) → (score, breakdown)
    def calculate_entity_score(entity) → (score, breakdown)
    def recalculate_all_scores(filters) → stats
```

**Algorithm:**
1. Fetch all events for entity
2. Apply event weights from profile
3. Apply time decay if enabled
4. Aggregate into total score
5. Generate breakdown by event type and source
6. Store result and history

**Time Decay Formula:**
```python
if event_age > decay_days:
    final_weight = base_weight * decay_factor
else:
    final_weight = base_weight
```

### 4. Interface Layer

**Purpose:** Expose functionality via APIs and CLI.

#### REST API (FastAPI)

**Endpoints:**

| Method | Path | Purpose |
|--------|------|---------|
| GET | /health | Health check |
| POST | /profiles | Create profile |
| GET | /profiles | List profiles |
| GET | /profiles/{id} | Get profile |
| PATCH | /profiles/{id} | Update profile |
| DELETE | /profiles/{id} | Delete profile |
| POST | /ingest/run | Trigger ingestion |
| GET | /ingest/test-connections | Test sources |
| POST | /scores/recalculate | Recalc scores |
| GET | /scores/top-contacts | Top entities |
| GET | /scores/contact/{id} | Entity detail |
| GET | /stats | Statistics |

**Features:**
- Pydantic schemas for validation
- OpenAPI/Swagger docs
- CORS middleware
- Error handling

#### CLI (Typer)

**Commands:**
- `init`: Initialize database
- `ingest-all`: Fetch from all sources
- `recalc-all`: Recalculate scores
- `top-contacts`: Display rankings
- `stats`: Show statistics
- `test-sources`: Test connections

**Features:**
- Rich terminal output
- Tables and colors
- Progress indicators
- Error handling

## Data Flow

### Ingestion Flow

```
1. Trigger (API/CLI)
   ↓
2. SourceManager.ingest_from_all_sources()
   ↓
3. For each source:
   ├─ source.fetch_new_events()
   ├─ Standardize to StandardEvent
   ├─ Check for duplicates
   └─ Store in database
   ↓
4. Return statistics
```

### Score Calculation Flow

```
1. Trigger (API/CLI/Auto)
   ↓
2. ScoringEngine.recalculate_all_scores()
   ↓
3. For each entity:
   ├─ Fetch all events
   ├─ Apply event weights
   ├─ Apply time decay
   ├─ Calculate total
   ├─ Generate breakdown
   ├─ Update entity.latest_score
   └─ Save to score_history
   ↓
4. Return statistics
```

### Query Flow

```
1. API Request
   ↓
2. Repository query
   ↓
3. Database query (filtered)
   ↓
4. Transform to schema
   ↓
5. JSON response
```

## Database Schema

### ERD (Entity Relationship Diagram)

```
┌─────────────────────────┐
│  engagement_entities    │
├─────────────────────────┤
│ id (PK)                 │
│ external_id             │◄────┐
│ entity_type (enum)      │     │
│ latest_score            │     │
│ score_breakdown (json)  │     │
│ last_activity_at        │     │
│ created_at              │     │
│ updated_at              │     │
└─────────────────────────┘     │
          △                      │
          │                      │
          │ 1:N                  │
          │                      │
┌─────────┴───────────────┐     │
│  engagement_events      │     │
├─────────────────────────┤     │
│ id (PK)                 │     │
│ engagement_entity_id(FK)├─────┘
│ external_id             │
│ entity_type             │
│ source_system           │
│ event_type              │
│ weight                  │
│ metadata (json)         │
│ occurred_at             │
│ ingested_at             │
└─────────────────────────┘

┌─────────────────────────┐
│  scoring_profiles       │
├─────────────────────────┤
│ id (PK)                 │◄────┐
│ name (unique)           │     │
│ description             │     │
│ rules (json)            │     │
│ is_default              │     │
│ created_at              │     │
│ updated_at              │     │
└─────────────────────────┘     │
                                │
                                │
┌─────────────────────────┐     │
│  score_history          │     │
├─────────────────────────┤     │
│ id (PK)                 │     │
│ engagement_entity_id(FK)│     │
│ scoring_profile_id (FK) ├─────┘
│ score_value             │
│ score_components (json) │
│ calculated_at           │
└─────────────────────────┘
```

### Indexes

**engagement_entities:**
- PRIMARY KEY: id
- UNIQUE: (external_id, entity_type)
- INDEX: latest_score
- INDEX: last_activity_at

**engagement_events:**
- PRIMARY KEY: id
- INDEX: engagement_entity_id
- INDEX: (source_system, event_type)
- INDEX: (external_id, occurred_at)
- INDEX: occurred_at

**scoring_profiles:**
- PRIMARY KEY: id
- UNIQUE: name
- INDEX: is_default

**score_history:**
- PRIMARY KEY: id
- INDEX: (engagement_entity_id, calculated_at)
- INDEX: scoring_profile_id

## Configuration Management

### Settings Hierarchy

```
1. Environment Variables (.env)
   ↓
2. Settings Class (Pydantic)
   ↓
3. Application Core
```

### Key Settings

```python
class Settings:
    # Database
    database_url: str
    indie_crm_db_url: Optional[str]
    email_engine_db_url: Optional[str]

    # Scoring
    default_scoring_profile_id: int
    score_decay_enabled: bool
    score_decay_days: int
    score_decay_factor: float

    # API
    api_host: str
    api_port: int
    api_secret_key: str

    # Environment
    app_env: str
    log_level: str
```

## Extensibility Points

### Adding New Event Sources

1. Create class extending `EventSource`
2. Implement `fetch_new_events()`
3. Implement `test_connection()`
4. Register in `SourceManager._configure_sources()`

```python
class HubSpotSource(EventSource):
    def fetch_new_events(self, since, limit):
        # Implement HubSpot fetching
        for raw_event in fetch_from_hubspot():
            yield StandardEvent(...)

    def test_connection(self):
        # Test HubSpot API
        return True/False
```

### Adding New Event Types

1. Add to source's event mapping
2. Add weight to scoring profile
3. No code changes needed!

### Adding New Entity Types

1. Add to `EntityType` enum
2. Update source mapping
3. Update UI/reporting as needed

## Security Considerations

### Current Implementation

- Environment-based configuration
- No hardcoded credentials
- Database connection pooling
- SQL injection prevention (SQLAlchemy ORM)

### Production Recommendations

- [ ] API authentication/authorization
- [ ] Rate limiting
- [ ] Input validation (Pydantic handles basic)
- [ ] HTTPS/TLS
- [ ] Database encryption at rest
- [ ] Audit logging
- [ ] Secret management (Vault, AWS Secrets Manager)
- [ ] CORS configuration
- [ ] Network isolation

## Performance Considerations

### Current Optimizations

- Database indexes on key fields
- Connection pooling
- Batch processing in ingestion
- Lazy loading of relationships
- JSON fields for flexible data

### Scaling Strategies

**Horizontal Scaling:**
- Read replicas for queries
- Load balancer for API
- Separate ingestion workers

**Vertical Scaling:**
- Increase database resources
- Optimize queries
- Add caching (Redis)

**Data Volume:**
- Partition events by date
- Archive old score history
- Implement data retention policies

## Monitoring and Observability

### Recommended Metrics

**Application:**
- Ingestion success/failure rate
- Average scores
- API response times
- Event processing rate

**Infrastructure:**
- Database connections
- CPU/Memory usage
- API request rate
- Error rates

### Logging

Current logging includes:
- INFO: Normal operations
- WARNING: Recoverable issues
- ERROR: Failures
- DEBUG: Detailed debugging

## Testing Strategy

### Unit Tests

- Scoring engine logic
- Event normalization
- Repository operations
- Model validation

### Integration Tests

- Database operations
- API endpoints
- CLI commands
- Source connectivity

### E2E Tests

- Full ingestion workflow
- Score calculation accuracy
- API client flows

## Future Enhancements

### Planned Features

- [ ] Webhook endpoints for real-time events
- [ ] Push scores back to CRM
- [ ] Email notifications for score thresholds
- [ ] Dashboard UI
- [ ] Advanced analytics
- [ ] Machine learning predictions
- [ ] Multi-tenancy support
- [ ] GraphQL API

### Integration Opportunities

- Slack notifications
- Zapier/Make.com webhooks
- BI tool connectors
- Export to data warehouse
