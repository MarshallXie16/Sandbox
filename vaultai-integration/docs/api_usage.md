# VaultAI API Usage Guide

## Authentication

All API endpoints require authentication via API key header:

```bash
X-VaultAI-API-Key: your_api_key_here
```

Configure API keys in `.env`:
```env
VAULTAI_API_KEYS=key1,key2,key3
```

## Base URL

```
http://localhost:8010/api/v1/vaultai
```

## Exit Ready Endpoints

### Generate Investment Teaser

**Endpoint**: `POST /exit-ready/teaser`

**Description**: Generate a professional investment teaser for a company.

**Request**:
```json
{
  "company_name": "Acme Corporation",
  "industry": "SaaS",
  "revenue": 50.0,
  "ebitda": 15.0,
  "year_founded": 2015,
  "employees": 120,
  "description": "Leading provider of cloud-based workflow automation for enterprises",
  "unique_selling_points": [
    "98% customer retention rate",
    "Proprietary AI engine",
    "100% recurring revenue model"
  ],
  "additional_context": "Recently expanded to EU market"
}
```

**Response**:
```json
{
  "teaser": "Acme Corporation is a leading SaaS provider...",
  "word_count": 285,
  "pii_detected": {}
}
```

**Example**:
```bash
curl -X POST http://localhost:8010/api/v1/vaultai/exit-ready/teaser \
  -H "X-VaultAI-API-Key: your_key" \
  -H "Content-Type: application/json" \
  -d @teaser_request.json
```

### Generate Exit Readiness Checklist

**Endpoint**: `POST /exit-ready/checklist`

**Description**: Create a comprehensive exit readiness checklist.

**Request**:
```json
{
  "company_name": "Acme Corporation",
  "industry": "SaaS",
  "revenue": 50.0,
  "exit_timeline_months": 18,
  "current_challenges": [
    "Need to improve gross margins",
    "Customer concentration risk"
  ]
}
```

**Response**:
```json
{
  "checklist": [
    {
      "category": "Financial",
      "item": "Audit financial statements for last 3 years",
      "priority": "High",
      "estimated_time": "4 weeks"
    },
    {
      "category": "Legal",
      "item": "Review and update all customer contracts",
      "priority": "High",
      "estimated_time": "6 weeks"
    }
  ],
  "summary": "Company is moderately prepared for exit with key gaps in financial audits and legal documentation"
}
```

### Summarize Exit Ready Data

**Endpoint**: `POST /exit-ready/summary`

**Description**: Summarize exit readiness data and provide insights.

**Request**:
```json
{
  "company_name": "Acme Corporation",
  "data": {
    "financial_score": 85,
    "legal_score": 72,
    "operational_score": 90,
    "strategic_score": 78
  },
  "focus_areas": ["financial", "legal"]
}
```

**Response**:
```json
{
  "summary": "Acme Corporation shows strong operational readiness...",
  "key_findings": [
    "Financial documentation is mostly complete",
    "Legal structure needs review",
    "Strong operational metrics"
  ],
  "recommendations": [
    "Complete financial audit by Q2",
    "Engage legal counsel for contract review",
    "Document key operational processes"
  ]
}
```

## Facilitator Endpoints

### Draft Facilitation Message

**Endpoint**: `POST /facilitator/draft-message`

**Description**: Draft a professional facilitation message for deal negotiations.

**Request**:
```json
{
  "context": "Buyer has submitted LOI at $100M valuation, seller counter-offered at $120M",
  "message_type": "update",
  "recipient_role": "buyer",
  "key_points": [
    "Seller has reviewed the LOI",
    "Counter-offer submitted at $120M",
    "Request for meeting to discuss valuation gap"
  ],
  "tone": "professional"
}
```

**Response**:
```json
{
  "message": "Dear [Buyer],\n\nThank you for your Letter of Intent...",
  "word_count": 156,
  "pii_detected": {}
}
```

### Summarize Negotiation

**Endpoint**: `POST /facilitator/summarize`

**Description**: Summarize negotiation progress and extract action items.

**Request**:
```json
{
  "deal_id": "DEAL-2025-001",
  "conversation_history": [
    {
      "role": "buyer",
      "content": "We're interested at $100M valuation"
    },
    {
      "role": "seller",
      "content": "Our minimum is $120M based on recent comps"
    },
    {
      "role": "buyer",
      "content": "Can we meet in the middle at $110M?"
    }
  ],
  "focus": "valuation"
}
```

