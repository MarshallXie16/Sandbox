# Testing Strategy: GrowthPact

## Testing Philosophy
- **Test early, test often**: Write tests alongside features
- **Aim for 80% coverage**: Focus on critical paths
- **Test behavior, not implementation**: Tests should survive refactoring
- **Fast feedback**: Unit tests < 1s, integration tests < 10s

---

## Test Coverage Goals

### Backend Coverage Targets
- **Overall**: 80% code coverage minimum
- **Critical paths**: 95% coverage
  - Authentication (registration, login, token refresh)
  - Matching algorithm
  - Partnership creation
  - Payment processing (future)
- **Business logic**: 90% coverage (services layer)
- **API endpoints**: 85% coverage
- **Utilities**: 90% coverage

### Frontend Coverage Targets
- **Overall**: 70% code coverage minimum
- **Critical components**: 85% coverage
  - Authentication flow
  - Partnership dashboard
  - Check-in forms
  - Payment modals (future)
- **Utility functions**: 90% coverage
- **Hooks**: 80% coverage

---

## Backend Testing

### Test Structure
```
backend/tests/
├── conftest.py               # Shared fixtures
├── unit/                     # Unit tests
│   ├── test_auth.py
│   ├── test_matching_algorithm.py
│   ├── test_partnership_service.py
│   └── test_utils.py
├── integration/              # Integration tests
│   ├── test_auth_endpoints.py
│   ├── test_user_endpoints.py
│   ├── test_partnership_endpoints.py
│   ├── test_matching_endpoints.py
│   ├── test_goal_endpoints.py
│   └── test_checkin_endpoints.py
├── e2e/                      # End-to-end tests
│   ├── test_registration_to_match.py
│   ├── test_partnership_flow.py
│   └── test_season_renewal.py
└── fixtures/                 # Test data factories
    ├── user_factory.py
    ├── partnership_factory.py
    └── goal_factory.py
```

### Running Backend Tests

```bash
cd backend
source venv/bin/activate

# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html tests/

# Run specific test file
pytest tests/integration/test_auth_endpoints.py

# Run specific test
pytest tests/integration/test_auth_endpoints.py::test_register_user

# Run only unit tests
pytest tests/unit/

# Run only integration tests
pytest tests/integration/

# Run with verbose output
pytest -v

# Run with print statements visible
pytest -s
```

### Test Fixtures (conftest.py)

```python
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.database import Base, get_db
from app.config import settings

# Test database URL (separate from development)
TEST_DATABASE_URL = "postgresql+asyncpg://test:test@localhost:5432/growthpact_test"

@pytest.fixture(scope="session")
async def async_engine():
    """Create test database engine"""
    engine = create_async_engine(TEST_DATABASE_URL, echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()

@pytest.fixture
async def db_session(async_engine):
    """Create a fresh database session for each test"""
    async_session = sessionmaker(
        async_engine, class_=AsyncSession, expire_on_commit=False
    )
    async with async_session() as session:
        yield session
        await session.rollback()

@pytest.fixture
async def client(db_session):
    """Create test client with database override"""
    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac
    app.dependency_overrides.clear()

@pytest.fixture
async def test_user(db_session):
    """Create a test user"""
    from app.models.user import User
    from app.core.security import get_password_hash

    user = User(
        email="test@example.com",
        username="testuser",
        full_name="Test User",
        password_hash=get_password_hash("TestPass123")
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user

@pytest.fixture
async def auth_headers(test_user):
    """Generate auth headers for authenticated requests"""
    from app.core.auth import create_access_token

    token = create_access_token(data={"sub": str(test_user.id)})
    return {"Authorization": f"Bearer {token}"}
```

### Example Unit Test

```python
# tests/unit/test_matching_algorithm.py
import pytest
from app.services.matching_service import calculate_match_score
from app.schemas.user_profile import UserProfile

def test_calculate_match_score_complementary():
    """Test that complementary strengths/struggles score highly"""
    user1 = UserProfile(
        strengths=["career", "fitness"],
        struggles=["fashion", "relationships"],
        communication_style="direct",
        commitment_level="moderate"
    )
    user2 = UserProfile(
        strengths=["fashion", "relationships"],
        struggles=["career", "fitness"],
        communication_style="direct",
        commitment_level="moderate"
    )

    score = calculate_match_score(user1, user2)

    # Perfect complementarity should score > 0.8
    assert score > 0.8, f"Expected high score for complementary users, got {score}"

def test_calculate_match_score_no_overlap():
    """Test that users with no overlap score poorly"""
    user1 = UserProfile(
        strengths=["career"],
        struggles=["fitness"],
        communication_style="direct",
        commitment_level="moderate"
    )
    user2 = UserProfile(
        strengths=["fashion"],
        struggles=["cooking"],
        communication_style="supportive",
        commitment_level="casual"
    )

    score = calculate_match_score(user1, user2)

    # No overlap should score < 0.4
    assert score < 0.4, f"Expected low score for non-overlapping users, got {score}"
```

