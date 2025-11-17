# GrowthPact: Development Memory

## Project Overview
**GrowthPact** is a mutual accountability platform where users with complementary strengths become each other's "growth buddies." This document serves as the persistent memory for the autonomous development agent.

**Status**: Foundation phase - setting up architecture and core systems

---

## Project Structure

### Directory Layout
```
accountability-partner-app/
├── backend/                    # FastAPI backend
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py            # FastAPI app entry point
│   │   ├── config.py          # Configuration management
│   │   ├── database.py        # Database connection
│   │   ├── models/            # SQLAlchemy models
│   │   ├── schemas/           # Pydantic schemas
│   │   ├── api/               # API routes
│   │   │   ├── v1/
│   │   │   │   ├── auth.py
│   │   │   │   ├── users.py
│   │   │   │   ├── partnerships.py
│   │   │   │   ├── goals.py
│   │   │   │   ├── checkins.py
│   │   │   │   └── matching.py
│   │   ├── core/              # Core functionality
│   │   │   ├── auth.py        # JWT handling
│   │   │   ├── security.py    # Password hashing
│   │   │   └── dependencies.py # FastAPI dependencies
│   │   ├── services/          # Business logic
│   │   │   ├── matching_service.py
│   │   │   ├── notification_service.py
│   │   │   └── partnership_service.py
│   │   └── utils/             # Utilities
│   ├── alembic/               # Database migrations
│   ├── tests/                 # Backend tests
│   ├── requirements.txt       # Python dependencies
│   └── .env.example
│
├── frontend/                  # React frontend
│   ├── src/
│   │   ├── components/        # React components
│   │   │   ├── ui/           # shadcn/ui components
│   │   │   ├── layout/       # Layout components
│   │   │   └── features/     # Feature components
│   │   ├── pages/            # Page components
│   │   ├── hooks/            # Custom React hooks
│   │   ├── stores/           # Zustand stores
│   │   ├── api/              # API client
│   │   ├── utils/            # Utilities
│   │   └── App.tsx
│   ├── public/
│   ├── package.json
│   └── .env.example
│
├── docs/                      # Additional documentation
├── docker-compose.yml         # Local development setup
├── .gitignore
├── business_plan.md
├── product_design.md
├── technical_requirements.md
├── roadmap.md
├── user_stories.md
├── memory.md                  # This file
├── tasks.md
├── testing.md
├── fixed_bugs.md
└── README.md
```

---

## Key Architectural Decisions

### Decision 1: FastAPI for Backend
**Date**: 2025-11-17
**Context**: Needed high-performance async Python framework
**Decision**: Use FastAPI over Django/Flask
**Rationale**:
- Native async/await support (important for WebSockets)
- Automatic OpenAPI documentation
- Pydantic validation built-in
- Modern, type-safe, fast
**Consequences**: Team must learn FastAPI patterns, but benefits outweigh learning curve

### Decision 2: PostgreSQL over NoSQL
**Date**: 2025-11-17
**Context**: Database choice for partnerships, goals, check-ins
**Decision**: Use PostgreSQL with SQLAlchemy ORM
**Rationale**:
- Data is highly relational (users ↔ partnerships ↔ goals)
- ACID compliance needed for partnership integrity
- JSON support via JSONB for flexible metadata
- Mature, well-supported, easy to scale with read replicas
**Consequences**: More rigid schema, but worth it for data integrity

### Decision 3: JWT Authentication
**Date**: 2025-11-17
**Context**: Authentication strategy
**Decision**: JWT with short-lived access tokens + refresh tokens
**Rationale**:
- Stateless (scales horizontally)
- Standard industry practice
- Easy to implement with FastAPI
**Consequences**: Cannot revoke tokens easily (mitigated with short expiry)

### Decision 4: Monorepo Structure
**Date**: 2025-11-17
**Context**: Code organization
**Decision**: Separate `backend/` and `frontend/` folders in one repo
**Rationale**:
- Simpler for MVP (one repo to manage)
- Easier to coordinate API contracts
- Single CI/CD pipeline
**Consequences**: May split into multiple repos if team grows

### Decision 5: shadcn/ui for Frontend Components
**Date**: 2025-11-17
**Context**: UI component library choice
**Decision**: Use shadcn/ui (Radix UI primitives + Tailwind)
**Rationale**:
- Copy-paste components (no npm bloat)
- Full customization control
- Accessible by default (WCAG AA)
- Modern, beautiful design
**Consequences**: More initial setup than off-the-shelf library, but better long-term

---

## Database Schema Insights

### Key Tables
1. **users**: Core user data (email, password, profile)
2. **user_profiles**: Matching data (strengths, struggles, preferences)
3. **partnerships**: Active partnerships between two users
4. **check_ins**: Check-in posts within partnerships
5. **goals**: Individual and mutual goals
6. **tasks**: Micro-coaching tasks assigned between partners
7. **match_queue**: Users waiting to be matched
8. **reports**: Safety reports for moderation