**Response**:
```json
{
  "summary": "Negotiation centered on valuation gap between buyer's $100M and seller's $120M...",
  "key_points": [
    "Initial bid: $100M",
    "Seller minimum: $120M",
    "Buyer counter: $110M"
  ],
  "action_items": [
    "Schedule valuation discussion meeting",
    "Prepare comparable transaction analysis",
    "Review financial projections"
  ],
  "sentiment": "neutral"
}
```

## CRM Endpoints

### Find Matches

**Endpoint**: `POST /crm/match`

**Description**: AI-powered matching of buyers and sellers.

**Request**:
```json
{
  "entity_type": "buyer",
  "entity_data": {
    "name": "Strategic Acquirer Inc",
    "target_industries": ["SaaS", "FinTech"],
    "revenue_range": [20, 100],
    "geography": ["US", "Canada"]
  },
  "candidate_pool": [
    {
      "id": "SELLER-001",
      "name": "CloudTech Solutions",
      "industry": "SaaS",
      "revenue": 45,
      "location": "California, US"
    },
    {
      "id": "SELLER-002",
      "name": "PaymentPro",
      "industry": "FinTech",
      "revenue": 30,
      "location": "New York, US"
    }
  ]
}
```

**Response**:
```json
{
  "matches": [
    {
      "entity_id": "SELLER-001",
      "score": 0.92,
      "reasoning": "Strong strategic fit in SaaS, revenue in target range, US-based",
      "strengths": [
        "Industry alignment",
        "Revenue within target range",
        "Geographic proximity"
      ],
      "concerns": [
        "Verify customer concentration"
      ]
    }
  ],
  "total_evaluated": 2
}
```

### Enrich Profile

**Endpoint**: `POST /crm/enrich`

**Description**: Enrich entity profile with AI-generated insights.

**Request**:
```json
{
  "entity_id": "BUYER-123",
  "entity_data": {
    "name": "Strategic Acquirer Inc",
    "industry": "Private Equity",
    "aum": 5000,
    "investment_focus": ["SaaS", "B2B"],
    "recent_acquisitions": 3
  },
  "enrichment_type": "insights"
}
```

**Response**:
```json
{
  "enriched_data": {
    "acquisition_capacity": "high",
    "target_profile": "mid-market SaaS companies",
    "deal_pace": "active"
  },
  "insights": [
    "Frequent acquirer with 3 deals in last 12 months",
    "Strong focus on B2B SaaS segment",
    "Well-capitalized with $5B AUM"
  ],
  "recommendations": [
    "Prioritize SaaS deal flow",
    "Consider companies in $20-100M revenue range",
    "Highlight operational value-add capabilities"
  ]
}
```

## Analytics Endpoints

### Generate Insights

**Endpoint**: `POST /analytics/insights`

**Description**: Generate insights from analytics data.

**Request**:
```json
{
  "data_type": "deals",
  "data": {
    "total_deals": 45,
    "closed_deals": 12,
    "avg_deal_size": 50000000,
    "avg_time_to_close": 180,
    "conversion_rate": 0.27
  },
  "time_period": "2024-Q4",
  "focus_areas": ["conversion", "timeline"]
}
```

**Response**:
```json
{
  "insights": [
    "Conversion rate of 27% is above industry average",
    "Average deal cycle of 180 days indicates efficient process",
    "Deal sizes trending upward in Q4"
  ],
  "trends": [
    "Increased deal velocity compared to Q3",
    "Higher average deal values"
  ],
  "recommendations": [
    "Document best practices from high-converting deals",
    "Consider strategies to reduce time-to-close further",
    "Maintain focus on larger deal sizes"
  ],
  "summary": "Strong Q4 performance with above-average conversion rates..."
}
```

### Generate Report

**Endpoint**: `POST /analytics/report`

**Description**: Generate formatted analytics reports.

**Request**:
```json
{
  "report_type": "quarterly",
  "data": {
    "deals_closed": 12,
    "revenue": 600000000,
    "new_users": 150,
    "engagement_score": 8.5
  },
  "sections": [
    "executive_summary",
    "key_metrics",
    "trends",
    "recommendations"
  ],
  "format": "markdown"
}
```

**Response**:
```json
{
  "report": "# Q4 2024 Analytics Report\n\n## Executive Summary\n...",
  "format": "markdown",
  "word_count": 850
}
```

