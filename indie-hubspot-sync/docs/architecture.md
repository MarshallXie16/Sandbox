# Architecture Documentation

## Overview

The HubSpot-IndieStack sync service is designed as a modular, maintainable system that treats IndieStack as the source of truth while using HubSpot as a UI layer.

## System Components

```
┌─────────────────────────────────────────────────────────────┐
│                        Sync Service                          │
│                                                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │   FastAPI    │  │   Typer CLI  │  │ Scheduled    │      │
│  │   (API)      │  │              │  │ Jobs (Cron)  │      │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘      │
│         │                 │                  │               │
│         └─────────────────┴──────────────────┘               │
│                           │                                  │
│                  ┌────────▼────────┐                         │
│                  │  SyncService    │                         │
│                  │  (Core Logic)   │                         │
│                  └────────┬────────┘                         │
│                           │                                  │
│         ┌─────────────────┼─────────────────┐               │
│         │                 │                 │               │
│  ┌──────▼───────┐  ┌─────▼─────┐  ┌────────▼────────┐      │
│  │   HubSpot    │  │  Mapping  │  │  IndieStack     │      │
│  │   Client     │  │  Engine   │  │  Repository     │      │
│  └──────┬───────┘  └─────┬─────┘  └────────┬────────┘      │
│         │                 │                 │               │
└─────────┼─────────────────┼─────────────────┼───────────────┘
          │                 │                 │
          │                 │                 │
     ┌────▼─────┐    ┌──────▼──────┐   ┌─────▼──────┐
     │ HubSpot  │    │   field_    │   │ IndieStack │
     │   API    │    │ mappings.   │   │    DB      │
     │          │    │   yaml      │   │            │
     └──────────┘    └─────────────┘   └────────────┘

                    ┌─────────────┐
                    │  Tracking   │
                    │   Database  │
                    │  (SQLite/   │
                    │ PostgreSQL) │
                    └─────────────┘
```

## Module Breakdown

### 1. Core (`app/core/`)

**config.py**
- Loads environment variables using Pydantic Settings
- Provides application-wide configuration
- Type-safe access to settings

**database.py**
- SQLAlchemy engine and session management
- Database initialization
- Session factory for dependency injection

**logging.py**
- Structured logging with structlog
- JSON and text output formats
- Context propagation

### 2. Models (`app/models/`)

**tracking.py**
- SQLAlchemy models for sync tracking database
- `SyncObject`: Maps IndieStack ↔ HubSpot records
- `SyncRun`: Tracks sync operations
- `SyncError`: Logs errors for debugging

### 3. HubSpot Integration (`app/hubspot/`)

**client.py**
- HTTP client for HubSpot CRM v3 API
- CRUD operations for Contacts, Companies, Deals
- Association management
- Rate limiting and error handling

### 4. IndieStack Integration (`app/indie/`)

**models.py**
- SQLAlchemy models representing IndieStack schema
- `IndieContact`, `IndieCompany`, `IndieDeal`
- Maps to expected indie-crm-core structure

**repository.py**
- Repository pattern for data access
- `IndieDatabaseRepository`: Direct DB access
- Protocol for future API-based access
- Abstraction allows swapping implementation

### 5. Mapping Engine (`app/mappings/`)

**engine.py**
- Reads YAML field mapping configuration
- Transforms IndieStack records → HubSpot properties
- Transforms HubSpot objects → IndieStack payloads
- Respects directional constraints
- Applies field transformations (datetime, enums, etc.)

### 6. Sync Service (`app/services/`)

**sync_service.py**
- Orchestrates bidirectional sync
- Implements conflict resolution strategies
- Manages sync runs and error tracking
- Handles pagination and batching

### 7. API (`app/api/`)

**main.py**
- FastAPI application setup
- CORS configuration
- Startup/shutdown hooks

**routes.py**
- REST endpoints for sync control
- Health checks, stats, monitoring
- Sync run history and error inspection

### 8. CLI (`app/cli/`)

**main.py**
- Typer-based command-line interface
- Sync commands with rich output
- Configuration viewing
- Troubleshooting tools

## Data Flow

### IndieStack → HubSpot Sync

