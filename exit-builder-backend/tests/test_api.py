"""
Tests for API endpoints
"""
import pytest
from decimal import Decimal
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.db import Base, get_db
from app.main import app
from app.models import ValuationMethod, IndustryMultiple, ReportTemplate


# Test database setup
TEST_DATABASE_URL = "sqlite:///:memory:"


@pytest.fixture
def test_db():
    """Create a test database"""
    engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = TestingSessionLocal()

    # Seed required data
    # Add valuation methods
    sde_method = ValuationMethod(
        code="SDE_MULTIPLE",
        name="SDE Multiple Method",
        description="SDE-based valuation",
        is_active=True
    )
    ebitda_method = ValuationMethod(
        code="EBITDA_MULTIPLE",
        name="EBITDA Multiple Method",
        description="EBITDA-based valuation",
        is_active=True
    )
    session.add(sde_method)
    session.add(ebitda_method)

    # Add report template
    template = ReportTemplate(
        code="QUICK_SUMMARY",
        name="Quick Valuation Summary",
        description="Quick summary report",
        version=1,
        is_active=True
    )
    session.add(template)

    # Add industry multiples
    industry_multiple = IndustryMultiple(
        industry_code="238220",
        metric_type="SDE",
        multiple_low=Decimal("2.8"),
        multiple_mid=Decimal("3.2"),
        multiple_high=Decimal("3.6"),
        source="Test Data"
    )
    session.add(industry_multiple)

    session.commit()
    yield session

    session.close()
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def client(test_db):
    """Create a test client with test database"""
    def override_get_db():
        try:
            yield test_db
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    test_client = TestClient(app)
    yield test_client
    app.dependency_overrides.clear()


def test_health_check(client):
    """Test health check endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "version" in data


def test_root_endpoint(client):
    """Test root endpoint"""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "version" in data


def test_create_quick_project(client):
    """Test creating a quick valuation project"""
    payload = {
        "client": {
            "name": "ABC HVAC",
            "contact_name": "John Doe",
            "email": "john@example.com",
            "phone": "604-123-4567"
        },
        "project": {
            "business_name": "ABC HVAC",
            "industry_code": "238220",
            "location": "Vancouver, BC"
        },
        "financial": {
            "metric_type": "SDE",
            "metric_value": 270000,
            "revenue": 1350000
        }
    }

    response = client.post("/api/v1/projects/quick", json=payload)
    assert response.status_code == 201

    data = response.json()
    assert "project_id" in data
    assert "client_id" in data
    assert "report_id" in data
    assert "valuation_summary" in data

    summary = data["valuation_summary"]
    # 270000 * 2.8 = 756000
    # 270000 * 3.2 = 864000
    # 270000 * 3.6 = 972000
    assert summary["recommended_value_low"] == 756000
    assert summary["recommended_value_mid"] == 864000
    assert summary["recommended_value_high"] == 972000
    assert summary["currency"] == "CAD"


def test_create_quick_project_invalid_metric(client):
    """Test creating project with invalid metric type"""
    payload = {
        "client": {
            "name": "Test Business"
        },
        "project": {
            "business_name": "Test Business",
            "industry_code": "238220"
        },
        "financial": {
            "metric_type": "INVALID",  # Invalid
            "metric_value": 100000,
            "revenue": 500000
        }
    }

    response = client.post("/api/v1/projects/quick", json=payload)
    assert response.status_code == 422  # Validation error


def test_get_project(client):
    """Test getting project details"""
    # First create a project
    payload = {
        "client": {
            "name": "Test Client"
        },
        "project": {
            "business_name": "Test Business",
            "industry_code": "238220"
        },
        "financial": {
            "metric_type": "SDE",
            "metric_value": 200000,
            "revenue": 1000000
        }
    }

    create_response = client.post("/api/v1/projects/quick", json=payload)
    assert create_response.status_code == 201
    project_id = create_response.json()["project_id"]

    # Get project details
    response = client.get(f"/api/v1/projects/{project_id}")
    assert response.status_code == 200

    data = response.json()
    assert data["project"]["business_name"] == "Test Business"
    assert data["client"]["name"] == "Test Client"
    assert data["financial"]["sde"] == 200000
    assert data["valuation"] is not None


def test_get_nonexistent_project(client):
    """Test getting a non-existent project"""
    fake_uuid = "00000000-0000-0000-0000-000000000000"
    response = client.get(f"/api/v1/projects/{fake_uuid}")
    assert response.status_code == 404


def test_get_project_report(client):
    """Test getting project report"""
    # First create a project
    payload = {
        "client": {
            "name": "Report Test Client"
        },
        "project": {
            "business_name": "Report Test Business",
            "industry_code": "238220"
        },
        "financial": {
            "metric_type": "SDE",
            "metric_value": 250000,
            "revenue": 1200000
        }
    }

    create_response = client.post("/api/v1/projects/quick", json=payload)
    assert create_response.status_code == 201
    project_id = create_response.json()["project_id"]

    # Get project report
    response = client.get(f"/api/v1/projects/{project_id}/report")
    assert response.status_code == 200

    data = response.json()
    assert "report_id" in data
    assert "title" in data
    assert "content" in data
    assert "Quick Valuation Summary" in data["title"]
    assert "Report Test Business" in data["content"]
