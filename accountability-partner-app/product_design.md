# Product Design: GrowthPact

## Technical Architecture

### Tech Stack

#### Backend
- **Framework**: FastAPI (Python 3.11+)
  - High performance, async support
  - Automatic API documentation (OpenAPI/Swagger)
  - Native Pydantic validation
- **Database**: PostgreSQL 15+
  - Relational data (users, partnerships, goals)
  - JSONB for flexible metadata
  - Full-text search capabilities
- **ORM**: SQLAlchemy 2.0
  - Type-safe, async support
  - Migration management with Alembic
- **Authentication**: JWT (JSON Web Tokens)
  - Access tokens (15 min expiry)
  - Refresh tokens (7 day expiry)
  - Bcrypt password hashing
- **Task Queue**: Redis + Celery (for async jobs)
  - Match generation
  - Email notifications
  - Ghosting detection cron jobs
- **Real-time**: WebSockets (FastAPI native)
  - Live partnership updates
  - Real-time check-in notifications
  - Typing indicators

#### Frontend
- **Framework**: React 18+ with TypeScript
- **Build Tool**: Vite
- **Styling**: Tailwind CSS 3+
- **UI Components**: shadcn/ui (Radix UI primitives)
- **State Management**: Zustand
- **Routing**: React Router v6
- **API Client**: Axios with React Query
- **Form Handling**: React Hook Form + Zod validation
- **Real-time**: Socket.io-client

#### Infrastructure & DevOps
- **Containerization**: Docker + Docker Compose
- **Web Server**: Nginx (reverse proxy)
- **File Storage**: AWS S3 (profile pictures, voice notes)
- **Email**: SendGrid
- **Monitoring**: Sentry (error tracking)
- **Analytics**: PostHog (open-source product analytics)

### System Architecture

```
┌─────────────┐
│   Client    │
│  (React)    │
└──────┬──────┘
       │
       ├──── HTTP/REST ────┐
       │                   │
       └──── WebSocket ────┤
                           │
                    ┌──────▼──────┐
                    │   Nginx     │
                    │ (Reverse    │
                    │   Proxy)    │
                    └──────┬──────┘
                           │
                    ┌──────▼──────┐
                    │   FastAPI   │
                    │  (Backend)  │
                    └──────┬──────┘
                           │
          ┌────────────────┼────────────────┐
          │                │                │
    ┌─────▼─────┐   ┌─────▼─────┐   ┌─────▼─────┐
    │ PostgreSQL│   │   Redis   │   │    S3     │
    │ (Primary  │   │  (Cache + │   │  (Files)  │
    │   Data)   │   │   Queue)  │   │           │
    └───────────┘   └─────┬─────┘   └───────────┘
                          │
                    ┌─────▼─────┐
                    │   Celery  │
                    │  Workers  │
                    └───────────┘
```

## Database Schema

### MVP Database Design

#### Users Table
```sql
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    username VARCHAR(50) UNIQUE NOT NULL,
    full_name VARCHAR(100),
    profile_picture_url TEXT,
    bio TEXT,
    date_of_birth DATE,
    timezone VARCHAR(50) DEFAULT 'UTC',

    -- Verification & safety
    is_verified BOOLEAN DEFAULT FALSE,
    verification_tier VARCHAR(20) DEFAULT 'basic', -- basic, phone, id
    is_active BOOLEAN DEFAULT TRUE,
    is_banned BOOLEAN DEFAULT FALSE,

    -- Gamification
    total_points INTEGER DEFAULT 0,
    streak_count INTEGER DEFAULT 0,

    -- Metadata
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    last_login_at TIMESTAMP
);

CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_username ON users(username);
```

#### User Profiles Table (Matching Data)
```sql
CREATE TABLE user_profiles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,

    -- Strengths & Struggles (stored as arrays)
    strengths TEXT[] DEFAULT '{}', -- e.g., ['career', 'fitness', 'finance']
    struggles TEXT[] DEFAULT '{}', -- e.g., ['relationships', 'fashion', 'public_speaking']

    -- Matching preferences
    communication_style VARCHAR(50), -- 'direct', 'supportive', 'motivational'
    commitment_level VARCHAR(50), -- 'casual', 'moderate', 'intense'
    preferred_check_in_frequency VARCHAR(50), -- 'daily', '3x_week', 'weekly'

    -- Availability
    available_days_of_week INTEGER[], -- [1,2,3,4,5] (Mon-Fri)
    preferred_check_in_time VARCHAR(20), -- 'morning', 'afternoon', 'evening'

    -- Goals (JSONB for flexibility)
    current_goals JSONB DEFAULT '[]',
    -- Example: [{"area": "career", "goal": "Get promoted", "timeline": "6 months"}]

    -- Matching metadata
    active_partnerships_count INTEGER DEFAULT 0,
    max_partnerships INTEGER DEFAULT 3,
    is_seeking_partner BOOLEAN DEFAULT TRUE,

    -- Behavioral metrics
    ghosting_score FLOAT DEFAULT 0.0, -- 0 (never ghosts) to 1 (frequent ghoster)
    reciprocity_score FLOAT DEFAULT 0.5, -- 0 (takes) to 1 (gives)

    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_user_profiles_user_id ON user_profiles(user_id);
CREATE INDEX idx_user_profiles_seeking ON user_profiles(is_seeking_partner);
```

