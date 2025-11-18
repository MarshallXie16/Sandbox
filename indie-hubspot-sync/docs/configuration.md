# Configuration Guide

## Environment Variables

All configuration is managed through environment variables, loaded from a `.env` file.

### Required Variables

#### HubSpot Configuration

```bash
# HubSpot private app token
# Get this from: HubSpot Settings → Integrations → Private Apps
HUBSPOT_PRIVATE_APP_TOKEN=your_token_here
```

Required scopes for the HubSpot private app:
- `crm.objects.contacts.read`
- `crm.objects.contacts.write`
- `crm.objects.companies.read`
- `crm.objects.companies.write`
- `crm.objects.deals.read`
- `crm.objects.deals.write`

#### IndieStack Configuration

**For Database Integration Mode:**

```bash
# IndieStack database connection
INDIE_DB_HOST=localhost
INDIE_DB_PORT=5432
INDIE_DB_NAME=indie_crm
INDIE_DB_USER=indie_user
INDIE_DB_PASSWORD=your_password

# Integration mode
INDIE_INTEGRATION_MODE=database
```

**For API Integration Mode (future):**

```bash
# IndieStack API access
INDIE_API_URL=https://api.indiestack.local
INDIE_API_KEY=your_api_key

# Integration mode
INDIE_INTEGRATION_MODE=api
```

### Optional Variables

#### Sync Tracking Database

```bash
# Local tracking database URL
# Default: SQLite file in current directory
SYNC_DB_URL=sqlite:///./sync_tracking.db

# For production, consider PostgreSQL:
# SYNC_DB_URL=postgresql://user:pass@localhost/sync_tracking
```

#### Sync Behavior

```bash
# Default sync direction
# Options: indie_to_hubspot, hubspot_to_indie, bidirectional
DEFAULT_SYNC_DIRECTION=bidirectional

# Batch size for fetching records
# Higher = faster but more memory usage
SYNC_BATCH_SIZE=100

# Conflict resolution strategy
# Options: indie_wins, hubspot_wins, newest_wins
SYNC_CONFLICT_RESOLUTION=indie_wins
```

#### Logging

```bash
# Log level
# Options: DEBUG, INFO, WARNING, ERROR, CRITICAL
LOG_LEVEL=INFO

# Log format
# Options: json, text
LOG_FORMAT=json
```

#### API Server

```bash
# API server host
API_HOST=0.0.0.0

# API server port
API_PORT=8000

# Enable auto-reload (development only)
API_RELOAD=false
```

## Field Mappings Configuration

Field mappings are defined in `config/field_mappings.yaml`.

### Structure

```yaml
entity_type:              # contacts, companies, deals
  properties:
    field_name:
      indie_field:        # Field path in IndieStack
      hubspot_property:   # Property name in HubSpot
      direction:          # Sync direction
      transform:          # Optional transformation
```

### Direction Options

- **`bidirectional`**: Sync in both directions with conflict resolution
- **`indie_to_hubspot`**: Only sync from IndieStack → HubSpot
- **`hubspot_to_indie`**: Only sync from HubSpot → IndieStack

### Field Path Syntax

**Simple fields:**
```yaml
first_name:
  indie_field: first_name
  hubspot_property: firstname
  direction: bidirectional
```

**Nested JSON fields:**
```yaml
engagement_score:
  indie_field: details.engagement_score  # Access nested JSON
  hubspot_property: cl_engagement_score
  direction: indie_to_hubspot
```

### Transformations

Available transformation functions:

#### `datetime_to_timestamp`

Converts Python datetime to Unix timestamp (milliseconds).

```yaml
created_date:
  indie_field: created_at
  hubspot_property: createdate
  direction: indie_to_hubspot
  transform: datetime_to_timestamp
```

#### `date_to_timestamp`

Converts date to Unix timestamp.

```yaml
close_date:
  indie_field: close_date
  hubspot_property: closedate
  direction: bidirectional
  transform: date_to_timestamp
```

#### `stage_id_to_hubspot_stage`

Maps IndieStack stage IDs to HubSpot deal stages.

