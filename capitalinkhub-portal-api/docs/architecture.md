# Portal API Architecture

## System Overview

The Capital Ink Hub Portal API serves as a secure backend intermediary between the WordPress member portal (using Ultimate Member) and the IndieStack CRM system.

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                     WordPress + Ultimate Member              │
│                    (Member Portal Frontend)                  │
└──────────────────────────┬──────────────────────────────────┘
                           │ HTTP + API Key Auth
                           │ (Backend PHP calls)
                           ▼
┌─────────────────────────────────────────────────────────────┐
│               Capital Ink Hub Portal API                     │
│                    (This Service)                            │
│                                                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │   FastAPI    │  │   Services   │  │ Repositories │      │
│  │   Routers    │──▶│   Layer      │──▶│    Layer     │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
│                                              │               │
└──────────────────────────────────────────────┼──────────────┘
                                               │
                    ┌──────────────────────────┼────────────────┐
                    │                          │                │
                    ▼                          ▼                ▼
        ┌─────────────────────┐   ┌──────────────────┐  ┌──────────────┐
        │  IndieStack CRM DB  │   │ Engagement       │  │ Matching     │
        │    (PostgreSQL)     │   │ Tracker API      │  │ Engine API   │
        │                     │   │ (Future)         │  │ (Future)     │
        └─────────────────────┘   └──────────────────┘  └──────────────┘
```

## Component Breakdown

### 1. WordPress + Ultimate Member Layer

**Responsibility:** User-facing portal for buyers and sellers

**Components:**
- Ultimate Member: User registration, login, profile management
- Custom WordPress plugin: Integration with Portal API
- Member dashboard pages: Listings, interests, engagement

**Communication:**
- Makes HTTP requests to Portal API from PHP backend
- Never exposes API keys to browser
- Uses member context (um_user_id, email) in API calls

### 2. Portal API Layer (This Service)

**Responsibility:** Secure backend API, data transformation, business logic

**Key Components:**

#### 2.1 API Layer (`app/api/`)
- FastAPI routers for each domain
- Request validation via Pydantic
- Authentication via API key dependency
- Error handling and HTTP responses

#### 2.2 Service Layer (`app/services/`)
- **ProfileService:** Member resolution and profile retrieval
- **ListingsService:** Business listing anonymization and filtering
- **InterestService:** Interest tracking and CRM activity creation
- **RecommendationService:** Personalized recommendation generation
- **EngagementService:** Engagement scoring and event tracking
- **ResourceService:** Downloadable resource management

#### 2.3 Repository Layer (`app/repositories/`)
- Data access abstraction
- SQLAlchemy async query builders
- Domain-specific queries
- Pagination and filtering

#### 2.4 Integration Layer (`app/integrations/`)
- **Engagement Tracker Client:** Stub + future HTTP client
- **Matching Engine Client:** Stub + future HTTP client
- Protocol-based design for easy swapping

### 3. Data Layer

#### 3.1 IndieStack CRM Database (PostgreSQL)

**CRM Tables (Read/Write):**
- `contacts` - Buyer/seller contact records
- `companies` - Business entities
- `deals` - Listings/opportunities
- `activities` - Timeline events and interactions

**Portal Tables (Managed by this service):**
- `portal_members` - WordPress user ↔ CRM contact mapping
- `portal_interests` - Buyer interest tracking
- `portal_resources` - Resource metadata

#### 3.2 Future Integrations
- **Engagement Tracker:** Real-time engagement scoring
- **Matching Engine:** ML-based buyer-listing matching

## Data Flow Examples

### Example 1: Member Resolution

```
WordPress User Logs In
    │
    ├─ WordPress calls POST /api/v1/members/resolve
    │  with: um_user_id, email, role
    │
    ▼
Portal API receives request
    │
    ├─ ProfileService.resolve_member()
    │  │
    │  ├─ Check portal_members for um_user_id
    │  │  (Cache lookup)
    │  │
    │  ├─ If not found:
    │  │  ├─ Search contacts by email
    │  │  ├─ Create contact if needed
    │  │  └─ Create portal_members mapping
    │  │
    │  └─ Return MemberProfile
    │
    ▼
WordPress receives member_id + profile
    │
    └─ Store member_id in session for future calls
```

### Example 2: Expressing Interest

```
Buyer clicks "I'm Interested" on Listing
    │
    ├─ WordPress calls POST /api/v1/listings/{id}/interest
    │  with: member_id, note
    │
    ▼
Portal API receives request
    │
    ├─ InterestService.create_interest()
    │  │
    │  ├─ Validate member and listing exist
    │  │
    │  ├─ Check for duplicate interest
    │  │
    │  ├─ Create portal_interests record
    │  │
    │  ├─ Create CRM activity
    │  │  (type: "portal_interest")
    │  │
    │  └─ Commit transaction
    │
    ▼
Portal API returns InterestResponse
    │
    └─ WordPress shows confirmation to user
```

### Example 3: Listing Browse

```
Buyer views "Available Businesses" page
    │
    ├─ WordPress calls GET /api/v1/listings
    │  with: industry, region, min_price, max_price, page
    │
    ▼
