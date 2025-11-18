# Portal API Usage Guide

Complete reference for Portal API endpoints with curl examples.

## Base URL

```
Development: http://localhost:8000
Production: https://portal-api.capitalinkhub.com
```

## Authentication

All endpoints (except `/health`) require API key authentication via header:

```bash
X-API-Key: your-api-key-here
```

## Common Response Formats

### Success Response
```json
{
  "field1": "value1",
  "field2": "value2"
}
```

### Error Response
```json
{
  "error": "ErrorType",
  "message": "Human-readable error message",
  "details": { /* optional */ }
}
```

### Paginated Response
```json
{
  "items": [ /* array of items */ ],
  "pagination": {
    "page": 1,
    "page_size": 20,
    "total_items": 150,
    "total_pages": 8,
    "has_next": true,
    "has_prev": false
  }
}
```

---

## Health Check

### GET /api/v1/health

Check API health status (no authentication required).

**Example:**
```bash
curl http://localhost:8000/api/v1/health
```

**Response:**
```json
{
  "status": "ok",
  "version": "0.1.0",
  "env": "dev"
}
```

---

## Member Operations

### POST /api/v1/members/resolve

Resolve or create a portal member mapping for a WordPress/Ultimate Member user.

**Headers:**
```
X-API-Key: your-api-key
Content-Type: application/json
```

**Request Body:**
```json
{
  "um_user_id": "123",
  "email": "buyer@example.com",
  "role": "buyer",
  "first_name": "John",
  "last_name": "Doe"
}
```

**Example:**
```bash
curl -X POST http://localhost:8000/api/v1/members/resolve \
  -H "X-API-Key: your-api-key" \
  -H "Content-Type: application/json" \
  -d '{
    "um_user_id": "123",
    "email": "buyer@example.com",
    "role": "buyer",
    "first_name": "John",
    "last_name": "Doe"
  }'
```

**Response:**
```json
{
  "member_id": 45,
  "contact_id": 789,
  "um_user_id": "123",
  "role": "buyer",
  "is_new": false,
  "profile": {
    "member_id": 45,
    "contact_id": 789,
    "um_user_id": "123",
    "role": "buyer",
    "contact": {
      "id": 789,
      "first_name": "John",
      "last_name": "Doe",
      "email": "buyer@example.com",
      "phone": null,
      "title": null,
      "category": "buyer"
    },
    "company": null
  }
}
```

### GET /api/v1/members/{member_id}/profile

Get full member profile.

**Example:**
```bash
curl http://localhost:8000/api/v1/members/45/profile \
  -H "X-API-Key: your-api-key"
```

**Response:**
```json
{
  "member_id": 45,
  "contact_id": 789,
  "um_user_id": "123",
  "role": "buyer",
  "contact": {
    "id": 789,
    "first_name": "John",
    "last_name": "Doe",
    "email": "buyer@example.com",
    "phone": "+1-555-0123",
    "title": "CEO",
    "category": "buyer"
  },
  "company": {
    "id": 456,
    "name": "Acme Corp",
    "website": "https://acme.example.com",
    "industry": "Technology",
    "region": "California"
  }
}
```

### GET /api/v1/members/{member_id}/engagement

Get engagement summary for a member.

**Example:**
```bash
curl http://localhost:8000/api/v1/members/45/engagement \
  -H "X-API-Key: your-api-key"
```

**Response:**
```json
{
  "engagement_score": 72,
  "total_events": 15,
  "recent_events": [
    {
      "event_type": "portal_interest",
      "occurred_at": "2025-01-15T10:30:00Z",
      "subject": "Interest expressed via portal",
      "description": "Interested in Tech SaaS Company",
      "metadata": null
    }
  ],
  "last_activity_date": "2025-01-15T10:30:00Z",
  "email_opens": 8,
  "link_clicks": 5,
  "form_submissions": 2
}
```

---

## Listing Operations

### GET /api/v1/listings

Browse active business listings with optional filters.

**Query Parameters:**
- `industry` (optional): Filter by industry
- `region` (optional): Filter by region
- `min_price` (optional): Minimum asking price
- `max_price` (optional): Maximum asking price
- `min_revenue` (optional): Minimum revenue
- `max_revenue` (optional): Maximum revenue
- `status` (optional): Deal status
- `page` (optional, default=1): Page number
- `page_size` (optional, default=20): Items per page

