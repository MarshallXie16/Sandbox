# User Stories: GrowthPact

## User Personas

### Primary Personas

**Sarah - The Career Climber**
- Age: 26
- Role: Junior Software Engineer
- Struggles: Public speaking, professional networking, personal branding
- Excels: Technical skills, problem-solving, coding
- Goals: Get promoted to senior engineer within 1 year
- Motivation: Wants structured accountability without expensive coaching

**Marcus - The Career Pivoter**
- Age: 32
- Role: Fashion Buyer transitioning to UX Design
- Struggles: Learning to code, tech industry norms
- Excels: Visual design, personal style, creative thinking
- Goals: Land first UX role in 6 months
- Motivation: Needs someone who understands struggle + can teach

**Alex - The Fitness Enthusiast**
- Age: 29
- Role: Marketing Manager
- Struggles: Career advancement, salary negotiation
- Excels: Fitness, healthy habits, discipline
- Goals: Become marketing director, negotiate 20% raise
- Motivation: Will help with fitness if someone helps with career

---

## Epic 1: User Onboarding

### Story 1.1: Account Creation
**As a** new user
**I want to** create an account with email and password
**So that** I can access the platform securely

**Acceptance Criteria:**
- [ ] User can enter email, password, and confirm password
- [ ] Email validation (format, uniqueness)
- [ ] Password requirements: min 8 chars, uppercase, lowercase, number
- [ ] Error messages for invalid inputs
- [ ] Confirmation email sent upon registration
- [ ] Redirect to onboarding after successful registration

**Technical Notes:**
- POST `/api/v1/auth/register`
- Bcrypt password hashing
- JWT tokens generated on registration

---

### Story 1.2: Profile Setup
**As a** newly registered user
**I want to** set up my profile with strengths and struggles
**So that** I can be matched with compatible partners

**Acceptance Criteria:**
- [ ] User selects 2-4 strengths from predefined categories
- [ ] User selects 2-4 struggles from predefined categories
- [ ] Categories: Career, Fitness, Relationships, Finance, Fashion, Public Speaking, Creativity, Health, Social Skills
- [ ] User can add custom strength/struggle (text input)
- [ ] User sets communication style (Direct, Supportive, Motivational)
- [ ] User sets commitment level (Casual, Moderate, Intense)
- [ ] User sets preferred check-in frequency (Daily, 3x/week, Weekly)
- [ ] Profile saved and user redirected to matching queue

**UI/UX:**
- Multi-step form (3 steps: About You, Your Strengths, Your Struggles)
- Progress bar showing completion
- Skip option available (default values used)

---

### Story 1.3: Email Verification
**As a** registered user
**I want to** verify my email address
**So that** I can access all platform features and be trusted

**Acceptance Criteria:**
- [ ] Verification email sent with unique token link
- [ ] Clicking link verifies account
- [ ] Verified badge displayed on profile
- [ ] Unverified users reminded to verify (banner)
- [ ] Resend verification email option

---

## Epic 2: Matching & Partnership Creation

### Story 2.1: Enter Match Queue
**As a** user who has completed onboarding
**I want to** enter the matching queue
**So that** I can be paired with a compatible partner

**Acceptance Criteria:**
- [ ] User enters queue automatically after profile setup
- [ ] User sees "Finding your match..." loading state
- [ ] Queue position displayed (optional: "3 ahead of you")
- [ ] Estimated wait time shown
- [ ] User can exit queue (with confirmation)

**Technical Notes:**
- Match queue table tracks users awaiting matches
- Background job runs every 5 minutes to generate matches
- Priority score based on wait time + profile completeness

---

### Story 2.2: Review Match Suggestions
**As a** user in the match queue
**I want to** review suggested partners
**So that** I can choose someone I'm compatible with

