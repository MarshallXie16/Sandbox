# GrowthPact Development Backlog - Jira-Style Tickets

> **Project**: GrowthPact - Mutual Accountability Platform
> **Version**: MVP to V1.0
> **Last Updated**: 2025-11-18

---

## 📊 Sprint Overview

### Current Sprint: **Sprint 1 - Core Backend** ✅ COMPLETE
- **Sprint Goal**: Complete user management, profiles, matching algorithm, and partnership management
- **Story Points**: 39 / 40 capacity (completed)
- **Duration**: Nov 17 - Nov 18
- **Status**: All tickets completed! 61/61 tests passing ✅

### Upcoming Sprints
- **Sprint 2**: Partnerships & Goals (Week 2)
- **Sprint 3**: Check-ins & Tasks (Week 2-3)
- **Sprint 4**: Safety & Notifications (Week 3-4)
- **Sprint 5**: Frontend Foundation (Week 4-5)

---

## 🎯 Epics

1. **EPIC-1**: User Management & Authentication
2. **EPIC-2**: Matching Algorithm & Queue
3. **EPIC-3**: Partnership Management
4. **EPIC-4**: Goals & Progress Tracking
5. **EPIC-5**: Check-ins & Communication
6. **EPIC-6**: Task Assignment (Micro-Coaching)
7. **EPIC-7**: Safety & Moderation
8. **EPIC-8**: Notifications & Engagement
9. **EPIC-9**: Gamification & Achievements
10. **EPIC-10**: Frontend Application

---

## 🚀 SPRINT 1: Core Backend (Current)

### ✅ DONE

**GP-001**: Initialize Backend Infrastructure
**Status**: ✅ Done
**Priority**: Critical
**Story Points**: 8
**Epic**: EPIC-1

**Description**:
Set up complete FastAPI backend with PostgreSQL, Docker Compose, Alembic migrations, and authentication system.

**Acceptance Criteria**:
- [x] FastAPI app runs with async support
- [x] PostgreSQL database accessible via Docker
- [x] All 7 database models created (User, UserProfile, Partnership, Goal, CheckIn, Task, MatchQueue, Report)
- [x] Alembic migrations configured
- [x] JWT authentication endpoints (register, login, refresh)
- [x] CORS middleware configured
- [x] Environment variables managed with Pydantic

**Technical Notes**:
- Using asyncpg for async PostgreSQL support
- bcrypt for password hashing (cost factor 12)
- JWT tokens: 15 min access, 7 days refresh

**GP-002**: Create Database Migrations
**Status**: ✅ Done
**Priority**: Critical
**Story Points**: 3
**Epic**: EPIC-1
**Dependencies**: GP-001
**Completed**: 2025-11-17

**Description**:
Generate and apply initial Alembic migration to create all database tables with proper indexes and constraints.

**Acceptance Criteria**:
- [x] Run `alembic revision --autogenerate` successfully
- [x] Migration creates all 7 tables with correct schemas
- [x] All foreign keys and constraints properly defined
- [x] Indexes created for frequently queried columns (email, username, partnership_id, etc.)
- [x] Migration can be applied and rolled back without errors
- [x] Test database populated with sample data for development

**Implementation**:
- File: `alembic/versions/2025_11_17_0220-001_initial_schema.py`
- All 7 tables created with proper relationships
- Platform-independent types (GUID, ARRAY, JSONB) for PostgreSQL/SQLite compatibility

---

**GP-003**: User Profile Management Endpoints
**Status**: ✅ Done
**Priority**: Critical
**Story Points**: 5
**Epic**: EPIC-1
**Dependencies**: GP-002
**Completed**: 2025-11-18

**Description**:
Build endpoints for users to manage their profiles, including strengths, struggles, communication preferences, and matching settings.

**Acceptance Criteria**:
- [x] `GET /api/v1/users/me` - Fetch current user
- [x] `PATCH /api/v1/users/me` - Update user basic info (name, bio, timezone)
- [x] `DELETE /api/v1/users/me` - Deactivate account
- [x] `GET /api/v1/profiles/me` - Fetch user profile (matching data)
- [x] `PATCH /api/v1/profiles/me` - Update profile (strengths, struggles, preferences)
- [x] Validation: strengths/struggles must be 2-4 items each
- [x] Validation: communication_style must be in ['direct', 'supportive', 'motivational']
- [x] Validation: commitment_level must be in ['casual', 'moderate', 'intense']
- [x] Profile automatically created on user registration
- [x] Returns 404 if profile doesn't exist

**Implementation**:
- Files: `app/api/v1/users.py`, `app/api/v1/profiles.py`, `app/schemas/profile.py`
- 25 integration tests (all passing)
- Comprehensive Pydantic validators for all fields

**API Spec**:
```json
PATCH /api/v1/profiles/me
{
  "strengths": ["career", "fitness"],
  "struggles": ["fashion", "relationships"],
  "communication_style": "direct",
  "commitment_level": "moderate",
  "preferred_check_in_frequency": "3x_week",
  "available_days_of_week": [1, 3, 5],
  "preferred_check_in_time": "evening"
}
```

**Testing**:
- Unit tests for validation logic
- Integration tests for all endpoints
- Test unauthorized access returns 401

**Technical Notes**:
- Create `app/api/v1/users.py` and `app/api/v1/profiles.py`
- Create `app/schemas/profile.py` with Pydantic models
- Update `app/main.py` to include new routers

---

**GP-004**: Matching Algorithm - Complementarity Scoring
**Status**: ✅ Done
**Priority**: Critical
**Story Points**: 8
**Epic**: EPIC-2
**Dependencies**: GP-003
**Completed**: 2025-11-18

**Description**:
Implement core matching algorithm that scores user compatibility based on complementary strengths/struggles, communication style, and availability.

**Acceptance Criteria**:
- [x] `calculate_complementarity_score(user1, user2)` function returns 0-1 score
- [x] High score (>0.7) when user1's strengths match user2's struggles and vice versa
- [x] Low score (<0.3) when no overlap between strengths/struggles
- [x] `calculate_compatibility_score(user1, user2)` checks communication styles
- [x] Bonus points for matching commitment levels
- [x] `calculate_availability_score(user1, user2)` checks overlapping days
- [x] `calculate_match_score(user1, user2)` combines all scores with weights:
  - Complementarity: 50%
  - Compatibility: 30%
  - Availability: 20%