```yaml
stage:
  indie_field: stage_id
  hubspot_property: dealstage
  direction: indie_to_hubspot
  transform: stage_id_to_hubspot_stage
```

### Example Configurations

#### Contacts - Full Bidirectional Sync

```yaml
contacts:
  properties:
    first_name:
      indie_field: first_name
      hubspot_property: firstname
      direction: bidirectional

    last_name:
      indie_field: last_name
      hubspot_property: lastname
      direction: bidirectional

    primary_email:
      indie_field: primary_email
      hubspot_property: email
      direction: bidirectional
```

#### Companies - Custom Fields One-Way

```yaml
companies:
  properties:
    name:
      indie_field: name
      hubspot_property: name
      direction: bidirectional

    # Custom computed field (IndieStack only)
    health_score:
      indie_field: computed_health_score
      hubspot_property: cl_health_score
      direction: indie_to_hubspot
```

#### Deals - Mixed Directions

```yaml
deals:
  properties:
    # Basic info - bidirectional
    name:
      indie_field: name
      hubspot_property: dealname
      direction: bidirectional

    amount:
      indie_field: amount
      hubspot_property: amount
      direction: bidirectional

    # Workflow stage - IndieStack controls
    stage:
      indie_field: stage_id
      hubspot_property: dealstage
      direction: indie_to_hubspot
      transform: stage_id_to_hubspot_stage

    # Sales notes - HubSpot → IndieStack
    notes:
      indie_field: sales_notes
      hubspot_property: hs_sales_notes
      direction: hubspot_to_indie
```

## Conflict Resolution Strategies

### `indie_wins` (Default)

IndieStack is always treated as the source of truth.

**When to use:**
- IndieStack is your primary CRM
- HubSpot is primarily for sales/marketing UI
- You want strict control over data quality

**Behavior:**
- IndieStack → HubSpot: Always updates HubSpot
- HubSpot → IndieStack: Only creates new records, never updates existing

**Configuration:**
```bash
SYNC_CONFLICT_RESOLUTION=indie_wins
```

### `hubspot_wins`

HubSpot changes always take precedence.

**When to use:**
- Sales team makes all updates in HubSpot
- IndieStack is for analytics/reporting only
- You trust HubSpot data quality

**Behavior:**
- IndieStack → HubSpot: Only creates new records
- HubSpot → IndieStack: Always updates IndieStack

**Configuration:**
```bash
SYNC_CONFLICT_RESOLUTION=hubspot_wins
```

### `newest_wins`

Most recently updated record wins (based on `updated_at` timestamp).

**When to use:**
- Teams update in both systems
- You want automatic conflict resolution
- Timestamps are reliable

**Behavior:**
- Compares `updated_at` (IndieStack) vs `lastmodifieddate` (HubSpot)
- Updates the older record with newer data

**Configuration:**
```bash
SYNC_CONFLICT_RESOLUTION=newest_wins
```

## Sync Directions

### `indie_to_hubspot`

One-way sync from IndieStack to HubSpot.

**Use cases:**
- Initial HubSpot population
- IndieStack is master, HubSpot is read-only
- Pushing computed/enriched data to HubSpot

**Example:**
```bash
python sync_cli.py sync-contacts --direction indie_to_hubspot
```

### `hubspot_to_indie`

One-way sync from HubSpot to IndieStack.

**Use cases:**
- Migrating data from HubSpot
- Importing HubSpot-sourced leads
- Syncing sales notes back to IndieStack

**Example:**
```bash
python sync_cli.py sync-contacts --direction hubspot_to_indie
```

### `bidirectional`

Two-way sync with conflict resolution.

**Use cases:**
- Ongoing synchronization
- Teams work in both systems
- Keep everything in sync

**Example:**
```bash
python sync_cli.py sync-contacts --direction bidirectional
```

## Database Configuration

### SQLite (Default)

Best for:
- Development
- Small deployments (<10,000 records)
- Single-server setups

```bash
SYNC_DB_URL=sqlite:///./sync_tracking.db
```

### PostgreSQL (Recommended for Production)

Best for:
- Production deployments
- Large datasets
- Multi-server setups
- Better performance

```bash
SYNC_DB_URL=postgresql://user:password@localhost:5432/sync_tracking
```

