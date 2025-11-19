# API Usage Guide

## Authentication

All API endpoints require authentication via API key in the `X-API-Key` header:

```bash
curl -H "X-API-Key: your-api-key-here" http://localhost:8080/api/v1/health
```

Configure API keys in `.env`:
```
FACILITATOR_API_KEYS=key1,key2,key3
```

## Base URL

- Development: `http://localhost:8080`
- API prefix: `/api/v1`

## Endpoints

### Health Check

**GET** `/api/v1/health`

Check service status.

**Response:**
```json
{
  "status": "ok",
  "service": "facilitator-automation",
  "version": "1.0.0",
  "environment": "dev",
  "timestamp": "2025-01-19T12:00:00"
}
```

---

## Engagements

### Create Engagement

**POST** `/api/v1/facilitator/engagements`

Create a new facilitator engagement.

**Request:**
```json
{
  "seller_contact_id": 123,
  "company_id": 456,
  "listing_id": 789,
  "offer_fee_fixed": 5000,
  "success_fee_rate": 0.05,
  "currency": "CAD",
  "notes": "Phase 2 engagement for XYZ Corp"
}
```

**Response:** `201 Created`
```json
{
  "id": 1,
  "engagement_code": "FAC-2025-0001",
  "status": "draft",
  "seller_contact_id": 123,
  "company_id": 456,
  "listing_id": 789,
  "offer_fee_fixed": 5000.00,
  "success_fee_rate": 0.05,
  "currency": "CAD",
  "created_at": "2025-01-19T12:00:00",
  "updated_at": "2025-01-19T12:00:00"
}
```

### List Engagements

**GET** `/api/v1/facilitator/engagements?status=active&skip=0&limit=100`

List engagements with optional filters.

**Query Parameters:**
- `status` (optional): Filter by status (draft, active, closed_success, etc.)
- `seller_contact_id` (optional): Filter by seller
- `skip` (optional, default=0): Pagination offset
- `limit` (optional, default=100, max=1000): Page size

### Get Engagement

**GET** `/api/v1/facilitator/engagements/{engagement_id}`

Get single engagement by ID.

### Get Engagement Summary

**GET** `/api/v1/facilitator/engagements/{engagement_id}/summary`

Get engagement with all related buyers, offers, and closings.

**Response:**
```json
{
  "id": 1,
  "engagement_code": "FAC-2025-0001",
  "status": "offers_in_play",
  "buyer_intros": [...],
  "offers": [...],
  "closings": [...]
}
```

### Activate Engagement

**POST** `/api/v1/facilitator/engagements/{engagement_id}/activate`

Transition engagement from DRAFT to ACTIVE.

### Set Engagement Status

**POST** `/api/v1/facilitator/engagements/{engagement_id}/set-status`

Change engagement status.

**Request:**
```json
{
  "status": "offers_in_play",
  "notes": "First offer received"
}
```

---

## Buyer Introductions

### Introduce Buyer

**POST** `/api/v1/facilitator/engagements/{engagement_id}/buyers`

Introduce a buyer to an engagement (creates Introduced Buyer record).

**Request:**
```json
{
  "buyer_contact_id": 321,
  "introduction_channel": "email",
  "notes": "Introduced via matching engine recommendation"
}
```

**Response:** `201 Created`
```json
{
  "id": 1,
  "engagement_id": 1,
  "buyer_contact_id": 321,
  "status": "invited",
  "introduction_channel": "email",
  "introduced_at": "2025-01-19T12:00:00",
  "created_at": "2025-01-19T12:00:00",
  "updated_at": "2025-01-19T12:00:00"
}
```

### List Buyer Intros

**GET** `/api/v1/facilitator/engagements/{engagement_id}/buyers`

List all introduced buyers for an engagement.

### Set Buyer Status

**POST** `/api/v1/facilitator/engagements/{engagement_id}/buyers/{buyer_intro_id}/set-status`

Update buyer intro status.

**Request:**
```json
{
  "status": "nda_signed",
  "notes": "NDA received and executed"
}
```

### Get Matching Candidates

**GET** `/api/v1/facilitator/engagements/{engagement_id}/buyers/matching-candidates?listing_id=789&limit=50`

Get candidate buyers from Matching Engine (suggestions only, does not create Introduced Buyers).

**Response:**
```json
{
  "engagement_id": 1,
  "candidates": [
    {
      "buyer_contact_id": 1001,
      "match_score": 0.95,
      "match_reasons": ["Industry match", "Size match"],
      "buyer_name": "John Doe",
      "company": "Acme Corp"
    }
  ]
}
```

---

## Offers

### Create Offer

**POST** `/api/v1/facilitator/engagements/{engagement_id}/offers`

Record an offer from an introduced buyer.

**Request:**
```json
{
  "buyer_intro_id": 1,
  "offer_date": "2025-01-20T10:00:00",
  "headline_price": 2500000,
  "currency": "CAD",
  "structure": {
    "deal_type": "asset",
    "cash": 2000000,
    "earnout": 500000
  },
  "notes": "Initial LOI received"
}
```