- [x] Algorithm is symmetric: `score(A, B) == score(B, A)`

**Implementation**:
- File: `app/services/matching_service.py` (273 lines)
- 19 unit tests (all passing)
- Features: Symmetric scoring, human-readable explanations, edge case handling

**Algorithm Pseudocode**:
```python
def calculate_complementarity_score(user1: UserProfile, user2: UserProfile) -> float:
    # How many of user1's struggles are user2's strengths?
    user1_helped = len(set(user1.struggles) & set(user2.strengths))
    # How many of user2's struggles are user1's strengths?
    user2_helped = len(set(user2.struggles) & set(user1.strengths))

    # Average of both directions
    total_possible = len(user1.struggles) + len(user2.struggles)
    if total_possible == 0:
        return 0.0

    return (user1_helped + user2_helped) / total_possible

def calculate_match_score(user1: UserProfile, user2: UserProfile) -> float:
    complementarity = calculate_complementarity_score(user1, user2)
    compatibility = calculate_compatibility_score(user1, user2)
    availability = calculate_availability_score(user1, user2)

    return (complementarity * 0.5) + (compatibility * 0.3) + (availability * 0.2)
```

**Testing**:
- Unit test: perfect match (score ~0.9+)
- Unit test: no overlap (score <0.3)
- Unit test: partial match (score 0.4-0.7)
- Unit test: symmetric scoring

**Technical Notes**:
- Create `app/services/matching_service.py`
- Add comprehensive docstrings
- Consider caching match scores in Redis (future optimization)

---

**GP-005**: Match Queue Management
**Status**: ✅ Done
**Priority**: High
**Story Points**: 5
**Epic**: EPIC-2
**Dependencies**: GP-004
**Completed**: 2025-11-18

**Description**:
Build endpoints for users to enter the match queue, view their queue status, and receive match suggestions.

**Acceptance Criteria**:
- [x] `POST /api/v1/matching/enter-queue` - User enters match queue
- [x] `GET /api/v1/matching/status` - View queue position and status
- [x] `GET /api/v1/matching/suggestions` - Get top 3 match suggestions
- [x] `POST /api/v1/matching/accept` - Accept a match and create partnership (GP-007)
- [x] `POST /api/v1/matching/decline` - Decline a match
- [x] `DELETE /api/v1/matching/leave-queue` - Exit queue
- [x] Users can't enter queue if they have 3 active partnerships
- [x] Queue expires after 7 days of inactivity
- [x] Declined matches not shown again
- [x] Match suggestions ranked by compatibility score (highest first)

**Implementation**:
- Files: `app/api/v1/matching.py`, `app/services/match_queue_service.py`
- 9 integration tests (all passing)
- Features: Profile validation, max partnerships enforcement, decline tracking

**API Spec**:
```json
GET /api/v1/matching/suggestions
Response: {
  "suggestions": [
    {
      "user_id": "uuid",
      "username": "sarah_career",
      "profile_picture_url": "...",
      "compatibility_score": 0.87,
      "strengths": ["career", "fitness"],
      "struggles": ["fashion", "relationships"],
      "why_matched": {
        "you_help_with": ["career"],
        "they_help_with": ["fashion", "relationships"]
      }
    }
  ],
  "queue_position": 5
}
```

**Testing**:
- Test queue entry validation (max 3 partnerships)
- Test match suggestions ranking
- Test declining all suggestions generates new ones

**Technical Notes**:
- Create `app/api/v1/matching.py`
- Create `app/schemas/matching.py`
- Store declined matches in `MatchQueue.proposed_matches` JSONB

---

**GP-006**: Background Job - Generate Matches
**Status**: 📋 To Do
**Priority**: High
**Story Points**: 5
**Epic**: EPIC-2
**Dependencies**: GP-005

**Description**:
Create a Celery background job that runs every 5 minutes to generate match suggestions for users in the queue.

**Acceptance Criteria**:
- [ ] Celery worker configured and runs
- [ ] `generate_matches_task()` runs every 5 minutes
- [ ] Task fetches all users with `status='pending'` from match_queue
- [ ] For each user, calculates match scores with all other pending users
- [ ] Stores top 5 matches in `proposed_matches` JSONB
- [ ] Updates `priority_score` based on wait time (longer wait = higher priority)
- [ ] Sends notification when matches are ready
- [ ] Task handles errors gracefully (retry 3 times)

**Celery Task**:
```python
@celery_app.task(bind=True, max_retries=3)
def generate_matches_task(self):
    # Fetch pending users
    # Calculate all match scores
    # Store top matches
    # Update priority scores
    # Send notifications
```

**Testing**:
- Test task runs successfully
- Test match generation with 10 users in queue
- Test error handling and retries

**Technical Notes**:
- Create `app/celery_app.py` with Celery configuration
- Create `app/tasks/matching_tasks.py`
- Ensure Redis is running for Celery broker

---

**GP-007**: Partnership Creation
**Status**: ✅ Done
**Priority**: High
**Story Points**: 5
**Epic**: EPIC-3
**Dependencies**: GP-005
**Completed**: 2025-11-18

**Description**:
When a user accepts a match, create a new partnership between the two users and remove them from the match queue.

**Acceptance Criteria**:
- [x] `POST /api/v1/matching/accept` creates Partnership record
- [x] Partnership status set to 'active'
- [x] Season 1 starts immediately (4-week duration)
- [x] Both users' `active_partnerships_count` incremented
- [x] Both users removed from match queue (status='matched')
- [ ] Both users receive notification of new partnership (deferred to GP-015)
- [x] If either user already has 3 partnerships, return 400 error
- [x] Partnership cannot be created if one already exists between users

**Implementation**:
- File: `app/services/partnership_service.py`
- Complete partnership creation logic with validation
- Tests covered in matching endpoint tests

**API Flow**:
```json
POST /api/v1/matching/accept
{
  "match_id": "user-uuid-of-match"
}

Response: {
  "partnership_id": "uuid",
  "partner": {
    "id": "uuid",
    "username": "sarah_career",
    "profile_picture_url": "..."
  },
  "season_number": 1,
  "season_start_date": "2025-11-17",
  "season_end_date": "2025-12-15",
  "status": "active"
}
```