### Important Relationships
- **User ↔ Partnership**: Many-to-many (a user can have multiple partnerships)
- **Partnership ↔ Goals**: One-to-many (a partnership has many goals)
- **Partnership ↔ Check-Ins**: One-to-many
- **User ↔ Tasks**: Many-to-many (user assigns tasks, receives tasks)

### Indexes to Add
- `users.email`, `users.username` (for login)
- `partnerships.user1_id`, `partnerships.user2_id` (for lookups)
- `check_ins.partnership_id`, `check_ins.created_at` (for feed queries)
- `match_queue.status`, `match_queue.priority_score` (for matching algorithm)

---

## Code Patterns & Conventions

### Backend Patterns

#### API Route Structure
```python
@router.post("/partnerships/{partnership_id}/check-ins", response_model=CheckInResponse)
async def create_check_in(
    partnership_id: UUID,
    check_in: CheckInCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> CheckIn:
    # 1. Validate user is part of partnership
    # 2. Create check-in
    # 3. Update partnership last_interaction_at
    # 4. Send notification to partner
    # 5. Update streak if applicable
    # 6. Return created check-in
    pass
```

#### Service Layer Pattern
```python
# services/partnership_service.py
class PartnershipService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_partnership(self, user1_id: UUID, user2_id: UUID) -> Partnership:
        # Business logic here
        pass

    async def calculate_health_score(self, partnership_id: UUID) -> float:
        # Complex calculation
        pass
```

#### Error Handling
```python
from fastapi import HTTPException, status

# Use specific HTTP status codes
raise HTTPException(
    status_code=status.HTTP_404_NOT_FOUND,
    detail="Partnership not found"
)

# For validation errors, Pydantic handles automatically
```

### Frontend Patterns

#### Component Structure
```tsx
// components/features/CheckInForm.tsx
interface CheckInFormProps {
  partnershipId: string;
  onSuccess?: () => void;
}

export function CheckInForm({ partnershipId, onSuccess }: CheckInFormProps) {
  const { mutate: createCheckIn } = useCreateCheckIn();

  // Form handling with react-hook-form + zod
  return (
    <form>...</form>
  );
}
```

#### API Client Pattern
```typescript
// api/partnerships.ts
export const partnershipsApi = {
  getPartnership: (id: string) =>
    api.get<Partnership>(`/partnerships/${id}`),

  createCheckIn: (partnershipId: string, data: CheckInCreate) =>
    api.post<CheckIn>(`/partnerships/${partnershipId}/check-ins`, data),
};
```

#### Zustand Store Pattern
```typescript
// stores/authStore.ts
interface AuthState {
  user: User | null;
  token: string | null;
  setUser: (user: User) => void;
  logout: () => void;
}

export const useAuthStore = create<AuthState>((set) => ({
  user: null,
  token: null,
  setUser: (user) => set({ user }),
  logout: () => set({ user: null, token: null }),
}));
```

---

## Dependencies & Their Purposes

### Backend Dependencies
- **fastapi**: Web framework
- **uvicorn**: ASGI server
- **sqlalchemy**: ORM
- **alembic**: Database migrations
- **pydantic**: Data validation
- **python-jose**: JWT handling
- **passlib[bcrypt]**: Password hashing
- **python-multipart**: File upload support
- **redis**: Caching and task queue
- **celery**: Async task processing
- **boto3**: AWS S3 integration
- **sendgrid**: Email sending
- **pytest**: Testing framework
- **httpx**: Async HTTP client (for testing)