#### Partnerships Table
```sql
CREATE TABLE partnerships (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user1_id UUID REFERENCES users(id) ON DELETE CASCADE,
    user2_id UUID REFERENCES users(id) ON DELETE CASCADE,

    -- Partnership metadata
    status VARCHAR(50) DEFAULT 'active', -- 'pending', 'active', 'completed', 'cancelled'
    season_number INTEGER DEFAULT 1,
    current_season_start_date DATE DEFAULT CURRENT_DATE,
    current_season_end_date DATE DEFAULT CURRENT_DATE + INTERVAL '4 weeks',

    -- Shared goals
    mutual_goals JSONB DEFAULT '[]',
    -- Example: [{"goal": "Check in 3x per week", "completed": false}]

    -- Partnership settings
    check_in_frequency VARCHAR(50) DEFAULT 'weekly',
    check_in_days INTEGER[] DEFAULT '{1,3,5}', -- Mon, Wed, Fri
    communication_methods TEXT[] DEFAULT '{"text"}', -- text, voice, photo

    -- Health metrics
    balance_score FLOAT DEFAULT 0.5, -- 0 (user1 gives more) to 1 (user2 gives more)
    engagement_score FLOAT DEFAULT 0.0, -- 0 (inactive) to 1 (highly engaged)
    last_interaction_at TIMESTAMP,

    -- Anti-ghosting
    user1_last_active_at TIMESTAMP DEFAULT NOW(),
    user2_last_active_at TIMESTAMP DEFAULT NOW(),
    nudge_count INTEGER DEFAULT 0,

    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),

    CONSTRAINT check_different_users CHECK (user1_id != user2_id),
    CONSTRAINT unique_partnership UNIQUE (user1_id, user2_id)
);

CREATE INDEX idx_partnerships_user1 ON partnerships(user1_id);
CREATE INDEX idx_partnerships_user2 ON partnerships(user2_id);
CREATE INDEX idx_partnerships_status ON partnerships(status);
```

#### Check-Ins Table
```sql
CREATE TABLE check_ins (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    partnership_id UUID REFERENCES partnerships(id) ON DELETE CASCADE,
    author_id UUID REFERENCES users(id) ON DELETE CASCADE,

    -- Check-in content
    content_type VARCHAR(50) DEFAULT 'text', -- 'text', 'voice', 'photo'
    text_content TEXT,
    media_url TEXT, -- S3 URL for voice/photo

    -- Structured prompts
    what_i_did TEXT,
    what_i_struggled_with TEXT,
    what_i_need TEXT,

    -- Sentiment analysis (future AI feature)
    sentiment_score FLOAT, -- -1 (negative) to 1 (positive)

    -- Engagement
    is_read BOOLEAN DEFAULT FALSE,
    response_id UUID REFERENCES check_ins(id), -- if this is a response to another check-in

    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_check_ins_partnership ON check_ins(partnership_id);
CREATE INDEX idx_check_ins_author ON check_ins(author_id);
CREATE INDEX idx_check_ins_created_at ON check_ins(created_at DESC);
```

#### Goals Table
```sql
CREATE TABLE goals (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    partnership_id UUID REFERENCES partnerships(id) ON DELETE CASCADE,
    owner_id UUID REFERENCES users(id) ON DELETE CASCADE, -- NULL if mutual goal

    -- Goal details
    title VARCHAR(200) NOT NULL,
    description TEXT,
    category VARCHAR(50), -- 'career', 'fitness', 'relationships', etc.
    is_mutual BOOLEAN DEFAULT FALSE,

    -- Tracking
    status VARCHAR(50) DEFAULT 'in_progress', -- 'not_started', 'in_progress', 'completed', 'abandoned'
    target_date DATE,
    completed_at TIMESTAMP,

    -- Subtasks
    subtasks JSONB DEFAULT '[]',
    -- Example: [{"task": "Update resume", "completed": true}, {...}]

    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_goals_partnership ON goals(partnership_id);
CREATE INDEX idx_goals_owner ON goals(owner_id);
CREATE INDEX idx_goals_status ON goals(status);
```