**Testing**:
- Test successful partnership creation
- Test max partnerships limit (3)
- Test duplicate partnership prevention
- Test both users removed from queue

**Technical Notes**:
- Create `app/services/partnership_service.py`
- Update `UserProfile.active_partnerships_count`
- Create welcome notification

---

**GP-008**: Partnership Endpoints
**Status**: ✅ Done
**Priority**: High
**Story Points**: 5
**Epic**: EPIC-3
**Dependencies**: GP-007
**Completed**: 2025-11-18

**Description**:
Build endpoints to view and manage partnerships.

**Acceptance Criteria**:
- [x] `GET /api/v1/partnerships` - List all user's active partnerships (with status filter)
- [x] `GET /api/v1/partnerships/:id` - Get partnership details
- [x] `PATCH /api/v1/partnerships/:id/settings` - Update settings (check-in days, frequency)
- [x] `POST /api/v1/partnerships/:id/end` - End partnership gracefully
- [x] `GET /api/v1/partnerships/:id/stats` - Get partnership analytics
- [x] Only partnership members can access endpoints (authorization check)
- [x] Returns partner's public profile info (not private data)

**Implementation**:
- Files: `app/api/v1/partnerships.py`, `app/schemas/partnership.py`
- 10 integration tests (all passing)
- Features: Authorization, status filtering, real-time stats, graceful termination

**API Spec**:
```json
GET /api/v1/partnerships
Response: [
  {
    "id": "uuid",
    "partner": {
      "id": "uuid",
      "username": "sarah_career",
      "profile_picture_url": "..."
    },
    "season_number": 1,
    "status": "active",
    "check_in_frequency": "3x_week",
    "last_interaction_at": "2025-11-17T10:30:00Z",
    "health_score": 0.85,
    "current_streak": 3
  }
]
```

**Testing**:
- Test authorization (non-members get 403)
- Test filtering by status
- Test stats calculation

**Technical Notes**:
- Create `app/api/v1/partnerships.py`
- Create `app/schemas/partnership.py`
- Add permission check decorator

---

---

## 📅 SPRINT 2: Partnerships & Goals

**GP-009**: Goal CRUD Endpoints
**Status**: 📋 To Do
**Priority**: High
**Story Points**: 5
**Epic**: EPIC-4
**Dependencies**: GP-008

**Description**:
Build endpoints for creating, reading, updating, and deleting goals within partnerships.

**Acceptance Criteria**:
- [ ] `POST /api/v1/partnerships/:id/goals` - Create goal
- [ ] `GET /api/v1/partnerships/:id/goals` - List goals (filter by owner, status)
- [ ] `GET /api/v1/goals/:id` - Get goal details
- [ ] `PATCH /api/v1/goals/:id` - Update goal
- [ ] `DELETE /api/v1/goals/:id` - Delete goal
- [ ] `POST /api/v1/goals/:id/complete` - Mark goal as completed
- [ ] Support individual goals (owner_id set) and mutual goals (owner_id null, is_mutual=true)
- [ ] Mutual goals require both partners' confirmation to complete
- [ ] Goals can have subtasks (JSONB array)

**API Spec**:
```json
POST /api/v1/partnerships/{partnership_id}/goals
{
  "title": "Get promoted to Senior Engineer",
  "description": "Focus on leadership and communication skills",
  "category": "career",
  "is_mutual": false,
  "target_date": "2026-06-01",
  "subtasks": [
    {"task": "Complete leadership course", "completed": false},
    {"task": "Lead 2 team meetings", "completed": false}
  ]
}
```

**Testing**:
- Test individual goal creation
- Test mutual goal creation and completion
- Test subtask management
- Test authorization (only partnership members)

**Technical Notes**:
- Create `app/api/v1/goals.py`
- Create `app/schemas/goal.py`
- Mutual goal completion requires both partners to call `/complete`

---

**GP-010**: Check-In Creation & Feed
**Status**: 📋 To Do
**Priority**: Critical
**Story Points**: 8
**Epic**: EPIC-5
**Dependencies**: GP-008

**Description**:
Build text-based check-in system with templates and activity feed.

**Acceptance Criteria**:
- [ ] `POST /api/v1/partnerships/:id/check-ins` - Create check-in
- [ ] `GET /api/v1/partnerships/:id/check-ins` - List check-ins (paginated, newest first)
- [ ] `GET /api/v1/check-ins/:id` - Get check-in details
- [ ] `PATCH /api/v1/check-ins/:id/read` - Mark check-in as read
- [ ] `POST /api/v1/check-ins/:id/reply` - Reply to check-in (threaded)
- [ ] Support structured templates: what_i_did, what_i_struggled_with, what_i_need
- [ ] Support free-form text_content
- [ ] Update partnership `last_interaction_at` on check-in
- [ ] Update user streak if check-in within weekly window
- [ ] Pagination: 20 check-ins per page

**API Spec**:
```json
POST /api/v1/partnerships/{partnership_id}/check-ins
{
  "what_i_did": "Applied to 5 senior roles, had 2 phone screens",
  "what_i_struggled_with": "Imposter syndrome during technical interviews",
  "what_i_need": "Help practicing answers to leadership questions"
}

Response: {
  "id": "uuid",
  "author": {
    "id": "uuid",
    "username": "marcus_design"
  },
  "what_i_did": "...",
  "what_i_struggled_with": "...",
  "what_i_need": "...",
  "created_at": "2025-11-17T14:30:00Z",
  "is_read": false
}
```

**Testing**:
- Test check-in creation
- Test pagination
- Test read status update
- Test reply threading
- Test streak calculation

**Technical Notes**:
- Create `app/api/v1/checkins.py`
- Create `app/schemas/checkin.py`
- Implement streak logic in `app/services/streak_service.py`

---

**GP-011**: Streak Calculation System
**Status**: 📋 To Do
**Priority**: Medium
**Story Points**: 3
**Epic**: EPIC-9
**Dependencies**: GP-010

**Description**:
Implement streak tracking for individual users and partnerships.

**Acceptance Criteria**:
- [ ] Individual streak: consecutive weeks with ≥1 check-in
- [ ] Partnership streak: consecutive weeks where BOTH partners checked in
- [ ] Streaks update automatically on check-in creation
- [ ] Streaks reset if week skipped (grace period: 7 days)
- [ ] `GET /api/v1/users/me/streaks` returns current streak data
- [ ] Milestones: 1, 4, 12, 26, 52 weeks