### Frontend Dependencies
- **react**: UI framework
- **react-router-dom**: Routing
- **@tanstack/react-query**: Server state management
- **zustand**: Client state management
- **axios**: HTTP client
- **react-hook-form**: Form handling
- **zod**: Schema validation
- **tailwindcss**: Styling
- **@radix-ui/***: Headless UI primitives (via shadcn/ui)
- **socket.io-client**: WebSocket client
- **date-fns**: Date manipulation
- **lucide-react**: Icons

---

## Environment Variables

### Backend (.env)
```bash
# Database
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/growthpact

# JWT
SECRET_KEY=<random-secret-key>
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=15
REFRESH_TOKEN_EXPIRE_DAYS=7

# Redis
REDIS_URL=redis://localhost:6379

# AWS S3
AWS_ACCESS_KEY_ID=<key>
AWS_SECRET_ACCESS_KEY=<secret>
AWS_REGION=us-east-1
S3_BUCKET_NAME=growthpact-uploads-dev

# SendGrid
SENDGRID_API_KEY=<key>
FROM_EMAIL=noreply@growthpact.com

# Environment
ENVIRONMENT=development  # development, staging, production
DEBUG=True
```

### Frontend (.env)
```bash
VITE_API_BASE_URL=http://localhost:8000/api/v1
VITE_WS_URL=ws://localhost:8000/ws
```

---

## Lessons Learned

### Lesson 1: Start with Migrations Early
**Context**: Database schema changes frequently in early development
**Learning**: Set up Alembic migrations from day 1, even for initial schema
**Impact**: Easier to track changes and rollback if needed

### Lesson 2: Type Safety Everywhere
**Context**: Bugs from mismatched types between frontend/backend
**Learning**: Use TypeScript + Pydantic strictly, generate types from OpenAPI spec
**Impact**: Catch errors at compile time, not runtime

### Lesson 3: Test Authentication First
**Context**: Auth bugs block all other development
**Learning**: Build robust auth system first with comprehensive tests
**Impact**: Solid foundation for all protected endpoints

---

## Matching Algorithm Notes

### Core Matching Logic
The matching algorithm needs to optimize for:
1. **Complementary Skills**: User A's struggles = User B's strengths (and vice versa)
2. **Compatibility**: Similar communication styles and commitment levels
3. **Availability**: Overlapping check-in schedules
4. **Balance**: Both users should benefit equally

### Scoring Formula (v1)
```python
def calculate_match_score(user1: UserProfile, user2: UserProfile) -> float:
    # Complementarity: How well do strengths/struggles align?
    complementarity = calculate_complementarity(user1, user2)  # 0-1

    # Compatibility: Communication style + commitment level match
    compatibility = calculate_compatibility(user1, user2)  # 0-1

    # Availability: Overlapping check-in days/times
    availability = calculate_availability(user1, user2)  # 0-1

    # Weighted average
    score = (
        complementarity * 0.5 +
        compatibility * 0.3 +
        availability * 0.2
    )

    return score
```

### Future Enhancements
- Machine learning model trained on successful partnerships
- Incorporate user feedback (did they renew partnership?)
- Balance experience levels (new users with veterans)

---

## Anti-Ghosting Strategy

### Detection
- Track `last_interaction_at` for each user in partnership
- If user inactive for 7 days → trigger nudge sequence

### Nudge Sequence
1. **Day 7**: Friendly reminder email ("Your partner misses you!")
2. **Day 10**: In-app notification + second email
3. **Day 14**: Partner notified that user may be ghosting
4. **Day 21**: Partnership marked "at risk", re-matching offered to active partner
5. **Day 30**: Partnership auto-cancelled, ghosting score increases

### Ghosting Score
- Tracks user's history of ghosting
- Users with high ghosting score:
  - Lower priority in match queue
  - Cannot enter queue for 7 days after ghost (cooldown)
  - Flagged to future partners (transparency)

---

## Performance Optimization Notes

### Database Query Optimization
- Use `select_related()` / `joinedload()` to avoid N+1 queries
- Index foreign keys and frequently filtered columns
- Use Redis to cache:
  - User profiles (5 min TTL)
  - Partnership data (1 min TTL)
  - Match suggestions (10 min TTL)

### API Response Times
- Target: < 100ms for simple queries, < 200ms for complex
- Use async database queries (asyncpg for PostgreSQL)
- Pagination for list endpoints (max 50 items per page)

### Frontend Performance
- Code splitting by route
- Lazy load images
- Optimize bundle size (< 500 KB initial load)
- Use React Query for automatic caching

---

## Security Checklist

- [x] Passwords hashed with bcrypt (cost 12)
- [x] JWT tokens with short expiry
- [ ] Rate limiting on all endpoints (100 req/min per user)
- [ ] CORS configured to whitelist frontend domain
- [ ] Input validation with Pydantic
- [ ] SQL injection prevention (ORM parameterized queries)
- [ ] XSS prevention (CSP headers, sanitize HTML)
- [ ] CSRF protection (SameSite cookies)
- [ ] File upload validation (type, size, virus scan)
- [ ] HTTPS enforced in production
- [ ] Environment variables never committed to git

---

## Testing Strategy

### Backend Testing
- **Unit tests**: Services, utilities (80% coverage)
- **Integration tests**: API endpoints with test database
- **E2E tests**: Critical user flows (pytest + httpx)

### Frontend Testing
- **Unit tests**: Utilities, hooks (Vitest)
- **Component tests**: React Testing Library
- **E2E tests**: Playwright for critical flows

### Test Data
- Use factories (factory_boy for Python) to generate test data
- Reset test database after each test
- Mock external services (S3, SendGrid) in tests

---

## Deployment Strategy

### MVP Deployment (Simple)
- **Backend**: Single EC2 instance with Docker
- **Database**: RDS PostgreSQL (small instance)
- **Frontend**: S3 + CloudFront static hosting
- **CI/CD**: GitHub Actions (test → build → deploy)

### Production Deployment (Scalable)
- **Backend**: ECS Fargate with auto-scaling
- **Database**: RDS Multi-AZ with read replicas
- **Cache**: ElastiCache Redis cluster
- **Frontend**: CloudFront + S3
- **Monitoring**: Sentry + CloudWatch + PostHog

---

## Next Steps (Auto-Generated from Tasks)
See `tasks.md` for current sprint tasks.

---

**Version**: 1.0
**Last Updated**: 2025-11-17
**Maintained By**: Autonomous Development Agent