### Example Integration Test

```python
# tests/integration/test_auth_endpoints.py
import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_register_user(client: AsyncClient):
    """Test user registration endpoint"""
    response = await client.post("/api/v1/auth/register", json={
        "email": "newuser@example.com",
        "password": "SecurePass123",
        "username": "newuser",
        "full_name": "New User"
    })

    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "newuser@example.com"
    assert data["username"] == "newuser"
    assert "password" not in data  # Password should not be returned

@pytest.mark.asyncio
async def test_register_duplicate_email(client: AsyncClient, test_user):
    """Test registration with duplicate email fails"""
    response = await client.post("/api/v1/auth/register", json={
        "email": test_user.email,  # Already exists
        "password": "SecurePass123",
        "username": "anotheruser",
        "full_name": "Another User"
    })

    assert response.status_code == 400
    assert "already registered" in response.json()["detail"].lower()

@pytest.mark.asyncio
async def test_login_success(client: AsyncClient, test_user):
    """Test successful login"""
    response = await client.post("/api/v1/auth/login", json={
        "email": test_user.email,
        "password": "TestPass123"
    })

    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"

@pytest.mark.asyncio
async def test_get_current_user(client: AsyncClient, test_user, auth_headers):
    """Test getting current user with valid token"""
    response = await client.get("/api/v1/users/me", headers=auth_headers)

    assert response.status_code == 200
    data = response.json()
    assert data["email"] == test_user.email
    assert data["username"] == test_user.username
```

### Example E2E Test

```python
# tests/e2e/test_registration_to_match.py
import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_full_onboarding_flow(client: AsyncClient):
    """Test complete flow from registration to match acceptance"""

    # Step 1: Register user 1
    response = await client.post("/api/v1/auth/register", json={
        "email": "sarah@example.com",
        "password": "SecurePass123",
        "username": "sarah",
        "full_name": "Sarah Johnson"
    })
    assert response.status_code == 201

    # Step 2: Login user 1
    response = await client.post("/api/v1/auth/login", json={
        "email": "sarah@example.com",
        "password": "SecurePass123"
    })
    user1_token = response.json()["access_token"]
    user1_headers = {"Authorization": f"Bearer {user1_token}"}

    # Step 3: Create profile for user 1
    response = await client.patch(
        "/api/v1/profiles/me",
        headers=user1_headers,
        json={
            "strengths": ["career", "fitness"],
            "struggles": ["fashion", "relationships"],
            "communication_style": "direct",
            "commitment_level": "moderate"
        }
    )
    assert response.status_code == 200

    # Step 4: Enter match queue
    response = await client.post(
        "/api/v1/matching/enter-queue",
        headers=user1_headers
    )
    assert response.status_code == 200

    # Step 5: Register and onboard user 2 (complementary profile)
    # ... (similar steps)

    # Step 6: Get match suggestions for user 1
    response = await client.get(
        "/api/v1/matching/suggestions",
        headers=user1_headers
    )
    assert response.status_code == 200
    suggestions = response.json()
    assert len(suggestions) > 0

    # Step 7: Accept match
    match_id = suggestions[0]["id"]
    response = await client.post(
        f"/api/v1/matching/accept",
        headers=user1_headers,
        json={"match_id": match_id}
    )
    assert response.status_code == 201

    # Step 8: Verify partnership created
    response = await client.get(
        "/api/v1/partnerships",
        headers=user1_headers
    )
    partnerships = response.json()
    assert len(partnerships) == 1
    assert partnerships[0]["status"] == "active"
```

---

## Frontend Testing

### Test Structure
```
frontend/src/
├── __tests__/                # Tests mirror src structure
│   ├── components/
│   │   ├── ui/
│   │   ├── layout/
│   │   └── features/
│   ├── hooks/
│   ├── utils/
│   └── pages/
├── test-utils.tsx            # Testing utilities
└── setupTests.ts             # Test configuration
```

### Running Frontend Tests