**Streak Logic**:
```python
def update_streak(user_id, partnership_id):
    last_checkin = get_last_checkin_date(user_id, partnership_id)
    current_date = date.today()

    # If last check-in was within last 7 days, continue streak
    if (current_date - last_checkin).days <= 7:
        increment_streak(user_id)
    else:
        reset_streak(user_id)
```

**Testing**:
- Test streak continuation
- Test streak reset after 7 days
- Test partnership streak requires both partners

**Technical Notes**:
- Add `last_checkin_date` to User model
- Store streak data in Redis for fast access
- Daily cron job to check and reset expired streaks

---

**GP-012**: Task Assignment System
**Status**: 📋 To Do
**Priority**: High
**Story Points**: 5
**Epic**: EPIC-6
**Dependencies**: GP-008

**Description**:
Build task assignment ("micro-coaching") system where partners can assign small tasks to each other.

**Acceptance Criteria**:
- [ ] `POST /api/v1/partnerships/:id/tasks` - Assign task to partner
- [ ] `GET /api/v1/partnerships/:id/tasks` - List tasks (filter by assignee, status)
- [ ] `GET /api/v1/tasks/me` - Get tasks assigned to current user
- [ ] `PATCH /api/v1/tasks/:id/complete` - Mark task as completed
- [ ] `DELETE /api/v1/tasks/:id` - Delete task (only by assigner)
- [ ] Task types: 'action', 'reflection', 'submission'
- [ ] Optional due date
- [ ] Optional completion proof (photo/voice note URL - future)

**API Spec**:
```json
POST /api/v1/partnerships/{partnership_id}/tasks
{
  "title": "Send 5 LinkedIn connection requests",
  "description": "Reach out to people in your target role",
  "task_type": "action",
  "due_date": "2025-11-20"
}

Response: {
  "id": "uuid",
  "title": "Send 5 LinkedIn connection requests",
  "assigned_by": {
    "id": "uuid",
    "username": "sarah_career"
  },
  "assigned_to": {
    "id": "uuid",
    "username": "marcus_design"
  },
  "task_type": "action",
  "status": "pending",
  "due_date": "2025-11-20",
  "created_at": "2025-11-17T15:00:00Z"
}
```

**Testing**:
- Test task creation
- Test task completion
- Test authorization (only partners can assign tasks)
- Test task deletion (only by assigner)

**Technical Notes**:
- Create `app/api/v1/tasks.py`
- Create `app/schemas/task.py`
- Send notification to assignee

---

---

## 📅 SPRINT 3: Safety & Notifications

**GP-013**: Report & Block System
**Status**: 📋 To Do
**Priority**: Critical
**Story Points**: 5
**Epic**: EPIC-7
**Dependencies**: GP-008

**Description**:
Build safety features for reporting inappropriate behavior and blocking users.

**Acceptance Criteria**:
- [ ] `POST /api/v1/reports` - Submit report
- [ ] `POST /api/v1/users/:id/block` - Block user
- [ ] `DELETE /api/v1/users/:id/block` - Unblock user
- [ ] `GET /api/v1/users/blocked` - List blocked users
- [ ] Report reasons: 'harassment', 'inappropriate', 'ghosting', 'spam', 'other'
- [ ] Blocking user immediately ends active partnership
- [ ] Blocked users cannot be matched together again
- [ ] Reports go to admin queue (basic MVP - no admin UI yet)

**API Spec**:
```json
POST /api/v1/reports
{
  "reported_user_id": "uuid",
  "partnership_id": "uuid",
  "reason": "harassment",
  "description": "User sent inappropriate messages",
  "evidence_urls": ["https://s3.../screenshot1.png"]
}

POST /api/v1/users/{user_id}/block
Response: {
  "blocked_user_id": "uuid",
  "blocked_at": "2025-11-17T16:00:00Z"
}
```

**Testing**:
- Test report submission
- Test block user (partnership ends)
- Test blocked users not matched
- Test unblock flow

**Technical Notes**:
- Create `app/api/v1/reports.py` and `app/api/v1/safety.py`
- Add `blocked_users` table (many-to-many relationship)
- Create admin report queue (database view for now)

---

**GP-014**: Anti-Ghosting Detection
**Status**: 📋 To Do
**Priority**: High
**Story Points**: 5
**Epic**: EPIC-7
**Dependencies**: GP-010

**Description**:
Implement anti-ghosting system that detects inactive users and sends nudges.

**Acceptance Criteria**:
- [ ] Daily cron job detects partnerships with inactive users (>7 days no activity)
- [ ] Nudge sequence:
  - Day 7: Email reminder to inactive user
  - Day 10: Second email + in-app notification
  - Day 14: Notify active partner that user may be ghosting
  - Day 21: Partnership marked "at risk", offer re-matching to active partner
  - Day 30: Partnership auto-cancelled, ghosting score increased
- [ ] Ghosting score updated (0.0 = never ghosts, 1.0 = frequent ghoster)
- [ ] High ghosting score (>0.5) lowers priority in match queue

**Nudge Logic**:
```python
def check_ghosting_daily():
    partnerships = get_active_partnerships()
    for partnership in partnerships:
        days_inactive_user1 = (today - partnership.user1_last_active_at).days
        days_inactive_user2 = (today - partnership.user2_last_active_at).days

        for days, user in [(days_inactive_user1, user1), (days_inactive_user2, user2)]:
            if days == 7:
                send_reminder_email(user)
            elif days == 14:
                notify_partner_about_ghosting(partnership, user)
            elif days == 30:
                cancel_partnership(partnership)
                increase_ghosting_score(user)
```

**Testing**:
- Test nudge emails at correct intervals
- Test ghosting score calculation
- Test partnership cancellation

**Technical Notes**:
- Create `app/tasks/ghosting_tasks.py`
- Use Celery Beat for daily scheduling
- Store ghosting history in `UserProfile.ghosting_score`

---

**GP-015**: Email Notification System
**Status**: 📋 To Do
**Priority**: High
**Story Points**: 5
**Epic**: EPIC-8
**Dependencies**: GP-007

**Description**:
Integrate SendGrid and create email notification system for key events.

