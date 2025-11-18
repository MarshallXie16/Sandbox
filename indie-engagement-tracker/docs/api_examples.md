# API Examples

This document provides comprehensive examples for using the Engagement Tracker REST API.

## Base URL

```
http://localhost:8001/api/v1
```

## Health Check

### Check API Health

```bash
curl http://localhost:8001/api/v1/health
```

**Response:**
```json
{
  "status": "healthy",
  "service": "engagement-tracker"
}
```

## Scoring Profiles

### Create Scoring Profile

```bash
curl -X POST http://localhost:8001/api/v1/profiles \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Sales-Focused",
    "description": "Emphasizes deal activities and meetings",
    "rules": {
      "event_weights": {
        "email_sent": 1.0,
        "email_open": 3.0,
        "email_click": 5.0,
        "call": 10.0,
        "meeting": 25.0,
        "deal_created": 30.0,
        "deal_stage_change": 20.0,
        "deal_won": 100.0
      },
      "time_decay": {
        "enabled": true,
        "decay_days": 60,
        "decay_factor": 0.3
      }
    },
    "is_default": false
  }'
```

**Response:**
```json
{
  "id": 2,
  "name": "Sales-Focused",
  "description": "Emphasizes deal activities and meetings",
  "rules": {
    "event_weights": {...},
    "time_decay": {...}
  },
  "is_default": false,
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-01-15T10:30:00Z"
}
```

### List All Profiles

```bash
curl http://localhost:8001/api/v1/profiles
```

**Response:**
```json
[
  {
    "id": 1,
    "name": "Default",
    "description": "Default scoring profile",
    "rules": {...},
    "is_default": true,
    "created_at": "2024-01-01T00:00:00Z",
    "updated_at": "2024-01-01T00:00:00Z"
  },
  {
    "id": 2,
    "name": "Sales-Focused",
    "description": "Emphasizes deal activities",
    "rules": {...},
    "is_default": false,
    "created_at": "2024-01-15T10:30:00Z",
    "updated_at": "2024-01-15T10:30:00Z"
  }
]
```

### Get Specific Profile

```bash
curl http://localhost:8001/api/v1/profiles/1
```

### Update Profile

```bash
curl -X PATCH http://localhost:8001/api/v1/profiles/2 \
  -H "Content-Type: application/json" \
  -d '{
    "description": "Updated description",
    "is_default": true
  }'
```

### Delete Profile

```bash
curl -X DELETE http://localhost:8001/api/v1/profiles/2
```

## Event Ingestion

### Test Source Connections

```bash
curl http://localhost:8001/api/v1/ingest/test-connections
```

**Response:**
```json
{
  "sources": {
    "EmailEngineSource": true,
    "IndieCrmActivitySource": true
  },
  "all_ok": true
}
```

### Run Event Ingestion

Basic ingestion:

```bash
curl -X POST http://localhost:8001/api/v1/ingest/run \
  -H "Content-Type: application/json" \
  -d '{}'
```

With filters:

```bash
curl -X POST http://localhost:8001/api/v1/ingest/run \
  -H "Content-Type: application/json" \
  -d '{
    "since": "2024-01-01T00:00:00Z",
    "limit": 1000,
    "dry_run": false
  }'
```