#### Tasks Table (Micro-Coaching)
```sql
CREATE TABLE tasks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    partnership_id UUID REFERENCES partnerships(id) ON DELETE CASCADE,
    assigned_by_user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    assigned_to_user_id UUID REFERENCES users(id) ON DELETE CASCADE,

    -- Task details
    title VARCHAR(200) NOT NULL,
    description TEXT,
    task_type VARCHAR(50), -- 'action', 'reflection', 'submission'

    -- Completion
    status VARCHAR(50) DEFAULT 'pending', -- 'pending', 'completed', 'skipped'
    completed_at TIMESTAMP,
    completion_proof_url TEXT, -- S3 URL for photo/voice proof

    -- Metadata
    due_date DATE,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_tasks_assigned_to ON tasks(assigned_to_user_id);
CREATE INDEX idx_tasks_partnership ON tasks(partnership_id);
```

#### Match Queue Table (For Algorithm)
```sql
CREATE TABLE match_queue (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,

    -- Matching status
    status VARCHAR(50) DEFAULT 'pending', -- 'pending', 'matched', 'expired'
    priority_score FLOAT DEFAULT 0.5, -- Higher = prioritize matching

    -- Match attempts
    proposed_matches JSONB DEFAULT '[]',
    -- Example: [{"user_id": "...", "compatibility_score": 0.85, "declined": false}]

    created_at TIMESTAMP DEFAULT NOW(),
    expires_at TIMESTAMP DEFAULT NOW() + INTERVAL '7 days'
);

CREATE INDEX idx_match_queue_status ON match_queue(status);
CREATE INDEX idx_match_queue_priority ON match_queue(priority_score DESC);
```

#### Reports Table (Safety)
```sql
CREATE TABLE reports (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    reporter_id UUID REFERENCES users(id) ON DELETE CASCADE,
    reported_user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    partnership_id UUID REFERENCES partnerships(id) ON DELETE SET NULL,

    -- Report details
    reason VARCHAR(50) NOT NULL, -- 'harassment', 'inappropriate', 'ghosting', 'spam'
    description TEXT,
    evidence_urls TEXT[], -- Screenshots, etc.

    -- Resolution
    status VARCHAR(50) DEFAULT 'pending', -- 'pending', 'investigating', 'resolved', 'dismissed'
    admin_notes TEXT,
    action_taken VARCHAR(100), -- 'warning', 'temp_ban', 'permanent_ban', 'no_action'

    created_at TIMESTAMP DEFAULT NOW(),
    resolved_at TIMESTAMP
);

CREATE INDEX idx_reports_status ON reports(status);
CREATE INDEX idx_reports_reported_user ON reports(reported_user_id);
```

## API Endpoints (REST)

### Authentication
```
POST   /api/v1/auth/register          - Create new user account
POST   /api/v1/auth/login             - Login and get JWT tokens
POST   /api/v1/auth/refresh           - Refresh access token
POST   /api/v1/auth/logout            - Logout (invalidate refresh token)
POST   /api/v1/auth/forgot-password   - Send password reset email
POST   /api/v1/auth/reset-password    - Reset password with token
```

### Users & Profiles
```
GET    /api/v1/users/me               - Get current user profile
PATCH  /api/v1/users/me               - Update current user
DELETE /api/v1/users/me               - Deactivate account
POST   /api/v1/users/me/avatar        - Upload profile picture

GET    /api/v1/profiles/me            - Get matching profile
PATCH  /api/v1/profiles/me            - Update matching preferences
```

### Matching
```
POST   /api/v1/matching/enter-queue   - Enter match queue
GET    /api/v1/matching/status        - Get queue status
GET    /api/v1/matching/suggestions   - Get match suggestions
POST   /api/v1/matching/accept        - Accept a match
POST   /api/v1/matching/decline       - Decline a match
```

### Partnerships
```
GET    /api/v1/partnerships           - List user's partnerships
GET    /api/v1/partnerships/:id       - Get partnership details
PATCH  /api/v1/partnerships/:id       - Update partnership settings
POST   /api/v1/partnerships/:id/renew - Renew for new season
POST   /api/v1/partnerships/:id/end   - End partnership
GET    /api/v1/partnerships/:id/stats - Get partnership analytics
```

