# HubSpot ↔ IndieStack Sync Service

A bidirectional synchronization service that keeps HubSpot CRM and IndieStack CRM in sync, with IndieStack as the primary system-of-record.

## Overview

This service provides:

- **Bidirectional sync** between IndieStack CRM and HubSpot
- **Configurable field mappings** via YAML
- **Conflict resolution** with multiple strategies
- **REST API** for programmatic control
- **CLI tools** for manual operations
- **Comprehensive tracking** of sync operations and errors

## Architecture Philosophy

- **IndieStack = Source of Truth**: In conflicts, IndieStack data wins by default
- **HubSpot = UI Layer**: HubSpot serves as the primary user interface
- **Flexible Integration**: Supports both direct database access and API integration
- **Pluggable Mappings**: Field mappings are configured in YAML, not hardcoded

## Quick Start

### 1. Installation

```bash
cd indie-hubspot-sync

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configuration

```bash
# Copy example environment file
cp .env.example .env

# Edit .env with your credentials
# Required:
# - HUBSPOT_PRIVATE_APP_TOKEN
# - INDIE_DB_HOST, INDIE_DB_PORT, INDIE_DB_NAME, etc.
```

### 3. Initialize Database

```bash
# Initialize the sync tracking database
python sync_cli.py init
```

### 4. Run Your First Sync

```bash
# Dry run to see what would happen
python sync_cli.py sync-all --dry-run

# Actual sync
python sync_cli.py sync-all --direction bidirectional
```

## Configuration

### Environment Variables

See `.env.example` for all configuration options. Key settings:

- `HUBSPOT_PRIVATE_APP_TOKEN`: Your HubSpot private app token
- `INDIE_INTEGRATION_MODE`: `database` or `api` (database is default)
- `DEFAULT_SYNC_DIRECTION`: `indie_to_hubspot`, `hubspot_to_indie`, or `bidirectional`
- `SYNC_CONFLICT_RESOLUTION`: `indie_wins` (default), `hubspot_wins`, or `newest_wins`

### Field Mappings

Edit `config/field_mappings.yaml` to customize field mappings.

Example:

```yaml
contacts:
  properties:
    first_name:
      indie_field: first_name
      hubspot_property: firstname
      direction: bidirectional

    engagement_score:
      indie_field: details.engagement_score
      hubspot_property: cl_engagement_score
      direction: indie_to_hubspot
```

**Direction Options:**
- `bidirectional`: Sync in both directions (with conflict resolution)
- `indie_to_hubspot`: Only sync from IndieStack to HubSpot
- `hubspot_to_indie`: Only sync from HubSpot to IndieStack

## CLI Usage

### Sync Commands

```bash
# Sync specific entity types
python sync_cli.py sync-contacts --direction bidirectional
python sync_cli.py sync-companies --direction indie_to_hubspot
python sync_cli.py sync-deals --direction hubspot_to_indie

# Sync all entities
python sync_cli.py sync-all

# Dry run (preview changes without applying)
python sync_cli.py sync-all --dry-run
```

### Monitoring Commands

```bash
# View field mappings
python sync_cli.py show-mappings
python sync_cli.py show-mappings contacts

# List recent sync runs
python sync_cli.py list-runs --limit 10

# View details of a specific run
python sync_cli.py show-run 123

# Show current configuration
python sync_cli.py config
```

## API Usage

### Starting the API Server

```bash
# Start the FastAPI server
uvicorn app.api.main:app --host 0.0.0.0 --port 8000

# Or use the reload mode for development
uvicorn app.api.main:app --reload
```

### API Endpoints

**Health Check:**
```bash
curl http://localhost:8000/api/v1/health
```

**Trigger Sync:**
```bash
curl -X POST http://localhost:8000/api/v1/sync/run \
  -H "Content-Type: application/json" \
  -d '{
    "entities": ["contacts", "companies"],
    "direction": "bidirectional",
    "dry_run": false
  }'
