# GrowthPact

**A mutual accountability platform where users with complementary strengths become each other's growth buddies.**

🌱 Find partners who excel where you struggle
🤝 Structured tools for long-lasting partnerships
🔥 Anti-ghosting and anti-creep systems built-in
📊 Track progress with streaks, goals, and analytics

---

## Quick Start (Local Development)

### Prerequisites
- Python 3.11+
- Node.js 18 LTS
- Docker & Docker Compose
- PostgreSQL 15+ (via Docker)
- Redis 7+ (via Docker)

### 1. Clone and Setup

```bash
cd accountability-partner-app

# Copy environment files
cp backend/.env.example backend/.env
cp frontend/.env.example frontend/.env

# Edit backend/.env with your settings (database URL, secret key, etc.)
```

### 2. Start Services with Docker Compose

```bash
# Start PostgreSQL and Redis
docker-compose up -d

# Verify services are running
docker-compose ps
```

### 3. Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run database migrations
alembic upgrade head

# Start FastAPI server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Backend will be available at: http://localhost:8000
API docs (Swagger): http://localhost:8000/docs

### 4. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

Frontend will be available at: http://localhost:5173

---

## Project Structure

```
accountability-partner-app/
├── backend/           # FastAPI backend
├── frontend/          # React frontend
├── docs/             # Additional documentation
├── docker-compose.yml
├── business_plan.md
├── product_design.md
├── technical_requirements.md
├── roadmap.md
├── user_stories.md
├── memory.md         # Development memory (agent-maintained)
├── tasks.md          # Current tasks and backlog
├── testing.md        # Testing strategy
└── README.md         # This file
```

---

## Core Features (MVP)

### 1. Smart Matching
- Match users with complementary strengths/struggles
- Personality and commitment compatibility
- Maximum 3 active partnerships per user

### 2. The Pact: Shared Partnership Workspace
- Shared goal board (individual + mutual goals)
- Weekly check-in system with templates
- Progress dashboard with streaks
- Task assignment between partners

### 3. Anti-Ghosting System
- Automated nudge sequences
- Activity tracking and reminders
- Ghosting score calculation
- Partnership health meter

### 4. Safety Features
- Report and block functionality
- Content moderation
- No location sharing
- Verification tiers

### 5. Partnership Seasons
- 4-week partnership cycles
- End-of-season celebration
- Renewal or graceful exit

---

## Tech Stack

### Backend
- **Framework**: FastAPI (Python 3.11+)
- **Database**: PostgreSQL 15+ with SQLAlchemy 2.0
- **Caching**: Redis 7+
- **Task Queue**: Celery
- **Auth**: JWT (JSON Web Tokens)
- **File Storage**: AWS S3
- **Email**: SendGrid

### Frontend
- **Framework**: React 18+ with TypeScript
- **Build Tool**: Vite
- **Styling**: Tailwind CSS 3+
- **UI Components**: shadcn/ui (Radix UI)
- **State**: Zustand
- **API Client**: Axios + React Query
- **Forms**: React Hook Form + Zod

### DevOps
- **Containerization**: Docker
- **CI/CD**: GitHub Actions
- **Monitoring**: Sentry
- **Analytics**: PostHog

---

## Environment Variables

### Backend (.env)

```bash
# Database
DATABASE_URL=postgresql+asyncpg://growthpact:password@localhost:5432/growthpact_dev

# JWT
SECRET_KEY=your-secret-key-here-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=15
REFRESH_TOKEN_EXPIRE_DAYS=7

# Redis
REDIS_URL=redis://localhost:6379

# AWS S3 (optional for MVP)
AWS_ACCESS_KEY_ID=your-aws-key
AWS_SECRET_ACCESS_KEY=your-aws-secret
AWS_REGION=us-east-1
S3_BUCKET_NAME=growthpact-uploads-dev

# SendGrid (optional for MVP)
SENDGRID_API_KEY=your-sendgrid-key
FROM_EMAIL=noreply@growthpact.com

# Environment
ENVIRONMENT=development
DEBUG=True
```

### Frontend (.env)

```bash
VITE_API_BASE_URL=http://localhost:8000/api/v1
VITE_WS_URL=ws://localhost:8000/ws
```

---

## Development Workflow

### Running Tests

#### Backend Tests
```bash
cd backend
source venv/bin/activate
pytest
pytest --cov=app tests/  # With coverage
```

#### Frontend Tests
```bash
cd frontend
npm run test
npm run test:coverage
```

### Database Migrations

```bash
cd backend
source venv/bin/activate

# Create new migration
alembic revision --autogenerate -m "Description of changes"

# Apply migrations
alembic upgrade head

# Rollback one migration
alembic downgrade -1
```

### Code Quality

#### Backend (Python)
```bash
# Linting
ruff check app/

# Formatting
ruff format app/

# Type checking
mypy app/
```

#### Frontend (TypeScript)
```bash
# Linting
npm run lint

# Type checking
npm run type-check
```

---

## API Documentation

Once the backend is running, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Example API Endpoints

```bash
# Register new user
POST /api/v1/auth/register
{
  "email": "user@example.com",
  "password": "SecurePass123",
  "username": "johndoe",
  "full_name": "John Doe"
}

# Login
POST /api/v1/auth/login
{
  "email": "user@example.com",
  "password": "SecurePass123"
}

# Get current user
GET /api/v1/users/me
Authorization: Bearer <access_token>

# Create partnership check-in
POST /api/v1/partnerships/{partnership_id}/check-ins
{
  "what_i_did": "Applied to 5 jobs this week",
  "what_i_struggled_with": "Interview prep was difficult",
  "what_i_need": "Help with mock interviews"
}
```

---

## Deployment (Production)

### Backend Deployment (AWS)
1. **EC2 Instance**: t3.medium (2 vCPU, 4 GB RAM)
2. **RDS PostgreSQL**: db.t3.small
3. **ElastiCache Redis**: cache.t3.micro
4. **S3**: File storage
5. **CloudFront**: CDN for static assets

### Frontend Deployment
- **S3 + CloudFront** for static hosting
- Build command: `npm run build`
- Output directory: `dist/`

### CI/CD Pipeline (GitHub Actions)
1. Run tests on every push
2. Build Docker images
3. Deploy to staging on `develop` branch
4. Deploy to production on `main` branch (manual approval)

---

## Contributing

This project is currently in autonomous development mode. See `CLAUDE.md` for development guidelines.

### Development Process
1. Check `tasks.md` for current sprint tasks
2. Follow patterns documented in `memory.md`
3. Write tests for all new features
4. Update documentation as you build
5. Commit with conventional commit messages

---

## Roadmap

See `roadmap.md` for detailed development phases.

**Current Phase**: Foundation & MVP Backend (Week 1)

**Upcoming Milestones**:
- Week 2: Matching algorithm & partnerships
- Week 4: MVP launch (beta users)
- Week 12: Public launch (ProductHunt)
- Month 6: V1.0 with monetization
- Month 12: V2.0 with native mobile apps

---

## License

Proprietary - All rights reserved

---

## Support

For questions or issues:
- Check documentation in `docs/`
- Review `memory.md` for architectural decisions
- See `fixed_bugs.md` for known issues and solutions

---

**Built with autonomy by Claude** 🤖
**Version**: 0.1.0 (MVP Development)
**Last Updated**: 2025-11-17
