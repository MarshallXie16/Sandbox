# Tasks: GrowthPact Development

## Current Sprint: Foundation & MVP Backend (Week 1)

### 🔥 In Progress
None yet - starting development

### ✅ Completed
- [x] Create project structure and foundational documents
- [x] Define database schema
- [x] Write business plan and product design
- [x] Document technical requirements
- [x] Create development roadmap

### 📋 To Do (This Sprint)

#### Backend Setup (Priority: Critical)
- [ ] Initialize FastAPI project structure
- [ ] Set up PostgreSQL with Docker Compose
- [ ] Configure SQLAlchemy async engine
- [ ] Create Alembic migration setup
- [ ] Implement database models (users, user_profiles, partnerships, etc.)
- [ ] Write initial migration
- [ ] Set up pytest with async support
- [ ] Create .env.example with all required variables

#### Authentication System (Priority: Critical)
- [ ] Implement JWT token generation/validation
- [ ] Create password hashing utilities (bcrypt)
- [ ] Build user registration endpoint
- [ ] Build login endpoint (email + password)
- [ ] Build token refresh endpoint
- [ ] Build password reset flow (with email tokens)
- [ ] Add rate limiting to auth endpoints
- [ ] Write auth tests (registration, login, refresh, reset)

#### User Management (Priority: High)
- [ ] Create user profile endpoints (GET, PATCH)
- [ ] Implement profile picture upload (S3 integration)
- [ ] Build user profile creation (strengths/struggles)
- [ ] Add user deactivation endpoint
- [ ] Write user management tests

#### Core Dependencies (Priority: High)
- [ ] Create get_current_user dependency
- [ ] Create get_db dependency
- [ ] Add CORS middleware configuration
- [ ] Set up logging with structlog
- [ ] Configure Sentry error tracking

---

## Backlog (Prioritized)

### Phase 1: MVP Core Features (Weeks 1-2)

#### Matching System
- [ ] Design matching algorithm (complementarity scoring)
- [ ] Build match queue system
- [ ] Create match suggestion endpoint
- [ ] Implement accept/decline match flow
- [ ] Add max 3 partnerships limit check
- [ ] Write matching algorithm tests

#### Partnership Management
- [ ] Create partnership creation endpoint
- [ ] Build partnership detail endpoint
- [ ] Implement partnership settings update
- [ ] Add partnership workspace view endpoint
- [ ] Calculate partnership health score
- [ ] Write partnership tests

#### Goals System
- [ ] Create goal CRUD endpoints
- [ ] Implement individual vs mutual goal logic
- [ ] Add goal completion endpoint
- [ ] Build subtask management
- [ ] Add goal history/archiving
- [ ] Write goal tests

#### Check-Ins System
- [ ] Create check-in creation endpoint (text-based)
- [ ] Implement check-in templates
- [ ] Build check-in feed endpoint (pagination)
- [ ] Add check-in read/response functionality
- [ ] Calculate streak updates on check-in
- [ ] Write check-in tests

#### Task Assignment
- [ ] Create task assignment endpoint
- [ ] Build task completion flow
- [ ] Add task listing endpoint
- [ ] Implement task deletion
- [ ] Write task tests

### Phase 2: Engagement & Safety (Weeks 3-4)

#### Notification System
- [ ] Set up Celery with Redis
- [ ] Integrate SendGrid for emails
- [ ] Create email templates (welcome, match, check-in reminder)
- [ ] Build notification service
- [ ] Implement check-in reminder job
- [ ] Add partnership activity notifications
- [ ] Write notification tests

#### Partnership Seasons
- [ ] Implement 4-week season logic
- [ ] Build end-of-season celebration endpoint
- [ ] Create partnership renewal flow
- [ ] Add graceful partnership ending
- [ ] Archive completed partnerships
- [ ] Write season tests

#### Safety & Moderation
- [ ] Build report submission endpoint
- [ ] Create block user endpoint
- [ ] Implement report admin queue
- [ ] Add ghosting detection job (runs daily)
- [ ] Calculate ghosting score
- [ ] Build admin moderation dashboard (basic)
- [ ] Write safety tests

#### Analytics
- [ ] Build user analytics endpoint (streaks, goals completed)
- [ ] Create partnership stats endpoint
- [ ] Implement balance score calculation
- [ ] Add engagement score tracking
- [ ] Write analytics tests

### Phase 3: Real-Time & Media (Weeks 5-6)

#### WebSocket Support
- [ ] Set up FastAPI WebSocket routes
- [ ] Implement WebSocket authentication
- [ ] Build real-time partnership activity events
- [ ] Add typing indicators
- [ ] Create online/offline status
- [ ] Write WebSocket tests