**Response:** `201 Created`
```json
{
  "id": 1,
  "engagement_id": 1,
  "buyer_intro_id": 1,
  "offer_date": "2025-01-20T10:00:00",
  "headline_price": 2500000.00,
  "currency": "CAD",
  "structure": {...},
  "status": "received",
  "offer_fee_amount": 5000.00,
  "offer_fee_invoiced": false,
  "offer_fee_paid": false,
  "created_at": "2025-01-20T10:00:00"
}
```

### List Offers

**GET** `/api/v1/facilitator/engagements/{engagement_id}/offers`

List all offers for an engagement.

### Set Offer Status

**POST** `/api/v1/facilitator/offers/{offer_id}/set-status`

Update offer status.

**Request:**
```json
{
  "status": "accepted",
  "notes": "Seller accepted offer in principle"
}
```

### Mark Offer Fee

**POST** `/api/v1/facilitator/offers/{offer_id}/mark-fee`

Mark offer fee as invoiced/paid.

**Request:**
```json
{
  "invoiced": true,
  "paid": true
}
```

---

## Closings

### Record Closing

**POST** `/api/v1/facilitator/engagements/{engagement_id}/closings`

Record a deal closing with an introduced buyer. **This calculates success fees automatically.**

**Request:**
```json
{
  "buyer_intro_id": 1,
  "closing_date": "2025-04-01T00:00:00",
  "final_price": 2500000,
  "currency": "CAD",
  "final_structure": {
    "deal_type": "asset",
    "cash": 2000000,
    "earnout": 500000
  },
  "notes": "Transaction completed successfully"
}
```

**Response:** `201 Created`
```json
{
  "id": 1,
  "engagement_id": 1,
  "buyer_intro_id": 1,
  "closing_date": "2025-04-01T00:00:00",
  "final_price": 2500000.00,
  "currency": "CAD",
  "success_fee_rate": 0.05,
  "success_fee_gross_amount": 125000.00,
  "offer_fee_credit_amount": 5000.00,
  "success_fee_net_amount": 120000.00,
  "invoiced": false,
  "paid": false,
  "created_at": "2025-04-01T12:00:00"
}
```

**Fee Calculation Example:**
- Final price: $2,500,000
- Success fee rate: 5%
- Gross: $2,500,000 × 0.05 = $125,000
- Credit: $5,000 (offer fee paid)
- **Net: $125,000 - $5,000 = $120,000**

### Get Closing

**GET** `/api/v1/facilitator/engagements/{engagement_id}/closings`

Get closing for an engagement.

### Mark Closing Invoiced

**POST** `/api/v1/facilitator/closings/{closing_id}/mark-invoiced`

Mark success fee as invoiced/paid.

**Request:**
```json
{
  "invoiced": true,
  "paid": true
}
```

---

## Error Responses

All endpoints return standard error responses:

**400 Bad Request:**
```json
{
  "detail": "Invalid state transition: draft → closed_success"
}
```

**401 Unauthorized:**
```json
{
  "detail": "API key is required"
}
```

**404 Not Found:**
```json
{
  "detail": "Engagement not found"
}
```

---

## Complete Workflow Example

```bash
# 1. Create engagement
curl -X POST http://localhost:8080/api/v1/facilitator/engagements \
  -H "X-API-Key: your-key" \
  -H "Content-Type: application/json" \
  -d '{"seller_contact_id": 123, "company_id": 456, "listing_id": 789}'
# Returns: engagement_id = 1

# 2. Activate engagement
curl -X POST http://localhost:8080/api/v1/facilitator/engagements/1/activate \
  -H "X-API-Key: your-key"

# 3. Introduce buyer
curl -X POST http://localhost:8080/api/v1/facilitator/engagements/1/buyers \
  -H "X-API-Key: your-key" \
  -H "Content-Type: application/json" \
  -d '{"buyer_contact_id": 321, "introduction_channel": "email"}'
# Returns: buyer_intro_id = 1

# 4. Record offer
curl -X POST http://localhost:8080/api/v1/facilitator/engagements/1/offers \
  -H "X-API-Key: your-key" \
  -H "Content-Type: application/json" \
  -d '{
    "buyer_intro_id": 1,
    "offer_date": "2025-01-20T10:00:00",
    "headline_price": 2500000
  }'

# 5. Record closing (calculates fees)
curl -X POST http://localhost:8080/api/v1/facilitator/engagements/1/closings \
  -H "X-API-Key: your-key" \
  -H "Content-Type: application/json" \
  -d '{
    "buyer_intro_id": 1,
    "closing_date": "2025-04-01T00:00:00",
    "final_price": 2500000
  }'
# Returns closing with calculated success fees
```

---

For more examples, see the interactive API documentation at `http://localhost:8080/docs` when running the server.