**Acceptance Criteria:**
- [ ] User sees 1-3 match suggestions
- [ ] Each suggestion shows:
  - Partner's name, profile picture
  - Compatibility score (e.g., 85%)
  - Shared/complementary strengths and struggles
  - Communication style and commitment level
  - Bio snippet
- [ ] User can "Accept" or "Pass" on each suggestion
- [ ] If user passes all, new suggestions generated
- [ ] If user accepts, partner receives notification

**Compatibility Display:**
- "You excel in **Career**, they need help with **Career**"
- "They excel in **Fashion**, you need help with **Fashion**"
- "Mutual commitment: Moderate"

---

### Story 2.3: Accept Partnership
**As a** user who received a match request
**I want to** review and accept/decline the partnership
**So that** I can start working with a compatible partner

**Acceptance Criteria:**
- [ ] User receives notification (email + in-app)
- [ ] User sees partner's profile and compatibility details
- [ ] User can accept or decline
- [ ] If accepted, partnership is created
- [ ] Both users redirected to partnership workspace
- [ ] Welcome message sent to both partners

**Edge Cases:**
- User already has 3 active partnerships → show upgrade prompt
- Partner declines → user re-enters queue

---

## Epic 3: Partnership Workspace ("The Pact")

### Story 3.1: View Partnership Dashboard
**As a** user in an active partnership
**I want to** see our shared workspace
**So that** I can track our progress and collaborate

**Acceptance Criteria:**
- [ ] Dashboard displays:
  - Partner's name, profile picture, last active time
  - Partnership season (e.g., "Season 1, Week 2 of 4")
  - Current streak (days both partners checked in)
  - Upcoming check-in days
  - Recent activity feed
- [ ] Navigation to Goals, Check-Ins, Tasks tabs
- [ ] Quick actions: "Post Check-In", "Add Goal", "Assign Task"

**Design:**
- Clean, two-column layout
- Partner info on left, activity feed on right
- Visual progress bar for season completion

---

### Story 3.2: Set Mutual Goals
**As a** partnership member
**I want to** create mutual goals for our partnership
**So that** we have shared accountability targets

**Acceptance Criteria:**
- [ ] Either partner can create a mutual goal
- [ ] Mutual goal requires both partners' approval
- [ ] Goal includes: title, description, target date
- [ ] Both partners can mark subtasks as complete
- [ ] Goal completion requires both partners' confirmation
- [ ] Celebration animation when mutual goal completed

**Examples:**
- "Check in 3 times per week"
- "Complete first 4-week season together"
- "Both achieve one personal goal by end of season"

---

### Story 3.3: Set Individual Goals
**As a** partnership member
**I want to** create personal goals visible to my partner
**So that** my partner can hold me accountable

**Acceptance Criteria:**
- [ ] User creates goal with title, description, category, target date
- [ ] Goal visible to partner (read-only)
- [ ] User can add subtasks
- [ ] User marks goal as complete
- [ ] Partner receives notification when goal completed
- [ ] Goal history preserved after completion

**Categories:**
- Career, Fitness, Relationships, Finance, Creativity, Health, Personal Growth

---

## Epic 4: Check-Ins & Communication

### Story 4.1: Post Text Check-In
**As a** partnership member
**I want to** post a check-in update
**So that** my partner knows my progress and struggles

**Acceptance Criteria:**
- [ ] User fills out check-in form with:
  - "What I did this week" (required)
  - "What I struggled with" (optional)
  - "What I need from you" (optional)
  - Free-form notes (optional)
- [ ] Character limits: 500 per field
- [ ] Partner receives notification (email + in-app)
- [ ] Check-in appears in activity feed
- [ ] Streak updated if within check-in window

**Templates Provided:**
- Career: "Applied to X jobs, had Y interviews..."
- Fitness: "Worked out X times, hit Y goal..."
- Fashion: "Tried new outfit styles, need feedback on..."

---

### Story 4.2: Respond to Check-In
**As a** partnership member
**I want to** respond to my partner's check-in
**So that** I can provide support and accountability