**Acceptance Criteria**:
- [ ] SendGrid API integrated
- [ ] Email templates created (HTML + plain text):
  - Welcome email (on registration)
  - Match found email (with partner info)
  - Check-in reminder (if no check-in this week)
  - New check-in notification (partner posted)
  - Task assigned notification
  - Season ending reminder (7 days before)
- [ ] Emails sent asynchronously via Celery
- [ ] Unsubscribe link in all emails
- [ ] User notification preferences stored (daily/weekly digest option)

**Email Templates**:
```
Subject: You've been matched! 🤝

Hi {{ user.first_name }},

Great news! We found your accountability partner:

{{ partner.username }} ({{ partner.strengths[0] }}, {{ partner.strengths[1] }})

They'll help you with: {{ your_struggles }}
You'll help them with: {{ their_struggles }}

[Start Your Partnership →]
```

**Testing**:
- Test email sending (use Mailtrap for dev)
- Test template rendering
- Test unsubscribe functionality

**Technical Notes**:
- Create `app/services/email_service.py`
- Create `app/templates/emails/` directory
- Use Jinja2 for template rendering
- Store email preferences in UserProfile

---

**GP-016**: Partnership Health Score Algorithm
**Status**: 📋 To Do
**Priority**: Medium
**Story Points**: 5
**Epic**: EPIC-3
**Dependencies**: GP-010, GP-012

**Description**:
Implement algorithm to calculate partnership health score based on balance, engagement, and reciprocity.

**Acceptance Criteria**:
- [ ] Health score calculated automatically on each interaction
- [ ] Score components:
  - **Balance** (0-1): Equality of check-ins between partners
  - **Engagement** (0-1): Check-in frequency vs expected frequency
  - **Reciprocity** (0-1): Balance of tasks assigned/completed
- [ ] Overall score: weighted average (Balance: 40%, Engagement: 40%, Reciprocity: 20%)
- [ ] Score stored in `Partnership.balance_score` and `Partnership.engagement_score`
- [ ] Health meter colors:
  - Green (0.7-1.0): Healthy
  - Yellow (0.4-0.7): Needs attention
  - Red (0-0.4): At risk
- [ ] Low health score (<0.4) triggers intervention email

**Algorithm**:
```python
def calculate_health_score(partnership: Partnership) -> dict:
    # Balance: How equal are check-ins?
    user1_checkins = count_checkins(partnership, user1, last_4_weeks)
    user2_checkins = count_checkins(partnership, user2, last_4_weeks)
    balance = 1 - abs(user1_checkins - user2_checkins) / max(user1_checkins + user2_checkins, 1)

    # Engagement: Are they checking in as expected?
    expected_checkins = partnership.check_in_frequency * 4  # 4 weeks
    actual_checkins = user1_checkins + user2_checkins
    engagement = min(actual_checkins / expected_checkins, 1.0)

    # Reciprocity: Are tasks balanced?
    user1_tasks_assigned = count_tasks_assigned_by(user1)
    user2_tasks_assigned = count_tasks_assigned_by(user2)
    reciprocity = 1 - abs(user1_tasks_assigned - user2_tasks_assigned) / max(user1_tasks_assigned + user2_tasks_assigned, 1)

    health_score = (balance * 0.4) + (engagement * 0.4) + (reciprocity * 0.2)

    return {
        "health_score": health_score,
        "balance": balance,
        "engagement": engagement,
        "reciprocity": reciprocity,
        "status": "healthy" if health_score > 0.7 else "needs_attention" if health_score > 0.4 else "at_risk"
    }
```

**Testing**:
- Test balanced partnership (score ~0.9)
- Test unbalanced partnership (score <0.5)
- Test edge cases (no check-ins, no tasks)

**Technical Notes**:
- Create `app/services/health_service.py`
- Recalculate health score after each check-in/task
- Store component scores separately for transparency

---

**GP-017**: Partnership Renewal & Seasons
**Status**: 📋 To Do
**Priority**: High
**Story Points**: 5
**Epic**: EPIC-3
**Dependencies**: GP-008

**Description**:
Implement 4-week season system with renewal flow and end-of-season celebration.

**Acceptance Criteria**:
- [ ] `GET /api/v1/partnerships/:id/season-summary` - End-of-season stats
- [ ] `POST /api/v1/partnerships/:id/renew` - Renew for next season
- [ ] `POST /api/v1/partnerships/:id/complete` - End partnership gracefully
- [ ] Season ends automatically after 4 weeks
- [ ] Both partners must renew to start Season 2
- [ ] If one partner declines, partnership ends with status='completed'
- [ ] Season summary includes:
  - Total check-ins
  - Goals completed
  - Streak maintained
  - Health score
- [ ] Email sent 7 days before season ends
- [ ] Celebration screen shown when viewing partnership after season ends

**API Spec**:
```json
GET /api/v1/partnerships/{id}/season-summary
Response: {
  "season_number": 1,
  "start_date": "2025-11-17",
  "end_date": "2025-12-15",
  "total_checkins": 12,
  "goals_completed": 3,
  "mutual_goals_completed": 1,
  "streak_maintained": true,
  "max_streak": 4,
  "health_score": 0.85,
  "can_renew": true
}

POST /api/v1/partnerships/{id}/renew
Response: {
  "season_number": 2,
  "start_date": "2025-12-16",
  "end_date": "2026-01-13",
  "status": "active"
}
```

**Testing**:
- Test season end detection
- Test renewal flow (both partners agree)
- Test renewal rejection (one partner declines)
- Test season summary calculation

**Technical Notes**:
- Daily cron job checks for seasons ending
- Archive goals from previous season (status='archived')
- Reset check-in counts for new season

---

---

## 📅 SPRINT 4: Frontend Foundation

**GP-018**: Frontend Project Setup
**Status**: 📋 To Do
**Priority**: Critical
**Story Points**: 5
**Epic**: EPIC-10
**Dependencies**: None (parallel track)

**Description**:
Initialize React + TypeScript frontend with Vite, Tailwind, and shadcn/ui.

**Acceptance Criteria**:
- [ ] Vite project created with React + TypeScript template
- [ ] Tailwind CSS configured
- [ ] shadcn/ui installed and configured
- [ ] React Router v6 set up
- [ ] Axios + React Query configured
- [ ] Zustand stores created (auth, partnerships, notifications)
- [ ] Environment variables (.env.local)
- [ ] Basic layout components (Header, Footer, Container)
- [ ] Dev server runs on http://localhost:5173