```bash
cd frontend

# Run all tests
npm run test

# Run with coverage
npm run test:coverage

# Run in watch mode (during development)
npm run test:watch

# Run specific test file
npm run test CheckInForm.test.tsx

# Run E2E tests with Playwright
npm run test:e2e
```

### Test Utilities (test-utils.tsx)

```tsx
import { render, RenderOptions } from '@testing-library/react'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { BrowserRouter } from 'react-router-dom'
import { ReactElement } from 'react'

const createTestQueryClient = () =>
  new QueryClient({
    defaultOptions: {
      queries: { retry: false },
      mutations: { retry: false },
    },
  })

interface AllProvidersProps {
  children: React.ReactNode
}

function AllProviders({ children }: AllProvidersProps) {
  const queryClient = createTestQueryClient()

  return (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>{children}</BrowserRouter>
    </QueryClientProvider>
  )
}

function customRender(ui: ReactElement, options?: Omit<RenderOptions, 'wrapper'>) {
  return render(ui, { wrapper: AllProviders, ...options })
}

export * from '@testing-library/react'
export { customRender as render }
```

### Example Component Test

```tsx
// src/components/features/__tests__/CheckInForm.test.tsx
import { render, screen, waitFor } from '@/test-utils'
import { CheckInForm } from '../CheckInForm'
import userEvent from '@testing-library/user-event'
import { vi } from 'vitest'

describe('CheckInForm', () => {
  it('renders all form fields', () => {
    render(<CheckInForm partnershipId="123" />)

    expect(screen.getByLabelText(/what i did/i)).toBeInTheDocument()
    expect(screen.getByLabelText(/what i struggled with/i)).toBeInTheDocument()
    expect(screen.getByLabelText(/what i need/i)).toBeInTheDocument()
    expect(screen.getByRole('button', { name: /submit/i })).toBeInTheDocument()
  })

  it('submits form with valid data', async () => {
    const onSuccess = vi.fn()
    const user = userEvent.setup()

    render(<CheckInForm partnershipId="123" onSuccess={onSuccess} />)

    await user.type(screen.getByLabelText(/what i did/i), 'Applied to 5 jobs')
    await user.type(screen.getByLabelText(/what i struggled with/i), 'Interview prep')
    await user.click(screen.getByRole('button', { name: /submit/i }))

    await waitFor(() => {
      expect(onSuccess).toHaveBeenCalled()
    })
  })

  it('shows validation errors for empty required fields', async () => {
    const user = userEvent.setup()

    render(<CheckInForm partnershipId="123" />)

    await user.click(screen.getByRole('button', { name: /submit/i }))

    expect(await screen.findByText(/this field is required/i)).toBeInTheDocument()
  })
})
```

### Example Hook Test

```tsx
// src/hooks/__tests__/useAuth.test.tsx
import { renderHook, waitFor } from '@testing-library/react'
import { useAuth } from '../useAuth'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'

describe('useAuth', () => {
  it('returns null user when not authenticated', () => {
    const queryClient = new QueryClient()
    const wrapper = ({ children }: { children: React.ReactNode }) => (
      <QueryClientProvider client={queryClient}>{children}</QueryClientProvider>
    )

    const { result } = renderHook(() => useAuth(), { wrapper })

    expect(result.current.user).toBeNull()
    expect(result.current.isAuthenticated).toBe(false)
  })

  it('logs in user successfully', async () => {
    // ... test login logic
  })
})
```

---

## E2E Testing (Playwright)

### Test Structure
```
frontend/e2e/
├── auth.spec.ts              # Authentication flows
├── onboarding.spec.ts        # User onboarding
├── matching.spec.ts          # Matching flow
├── partnership.spec.ts       # Partnership interactions
└── fixtures/                 # Test data
```

### Running E2E Tests

```bash
cd frontend

# Run all E2E tests
npx playwright test

# Run in headed mode (see browser)
npx playwright test --headed

# Run specific test
npx playwright test e2e/auth.spec.ts

# Debug mode
npx playwright test --debug

# Generate test report
npx playwright show-report
```

### Example E2E Test