### Goals
```
GET    /api/v1/partnerships/:id/goals        - List partnership goals
POST   /api/v1/partnerships/:id/goals        - Create new goal
GET    /api/v1/goals/:id                     - Get goal details
PATCH  /api/v1/goals/:id                     - Update goal
DELETE /api/v1/goals/:id                     - Delete goal
POST   /api/v1/goals/:id/complete            - Mark goal as completed
```

### Check-Ins
```
GET    /api/v1/partnerships/:id/check-ins    - List check-ins
POST   /api/v1/partnerships/:id/check-ins    - Create check-in
GET    /api/v1/check-ins/:id                 - Get check-in details
PATCH  /api/v1/check-ins/:id/read            - Mark check-in as read
```

### Tasks
```
GET    /api/v1/partnerships/:id/tasks        - List partnership tasks
POST   /api/v1/partnerships/:id/tasks        - Assign new task
PATCH  /api/v1/tasks/:id/complete            - Complete task
DELETE /api/v1/tasks/:id                     - Delete task
```

### Safety & Reporting
```
POST   /api/v1/reports                - Submit report
POST   /api/v1/users/:id/block        - Block user
DELETE /api/v1/users/:id/block        - Unblock user
```

## WebSocket Events

### Connection
```
connect    - Establish WebSocket connection (with JWT)
disconnect - Close connection
```

### Partnership Events
```
partnership:update     - Partnership data changed
partnership:activity   - Partner is active
```

### Check-In Events
```
checkin:new           - New check-in posted
checkin:typing        - Partner is typing
```

### Notification Events
```
notification:new      - New system notification
```

## MVP Feature Prioritization

### Phase 1: Core MVP (Weeks 1-2)
- [ ] User registration & authentication
- [ ] Basic profile creation (strengths/struggles)
- [ ] Simple matching algorithm (1:1 complementary matching)
- [ ] Partnership workspace (basic view)
- [ ] Text-based check-ins
- [ ] Goal creation and tracking
- [ ] Partnership renewal flow

### Phase 2: Enhanced MVP (Weeks 3-4)
- [ ] Advanced matching (personality, commitment level)
- [ ] Check-in templates and prompts
- [ ] Task assignment system
- [ ] Partnership analytics (basic stats)
- [ ] Email notifications
- [ ] Anti-ghosting nudges (automated)
- [ ] Report/block functionality

### Phase 3: Growth Features (Weeks 5-6)
- [ ] Real-time WebSocket updates
- [ ] Voice note support
- [ ] Photo submissions
- [ ] Balance meter algorithm
- [ ] Verified user badges
- [ ] Achievement system
- [ ] Mobile-responsive design polish

## Full Product Features (Future)

### V2.0 Features
- Native mobile apps (iOS/Android)
- AI coaching assistant (GPT-4 integration)
- Group accountability pods (3-5 users)
- Calendar integration (Google, Outlook)
- Advanced matching with ML
- Partnership health predictions
- Video check-ins

### Enterprise Features
- Team dashboards
- Admin controls
- Custom branding
- SSO integration
- Analytics exports

## Security & Privacy

### Security Measures
1. **Authentication**: JWT with short-lived access tokens
2. **Password**: Bcrypt hashing with salt
3. **API**: Rate limiting (100 req/min per user)
4. **XSS Protection**: Input sanitization, CSP headers
5. **CSRF Protection**: SameSite cookies
6. **SQL Injection**: Parameterized queries (SQLAlchemy ORM)
7. **File Upload**: Virus scanning, size limits, type validation

### Privacy Controls
1. **Data Minimization**: Collect only necessary data
2. **Encryption**: TLS 1.3 for transport, AES-256 for data at rest
3. **Right to Delete**: Full account deletion within 30 days
4. **Data Export**: Users can export all their data (JSON)
5. **GDPR Compliance**: Cookie consent, privacy policy
6. **No Location Tracking**: Timezone only for check-in scheduling

## Performance Requirements

### Response Time Targets
- API endpoints: < 200ms (p95)
- Database queries: < 50ms (p95)
- WebSocket latency: < 100ms
- Page load time: < 2 seconds (p95)

### Scalability Targets
- **MVP**: 1,000 concurrent users
- **V1.0**: 10,000 concurrent users
- **V2.0**: 100,000+ concurrent users

### Caching Strategy
- User profiles: Redis (5 min TTL)
- Partnership data: Redis (1 min TTL)
- Static assets: CDN (CloudFront)

---

**Version**: 1.0
**Last Updated**: 2025-11-17
**Status**: Active Development