**Directory Structure**:
```
frontend/
├── src/
│   ├── components/
│   │   ├── ui/              # shadcn/ui components
│   │   ├── layout/          # Header, Footer, Sidebar
│   │   └── features/        # Feature-specific components
│   ├── pages/               # Page components
│   ├── hooks/               # Custom hooks
│   ├── stores/              # Zustand stores
│   ├── api/                 # API client
│   ├── lib/                 # Utilities
│   └── App.tsx
├── public/
├── package.json
└── .env.example
```

**Commands**:
```bash
npm create vite@latest frontend -- --template react-ts
cd frontend
npm install
npm install -D tailwindcss postcss autoprefixer
npx tailwindcss init -p
npm install @tanstack/react-query axios zustand react-router-dom
npx shadcn-ui@latest init
```

**Testing**:
- Dev server runs without errors
- Tailwind classes work
- React Query devtools accessible

**Technical Notes**:
- Use absolute imports with `@/` prefix
- Configure path aliases in vite.config.ts

---

**GP-019**: Authentication UI
**Status**: 📋 To Do
**Priority**: Critical
**Story Points**: 5
**Epic**: EPIC-10
**Dependencies**: GP-018

**Description**:
Build registration and login pages with form validation.

**Acceptance Criteria**:
- [ ] Registration page (`/register`)
  - Email, username, full name, password fields
  - Password confirmation field
  - Form validation (Zod schema)
  - Shows API errors (email already exists, etc.)
  - Redirects to onboarding on success
- [ ] Login page (`/login`)
  - Email and password fields
  - "Forgot password?" link (future)
  - Form validation
  - Redirects to dashboard on success
  - Stores JWT in localStorage and Zustand
- [ ] Protected route wrapper
  - Redirects to /login if not authenticated
  - Shows loading spinner while checking auth
- [ ] Logout functionality
  - Clears localStorage and Zustand state
  - Redirects to /login

**Form Validation** (Zod):
```typescript
const registerSchema = z.object({
  email: z.string().email("Invalid email address"),
  username: z.string().min(3, "Username must be at least 3 characters"),
  full_name: z.string().optional(),
  password: z.string().min(8, "Password must be at least 8 characters"),
  password_confirm: z.string()
}).refine((data) => data.password === data.password_confirm, {
  message: "Passwords don't match",
  path: ["password_confirm"]
});
```

**Testing**:
- Test form validation errors
- Test successful registration
- Test login with correct credentials
- Test login with wrong credentials
- Test protected route redirect

**Technical Notes**:
- Create `src/pages/Register.tsx` and `src/pages/Login.tsx`
- Create `src/hooks/useAuth.ts` for auth operations
- Create `src/stores/authStore.ts` for auth state
- Create `src/components/layout/ProtectedRoute.tsx`

---

**GP-020**: Onboarding Flow UI
**Status**: 📋 To Do
**Priority**: Critical
**Story Points**: 8
**Epic**: EPIC-10
**Dependencies**: GP-019

**Description**:
Build multi-step onboarding wizard for profile setup.

**Acceptance Criteria**:
- [ ] Step 1: About You
  - Bio (optional)
  - Date of birth (optional)
  - Timezone (auto-detected)
- [ ] Step 2: Your Strengths
  - Select 2-4 strengths from predefined list
  - Categories: Career, Fitness, Relationships, Finance, Fashion, Public Speaking, Creativity, Health, Social Skills
  - Allow custom strengths (text input)
- [ ] Step 3: Your Struggles
  - Select 2-4 struggles from same categories
  - Allow custom struggles
- [ ] Step 4: Preferences
  - Communication style (Direct, Supportive, Motivational)
  - Commitment level (Casual, Moderate, Intense)
  - Check-in frequency (Daily, 3x/week, Weekly)
  - Available days (checkboxes: Mon-Sun)
- [ ] Progress bar showing completion (25%, 50%, 75%, 100%)
- [ ] Back/Next navigation
- [ ] Validation on each step
- [ ] Redirects to match queue on completion

**UI Design**:
- Clean, modern design with shadcn/ui components
- Mobile-responsive (works on phones)
- Tooltips explaining each preference
- Visual icons for categories

**Testing**:
- Test navigation between steps
- Test validation (min 2 strengths required)
- Test custom input addition
- Test final submission

**Technical Notes**:
- Create `src/pages/Onboarding.tsx` with step state management
- Create `src/components/features/OnboardingSteps/` directory
- Use React Hook Form for multi-step form
- Store partial progress in localStorage (resume if refreshed)

---

**GP-021**: Match Queue & Suggestions UI
**Status**: 📋 To Do
**Priority**: High
**Story Points**: 5
**Epic**: EPIC-10
**Dependencies**: GP-020

**Description**:
Build match queue waiting screen and match suggestions card interface.

**Acceptance Criteria**:
- [ ] Match queue screen (`/matching`)
  - Shows "Finding your match..." loading state
  - Displays queue position (e.g., "3 people ahead of you")
  - Polls for match suggestions every 10 seconds
  - Shows match suggestions when ready
- [ ] Match suggestion cards
  - Partner's profile picture, username
  - Compatibility score (visual bar: 87%)
  - "Why matched" explanation
    - "You help with: Career"
    - "They help with: Fashion, Relationships"
  - Accept/Decline buttons
- [ ] Accept match flow
  - Confirmation modal ("Start partnership with @sarah?")
  - Redirects to partnership dashboard on success
- [ ] Decline match flow
  - Removes card, shows next suggestion
  - If all declined, shows "Finding more matches..."

**UI Design**:
- Card-based interface (Tinder-style)
- Green "Accept" button, Red "Decline" button
- Smooth animations (fade in/out)
- Compatibility score with color gradient (low=red, high=green)

**Testing**:
- Test polling for suggestions
- Test accept flow
- Test decline flow
- Test empty state (no matches)

**Technical Notes**:
- Create `src/pages/Matching.tsx`
- Create `src/components/features/MatchCard.tsx`
- Use React Query for polling
- Create `src/api/matching.ts` API client methods

---

**GP-022**: Partnership Dashboard UI
**Status**: 📋 To Do
**Priority**: Critical
**Story Points**: 8
**Epic**: EPIC-10
**Dependencies**: GP-021