```typescript
// frontend/e2e/auth.spec.ts
import { test, expect } from '@playwright/test'

test.describe('Authentication Flow', () => {
  test('user can register, login, and access dashboard', async ({ page }) => {
    // Navigate to registration page
    await page.goto('http://localhost:5173/register')

    // Fill registration form
    await page.fill('input[name="email"]', 'test@example.com')
    await page.fill('input[name="password"]', 'SecurePass123')
    await page.fill('input[name="username"]', 'testuser')
    await page.fill('input[name="fullName"]', 'Test User')
    await page.click('button[type="submit"]')

    // Should redirect to onboarding
    await expect(page).toHaveURL(/\/onboarding/)

    // Complete profile setup
    await page.click('text=Career')  // Select strength
    await page.click('text=Fashion')  // Select struggle
    await page.click('button:has-text("Continue")')

    // Should redirect to dashboard
    await expect(page).toHaveURL(/\/dashboard/)
    await expect(page.locator('text=Welcome, Test User')).toBeVisible()
  })
})
```

---

## Load Testing

### Tool: Locust

```python
# backend/locust/locustfile.py
from locust import HttpUser, task, between

class GrowthPactUser(HttpUser):
    wait_time = between(1, 3)

    def on_start(self):
        """Login before running tasks"""
        response = self.client.post("/api/v1/auth/login", json={
            "email": "loadtest@example.com",
            "password": "LoadTest123"
        })
        self.token = response.json()["access_token"]
        self.headers = {"Authorization": f"Bearer {self.token}"}

    @task(3)
    def view_partnerships(self):
        """Fetch user's partnerships (high frequency)"""
        self.client.get("/api/v1/partnerships", headers=self.headers)

    @task(2)
    def view_check_ins(self):
        """Fetch check-ins for partnership"""
        partnership_id = "some-partnership-id"
        self.client.get(
            f"/api/v1/partnerships/{partnership_id}/check-ins",
            headers=self.headers
        )

    @task(1)
    def create_check_in(self):
        """Create a check-in (lower frequency)"""
        partnership_id = "some-partnership-id"
        self.client.post(
            f"/api/v1/partnerships/{partnership_id}/check-ins",
            headers=self.headers,
            json={
                "what_i_did": "Load testing the platform",
                "what_i_struggled_with": "Finding bugs",
                "what_i_need": "More test data"
            }
        )
```

### Run Load Tests

```bash
# Install Locust
pip install locust

# Run load test
cd backend/locust
locust -f locustfile.py --host=http://localhost:8000

# Open web UI at http://localhost:8089
# Set users: 100, spawn rate: 10, run test
```

---

## Test Data Factories

```python
# backend/tests/fixtures/user_factory.py
import factory
from app.models.user import User
from app.core.security import get_password_hash

class UserFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = User
        sqlalchemy_session_persistence = "commit"

    email = factory.Sequence(lambda n: f"user{n}@example.com")
    username = factory.Sequence(lambda n: f"user{n}")
    full_name = factory.Faker("name")
    password_hash = get_password_hash("TestPass123")
    is_verified = True
    is_active = True

# Usage in tests:
# user = UserFactory.create(db_session, email="specific@example.com")
```

---

## Continuous Integration

### GitHub Actions Workflow

```yaml
# .github/workflows/test.yml
name: Run Tests

on: [push, pull_request]

jobs:
  backend-tests:
    runs-on: ubuntu-latest
    services:
      postgres:
        image: postgres:15
        env:
          POSTGRES_USER: test
          POSTGRES_PASSWORD: test
          POSTGRES_DB: growthpact_test
        ports:
          - 5432:5432
      redis:
        image: redis:7
        ports:
          - 6379:6379

    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - name: Install dependencies
        run: |
          cd backend
          pip install -r requirements.txt
      - name: Run tests
        run: |
          cd backend
          pytest --cov=app --cov-report=xml
      - name: Upload coverage
        uses: codecov/codecov-action@v3

  frontend-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
        with:
          node-version: '18'
      - name: Install dependencies
        run: |
          cd frontend
          npm ci
      - name: Run tests
        run: |
          cd frontend
          npm run test:coverage
      - name: Upload coverage
        uses: codecov/codecov-action@v3
```

---

## QA Checklist

### Pre-Release Checklist
- [ ] All tests passing (backend + frontend)
- [ ] Code coverage > 80% (backend), > 70% (frontend)
- [ ] No critical security vulnerabilities (Snyk scan)
- [ ] Load testing completed (target: 100 concurrent users)
- [ ] E2E tests passing for critical flows
- [ ] Manual QA on staging environment
- [ ] Database migrations tested (up + down)
- [ ] Error tracking configured (Sentry)
- [ ] Performance benchmarks met (< 200ms p95 API latency)

---

**Version**: 1.0
**Last Updated**: 2025-11-17
**Maintained By**: Autonomous Development Agent