#### File Upload (S3)
- [ ] Configure AWS S3 bucket
- [ ] Implement file upload utility
- [ ] Add virus scanning (ClamAV or AWS)
- [ ] Create presigned URL generation
- [ ] Build voice note upload endpoint
- [ ] Add photo submission for tasks
- [ ] Strip EXIF data from images
- [ ] Write file upload tests

### Frontend (Weeks 2-6)

#### Initial Setup
- [ ] Initialize Vite + React + TypeScript
- [ ] Configure Tailwind CSS
- [ ] Set up shadcn/ui components
- [ ] Create layout components (Header, Footer, Sidebar)
- [ ] Configure React Router
- [ ] Set up Axios + React Query
- [ ] Create Zustand stores (auth, partnerships)

#### Authentication UI
- [ ] Build registration page
- [ ] Build login page
- [ ] Create password reset flow
- [ ] Add email verification reminder banner
- [ ] Build protected route wrapper

#### Onboarding Flow
- [ ] Create profile setup wizard (multi-step)
- [ ] Build strengths/struggles selection UI
- [ ] Add communication style picker
- [ ] Create commitment level selector
- [ ] Design match queue waiting screen

#### Matching UI
- [ ] Build match suggestions card component
- [ ] Create accept/decline action buttons
- [ ] Add compatibility score visualization
- [ ] Design "no matches yet" empty state

#### Partnership Dashboard
- [ ] Create partnership workspace layout
- [ ] Build goal board component
- [ ] Design check-in feed
- [ ] Add task list component
- [ ] Create partnership stats widget
- [ ] Build health meter visualization

#### Check-In UI
- [ ] Create check-in form with templates
- [ ] Build check-in card component
- [ ] Add reply/reaction functionality
- [ ] Design check-in history timeline

#### Goals & Tasks UI
- [ ] Build goal creation form
- [ ] Create goal card component
- [ ] Design task assignment modal
- [ ] Add task completion UI

#### Notifications UI
- [ ] Create notification center dropdown
- [ ] Build notification item component
- [ ] Add real-time notification updates (WebSocket)

#### Settings & Profile
- [ ] Build user settings page
- [ ] Create profile editing form
- [ ] Add notification preferences
- [ ] Design account deletion flow

---

## Technical Debt

### Performance
- [ ] Add database query profiling
- [ ] Implement Redis caching layer
- [ ] Optimize N+1 queries with eager loading
- [ ] Add database connection pooling

### Security
- [ ] Implement rate limiting middleware
- [ ] Add CSRF protection for state-changing endpoints
- [ ] Set up WAF rules (CloudFront)
- [ ] Add input sanitization for user content

### Testing
- [ ] Increase backend test coverage to 80%
- [ ] Add E2E tests for critical flows
- [ ] Set up load testing with Locust
- [ ] Create test data factories

### Documentation
- [ ] Write API documentation (beyond auto-generated)
- [ ] Create developer onboarding guide
- [ ] Document deployment process
- [ ] Add inline code documentation

---

## Bugs

### Critical
None reported yet

### High
None reported yet

### Medium
None reported yet

### Low
None reported yet

---

## Future Enhancements (Post-MVP)

### V1.0 Features
- [ ] AI coaching assistant (GPT-4 integration)
- [ ] Group accountability pods (3-5 users)
- [ ] Calendar integration (Google, Outlook)
- [ ] Advanced matching with ML
- [ ] Progressive Web App (PWA) with offline mode
- [ ] Push notifications (web push API)

### V2.0 Features
- [ ] Native mobile apps (React Native)
- [ ] Sentiment analysis on check-ins
- [ ] Partnership health predictions (ML)
- [ ] Coach marketplace
- [ ] Enterprise features (SSO, admin dashboard)
- [ ] Internationalization (i18n)

### Business Features
- [ ] Stripe payment integration
- [ ] Subscription management
- [ ] Referral program
- [ ] Affiliate system
- [ ] Analytics dashboard for admins

---

## Dependencies & Blockers

### Current Blockers
None

### Upcoming Needs
- AWS account for S3 (needed by Week 5)
- SendGrid account for emails (needed by Week 3)
- Stripe account for payments (V1.0)
- Domain name and SSL certificate (before launch)

---

## Sprint Planning

### Week 1 Goal (Current)
- Complete backend foundation (FastAPI, DB, auth)
- Initial database migrations
- Auth endpoints fully tested
- User profile endpoints working

### Week 2 Goal
- Matching algorithm implemented
- Partnership creation working
- Goals and check-ins endpoints
- Start frontend development

### Week 3 Goal
- Task assignment system
- Notification system with emails
- Partnership renewal flow
- Frontend authentication and onboarding

### Week 4 Goal
- Safety features (report, block)
- Anti-ghosting system
- Analytics dashboard
- Frontend partnership workspace

---

**Last Updated**: 2025-11-17
**Sprint**: Week 1 (Foundation)
**Next Review**: 2025-11-24