Dry run (don't save):

```bash
curl -X POST http://localhost:8001/api/v1/ingest/run \
  -H "Content-Type: application/json" \
  -d '{
    "dry_run": true
  }'
```

**Response:**
```json
{
  "total_fetched": 1523,
  "total_new": 1498,
  "total_duplicates": 25,
  "total_errors": 0,
  "dry_run": false,
  "sources": {
    "EmailEngineSource": {
      "fetched": 856,
      "new": 842,
      "duplicates": 14,
      "errors": 0
    },
    "IndieCrmActivitySource": {
      "fetched": 667,
      "new": 656,
      "duplicates": 11,
      "errors": 0
    }
  }
}
```

## Score Calculation

### Recalculate All Scores

Basic recalculation:

```bash
curl -X POST http://localhost:8001/api/v1/scores/recalculate \
  -H "Content-Type: application/json" \
  -d '{}'
```

With specific profile:

```bash
curl -X POST http://localhost:8001/api/v1/scores/recalculate \
  -H "Content-Type: application/json" \
  -d '{
    "profile_id": 2
  }'
```

Filter by entity type:

```bash
curl -X POST http://localhost:8001/api/v1/scores/recalculate \
  -H "Content-Type: application/json" \
  -d '{
    "entity_type": "contact",
    "min_events": 5
  }'
```

**Response:**
```json
{
  "total_entities": 1250,
  "recalculated": 1180,
  "skipped": 70,
  "errors": 0
}
```

## Score Queries

### Get Top Contacts

Basic query:

```bash
curl "http://localhost:8001/api/v1/scores/top-contacts?limit=10"
```

With filters:

```bash
curl "http://localhost:8001/api/v1/scores/top-contacts?limit=50&min_score=20&entity_type=contact"
```

With activity filter:

```bash
curl "http://localhost:8001/api/v1/scores/top-contacts?limit=20&since=2024-01-01T00:00:00Z"
```

**Response:**
```json
{
  "entities": [
    {
      "id": 42,
      "external_id": "contact_123",
      "entity_type": "contact",
      "latest_score": 87.5,
      "score_breakdown": {
        "total_events": 45,
        "by_event_type": {
          "email_sent": 12.0,
          "email_open": 27.0,
          "email_click": 15.0,
          "meeting": 30.0,
          "call": 16.0
        },
        "by_source": {
          "indie_crm": 46.0,
          "email_engine": 54.0
        },
        "time_decay_applied": true,
        "decayed_events": 8,
        "total_score": 87.5
      },
      "last_activity_at": "2024-01-14T15:30:00Z",
      "created_at": "2024-01-01T00:00:00Z",
      "updated_at": "2024-01-15T10:00:00Z"
    },
    ...
  ],
  "total": 10
}
```

### Get Contact Detail

```bash
curl "http://localhost:8001/api/v1/scores/contact/contact_123?entity_type=contact"
```

**Response:**
```json
{
  "entity": {
    "id": 42,
    "external_id": "contact_123",
    "entity_type": "contact",
    "latest_score": 87.5,
    "score_breakdown": {...},
    "last_activity_at": "2024-01-14T15:30:00Z",
    "created_at": "2024-01-01T00:00:00Z",
    "updated_at": "2024-01-15T10:00:00Z"
  },
  "recent_events": [
    {
      "id": 1523,
      "external_id": "contact_123",
      "entity_type": "contact",
      "source_system": "indie_crm",
      "event_type": "meeting",
      "weight": 15.0,
      "metadata": {
        "activity_id": 789,
        "activity_type": "meeting",
        "details": "Product demo"
      },
      "occurred_at": "2024-01-14T15:30:00Z",
      "ingested_at": "2024-01-14T16:00:00Z"
    },
    ...
  ],
  "score_history": [
    {
      "score_value": 87.5,
      "calculated_at": "2024-01-15T10:00:00Z",
      "components": {...}
    },
    {
      "score_value": 72.5,
      "calculated_at": "2024-01-10T10:00:00Z",
      "components": {...}
    }
  ]
}
```

### Get Deal Score

```bash
curl "http://localhost:8001/api/v1/scores/contact/deal_456?entity_type=deal"
```

## Statistics

### Get Overall Statistics

```bash
curl http://localhost:8001/api/v1/stats
```

**Response:**
```json
{
  "total_entities": 1250,
  "total_events": 15678,
  "average_score": 34.56,
  "by_entity_type": {
    "contact": 1100,
    "company": 50,
    "deal": 100
  },
  "active_last_30_days": 842
}
```

## Python Client Example

Here's a Python client example using `requests`:

```python
import requests
from datetime import datetime

BASE_URL = "http://localhost:8001/api/v1"

class EngagementTrackerClient:
    def __init__(self, base_url=BASE_URL):
        self.base_url = base_url

    def get_top_contacts(self, limit=50, min_score=None):
        params = {"limit": limit}
        if min_score:
            params["min_score"] = min_score

        response = requests.get(f"{self.base_url}/scores/top-contacts", params=params)
        response.raise_for_status()
        return response.json()

    def trigger_ingestion(self, since=None, dry_run=False):
        payload = {"dry_run": dry_run}
        if since:
            payload["since"] = since.isoformat()

        response = requests.post(f"{self.base_url}/ingest/run", json=payload)
        response.raise_for_status()
        return response.json()

    def recalculate_scores(self, profile_id=None, entity_type=None):
        payload = {}
        if profile_id:
            payload["profile_id"] = profile_id
        if entity_type:
            payload["entity_type"] = entity_type

        response = requests.post(f"{self.base_url}/scores/recalculate", json=payload)
        response.raise_for_status()
        return response.json()

    def get_contact_detail(self, external_id, entity_type="contact"):
        response = requests.get(
            f"{self.base_url}/scores/contact/{external_id}",
            params={"entity_type": entity_type}
        )
        response.raise_for_status()
        return response.json()

# Usage
client = EngagementTrackerClient()

# Get top 10 contacts
top_contacts = client.get_top_contacts(limit=10)
for entity in top_contacts["entities"]:
    print(f"{entity['external_id']}: {entity['latest_score']}")

# Trigger ingestion
result = client.trigger_ingestion()
print(f"Ingested {result['total_new']} new events")

# Recalculate scores
result = client.recalculate_scores(entity_type="contact")
print(f"Recalculated {result['recalculated']} entities")
```

## JavaScript/TypeScript Client Example

```typescript
class EngagementTrackerClient {
  private baseUrl: string;

  constructor(baseUrl: string = "http://localhost:8001/api/v1") {
    this.baseUrl = baseUrl;
  }

  async getTopContacts(limit: number = 50, minScore?: number) {
    const params = new URLSearchParams({ limit: limit.toString() });
    if (minScore) params.append("min_score", minScore.toString());

    const response = await fetch(
      `${this.baseUrl}/scores/top-contacts?${params}`
    );
    return response.json();
  }

  async triggerIngestion(since?: Date, dryRun: boolean = false) {
    const payload: any = { dry_run: dryRun };
    if (since) payload.since = since.toISOString();

    const response = await fetch(`${this.baseUrl}/ingest/run`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    return response.json();
  }

  async recalculateScores(profileId?: number, entityType?: string) {
    const payload: any = {};
    if (profileId) payload.profile_id = profileId;
    if (entityType) payload.entity_type = entityType;

    const response = await fetch(`${this.baseUrl}/scores/recalculate`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    return response.json();
  }
}

// Usage
const client = new EngagementTrackerClient();

// Get top contacts
const topContacts = await client.getTopContacts(10);
console.log(topContacts);

// Trigger ingestion
const result = await client.triggerIngestion();
console.log(`Ingested ${result.total_new} new events`);
```

## Error Handling

The API uses standard HTTP status codes:

- **200 OK**: Request succeeded
- **201 Created**: Resource created
- **204 No Content**: Successful deletion
- **400 Bad Request**: Invalid request parameters
- **404 Not Found**: Resource not found
- **500 Internal Server Error**: Server error

Error responses include details:

```json
{
  "detail": "Profile not found"
}
```

## Rate Limiting

Currently no rate limiting is implemented. For production use, consider:
- Implementing rate limiting middleware
- Using API keys for authentication
- Monitoring usage patterns

## Best Practices

1. **Use pagination** for large result sets
2. **Cache results** when appropriate
3. **Handle errors** gracefully
4. **Use dry-run** for testing
5. **Monitor ingestion** for errors
6. **Regular score recalculation** after bulk ingestion