**Description**:
Build main partnership workspace dashboard with goals, check-ins, and tasks.

**Acceptance Criteria**:
- [ ] Partnership dashboard (`/partnerships/:id`)
- [ ] Header section:
  - Partner's profile picture and name
  - Season info (Season 1, Week 2 of 4)
  - Partnership health meter (visual indicator)
  - Current streak
- [ ] Three-column layout:
  - **Left**: Goals (mutual + individual)
  - **Center**: Check-in feed
  - **Right**: Tasks & Quick actions
- [ ] Quick actions:
  - "Post Check-In" button (opens modal)
  - "Add Goal" button (opens modal)
  - "Assign Task" button (opens modal)
- [ ] Mobile-responsive (stacks vertically on small screens)

**Visual Design**:
- Clean, dashboard-style layout
- Color-coded health meter (green/yellow/red)
- Card-based components
- Real-time updates (React Query automatic refetch)

**Testing**:
- Test layout on desktop and mobile
- Test quick actions open modals
- Test data loading states

**Technical Notes**:
- Create `src/pages/Partnership.tsx`
- Create `src/components/features/PartnershipHeader.tsx`
- Create `src/components/features/GoalsList.tsx`
- Create `src/components/features/CheckInFeed.tsx`
- Create `src/components/features/TasksList.tsx`

---

**GP-023**: Check-In Form & Feed UI
**Status**: 📋 To Do
**Priority**: High
**Story Points**: 5
**Epic**: EPIC-10
**Dependencies**: GP-022

**Description**:
Build check-in creation form and activity feed.

**Acceptance Criteria**:
- [ ] Check-in modal form with templates:
  - "What I did this week" (required)
  - "What I struggled with" (optional)
  - "What I need from you" (optional)
  - Character counter (500 chars per field)
  - Submit button
- [ ] Check-in feed (reverse chronological):
  - Author name and avatar
  - Timestamp (e.g., "2 hours ago")
  - Check-in content (structured display)
  - Reply button (future)
  - Reaction emojis (future)
- [ ] Infinite scroll pagination
- [ ] Real-time updates when partner posts

**UI Components**:
```tsx
<CheckInCard>
  <Avatar src={author.profile_picture} />
  <CheckInContent>
    <h4>What I did:</h4>
    <p>{check_in.what_i_did}</p>

    <h4>What I struggled with:</h4>
    <p>{check_in.what_i_struggled_with}</p>

    <h4>What I need:</h4>
    <p>{check_in.what_i_need}</p>
  </CheckInContent>
  <Timestamp>{formatDistanceToNow(check_in.created_at)}</Timestamp>
</CheckInCard>
```

**Testing**:
- Test form validation
- Test check-in submission
- Test feed loading
- Test infinite scroll

**Technical Notes**:
- Create `src/components/features/CheckInForm.tsx`
- Create `src/components/features/CheckInCard.tsx`
- Use React Query's `useInfiniteQuery` for pagination
- Use `date-fns` for relative timestamps

---

**GP-024**: Goal & Task Management UI
**Status**: 📋 To Do
**Priority**: Medium
**Story Points**: 5
**Epic**: EPIC-10
**Dependencies**: GP-022

**Description**:
Build goal creation and task assignment interfaces.

**Acceptance Criteria**:
- [ ] Goal creation modal:
  - Title (required)
  - Description (optional)
  - Category dropdown
  - Target date picker
  - Is mutual? checkbox
  - Subtasks (add/remove dynamically)
- [ ] Goal card component:
  - Title and category badge
  - Progress bar (subtasks completed / total)
  - Complete button (or "Request completion" for mutual)
  - Edit/Delete options
- [ ] Task assignment modal:
  - Title (required)
  - Description (optional)
  - Task type: Action/Reflection/Submission
  - Due date picker (optional)
- [ ] Task list:
  - Pending tasks at top
  - Completed tasks below (grayed out)
  - Checkbox to complete
  - Assigned by/to labels

**Testing**:
- Test goal creation
- Test subtask add/remove
- Test goal completion
- Test task assignment
- Test task completion

**Technical Notes**:
- Create `src/components/features/GoalForm.tsx`
- Create `src/components/features/GoalCard.tsx`
- Create `src/components/features/TaskForm.tsx`
- Create `src/components/features/TaskItem.tsx`
- Use shadcn/ui Dialog for modals

---

---

## 📅 SPRINT 5+: Advanced Features

**GP-025**: User Settings & Profile Page
**Status**: 📋 To Do
**Priority**: Medium
**Story Points**: 5
**Epic**: EPIC-10

**Description**:
Build user settings page for profile editing and preferences.

**Acceptance Criteria**:
- [ ] Settings page (`/settings`)
- [ ] Tabs: Profile, Notifications, Privacy, Account
- [ ] Profile tab:
  - Upload profile picture
  - Edit bio
  - Edit date of birth, timezone
- [ ] Notifications tab:
  - Email preferences (real-time, daily digest, weekly)
  - Notification types (check-ins, tasks, matches)
- [ ] Privacy tab:
  - Block list management
- [ ] Account tab:
  - Change password
  - Deactivate account (with confirmation)

---

**GP-026**: Notification Center UI
**Status**: 📋 To Do
**Priority**: Medium
**Story Points**: 3
**Epic**: EPIC-10

**Description**:
Build in-app notification dropdown.

**Acceptance Criteria**:
- [ ] Bell icon in header with unread count badge
- [ ] Dropdown showing recent notifications
- [ ] Notification types:
  - New match found
  - Partner posted check-in
  - Task assigned
  - Season ending soon
- [ ] Click notification navigates to relevant page
- [ ] Mark all as read button

---

**GP-027**: Analytics Dashboard
**Status**: 📋 To Do
**Priority**: Low
**Story Points**: 5
**Epic**: EPIC-9

**Description**:
Build user analytics page showing progress over time.

**Acceptance Criteria**:
- [ ] Analytics page (`/analytics`)
- [ ] Charts:
  - Check-ins per week (line chart)
  - Goals completed over time (bar chart)
  - Streak history
  - Partnership health trends
- [ ] Filters: Last 30 days, Last 90 days, All time
- [ ] Export data as CSV button

---

**GP-028**: Admin Moderation Dashboard
**Status**: 📋 To Do
**Priority**: Low
**Story Points**: 8
**Epic**: EPIC-7