```

**List Sync Runs:**
```bash
curl http://localhost:8000/api/v1/sync/runs?limit=10
```

**Get Sync Run Details:**
```bash
curl http://localhost:8000/api/v1/sync/runs/123
```

**Get Statistics:**
```bash
curl http://localhost:8000/api/v1/sync/stats
```

## Conflict Resolution

When the same record is modified in both systems, the service uses one of these strategies:

### 1. IndieStack Wins (Default)

```bash
SYNC_CONFLICT_RESOLUTION=indie_wins
```

IndieStack is always treated as the source of truth. HubSpot changes are ignored if IndieStack has the record.

### 2. HubSpot Wins

```bash
SYNC_CONFLICT_RESOLUTION=hubspot_wins
```

HubSpot changes always override IndieStack.

### 3. Newest Wins

```bash
SYNC_CONFLICT_RESOLUTION=newest_wins
```

The most recently updated record (based on `updated_at` timestamps) wins.

## Scheduled Syncs

### Using Cron

```bash
# Edit crontab
crontab -e

# Add a job to sync every hour
0 * * * * cd /path/to/indie-hubspot-sync && /path/to/venv/bin/python sync_cli.py sync-all >> /var/log/sync.log 2>&1
```

### Using Systemd Timer

Create `/etc/systemd/system/indie-sync.service`:

```ini
[Unit]
Description=IndieStack HubSpot Sync
After=network.target

[Service]
Type=oneshot
User=youruser
WorkingDirectory=/path/to/indie-hubspot-sync
Environment="PATH=/path/to/venv/bin"
ExecStart=/path/to/venv/bin/python sync_cli.py sync-all
```

Create `/etc/systemd/system/indie-sync.timer`:

```ini
[Unit]
Description=Run IndieStack HubSpot Sync Hourly

[Timer]
OnCalendar=hourly
Persistent=true

[Install]
WantedBy=timers.target
```

Enable and start:

```bash
sudo systemctl enable indie-sync.timer
sudo systemctl start indie-sync.timer
```

## Database Schema

### Tracking Database Tables

**sync_objects**: Maps IndieStack records to HubSpot objects
- `entity_type`: contact, company, deal
- `indie_id`: Primary key in IndieStack
- `hubspot_id`: Corresponding HubSpot ID
- `last_synced_at`: Last sync timestamp
- `last_direction`: Direction of last sync

**sync_runs**: Tracks sync operations
- `started_at`, `finished_at`
- `status`: running, success, failed, partial
- `direction`: indie_to_hubspot, hubspot_to_indie, bidirectional
- `summary`: JSON statistics

**sync_errors**: Logs sync errors
- `sync_run_id`: Reference to sync run
- `entity_type`, `indie_id`, `hubspot_id`
- `error_message`: Error details
- `payload`: Full record data for debugging

## Development

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific test file
pytest tests/test_mapping_engine.py
```

### Code Formatting

```bash
# Format code
black app/ tests/

# Check style
flake8 app/ tests/

# Type checking
mypy app/
```

## Troubleshooting

### Common Issues

**1. Authentication Errors**

```
Error: 401 Unauthorized
```

Solution: Verify your `HUBSPOT_PRIVATE_APP_TOKEN` is correct and has the necessary scopes.

**2. Database Connection Errors**

```
Error: could not connect to server
```

Solution: Check your IndieStack database credentials in `.env`.

**3. Missing Field Mappings**

```
Warning: No mapping found for field 'xyz'
```

Solution: Add the field mapping to `config/field_mappings.yaml`.

### Debugging

Enable debug logging:

```bash
# In .env
LOG_LEVEL=DEBUG
LOG_FORMAT=text  # More readable than JSON for debugging
```

View logs in real-time:

```bash
python sync_cli.py sync-all --dry-run 2>&1 | tee sync_debug.log
```

## Security Considerations

1. **Never commit `.env`**: Keep credentials out of version control
2. **Use environment-specific configs**: Separate dev/staging/prod credentials
3. **Rotate tokens regularly**: Update HubSpot tokens periodically
4. **Restrict database access**: Use read-only credentials where possible
5. **Enable HTTPS**: Always use TLS for API communication

## Performance Optimization

For large datasets:

1. **Adjust batch size**:
   ```bash
   SYNC_BATCH_SIZE=500  # Default is 100
   ```

2. **Use incremental syncs**: Only sync records modified since last run
3. **Schedule during off-peak hours**: Run heavy syncs at night
4. **Monitor sync_runs table**: Track duration and optimize slow syncs

## Support

For issues or questions:

1. Check the [docs/](docs/) directory for detailed guides
2. Review sync errors in the tracking database
3. Enable debug logging for more details
4. Check HubSpot API status at status.hubspot.com

## License

Proprietary - All rights reserved