Setup:
```sql
-- Create database
CREATE DATABASE sync_tracking;

-- Create user
CREATE USER sync_user WITH PASSWORD 'secure_password';

-- Grant privileges
GRANT ALL PRIVILEGES ON DATABASE sync_tracking TO sync_user;
```

## Logging Configuration

### JSON Format (Default)

Best for:
- Production
- Log aggregation (ELK, Splunk, etc.)
- Programmatic analysis

```bash
LOG_FORMAT=json
```

Output:
```json
{"timestamp": "2024-01-15T10:30:00Z", "level": "info", "event": "sync_started", "entity_type": "contact"}
```

### Text Format

Best for:
- Development
- Human readability
- Debugging

```bash
LOG_FORMAT=text
```

Output:
```
2024-01-15 10:30:00 [info] sync_started entity_type=contact
```

### Log Levels

- **DEBUG**: Verbose output, shows all operations
- **INFO**: Normal operation logs
- **WARNING**: Potential issues
- **ERROR**: Errors that don't stop execution
- **CRITICAL**: Fatal errors

```bash
LOG_LEVEL=INFO
```

## API Server Configuration

### Development

```bash
API_HOST=127.0.0.1  # Local only
API_PORT=8000
API_RELOAD=true      # Auto-reload on code changes
```

Start:
```bash
uvicorn app.api.main:app --reload
```

### Production

```bash
API_HOST=0.0.0.0     # Accept external connections
API_PORT=8000
API_RELOAD=false     # Disable auto-reload
```

Start:
```bash
# Single worker
uvicorn app.api.main:app --host 0.0.0.0 --port 8000

# Multiple workers (recommended)
uvicorn app.api.main:app --host 0.0.0.0 --port 8000 --workers 4
```

### Behind Reverse Proxy (Nginx)

Nginx config:
```nginx
server {
    listen 80;
    server_name sync.example.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}
```

## Environment-Specific Configurations

### Development

`.env.development`:
```bash
HUBSPOT_PRIVATE_APP_TOKEN=test_token
INDIE_DB_HOST=localhost
SYNC_DB_URL=sqlite:///./dev_sync.db
LOG_LEVEL=DEBUG
LOG_FORMAT=text
API_RELOAD=true
```

### Staging

`.env.staging`:
```bash
HUBSPOT_PRIVATE_APP_TOKEN=staging_token
INDIE_DB_HOST=staging-db.internal
SYNC_DB_URL=postgresql://user:pass@staging-db/sync
LOG_LEVEL=INFO
LOG_FORMAT=json
API_RELOAD=false
```

### Production

`.env.production`:
```bash
HUBSPOT_PRIVATE_APP_TOKEN=prod_token
INDIE_DB_HOST=prod-db.internal
SYNC_DB_URL=postgresql://user:pass@prod-db/sync
LOG_LEVEL=WARNING
LOG_FORMAT=json
SYNC_BATCH_SIZE=500
API_RELOAD=false
```

## Security Best Practices

1. **Never commit `.env` files**
   - Add to `.gitignore`
   - Use `.env.example` as template

2. **Use strong passwords**
   - Generate random passwords
   - Rotate regularly

3. **Restrict database access**
   - Use read-only credentials where possible
   - Limit network access with firewall rules

4. **Rotate API tokens**
   - Update HubSpot tokens quarterly
   - Have a token rotation procedure

5. **Use HTTPS**
   - Always use TLS for API communication
   - Use SSL for database connections

6. **Limit API access**
   - Use authentication for API endpoints (add middleware)
   - Implement rate limiting

## Validation

Verify your configuration:

```bash
# Check configuration
python sync_cli.py config

# Test HubSpot connection
curl -H "Authorization: Bearer $HUBSPOT_PRIVATE_APP_TOKEN" \
  https://api.hubapi.com/crm/v3/objects/contacts?limit=1

# Test IndieStack database connection
psql -h $INDIE_DB_HOST -U $INDIE_DB_USER -d $INDIE_DB_NAME -c "SELECT 1;"

# Dry run to test full configuration
python sync_cli.py sync-contacts --dry-run
```