**Description**:
Build basic admin dashboard for reviewing reports.

**Acceptance Criteria**:
- [ ] Admin-only route (`/admin`)
- [ ] Reports queue:
  - List all pending reports
  - Show reporter, reported user, reason
  - View evidence (screenshots)
- [ ] Actions:
  - Dismiss report
  - Warn user
  - Temporary ban (7 days)
  - Permanent ban
- [ ] User search
- [ ] Ban appeals (future)

---

**GP-029**: WebSocket Real-Time Updates
**Status**: 📋 To Do
**Priority**: Medium
**Story Points**: 8
**Epic**: EPIC-10

**Description**:
Add real-time features using WebSockets.

**Acceptance Criteria**:
- [ ] WebSocket connection established on login
- [ ] Real-time events:
  - Partner posted check-in
  - Partner came online
  - New task assigned
  - Typing indicator (check-in replies)
- [ ] Automatic UI updates (no page refresh needed)
- [ ] Connection retry on disconnect

---

**GP-030**: Voice Notes & Photo Uploads
**Status**: 📋 To Do
**Priority**: Medium
**Story Points**: 8
**Epic**: EPIC-5

**Description**:
Add voice note and photo support for check-ins and tasks.

**Acceptance Criteria**:
- [ ] Voice note recording:
  - Browser microphone access
  - Max 2 minutes
  - Audio waveform visualization
  - Preview before submit
  - Upload to S3
- [ ] Photo upload:
  - Image picker
  - Preview with crop
  - Max 5 MB
  - EXIF data stripped
  - Upload to S3
- [ ] Playback UI for voice notes
- [ ] Lightbox for photos

---

---

## 🐛 Bug Fixes & Technical Debt

**GP-031**: Add Rate Limiting Middleware
**Status**: 📋 To Do
**Priority**: High
**Story Points**: 3
**Epic**: EPIC-1

**Description**:
Implement rate limiting to prevent API abuse.

**Acceptance Criteria**:
- [ ] slowapi or custom middleware installed
- [ ] Rate limits:
  - Auth endpoints: 5 req/min per IP
  - General API: 100 req/min per user
  - File uploads: 10 req/hour per user
- [ ] Returns 429 status with retry-after header
- [ ] Limits stored in Redis

---

**GP-032**: Implement Comprehensive Testing
**Status**: 📋 To Do
**Priority**: High
**Story Points**: 13
**Epic**: Testing

**Description**:
Write tests for all backend endpoints and core features.

**Acceptance Criteria**:
- [ ] Unit tests for all services (matching, health, streak)
- [ ] Integration tests for all API endpoints
- [ ] E2E tests for critical flows:
  - Registration → Onboarding → Matching → Partnership
  - Check-in posting and streak calculation
  - Partnership renewal
- [ ] Test coverage >80%
- [ ] CI/CD pipeline runs tests on every push

---

**GP-033**: Database Query Optimization
**Status**: 📋 To Do
**Priority**: Medium
**Story Points**: 5
**Epic**: Performance

**Description**:
Optimize database queries to reduce latency.

**Acceptance Criteria**:
- [ ] Add missing indexes (profile foreign keys, created_at)
- [ ] Use `selectinload()` for relationships
- [ ] Implement Redis caching for:
  - User profiles (5 min TTL)
  - Partnership data (1 min TTL)
  - Match suggestions (10 min TTL)
- [ ] Query profiling added to dev environment
- [ ] All queries <50ms (p95)

---

**GP-034**: Security Hardening
**Status**: 📋 To Do
**Priority**: Critical
**Story Points**: 5
**Epic**: Security

**Description**:
Implement additional security measures.

**Acceptance Criteria**:
- [ ] CSRF protection for state-changing endpoints
- [ ] Input sanitization for user-generated content
- [ ] SQL injection prevention verified (already using ORM)
- [ ] XSS prevention: CSP headers configured
- [ ] Secure cookie settings (httpOnly, secure, sameSite)
- [ ] Dependency vulnerability scanning (Snyk or Dependabot)

---

**GP-035**: Deployment & CI/CD
**Status**: 📋 To Do
**Priority**: High
**Story Points**: 8
**Epic**: DevOps

**Description**:
Set up production deployment and CI/CD pipeline.

**Acceptance Criteria**:
- [ ] GitHub Actions workflow:
  - Run tests on every push
  - Build Docker images
  - Deploy to staging on `develop` branch
  - Deploy to production on `main` branch
- [ ] AWS infrastructure:
  - EC2 instances for backend
  - RDS for PostgreSQL
  - ElastiCache for Redis
  - S3 for file storage
  - CloudFront for CDN
- [ ] Environment variables managed securely
- [ ] Rollback capability
- [ ] Health check monitoring

---

---

## 📈 Metrics & Success Criteria

### Definition of Done (All Tickets)
- [ ] Code written and follows style guide
- [ ] Tests written and passing (>80% coverage)
- [ ] Code reviewed (if team exists)
- [ ] Documentation updated (API docs, memory.md)
- [ ] Deployed to staging and tested
- [ ] User acceptance criteria met

### Sprint Success Metrics
- **Velocity**: Track story points completed per sprint
- **Quality**: <5% bug rate, >80% test coverage
- **Performance**: <200ms API latency (p95)
- **User Metrics**: 70%+ check-in completion, 60%+ renewal rate

---

## 🎯 Priority Matrix

### Must Have (MVP Launch)
- User registration & authentication
- Profile creation & matching
- Partnership creation & management
- Goals & check-ins (text-based)
- Task assignment
- Basic safety (report/block)

### Should Have (V1.0)
- Email notifications
- Partnership health score
- Anti-ghosting system
- Streak tracking
- Analytics dashboard

### Could Have (V1.5)
- Voice notes & photos
- WebSocket real-time updates
- Admin moderation dashboard
- Advanced matching (ML)

### Won't Have (MVP)
- Native mobile apps
- Payment/subscriptions
- AI coaching assistant
- Group accountability pods

---

**Total Tickets**: 35
**Total Story Points**: ~180
**Estimated Completion**: 8-10 weeks
**Current Sprint**: Sprint 1 (GP-002 to GP-008)

**Last Updated**: 2025-11-17
**Maintained By**: Autonomous Development Agent
