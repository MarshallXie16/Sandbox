# API Usage Guide

## Authentication

All analytics API endpoints require authentication using an API key.

### Setting API Key

Pass the API key in the `X-API-Key` header:

```bash
curl -H "X-API-Key: your-secret-key" \
  http://localhost:8008/api/v1/analytics/exit-ready/pipeline
```

## Base URL

Development: `http://localhost:8008`
Production: Configure based on deployment

## Endpoints

### Health Check

#### GET `/api/v1/health`

Check service health and version.

**Authentication:** Not required

**Response:**
```json
{
  "status": "ok",
  "version": "1.0.0",
  "env": "dev"
}
```

## Exit Ready Analytics

### GET `/api/v1/analytics/exit-ready/pipeline`

Get Exit Ready pipeline summary with case counts by status.

**Response:**
```json
{
  "total_cases": 42,
  "by_status": {
    "created": 3,
    "intake_pending": 5,
    "docs_collecting": 7,
    "valuation_done": 10,
    "report_ready": 4,
    "delivered": 9,
    "closed": 4
  }
}
```

### GET `/api/v1/analytics/exit-ready/durations`

Get average durations between stages.

**Response:**
```json
{
  "durations": [
    {
      "stage": "created_to_intake",
      "average_days": 5.2,
      "median_days": 4.0,
      "min_days": 1,
      "max_days": 15,
      "sample_size": 38
    },
    ...
  ]
}
```

### GET `/api/v1/analytics/exit-ready/volume`

Get case volume over time.

**Query Parameters:**
- `period` (string): "month" or "quarter" (default: "month")
- `from` (string): Start date YYYY-MM-DD (optional)
- `to` (string): End date YYYY-MM-DD (optional)

**Example:**
```bash
curl -H "X-API-Key: your-key" \
  "http://localhost:8008/api/v1/analytics/exit-ready/volume?period=month&from=2025-01-01&to=2025-03-31"
```

**Response:**
```json
{
  "period_type": "month",
  "data": [
    {
      "period": "2025-01",
      "created": 12,
      "delivered": 8,
      "closed": 5
    },
    {
      "period": "2025-02",
      "created": 15,
      "delivered": 10,
      "closed": 7
    }
  ]
}
```

## Facilitator Analytics

### GET `/api/v1/analytics/facilitator/engagements`

Get engagement status summary.

**Response:**
```json
{
  "total_engagements": 28,
  "by_status": {
    "draft": 2,
    "active": 8,
    "outreach_in_progress": 6,
    "offers_in_play": 4,
    "closed_success": 5,
    "closed_no_deal": 3
  }
}
```

### GET `/api/v1/analytics/facilitator/revenue`

Get revenue summary.

**Query Parameters:**
- `from` (string): Start date YYYY-MM-DD (optional)
- `to` (string): End date YYYY-MM-DD (optional)

**Example:**
```bash
curl -H "X-API-Key: your-key" \
  "http://localhost:8008/api/v1/analytics/facilitator/revenue?from=2025-01-01&to=2025-01-31"
```

**Response:**
```json
{
  "total_offer_fees": 25000.00,
  "total_success_fee_gross": 450000.00,
  "total_success_fee_net": 425000.00,
  "total_revenue": 450000.00,
  "closed_success_count": 5,
  "period_from": "2025-01-01",
  "period_to": "2025-01-31"
}
```

### GET `/api/v1/analytics/facilitator/funnel`

Get buyer introduction funnel.

**Response:**
```json
{
  "total_introduced_buyers": 150,
  "funnel_stages": [
    {
      "stage": "introduced",
      "count": 150,
      "conversion_rate": null
    },
    {
      "stage": "nda_signed",
      "count": 95,
      "conversion_rate": 63.3
    },
    {
      "stage": "teaser_sent",
      "count": 80,
      "conversion_rate": 84.2
    },
    {
      "stage": "info_access",
      "count": 45,
      "conversion_rate": 56.3
    },
    {
      "stage": "offer",
      "count": 18,
      "conversion_rate": 40.0
    },
    {
      "stage": "closing",
      "count": 5,
      "conversion_rate": 27.8
    }
  ]
}
```

## CRM Analytics

### GET `/api/v1/analytics/crm/overview`

Get CRM overview statistics.

**Response:**
```json
{
  "total_contacts": 1250,
  "total_sellers": 450,
  "total_buyers": 800,
  "total_companies": 380,
  "total_listings": 125,
  "active_listings": 68,
  "listings_by_status": {
    "active": 68,
    "under_negotiation": 22,
    "sold": 15,
    "withdrawn": 10,
    "expired": 10
  }
}
```

## Error Responses

### 401 Unauthorized

Missing or invalid API key.

```json
{
  "detail": "Invalid API key"
}
```

### 500 Internal Server Error

Server error or database connection issue.

```json
{
  "detail": "Internal server error"
}
```

## Rate Limiting

Currently no rate limiting is enforced. Consider implementing rate limiting in production.

## Best Practices

1. **Cache responses** where appropriate to reduce load
2. **Use date filters** to limit data volume
3. **Handle errors gracefully** with retry logic
4. **Secure API keys** and rotate regularly
5. **Monitor usage** to detect anomalies