**Example:**
```bash
curl "http://localhost:8000/api/v1/listings?industry=Technology&page=1&page_size=10" \
  -H "X-API-Key: your-api-key"
```

**Response:**
```json
{
  "items": [
    {
      "listing_id": 101,
      "title": "Profitable SaaS Platform",
      "industry": "Technology",
      "region": "West Coast",
      "revenue_range": "$2.5M-$5M",
      "ebitda_range": "$500K-$1M",
      "asking_price_range": "$5M-$10M",
      "short_description": "Established SaaS platform with recurring revenue...",
      "status": "Active",
      "posted_date": "2025-01-10T09:00:00Z"
    }
  ],
  "pagination": {
    "page": 1,
    "page_size": 10,
    "total_items": 45,
    "total_pages": 5,
    "has_next": true,
    "has_prev": false
  }
}
```

### GET /api/v1/listings/{listing_id}

Get detailed information about a specific listing.

**Example:**
```bash
curl http://localhost:8000/api/v1/listings/101 \
  -H "X-API-Key: your-api-key"
```

**Response:**
```json
{
  "listing_id": 101,
  "title": "Profitable SaaS Platform",
  "industry": "Technology",
  "region": "West Coast",
  "revenue_range": "$2.5M-$5M",
  "ebitda_range": "$500K-$1M",
  "asking_price_range": "$5M-$10M",
  "description": "Established SaaS platform serving B2B customers with 95% recurring revenue. Strong customer retention and growth trajectory.",
  "key_highlights": [
    "95% recurring revenue",
    "200+ enterprise customers",
    "Strong tech stack",
    "Experienced team"
  ],
  "status": "Active",
  "posted_date": "2025-01-10T09:00:00Z",
  "updated_date": "2025-01-15T14:30:00Z",
  "company_size": "11-50",
  "year_established": 2018
}
```

### POST /api/v1/listings/{listing_id}/interest

Express buyer interest in a listing.

**Request Body:**
```json
{
  "member_id": 45,
  "note": "Very interested in this opportunity. Would like to schedule a call."
}
```

**Example:**
```bash
curl -X POST http://localhost:8000/api/v1/listings/101/interest \
  -H "X-API-Key: your-api-key" \
  -H "Content-Type: application/json" \
  -d '{
    "member_id": 45,
    "note": "Very interested in this opportunity."
  }'
```

**Response:**
```json
{
  "interest_id": 234,
  "member_id": 45,
  "listing_id": 101,
  "status": "new",
  "created_at": "2025-01-15T16:45:00Z"
}
```

---

## Interest Operations

### GET /api/v1/members/{member_id}/interests

Get all listings a member has expressed interest in.

**Example:**
```bash
curl http://localhost:8000/api/v1/members/45/interests \
  -H "X-API-Key: your-api-key"
```

**Response:**
```json
[
  {
    "interest_id": 234,
    "listing": {
      "listing_id": 101,
      "title": "Profitable SaaS Platform",
      "industry": "Technology",
      "region": "West Coast",
      "revenue_range": "$2.5M-$5M",
      "ebitda_range": "$500K-$1M",
      "asking_price_range": "$5M-$10M",
      "short_description": "Established SaaS platform...",
      "status": "Active",
      "posted_date": "2025-01-10T09:00:00Z"
    },
    "status": "new",
    "note": "Very interested in this opportunity.",
    "created_at": "2025-01-15T16:45:00Z",
    "updated_at": "2025-01-15T16:45:00Z"
  }
]
```

---

## Recommendation Operations

### GET /api/v1/members/{member_id}/recommendations

Get personalized listing recommendations for a member.

**Query Parameters:**
- `limit` (optional, default=10): Maximum number of recommendations

**Example:**
```bash
curl "http://localhost:8000/api/v1/members/45/recommendations?limit=5" \
  -H "X-API-Key: your-api-key"
```