### Explain Metric

**Endpoint**: `POST /analytics/explain`

**Description**: Explain a metric or trend in plain language.

**Request**:
```json
{
  "metric_name": "Customer Acquisition Cost (CAC)",
  "current_value": 1500,
  "historical_values": [1200, 1300, 1400, 1500],
  "context": {
    "industry": "SaaS",
    "company_size": "mid-market"
  }
}
```

**Response**:
```json
{
  "explanation": "Customer Acquisition Cost (CAC) is the total cost to acquire a new customer...",
  "interpretation": "Your CAC of $1,500 is trending upward and slightly above mid-market SaaS benchmarks...",
  "factors": [
    "Increasing marketing spend",
    "Higher competition in target market",
    "Expanding into new segments"
  ],
  "suggestions": [
    "Optimize marketing channel mix",
    "Improve conversion funnel",
    "Consider account-based marketing for efficiency"
  ]
}
```

## Error Responses

### 401 Unauthorized

```json
{
  "detail": "Missing API key. Provide X-VaultAI-API-Key header."
}
```

### 422 Validation Error

```json
{
  "detail": [
    {
      "loc": ["body", "company_name"],
      "msg": "field required",
      "type": "value_error.missing"
    }
  ]
}
```

### 500 Internal Server Error

```json
{
  "error": "Internal Server Error",
  "message": "LLM request failed after 3 attempts"
}
```

## Rate Limiting

Default rate limits (configurable):
- 60 requests per minute per API key
- 1000 requests per hour per API key

Exceeded rate limit response:
```json
{
  "error": "rate_limit_exceeded",
  "message": "Rate limit exceeded. Try again in 30 seconds."
}
```

## Best Practices

### 1. Handle Errors Gracefully

```python
try:
    response = requests.post(
        "http://localhost:8010/api/v1/vaultai/exit-ready/teaser",
        headers={"X-VaultAI-API-Key": API_KEY},
        json=payload,
        timeout=30,
    )
    response.raise_for_status()
    data = response.json()
except requests.HTTPError as e:
    logger.error(f"API error: {e.response.status_code}")
except requests.Timeout:
    logger.error("Request timeout")
```

### 2. Use Timeouts

LLM requests can take 1-5 seconds. Set appropriate timeouts:

```python
response = requests.post(url, json=data, timeout=30)
```

### 3. Monitor PII Detection

Check `pii_detected` in responses and act accordingly:

```python
if response["pii_detected"]:
    logger.warning(f"PII detected: {response['pii_detected']}")
```

### 4. Batch When Possible

For analytics and reporting, batch multiple data points:

```python
# Instead of multiple calls
for metric in metrics:
    analyze(metric)

# Batch into single report request
report = generate_report(all_metrics)
```

### 5. Cache Results

LLM responses for static data can be cached:

```python
from functools import lru_cache

@lru_cache(maxsize=100)
def get_teaser(company_name, revenue, ...):
    return call_vaultai_api(...)
```

## Python Client Example

```python
import requests
from typing import Dict, Any

class VaultAIClient:
    def __init__(self, api_key: str, base_url: str = "http://localhost:8010"):
        self.api_key = api_key
        self.base_url = base_url
        self.headers = {
            "X-VaultAI-API-Key": api_key,
            "Content-Type": "application/json",
        }

    def generate_teaser(self, company_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate investment teaser."""
        response = requests.post(
            f"{self.base_url}/api/v1/vaultai/exit-ready/teaser",
            headers=self.headers,
            json=company_data,
            timeout=30,
        )
        response.raise_for_status()
        return response.json()

    def draft_message(self, message_data: Dict[str, Any]) -> Dict[str, Any]:
        """Draft facilitation message."""
        response = requests.post(
            f"{self.base_url}/api/v1/vaultai/facilitator/draft-message",
            headers=self.headers,
            json=message_data,
            timeout=30,
        )
        response.raise_for_status()
        return response.json()

# Usage
client = VaultAIClient(api_key="your_key")

teaser = client.generate_teaser({
    "company_name": "Acme Corp",
    "industry": "SaaS",
    "revenue": 50,
    "description": "...",
})

print(teaser["teaser"])
```

## Interactive API Documentation

Visit `http://localhost:8010/docs` for:
- Interactive Swagger UI
- Try endpoints directly in browser
- View request/response schemas
- See all available parameters

---

For more examples, see the `/examples` directory in the repository.