```
1. Fetch IndieStack records (via Repository)
   ↓
2. Check sync_objects table for existing mappings
   ↓
3. Transform IndieStack record → HubSpot properties (Mapping Engine)
   ↓
4. Create or Update HubSpot object (HubSpot Client)
   ↓
5. Update sync_objects with mapping and timestamp
   ↓
6. Log to sync_runs and sync_errors
```

### HubSpot → IndieStack Sync

```
1. Fetch HubSpot objects (via HubSpot Client)
   ↓
2. Check sync_objects table for existing mappings
   ↓
3. Apply conflict resolution if record exists in both systems
   ↓
4. Transform HubSpot object → IndieStack payload (Mapping Engine)
   ↓
5. Create or Update IndieStack record (Repository)
   ↓
6. Update sync_objects with mapping and timestamp
   ↓
7. Log to sync_runs and sync_errors
```

### Bidirectional Sync

```
1. Run IndieStack → HubSpot sync (pass 1)
   ↓
2. Run HubSpot → IndieStack sync (pass 2)
   ↓
3. Conflict resolution prevents infinite loops
   ↓
4. Combine statistics from both passes
```

## Conflict Resolution

### Strategy: `indie_wins` (Default)

```python
if record_exists_in_both_systems:
    if direction == "hubspot_to_indie":
        skip_update()  # IndieStack record is preserved
```

### Strategy: `hubspot_wins`

```python
if record_exists_in_both_systems:
    if direction == "indie_to_hubspot":
        skip_update()  # HubSpot record is preserved
```

### Strategy: `newest_wins`

```python
if record_exists_in_both_systems:
    indie_timestamp = indie_record.updated_at
    hubspot_timestamp = hubspot_record.properties.lastmodifieddate

    if direction == "indie_to_hubspot" and indie_timestamp < hubspot_timestamp:
        skip_update()
    elif direction == "hubspot_to_indie" and hubspot_timestamp < indie_timestamp:
        skip_update()
```

## Field Mapping System

### YAML Configuration

```yaml
contacts:
  properties:
    first_name:
      indie_field: first_name          # Field in IndieStack
      hubspot_property: firstname       # Property in HubSpot
      direction: bidirectional          # Sync direction
      transform: null                   # Optional transformation
```

### Nested Field Support

```yaml
engagement_score:
  indie_field: details.engagement_score  # JSON path notation
  hubspot_property: cl_engagement_score
  direction: indie_to_hubspot
```

The mapping engine extracts `indie_record["details"]["engagement_score"]`.

### Transformations

```yaml
created_date:
  indie_field: created_at
  hubspot_property: createdate
  direction: indie_to_hubspot
  transform: datetime_to_timestamp  # Custom transformation function
```

Supported transformations:
- `datetime_to_timestamp`: Python datetime → Unix timestamp (ms)
- `date_to_timestamp`: Date → Unix timestamp (ms)
- `stage_id_to_hubspot_stage`: Map stage IDs
- `pipeline_id_to_hubspot_pipeline`: Map pipeline IDs

## Database Schema Design

### sync_objects

Maintains the mapping between systems:

```sql
CREATE TABLE sync_objects (
    id INTEGER PRIMARY KEY,
    entity_type TEXT NOT NULL,        -- 'contact', 'company', 'deal'
    indie_id TEXT NOT NULL,           -- PK in IndieStack
    hubspot_id TEXT,                  -- PK in HubSpot
    last_synced_at TIMESTAMP,
    last_direction TEXT,
    details TEXT,                     -- JSON metadata
    created_at TIMESTAMP,
    updated_at TIMESTAMP,
    UNIQUE(entity_type, indie_id),
    UNIQUE(entity_type, hubspot_id)
);
```

### sync_runs

Tracks each sync operation:

```sql
CREATE TABLE sync_runs (
    id INTEGER PRIMARY KEY,
    started_at TIMESTAMP NOT NULL,
    finished_at TIMESTAMP,
    status TEXT NOT NULL,             -- 'running', 'success', 'failed', 'partial'
    direction TEXT NOT NULL,
    summary TEXT                      -- JSON stats
);
```

### sync_errors