**Acceptance Criteria:**
- [ ] User sees partner's check-in in feed
- [ ] User can reply with text (thread-style)
- [ ] User can react with emoji (🔥, 💪, ❤️, 👏)
- [ ] Partner notified of reply
- [ ] Replies shown chronologically under check-in

---

### Story 4.3: Upload Voice Note Check-In
**As a** partnership member
**I want to** record a voice note instead of typing
**So that** I can share updates more naturally

**Acceptance Criteria:**
- [ ] User clicks "Record Voice Note" button
- [ ] Browser requests microphone permission
- [ ] User can record up to 2 minutes
- [ ] Audio waveform displayed during recording
- [ ] User can preview before submitting
- [ ] Voice note uploaded to S3, URL saved
- [ ] Partner can play voice note in-app
- [ ] Playback controls: play/pause, speed (1x, 1.5x, 2x)

**Technical:**
- WebRTC API for recording
- Format: MP3 or M4A
- Max file size: 5 MB

---

### Story 4.4: Submit Photo for Task
**As a** partnership member
**I want to** upload a photo as proof of task completion
**So that** my partner can verify my progress

**Acceptance Criteria:**
- [ ] User selects task to complete
- [ ] User uploads photo (JPEG, PNG, WebP)
- [ ] Image preview shown before submission
- [ ] Max file size: 5 MB
- [ ] EXIF data stripped for privacy
- [ ] Partner sees photo in task completion notification

**Use Cases:**
- Fashion help: "Here's my outfit for the presentation"
- Fitness: "Completed today's workout (gym selfie)"
- Career: "Attended networking event (photo with speaker)"

---

## Epic 5: Task Assignment (Micro-Coaching)

### Story 5.1: Assign Task to Partner
**As a** partnership member
**I want to** assign a small task to my partner
**So that** I can help them make progress on their goals

**Acceptance Criteria:**
- [ ] User clicks "Assign Task" button
- [ ] User enters task title and description
- [ ] User selects due date (optional)
- [ ] User selects task type: Action, Reflection, Submission
- [ ] Partner receives notification
- [ ] Task appears in partner's task list

**Examples:**
- Action: "Send 5 LinkedIn connection requests"
- Reflection: "Write 3 sentences about your ideal job"
- Submission: "Record 30-second intro video"

---

### Story 5.2: Complete Assigned Task
**As a** partnership member
**I want to** complete tasks assigned by my partner
**So that** I make progress and my partner sees my effort

**Acceptance Criteria:**
- [ ] User sees task in "My Tasks" list
- [ ] User marks task as complete (checkbox)
- [ ] If task requires submission, user uploads photo/voice note
- [ ] Partner receives completion notification
- [ ] Task moved to "Completed" section
- [ ] Both partners earn points/achievements

---

## Epic 6: Safety & Trust

### Story 6.1: Report Inappropriate Behavior
**As a** user experiencing harassment
**I want to** report my partner's behavior
**So that** the platform can take action

**Acceptance Criteria:**
- [ ] User clicks "Report" button on partnership page
- [ ] User selects reason: Harassment, Inappropriate Content, Ghosting, Spam, Other
- [ ] User provides description (required, min 50 chars)
- [ ] User can upload screenshots (optional)
- [ ] Report submitted to admin queue
- [ ] User receives confirmation email
- [ ] Partnership automatically paused pending review

**Admin Flow:**
- Admin reviews report within 24 hours
- Admin can: warn user, temp ban, permanent ban, or dismiss
- Both parties notified of outcome

---

### Story 6.2: Block User
**As a** user who feels unsafe
**I want to** block my partner immediately
**So that** they cannot contact me

**Acceptance Criteria:**
- [ ] User clicks "Block User" button
- [ ] Confirmation modal shown (irreversible action)
- [ ] User confirms block
- [ ] Partnership immediately ended
- [ ] Blocked user cannot send messages or see user's profile
- [ ] Blocked user cannot be matched with user again
- [ ] User re-enters match queue (if < 3 active partnerships)

