# Usage Examples

This document provides practical examples for common sync scenarios.

## Table of Contents

1. [First-Time Setup](#first-time-setup)
2. [Basic Sync Operations](#basic-sync-operations)
3. [Advanced Scenarios](#advanced-scenarios)
4. [API Integration](#api-integration)
5. [Troubleshooting](#troubleshooting)

## First-Time Setup

### Complete Setup from Scratch

```bash
# 1. Clone or navigate to the project
cd indie-hubspot-sync

# 2. Create virtual environment
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure environment
cp .env.example .env
nano .env  # Edit with your credentials

# 5. Initialize tracking database
python sync_cli.py init

# 6. Verify configuration
python sync_cli.py config

# 7. Test with dry run
python sync_cli.py sync-contacts --dry-run

# 8. Run actual sync
python sync_cli.py sync-contacts
```

### Setting Up HubSpot Private App

1. Go to HubSpot Settings → Integrations → Private Apps
2. Click "Create private app"
3. Name: "IndieStack Sync Service"
4. Scopes needed:
   - `crm.objects.contacts.read`
   - `crm.objects.contacts.write`
   - `crm.objects.companies.read`
   - `crm.objects.companies.write`
   - `crm.objects.deals.read`
   - `crm.objects.deals.write`
5. Copy the token to `HUBSPOT_PRIVATE_APP_TOKEN` in `.env`

## Basic Sync Operations

### Sync Only New Contacts from IndieStack to HubSpot

This is useful for initial setup or when you want to populate HubSpot with your existing IndieStack contacts.

```bash
python sync_cli.py sync-contacts --direction indie_to_hubspot
```

### Import HubSpot Contacts into IndieStack

If you have existing contacts in HubSpot that aren't in IndieStack:

```bash
python sync_cli.py sync-contacts --direction hubspot_to_indie
```

### Keep Everything in Sync

For ongoing operations, use bidirectional sync:

```bash
# Sync all entity types
python sync_cli.py sync-all --direction bidirectional

# Or sync individually
python sync_cli.py sync-contacts --direction bidirectional
python sync_cli.py sync-companies --direction bidirectional
python sync_cli.py sync-deals --direction bidirectional
```

### Preview Changes Before Applying

Always test with dry run first:

```bash
# See what would change without actually changing it
python sync_cli.py sync-all --dry-run

# Review the output, then run for real
python sync_cli.py sync-all
```

## Advanced Scenarios

### Scenario 1: Initial Migration from HubSpot to IndieStack

You have 10,000 contacts in HubSpot and want to migrate to IndieStack as primary.

```bash
# Step 1: Dry run to see what will be imported
python sync_cli.py sync-contacts --direction hubspot_to_indie --dry-run

# Step 2: Import contacts
python sync_cli.py sync-contacts --direction hubspot_to_indie

# Step 3: Monitor the sync
python sync_cli.py list-runs

# Step 4: Check for errors
python sync_cli.py show-run 1  # Replace 1 with actual run ID

# Step 5: Set up bidirectional sync for ongoing changes
# Edit .env:
DEFAULT_SYNC_DIRECTION=bidirectional
SYNC_CONFLICT_RESOLUTION=indie_wins
```

### Scenario 2: Scheduled Hourly Syncs

Set up automatic syncing every hour.

**Using Cron:**

```bash
# Edit crontab
crontab -e

# Add this line (adjust paths):
0 * * * * cd /path/to/indie-hubspot-sync && /path/to/venv/bin/python sync_cli.py sync-all --direction bidirectional >> /var/log/indie-sync.log 2>&1

# Save and exit
# Verify:
crontab -l
```

**Using Systemd:**

```bash
# Create service file
sudo nano /etc/systemd/system/indie-sync.service

# Add content (see README for full example)

# Create timer file
sudo nano /etc/systemd/system/indie-sync.timer

# Enable and start
sudo systemctl daemon-reload
sudo systemctl enable indie-sync.timer
sudo systemctl start indie-sync.timer

# Check status
sudo systemctl status indie-sync.timer
```

### Scenario 3: Custom Field Mapping

You have custom fields in IndieStack that need to map to HubSpot custom properties.

**Edit `config/field_mappings.yaml`:**

```yaml
contacts:
  properties:
    # Add your custom fields
    nps_score:
      indie_field: custom_fields.nps_score
      hubspot_property: cl_nps_score
      direction: indie_to_hubspot

    last_interaction:
      indie_field: last_interaction_date
      hubspot_property: cl_last_interaction
      direction: bidirectional
      transform: date_to_timestamp
```

**Test the new mappings:**

```bash
# View your mappings
python sync_cli.py show-mappings contacts

# Test with dry run
python sync_cli.py sync-contacts --dry-run

# Run sync
python sync_cli.py sync-contacts
```

### Scenario 4: Handling Sync Errors

Some contacts failed to sync. Here's how to investigate and fix.

```bash
# Step 1: List recent runs to find the failed one
python sync_cli.py list-runs

# Step 2: View details of the failed run
python sync_cli.py show-run 123  # Replace with actual run ID

# Step 3: Check specific error details
# Look at the error messages in the output

# Step 4: Fix the issues
# Common fixes:
# - Update field mappings if fields don't exist
# - Fix data validation issues in source records
# - Ensure HubSpot custom properties exist

# Step 5: Re-run sync
python sync_cli.py sync-contacts
```

### Scenario 5: One-Way Sync for Specific Fields

You want most fields bidirectional, but some fields should only flow one way.

**Example: IndieStack calculates engagement scores, HubSpot should display them**

In `config/field_mappings.yaml`:

```yaml
contacts:
  properties:
    # Bidirectional fields
    first_name:
      indie_field: first_name
      hubspot_property: firstname
      direction: bidirectional

    # One-way field (IndieStack → HubSpot only)
    engagement_score:
      indie_field: details.engagement_score
      hubspot_property: cl_engagement_score
      direction: indie_to_hubspot
```

## API Integration

### Using the REST API

**Start the server:**

```bash
# Development mode (auto-reload)
uvicorn app.api.main:app --reload --port 8000

# Production mode
uvicorn app.api.main:app --host 0.0.0.0 --port 8000 --workers 4
```

### Example API Calls

**Health Check:**

```bash
curl http://localhost:8000/api/v1/health
```

Response:
```json
{
  "status": "healthy",
  "timestamp": "2024-01-15T10:30:00Z",
  "version": "1.0.0"
}
```

**Trigger a Sync:**

```bash
curl -X POST http://localhost:8000/api/v1/sync/run \
  -H "Content-Type: application/json" \
  -d '{
    "entities": ["contacts"],
    "direction": "bidirectional",
    "dry_run": false
  }'
```

Response:
```json
{
  "sync_run_id": 124,
  "results": {
    "contacts": {
      "created": 15,
      "updated": 42,
      "skipped": 3,
      "errors": 0
    }
  },
  "message": "Sync completed: 15 created, 42 updated, 0 errors"
}
```

**Get Sync Statistics:**

```bash
curl http://localhost:8000/api/v1/sync/stats
```

Response:
```json
{
  "total_runs": 50,
  "successful_runs": 48,
  "total_errors": 12,
  "synced_objects": {
    "contacts": 1523,
    "companies": 342,
    "deals": 89,
    "total": 1954
  },
  "last_sync": {
    "id": 50,
    "started_at": "2024-01-15T09:00:00Z",
    "status": "success",
    "direction": "bidirectional"
  }
}
```

**List Recent Sync Runs:**

```bash
curl "http://localhost:8000/api/v1/sync/runs?limit=5&offset=0"
```

**Get Sync Run Details:**

```bash
curl http://localhost:8000/api/v1/sync/runs/124
```

### Python Client Example

```python
import requests

BASE_URL = "http://localhost:8000/api/v1"

def trigger_sync(entities=["contacts"], direction="bidirectional", dry_run=False):
    """Trigger a sync operation."""
    response = requests.post(
        f"{BASE_URL}/sync/run",
        json={
            "entities": entities,
            "direction": direction,
            "dry_run": dry_run,
        }
    )
    return response.json()

def get_sync_stats():
    """Get sync statistics."""
    response = requests.get(f"{BASE_URL}/sync/stats")
    return response.json()

# Usage
result = trigger_sync(entities=["contacts", "companies"])
print(f"Created: {result['results']['contacts']['created']}")
print(f"Updated: {result['results']['contacts']['updated']}")

stats = get_sync_stats()
print(f"Total synced objects: {stats['synced_objects']['total']}")
```

### JavaScript/Node.js Client Example

```javascript
const axios = require('axios');

const BASE_URL = 'http://localhost:8000/api/v1';

async function triggerSync(entities = ['contacts'], direction = 'bidirectional', dryRun = false) {
  const response = await axios.post(`${BASE_URL}/sync/run`, {
    entities,
    direction,
    dry_run: dryRun
  });
  return response.data;
}

async function getSyncStats() {
  const response = await axios.get(`${BASE_URL}/sync/stats`);
  return response.data;
}

// Usage
(async () => {
  const result = await triggerSync(['contacts', 'companies']);
  console.log(`Created: ${result.results.contacts.created}`);
  console.log(`Updated: ${result.results.contacts.updated}`);

  const stats = await getSyncStats();
  console.log(`Total synced objects: ${stats.synced_objects.total}`);
})();
```

## Troubleshooting

### Debug a Failed Sync

```bash
# 1. Enable debug logging
# Edit .env:
LOG_LEVEL=DEBUG
LOG_FORMAT=text

# 2. Run sync with output to file
python sync_cli.py sync-contacts --dry-run 2>&1 | tee debug.log

# 3. Review the log
less debug.log

# 4. Check for specific errors
grep -i error debug.log
grep -i warning debug.log
```

### Verify Field Mappings

```bash
# Show all mappings
python sync_cli.py show-mappings

# Show specific entity
python sync_cli.py show-mappings contacts

# Test mapping with one record
python sync_cli.py sync-contacts --dry-run
```

### Check Database State

```bash
# Connect to tracking database
sqlite3 sync_tracking.db

# List all synced contacts
SELECT * FROM sync_objects WHERE entity_type = 'contact' LIMIT 10;

# Find contacts with errors
SELECT so.*
FROM sync_objects so
JOIN sync_errors se ON se.indie_id = so.indie_id
WHERE so.entity_type = 'contact';

# View recent sync runs
SELECT * FROM sync_runs ORDER BY started_at DESC LIMIT 10;

# Exit
.quit
```

### Reset and Start Fresh

```bash
# 1. Backup existing tracking database
cp sync_tracking.db sync_tracking.db.backup

# 2. Remove tracking database
rm sync_tracking.db

# 3. Reinitialize
python sync_cli.py init

# 4. Run fresh sync
python sync_cli.py sync-all --dry-run
python sync_cli.py sync-all
```

### Common Error Solutions

**Error: "401 Unauthorized"**
```bash
# Solution: Check HubSpot token
python sync_cli.py config
# Verify HUBSPOT_PRIVATE_APP_TOKEN is correct
# Regenerate token in HubSpot if needed
```

**Error: "Field 'xyz' does not exist"**
```bash
# Solution: Add custom property to HubSpot or update mapping
# 1. Go to HubSpot Settings → Properties
# 2. Create the custom property (e.g., cl_engagement_score)
# 3. Update field_mappings.yaml if needed
```

**Error: "Database connection refused"**
```bash
# Solution: Check IndieStack database settings
python sync_cli.py config
# Verify:
# - INDIE_DB_HOST is correct
# - INDIE_DB_PORT is correct (usually 5432)
# - Database is running and accessible
# Test connection:
psql -h localhost -U indie_user -d indie_crm
```

## Performance Tips

### For Large Datasets (10,000+ records)

```bash
# 1. Increase batch size
# Edit .env:
SYNC_BATCH_SIZE=500

# 2. Run syncs during off-peak hours
# Schedule for 2 AM:
0 2 * * * cd /path/to/indie-hubspot-sync && /path/to/venv/bin/python sync_cli.py sync-all

# 3. Sync entities separately to spread load
python sync_cli.py sync-contacts
sleep 300  # Wait 5 minutes
python sync_cli.py sync-companies
sleep 300
python sync_cli.py sync-deals
```

### Monitor Performance

```bash
# Time a sync operation
time python sync_cli.py sync-contacts

# View sync duration in database
sqlite3 sync_tracking.db
SELECT
  id,
  started_at,
  finished_at,
  (julianday(finished_at) - julianday(started_at)) * 86400 as duration_seconds
FROM sync_runs
ORDER BY started_at DESC
LIMIT 10;
```

## Best Practices

1. **Always test with dry run first**
   ```bash
   python sync_cli.py sync-all --dry-run
   ```

2. **Monitor sync runs regularly**
   ```bash
   python sync_cli.py list-runs
   ```

3. **Set up alerts for failures**
   ```bash
   # Check for failed runs in cron job
   # Add to cron script:
   FAILED=$(sqlite3 sync_tracking.db "SELECT COUNT(*) FROM sync_runs WHERE status='failed' AND started_at > datetime('now', '-1 hour')")
   if [ "$FAILED" -gt 0 ]; then
       echo "Sync failures detected!" | mail -s "Sync Alert" admin@example.com
   fi
   ```

4. **Keep field mappings in version control**
   ```bash
   git add config/field_mappings.yaml
   git commit -m "Update field mappings for new custom fields"
   ```

5. **Document custom configurations**
   - Keep notes on why certain fields are one-way
   - Document custom transformations
   - Maintain changelog for mapping updates