Logs errors for debugging:

```sql
CREATE TABLE sync_errors (
    id INTEGER PRIMARY KEY,
    sync_run_id INTEGER NOT NULL,
    sync_object_id INTEGER,
    entity_type TEXT NOT NULL,
    indie_id TEXT,
    hubspot_id TEXT,
    error_message TEXT NOT NULL,
    payload TEXT,                     -- JSON record data
    created_at TIMESTAMP NOT NULL,
    FOREIGN KEY (sync_run_id) REFERENCES sync_runs(id)
);
```

## Extensibility Points

### 1. Add New Entity Types

1. Add model to `app/indie/models.py`
2. Add methods to `app/indie/repository.py`
3. Add endpoints to `app/hubspot/client.py`
4. Add mappings to `config/field_mappings.yaml`
5. Add to `EntityType` enum

### 2. Add Custom Transformations

```python
# In app/mappings/engine.py

def _my_custom_transform(self, value: Any) -> Any:
    """Custom transformation logic."""
    return transformed_value

# Register in _apply_transform()
transformers = {
    "my_custom_transform": self._my_custom_transform,
    # ...
}
```

### 3. Switch to API Integration

```python
# Implement app/indie/api_client.py

class IndieAPIRepository:
    def get_contacts(self, ...):
        response = httpx.get(f"{api_url}/contacts")
        return response.json()

    # ... other methods

# Update app/indie/repository.py
def get_indie_repository():
    if settings.indie_integration_mode == "api":
        return IndieAPIRepository()
    else:
        return IndieDatabaseRepository()
```

### 4. Add Custom Conflict Resolution

```python
# In app/services/sync_service.py

def _should_update_indie(self, ...):
    strategy = settings.sync_conflict_resolution

    if strategy == "custom_strategy":
        # Custom logic
        return custom_decision()
```

## Performance Considerations

### Batching

```python
# In SyncService
batch_size = settings.sync_batch_size  # Default: 100

# Fetch in batches
for offset in range(0, total_count, batch_size):
    records = indie_repo.get_contacts(limit=batch_size, offset=offset)
    # Process batch
```

### Incremental Syncs

```python
# Sync only recently modified records
last_sync = get_last_successful_sync_time()
records = indie_repo.get_contacts(updated_since=last_sync)
```

### Connection Pooling

SQLAlchemy handles connection pooling automatically:

```python
engine = create_engine(
    url,
    pool_size=10,
    max_overflow=20,
)
```

## Error Handling

### Graceful Degradation

```python
try:
    hubspot_obj = self.hubspot.create_contact(props)
except httpx.HTTPError as e:
    # Log error
    sync_error = SyncError(...)
    db.add(sync_error)

    # Continue with next record instead of failing entire sync
    stats["errors"] += 1
    continue
```

### Retry Logic

Future enhancement: Add exponential backoff for transient errors.

## Security

### Credential Management

- Never hardcode credentials
- Use environment variables
- Consider secrets management (AWS Secrets Manager, HashiCorp Vault)

### Database Access

- Use read-only credentials where possible
- Limit network access to databases
- Encrypt connections (SSL/TLS)

### API Security

- Rotate HubSpot tokens regularly
- Use HTTPS for all API communication
- Implement rate limiting

## Monitoring & Observability

### Logging

Structured logs enable easy parsing:

```json
{
  "timestamp": "2024-01-15T10:30:00Z",
  "level": "info",
  "event": "sync_completed",
  "entity_type": "contact",
  "sync_run_id": 123,
  "stats": {"created": 10, "updated": 5, "errors": 0}
}
```

### Metrics

Key metrics to track:

- Sync duration
- Records processed per run
- Error rate
- API response times
- Database query performance

### Alerting

Monitor:

- Failed sync runs (status='failed')
- High error counts
- Long-running syncs
- Database connection issues

## Future Enhancements

1. **Real-time sync** via webhooks
2. **Conflict UI** for manual resolution
3. **Field-level change tracking**
4. **Multi-tenant support**
5. **Advanced transformations** (custom Python scripts)
6. **Sync scheduling UI**
7. **Performance dashboard**
8. **Audit trail** for compliance