**Response:**
```json
{
  "member_id": 45,
  "recommendations": [
    {
      "listing": {
        "listing_id": 102,
        "title": "Cloud Infrastructure Service",
        "industry": "Technology",
        "region": "West Coast",
        "revenue_range": "$2.5M-$5M",
        "ebitda_range": "$500K-$1M",
        "asking_price_range": "$5M-$10M",
        "short_description": "...",
        "status": "Active",
        "posted_date": "2025-01-12T11:00:00Z"
      },
      "match_score": 85.0,
      "match_reasons": [
        "Matches your preferred industry: Technology",
        "Located in your preferred region: West Coast",
        "Price matches your typical range"
      ]
    }
  ],
  "total_recommendations": 5,
  "algorithm": "heuristic_v1"
}
```

---

## Resource Operations

### GET /api/v1/resources

List downloadable resources.

**Query Parameters:**
- `category` (optional): Filter by category (buyer, seller, general)
- `resource_type` (optional): Filter by type (pdf, template, video)
- `is_gated` (optional): Filter by gated status (true/false)

**Example:**
```bash
curl "http://localhost:8000/api/v1/resources?category=buyer" \
  -H "X-API-Key: your-api-key"
```

**Response:**
```json
[
  {
    "slug": "buyer-checklist",
    "title": "Buyer's Acquisition Checklist",
    "description": "Essential checklist for buyers evaluating acquisition targets",
    "category": "buyer",
    "resource_type": "pdf",
    "file_size": 1024000,
    "is_gated": true,
    "download_count": 45,
    "url": "https://cdn.example.com/resources/buyer-checklist.pdf"
  }
]
```

### GET /api/v1/resources/{slug}

Get a specific resource by slug (increments download count).

**Example:**
```bash
curl http://localhost:8000/api/v1/resources/buyer-checklist \
  -H "X-API-Key: your-api-key"
```

**Response:**
```json
{
  "slug": "buyer-checklist",
  "title": "Buyer's Acquisition Checklist",
  "description": "Essential checklist for buyers evaluating acquisition targets",
  "category": "buyer",
  "resource_type": "pdf",
  "file_size": 1024000,
  "is_gated": true,
  "download_count": 46,
  "url": "https://cdn.example.com/resources/buyer-checklist.pdf"
}
```

---

## Error Codes

| Status Code | Meaning |
|-------------|---------|
| 200 | Success |
| 400 | Bad Request - Invalid input |
| 401 | Unauthorized - Invalid or missing API key |
| 404 | Not Found - Resource doesn't exist |
| 500 | Internal Server Error |

---

## Rate Limiting

Currently no rate limiting implemented. Future versions will include:
- Rate limit per API key
- Response headers: `X-RateLimit-Limit`, `X-RateLimit-Remaining`, `X-RateLimit-Reset`

---

## Best Practices

1. **Cache member resolution:** After resolving a member, cache the `member_id` in WordPress session
2. **Pagination:** Always use reasonable page sizes (10-50 items)
3. **Error handling:** Implement retry logic for 500 errors, don't retry 400/401/404
4. **Timeouts:** Set HTTP client timeout to 30 seconds
5. **Logging:** Log all API responses for debugging

---

## PHP Integration Example

```php
<?php
// Example WordPress/Ultimate Member integration

function portal_api_request($endpoint, $method = 'GET', $data = null) {
    $api_key = get_option('portal_api_key');
    $base_url = get_option('portal_api_base_url');

    $args = [
        'method' => $method,
        'headers' => [
            'X-API-Key' => $api_key,
            'Content-Type' => 'application/json',
        ],
        'timeout' => 30,
    ];

    if ($data && in_array($method, ['POST', 'PUT', 'PATCH'])) {
        $args['body'] = json_encode($data);
    }

    $response = wp_remote_request($base_url . $endpoint, $args);

    if (is_wp_error($response)) {
        error_log('Portal API error: ' . $response->get_error_message());
        return null;
    }

    return json_decode(wp_remote_retrieve_body($response), true);
}

// Resolve member after login
add_action('um_after_login', function($user_id) {
    $user = get_userdata($user_id);
    $um_role = um_user('role'); // Get Ultimate Member role

    $data = [
        'um_user_id' => (string)$user_id,
        'email' => $user->user_email,
        'role' => $um_role === 'um_buyer' ? 'buyer' : 'seller',
        'first_name' => $user->first_name,
        'last_name' => $user->last_name,
    ];

    $response = portal_api_request('/api/v1/members/resolve', 'POST', $data);

    if ($response) {
        // Store member_id in session for future use
        update_user_meta($user_id, 'portal_member_id', $response['member_id']);
    }
});
?>
```