Portal API receives request
    │
    ├─ ListingsService.get_listings()
    │  │
    │  ├─ DealsRepository queries deals + companies
    │  │  with JOIN and filters
    │  │
    │  ├─ For each result:
    │  │  ├─ Anonymize region (CA → West Coast)
    │  │  ├─ Convert prices to ranges ($2.5M → $2M-$5M)
    │  │  └─ Remove seller identity
    │  │
    │  └─ Return paginated ListingTeasers
    │
    ▼
Portal API returns listings + pagination
    │
    └─ WordPress renders listing cards
```

## Security Model

### Authentication Flow

1. **API Key Generation:**
   - Generated via CLI: `python portal_cli.py portal create-api-key`
   - Stored in Portal API `.env` as `PORTAL_API_KEY`
   - Added to WordPress plugin configuration

2. **Request Authentication:**
   - WordPress includes `X-API-Key` header in every request
   - Portal API validates via `verify_api_key` dependency
   - Invalid key → 401 Unauthorized

3. **Backend-Only Communication:**
   - API keys never exposed to browser
   - All requests originate from WordPress PHP backend
   - No CORS needed (unless explicitly configured)

### Data Protection

- **Listing Anonymization:** Seller names, exact addresses, precise financials removed
- **Region Generalization:** Specific locations → high-level regions
- **Price Banding:** Exact amounts → ranges
- **Role-Based Access:** Future enhancement for buyer/seller separation

## Scalability Considerations

### Current Design
- Async I/O throughout (FastAPI + asyncpg)
- Connection pooling for database
- Stateless API (can scale horizontally)

### Future Optimizations
- Redis caching for frequently accessed data
- Read replicas for CRM database
- CDN for resource downloads
- Rate limiting per API key

## Database Schema

### Portal-Specific Tables

#### portal_members
```sql
- id (PK)
- um_user_id (unique, indexed)
- contact_id (FK → contacts.id, indexed)
- role (buyer/seller/both)
- is_active
- metadata (JSONB)
- created_at, updated_at
```

#### portal_interests
```sql
- id (PK)
- member_id (FK → portal_members.id, indexed)
- contact_id (FK → contacts.id, indexed)
- listing_id (FK → deals.id, indexed)
- note (text)
- status (new/contacted/qualified/disqualified)
- metadata (JSONB)
- created_at, updated_at
- UNIQUE (member_id, listing_id)
```

#### portal_resources
```sql
- id (PK)
- slug (unique, indexed)
- title
- description
- category (buyer/seller/general, indexed)
- resource_type (pdf/template/video)
- file_url
- file_size
- is_gated
- is_active
- download_count
- metadata (JSONB)
- created_at, updated_at
```

## Extension Points

### 1. Engagement Tracker Integration

Replace stub with HTTP client:
```python
# In app/core/config.py
ENGAGEMENT_TRACKER_BASE_URL = "https://tracker.example.com"

# In app/integrations/engagement_tracker.py
# HTTP client activates automatically when URL is configured
```

### 2. Matching Engine Integration

Similar to engagement tracker:
```python
MATCHING_ENGINE_BASE_URL = "https://matching.example.com"
```

Service layer checks for integration and falls back to heuristic algorithm if not available.

### 3. Resource Storage

Current: Stores file_url in database
Future: Integrate with S3/CDN:
```python
# In ResourceService._get_resource_url()
# Generate signed S3 URL with expiration
```

## Deployment

### Development
```bash
uvicorn main:app --reload
```

### Production
```bash
# Via systemd service
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4

# Via Docker
docker run -p 8000:8000 portal-api

# Via Kubernetes
kubectl apply -f k8s/portal-api.yaml
```

### Environment-Specific Configuration

- `PORTAL_ENV=dev` → Enables /docs, detailed logging
- `PORTAL_ENV=prod` → Disables /docs, structured JSON logging

## Monitoring & Observability

### Logging
- Structured JSON logs in production
- Human-readable logs in development
- Log levels: DEBUG, INFO, WARNING, ERROR
- Request/response logging with duration

### Health Checks
- `GET /api/v1/health` → Quick health status
- Returns: status, version, environment

### Future Enhancements
- Prometheus metrics
- Distributed tracing (OpenTelemetry)
- Error tracking (Sentry)
- Performance monitoring

## Testing Strategy

### Unit Tests
- Service layer business logic
- Repository query building
- Data transformation functions

### Integration Tests
- API endpoint behavior
- Database operations
- Error handling

### Load Testing
- Listing browse under high concurrency
- Member resolution performance
- Database query optimization

## Migration Strategy

### Initial Setup
1. Deploy Portal API service
2. Run migrations: `alembic upgrade head`
3. Configure WordPress plugin with API key
4. Test member resolution flow

### Data Migration (if needed)
1. Export existing WordPress users
2. Bulk create contact records in CRM
3. Bulk create portal_members mappings
4. Validate mappings via CLI

See [integration_ultimate_member.md](integration_ultimate_member.md) for WordPress-specific integration details.