---

### Story 6.3: Partnership Health Meter
**As a** partnership member
**I want to** see our partnership health score
**So that** I know if the relationship is balanced

**Acceptance Criteria:**
- [ ] Health meter displayed on partnership dashboard
- [ ] Score based on:
  - Balance: Are both partners contributing equally?
  - Engagement: Are both partners active?
  - Reciprocity: Are tasks and check-ins balanced?
- [ ] Visual indicator: Green (healthy), Yellow (needs attention), Red (at risk)
- [ ] Tooltip explains score components
- [ ] Suggestions for improvement shown if score < 0.6

**Algorithm:**
- Balance = |user1_checkins - user2_checkins| / total_checkins
- Engagement = (checkins_this_week / expected_checkins)
- Reciprocity = |user1_tasks_completed - user2_tasks_completed| / total_tasks

---

## Epic 7: Partnership Renewal & Seasons

### Story 7.1: End-of-Season Celebration
**As a** partnership member completing a 4-week season
**I want to** celebrate our achievements
**So that** I feel accomplished and motivated to continue

**Acceptance Criteria:**
- [ ] At end of 4 weeks, both partners see celebration screen
- [ ] Screen displays:
  - Total check-ins completed
  - Goals achieved
  - Streak maintained
  - Tasks completed
  - Partnership health score
- [ ] Confetti animation 🎉
- [ ] Option to share achievements to social media
- [ ] Prompt to renew partnership or part ways

---

### Story 7.2: Renew Partnership
**As a** partnership member who enjoyed the season
**I want to** renew our partnership for another 4 weeks
**So that** we can continue supporting each other

**Acceptance Criteria:**
- [ ] Both partners must agree to renew
- [ ] If one declines, partnership ends gracefully
- [ ] If both agree:
  - Season number increments (Season 2, Season 3...)
  - New 4-week cycle starts
  - Previous goals archived
  - New mutual goals can be set
- [ ] Partnership history preserved

---

### Story 7.3: End Partnership Gracefully
**As a** partnership member who wants to move on
**I want to** end the partnership without hard feelings
**So that** I can find a new partner

**Acceptance Criteria:**
- [ ] User selects "Don't renew" at end of season
- [ ] Partner notified with kind message
- [ ] Partnership marked as "Completed" (not "Cancelled")
- [ ] Both users can leave optional feedback
- [ ] Both users re-enter match queue (if < 3 active)
- [ ] Partnership viewable in history (read-only)

---

## Epic 8: Gamification & Engagement

### Story 8.1: Track Streaks
**As a** user
**I want to** see my check-in streak
**So that** I stay motivated to maintain consistency

**Acceptance Criteria:**
- [ ] Individual streak: consecutive weeks with ≥1 check-in
- [ ] Partnership streak: consecutive weeks both partners checked in
- [ ] Streak displayed prominently on dashboard
- [ ] Streak milestones: 1 week, 4 weeks, 12 weeks, 26 weeks, 52 weeks
- [ ] Achievement unlocked at each milestone
- [ ] Streak reset if week skipped (with grace period explanation)

---

### Story 8.2: Earn Achievements
**As a** user completing milestones
**I want to** unlock achievements
**So that** I feel recognized and gamified

**Achievements:**
- 🎯 "First Goal" - Set your first goal
- 📝 "First Check-In" - Post your first check-in
- 🤝 "Partnership Formed" - Match with your first partner
- 🔥 "4-Week Streak" - Check in for 4 consecutive weeks
- 🏆 "Goal Crusher" - Complete 5 goals
- 💪 "Helpful Partner" - Assign 10 tasks
- 🎉 "Renewal Master" - Renew partnership 3 times
- ⭐ "Verified" - Complete email and phone verification

