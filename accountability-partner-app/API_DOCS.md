# GrowthPact API Documentation

**Version**: 1.0
**Base URL**: `/api/v1`
**Authentication**: JWT Bearer Token

---

## Table of Contents
1. [Authentication](#authentication)
2. [Users & Profiles](#users--profiles)
3. [Matching & Queue](#matching--queue)
4. [Partnerships](#partnerships) *(Coming Soon)*
5. [Error Handling](#error-handling)

---

## Authentication

### Register User
```http
POST /api/v1/auth/register
Content-Type: application/json

{
  "email": "sarah@example.com",
  "username": "sarah_career",
  "full_name": "Sarah Johnson",
  "password": "SecurePass123"
}
```

**Response (201)**:
```json
{
  "id": "123e4567-e89b-12d3-a456-426614174000",
  "email": "sarah@example.com",
  "username": "sarah_career",
  "full_name": "Sarah Johnson",
  "profile_picture_url": null,
  "bio": null,
  "timezone": "UTC",
  "is_verified": false,
  "total_points": 0,
  "streak_count": 0,
  "created_at": "2025-11-18T10:30:00Z"
}
```

### Login
```http
POST /api/v1/auth/login
Content-Type: application/json

{
  "email": "sarah@example.com",
  "password": "SecurePass123"
}
```

**Response (200)**:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

### Refresh Token
```http
POST /api/v1/auth/refresh
Content-Type: application/json

{
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

**Response (200)**:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

---

## Users & Profiles

All endpoints require `Authorization: Bearer <access_token>` header.

### Get Current User
```http
GET /api/v1/users/me
Authorization: Bearer <access_token>
```

**Response (200)**:
```json
{
  "id": "123e4567-e89b-12d3-a456-426614174000",
  "email": "sarah@example.com",
  "username": "sarah_career",
  "full_name": "Sarah Johnson",
  "profile_picture_url": null,
  "bio": "Aspiring entrepreneur looking for accountability!",
  "timezone": "America/New_York",
  "is_verified": false,
  "total_points": 0,
  "streak_count": 0,
  "created_at": "2025-11-18T10:30:00Z"
}
```

### Update User Profile
```http
PATCH /api/v1/users/me
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "full_name": "Sarah J. Johnson",
  "bio": "Startup founder seeking growth accountability",
  "timezone": "America/Los_Angeles"
}
```

**Response (200)**: Updated user object

### Deactivate Account
```http
DELETE /api/v1/users/me
Authorization: Bearer <access_token>
```

**Response (204)**: No content

### Get User Profile (Matching Data)
```http
GET /api/v1/profiles/me
Authorization: Bearer <access_token>
```

**Response (200)**:
```json
{
  "id": "profile-uuid",
  "user_id": "user-uuid",
  "strengths": ["career", "fitness"],
  "struggles": ["fashion", "relationships"],
  "communication_style": "direct",
  "commitment_level": "moderate",
  "preferred_check_in_frequency": "3x_week",
  "available_days_of_week": [1, 3, 5],
  "preferred_check_in_time": "evening",
  "active_partnerships_count": 1,
  "max_partnerships": 3,
  "is_seeking_partner": true,
  "ghosting_score": 0.0,
  "reciprocity_score": 0.5
}
```

### Update Profile (Matching Preferences)
```http
PATCH /api/v1/profiles/me
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "strengths": ["career", "fitness", "finance"],
  "struggles": ["fashion", "relationships"],
  "communication_style": "direct",
  "commitment_level": "moderate",
  "preferred_check_in_frequency": "3x_week",
  "available_days_of_week": [1, 3, 5],
  "preferred_check_in_time": "evening"
}
```

**Validation Rules**:
- `strengths`: 2-4 items
- `struggles`: 2-4 items
- `communication_style`: "direct", "supportive", or "motivational"
- `commitment_level`: "casual", "moderate", or "intense"
- `preferred_check_in_frequency`: "daily", "3x_week", or "weekly"
- `available_days_of_week`: Array of integers 1-7 (Monday=1, Sunday=7)
- `preferred_check_in_time`: "morning", "afternoon", or "evening"

**Response (200)**: Updated profile object

---

## Matching & Queue

### Enter Match Queue
```http
POST /api/v1/matching/enter-queue
Authorization: Bearer <access_token>
```

**Requirements**:
- Profile must be complete (2+ strengths, 2+ struggles)
- User must have < 3 active partnerships
- Queue entry expires after 7 days

**Response (201)**:
```json
{
  "in_queue": true,
  "status": "pending",
  "queue_position": 5,
  "entered_at": "2025-11-18T10:30:00Z",
  "expires_at": "2025-11-25T10:30:00Z",
  "has_suggestions": false,
  "suggestions_count": 0
}
```

**Error (400)**: Profile incomplete or max partnerships reached

### Get Queue Status
```http
GET /api/v1/matching/status
Authorization: Bearer <access_token>
```

**Response (200)**:
```json
{
  "in_queue": true,
  "status": "pending",
  "queue_position": 3,
  "entered_at": "2025-11-18T10:30:00Z",
  "expires_at": "2025-11-25T10:30:00Z",
  "has_suggestions": true,
  "suggestions_count": 3
}
```

Status values: `pending`, `matched`, `expired`, `cancelled`, `not_in_queue`

### Get Match Suggestions
```http
GET /api/v1/matching/suggestions
Authorization: Bearer <access_token>
```

**Response (200)**:
```json
{
  "suggestions": [
    {
      "user_id": "match-user-uuid",
      "username": "mike_fitness",
      "profile_picture_url": "https://...",
      "compatibility_score": 0.87,
      "strengths": ["fashion", "relationships"],
      "struggles": ["career", "fitness"],
      "communication_style": "supportive",
      "commitment_level": "moderate",
      "why_matched": {
        "you_help_with": ["career"],
        "they_help_with": ["fashion", "relationships"]
      }
    },
    {
      "user_id": "another-match-uuid",
      "username": "alex_entrepreneur",
      "compatibility_score": 0.75,
      "strengths": ["fashion"],
      "struggles": ["career", "fitness"],
      "communication_style": "direct",
      "commitment_level": "intense",
      "why_matched": {
        "you_help_with": ["career", "fitness"],
        "they_help_with": ["fashion"]
      }
    }
  ],
  "queue_position": 3,
  "total_in_queue": 47
}
```

**Matching Algorithm**:
- **Complementarity (50%)**: How well strengths/struggles align
- **Compatibility (30%)**: Communication style and commitment level
- **Availability (20%)**: Schedule overlap

Declined matches are automatically filtered out.

**Error (400)**: Not in queue

### Accept Match
```http
POST /api/v1/matching/accept
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "match_id": "user-uuid-of-match"
}
```

**Creates**:
- New Partnership (Season 1, 4 weeks)
- Removes both users from queue
- Updates active_partnerships_count

**Response (201)**:
```json
{
  "partnership_id": "partnership-uuid",
  "partner": {
    "id": "partner-uuid",
    "username": "mike_fitness",
    "full_name": "Mike Johnson",
    "profile_picture_url": "https://...",
    "strengths": ["fashion", "relationships"],
    "struggles": ["career", "fitness"]
  },
  "season_number": 1,
  "season_start_date": "2025-11-18T00:00:00Z",
  "season_end_date": "2025-12-16T00:00:00Z",
  "status": "active",
  "message": "Partnership created successfully!"
}
```

**Error (400)**:
- Either user has 3 partnerships
- Partnership already exists
- Match not in suggestions

### Decline Match
```http
POST /api/v1/matching/decline
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "match_id": "user-uuid-to-decline",
  "reason": "Not a good fit for me"
}
```

**Response (204)**: No content

The declined user will not appear in future suggestions.

### Leave Queue
```http
DELETE /api/v1/matching/leave-queue
Authorization: Bearer <access_token>
```

**Response (204)**: No content

Sets queue status to `cancelled`. Can re-enter anytime.

---

## Partnerships

All endpoints require `Authorization: Bearer <access_token>` header.
Only partnership members can access partnership data (authorization enforced).

### List Partnerships
```http
GET /api/v1/partnerships?status=active
Authorization: Bearer <access_token>
```

**Query Parameters**:
- `status` (optional): Filter by status (`active`, `completed`, `cancelled`)

**Response (200)**:
```json
{
  "partnerships": [
    {
      "id": "partnership-uuid",
      "partner": {
        "id": "partner-uuid",
        "username": "mike_fitness",
        "full_name": "Mike Johnson",
        "profile_picture_url": "https://...",
        "strengths": ["fashion", "relationships"],
        "struggles": ["career", "fitness"]
      },
      "status": "active",
      "season_number": 1,
      "current_season_start_date": "2025-11-18",
      "current_season_end_date": "2025-12-16",
      "mutual_goals": [],
      "check_in_frequency": "3x_week",
      "check_in_days": [1, 3, 5],
      "communication_methods": ["text"],
      "balance_score": 0.5,
      "engagement_score": 1.0,
      "last_interaction_at": "2025-11-18T10:30:00Z",
      "created_at": "2025-11-18T10:30:00Z"
    }
  ],
  "total": 1
}
```

### Get Partnership Details
```http
GET /api/v1/partnerships/:id
Authorization: Bearer <access_token>
```

**Authorization**: Only partnership members (user1 or user2) can access.

**Response (200)**: Same as partnership object above

**Error (403)**: Not a member of this partnership
**Error (404)**: Partnership not found

### Update Partnership Settings
```http
PATCH /api/v1/partnerships/:id/settings
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "check_in_frequency": "daily",
  "check_in_days": [1, 2, 3, 4, 5],
  "communication_methods": ["text", "voice", "photo"]
}
```

**Authorization**: Only partnership members can update settings.

**Validation Rules**:
- `check_in_frequency`: "daily", "3x_week", or "weekly"
- `check_in_days`: Array of integers 1-7 (Monday=1, Sunday=7)
- `communication_methods`: Array containing "text", "voice", and/or "photo"

**Response (200)**: Updated partnership object

**Error (403)**: Not a member of this partnership
**Error (422)**: Validation error

### End Partnership
```http
POST /api/v1/partnerships/:id/end
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "reason": "Completed our goals together!",
  "give_feedback": true
}
```

**Authorization**: Only partnership members can end the partnership.

**Effects**:
- Sets partnership status to `completed`
- Decrements `active_partnerships_count` for both users
- Sets `is_seeking_partner` to `true` if count < 3

**Response (204)**: No content

**Error (400)**: Partnership already ended
**Error (403)**: Not a member of this partnership

### Get Partnership Stats
```http
GET /api/v1/partnerships/:id/stats
Authorization: Bearer <access_token>
```

**Authorization**: Only partnership members can access stats.

**Response (200)**:
```json
{
  "partnership_id": "partnership-uuid",
  "season_number": 1,
  "days_active": 14,
  "total_check_ins": 12,
  "user_check_ins": 6,
  "partner_check_ins": 6,
  "total_goals": 4,
  "completed_goals": 2,
  "balance_score": 0.5,
  "engagement_score": 0.85,
  "current_streak": 5,
  "longest_streak": 5,
  "last_interaction_at": "2025-11-18T10:30:00Z"
}
```

**Metrics Explained**:
- `days_active`: Days since partnership started
- `user_check_ins`: Your check-in count
- `partner_check_ins`: Partner's check-in count
- `balance_score`: 0.0-1.0, measures reciprocity (0.5 = balanced)
- `engagement_score`: 0.0-1.0, measures overall engagement
- `current_streak`: Current consecutive check-in streak
- `longest_streak`: Longest streak achieved

**Error (403)**: Not a member of this partnership
**Error (404)**: Partnership not found

---

## Error Handling

### Standard Error Response
```json
{
  "detail": "Error message here"
}
```

### Common HTTP Status Codes

| Code | Meaning | Example |
|------|---------|---------|
| 200 | OK | Request succeeded |
| 201 | Created | Resource created |
| 204 | No Content | Deletion succeeded |
| 400 | Bad Request | Validation error |
| 401 | Unauthorized | Missing/invalid token |
| 403 | Forbidden | Insufficient permissions |
| 404 | Not Found | Resource doesn't exist |
| 422 | Unprocessable Entity | Pydantic validation failed |
| 500 | Internal Server Error | Server error |

### Validation Errors (422)
```json
{
  "detail": [
    {
      "type": "too_short",
      "loc": ["body", "strengths"],
      "msg": "List should have at least 2 items after validation, not 1",
      "input": ["career"],
      "ctx": {
        "field_type": "List",
        "min_length": 2,
        "actual_length": 1
      }
    }
  ]
}
```

---

## Rate Limiting

*(Not yet implemented - planned for production)*

- **Default**: 100 requests/minute per user
- **Auth endpoints**: 5 requests/minute (brute force protection)
- **Headers**: `X-RateLimit-Limit`, `X-RateLimit-Remaining`, `X-RateLimit-Reset`

---

## WebSocket Events

*(Coming in future sprints)*

Real-time events for:
- Partnership notifications
- Check-in reminders
- Match suggestions ready
- Partner online status

---

## Testing the API

### Using cURL
```bash
# Register
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","username":"testuser","password":"TestPass123"}'

# Login
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"TestPass123"}'

# Get profile (with token)
curl http://localhost:8000/api/v1/users/me \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### Using Swagger UI
Visit `http://localhost:8000/docs` when running in development mode.

---

**Last Updated**: 2025-11-18
**Test Coverage**: 64/64 tests passing ✅ (19 unit + 45 integration)