**Display:**
- Badge collection page
- Badges shown on profile
- Share achievements to social media

---

### Story 8.3: View Analytics Dashboard
**As a** user
**I want to** see my progress over time
**So that** I can reflect on my growth

**Acceptance Criteria:**
- [ ] Dashboard shows:
  - Total check-ins (weekly chart)
  - Goals completed vs in-progress
  - Current streaks (all partnerships)
  - Partnership health scores (all partnerships)
  - Time in platform (days since registration)
- [ ] Filter by date range: Last 7 days, 30 days, All time
- [ ] Export data as PDF or CSV

---

## Epic 9: Notifications & Reminders

### Story 9.1: Receive Check-In Reminder
**As a** user who hasn't checked in this week
**I want to** receive a reminder
**So that** I don't break my streak

**Acceptance Criteria:**
- [ ] Email sent on check-in day if no check-in posted
- [ ] Reminder sent 24 hours before check-in deadline
- [ ] Reminder includes:
  - Partnership name
  - Days until deadline
  - Quick link to post check-in
- [ ] User can customize reminder timing in settings
- [ ] User can disable reminders

---

### Story 9.2: Receive Partnership Activity Notifications
**As a** user
**I want to** be notified when my partner is active
**So that** I stay engaged with the partnership

**Notification Triggers:**
- Partner posted a check-in
- Partner completed a goal
- Partner assigned you a task
- Partner completed your assigned task
- Partnership health score dropped below 0.6
- Season ending in 7 days
- Partner hasn't checked in in 7 days (anti-ghosting nudge)

**Channels:**
- In-app notification center
- Email (configurable frequency: real-time, daily digest, weekly digest)
- Browser push notifications (V1.0+)

---

## Epic 10: Freemium & Monetization (V1.0+)

### Story 10.1: Free Tier Limitations
**As a** free user
**I want to** understand what I get for free
**So that** I know when to upgrade

**Free Tier:**
- 1 active partnership
- Basic check-in templates
- Goal tracking (up to 5 active goals)
- Task assignment
- Email notifications
- Basic analytics

---

### Story 10.2: Upgrade to Pro
**As a** user who wants more partnerships
**I want to** upgrade to Pro
**So that** I can have up to 3 active partnerships

**Pro Tier ($9.99/month):**
- 3 active partnerships
- AI coaching assistant
- Advanced analytics
- Voice note check-ins (unlimited)
- Priority matching
- Custom check-in templates
- Partnership health predictions

**Upgrade Flow:**
- User clicks "Upgrade to Pro" button
- Stripe Checkout modal opens
- User enters payment info
- Subscription activated immediately
- User can now create 2 more partnerships

---

## Non-Functional User Stories

### Story NF.1: Fast Load Times
**As a** user
**I want to** see pages load in under 2 seconds
**So that** I have a smooth experience

**Acceptance Criteria:**
- [ ] First Contentful Paint < 1.5s
- [ ] Time to Interactive < 3s
- [ ] API responses < 200ms (p95)

---

### Story NF.2: Mobile-Friendly Design
**As a** mobile user
**I want to** use the app on my phone
**So that** I can check in on the go

**Acceptance Criteria:**
- [ ] Responsive design for screens 320px+
- [ ] Touch-friendly buttons (min 44x44px)
- [ ] Mobile navigation (bottom nav or hamburger)
- [ ] Works offline for reading check-ins (PWA)

---

### Story NF.3: Accessible Interface
**As a** user with visual impairment
**I want to** use a screen reader
**So that** I can navigate the app

**Acceptance Criteria:**
- [ ] WCAG 2.1 Level AA compliance
- [ ] All images have alt text
- [ ] Keyboard navigation works
- [ ] Color contrast ratio ≥ 4.5:1
- [ ] ARIA labels on interactive elements

---

**Version**: 1.0
**Last Updated**: 2025-11-17
**Status**: Active Development
