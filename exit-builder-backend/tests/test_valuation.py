"""
Tests for valuation logic
"""
import pytest
from decimal import Decimal
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.db import Base
from app.models import (
    Client,
    Project,
    FinancialInput,
    IndustryMultiple,
    ValuationMethod
)
from app.services.valuation_core import run_quick_valuation, ValuationError


# Test database setup
TEST_DATABASE_URL = "sqlite:///:memory:"


@pytest.fixture
def db_session():
    """Create a test database session"""
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
    session.commit()

    yield session

    session.close()
    Base.metadata.drop_all(bind=engine)


def test_quick_valuation_with_sde(db_session):
    """Test Quick Valuation with SDE metric"""
    # Create client
    client = Client(
        name="Test Client",
        email="test@example.com"
    )
    db_session.add(client)
    db_session.flush()

    # Create project
    project = Project(
        client_id=client.id,
        business_name="Test Business",
        industry_code="238220",
        project_type="quick",
        status="draft"
    )
    db_session.add(project)
    db_session.flush()

    # Create financial input
    financial = FinancialInput(
        project_id=project.id,
        year=0,
        revenue=1000000,
        sde=200000
    )
    db_session.add(financial)

    # Create industry multiple
    industry_multiple = IndustryMultiple(
        industry_code="238220",
        metric_type="SDE",
        multiple_low=Decimal("2.5"),
        multiple_mid=Decimal("3.0"),
        multiple_high=Decimal("3.5"),
        source="Test Data"
    )
    db_session.add(industry_multiple)
    db_session.commit()

    # Run valuation
    summary = run_quick_valuation(db_session, project.id)

    # Assertions
    assert summary is not None
    assert summary.recommended_value_low == Decimal("500000")  # 200000 * 2.5
    assert summary.recommended_value_mid == Decimal("600000")  # 200000 * 3.0
    assert summary.recommended_value_high == Decimal("700000")  # 200000 * 3.5
    assert summary.currency == "CAD"


def test_quick_valuation_with_ebitda(db_session):
    """Test Quick Valuation with EBITDA metric"""
    # Create client
    client = Client(name="Test Client")
    db_session.add(client)
    db_session.flush()

    # Create project
    project = Project(
        client_id=client.id,
        business_name="Test Business",
        industry_code="541611",
        project_type="quick",
        status="draft"
    )
    db_session.add(project)
    db_session.flush()

    # Create financial input with EBITDA
    financial = FinancialInput(
        project_id=project.id,
        year=0,
        revenue=2000000,
        ebitda=400000
    )
    db_session.add(financial)

    # Create industry multiple for EBITDA
    industry_multiple = IndustryMultiple(
        industry_code="541611",
        metric_type="EBITDA",
        multiple_low=Decimal("4.0"),
        multiple_mid=Decimal("5.0"),
        multiple_high=Decimal("6.0"),
        source="Test Data"
    )
    db_session.add(industry_multiple)
    db_session.commit()

    # Run valuation
    summary = run_quick_valuation(db_session, project.id)

    # Assertions
    assert summary.recommended_value_low == Decimal("1600000")  # 400000 * 4.0
    assert summary.recommended_value_mid == Decimal("2000000")  # 400000 * 5.0
    assert summary.recommended_value_high == Decimal("2400000")  # 400000 * 6.0


def test_valuation_missing_industry_multiple(db_session):
    """Test that valuation fails when industry multiple is missing"""
    # Create client
    client = Client(name="Test Client")
    db_session.add(client)
    db_session.flush()

    # Create project with non-existent industry
    project = Project(
        client_id=client.id,
        business_name="Test Business",
        industry_code="999999",  # Non-existent
        project_type="quick",
        status="draft"
    )
    db_session.add(project)
    db_session.flush()

    # Create financial input
    financial = FinancialInput(
        project_id=project.id,
        year=0,
        revenue=1000000,
        sde=200000
    )
    db_session.add(financial)
    db_session.commit()

    # Should raise ValuationError
    with pytest.raises(ValuationError) as exc_info:
        run_quick_valuation(db_session, project.id)

    assert "No industry multiples found" in str(exc_info.value)


def test_valuation_missing_financial_metric(db_session):
    """Test that valuation fails when both SDE and EBITDA are missing"""
    # Create client
    client = Client(name="Test Client")
    db_session.add(client)
    db_session.flush()

    # Create project
    project = Project(
        client_id=client.id,
        business_name="Test Business",
        industry_code="238220",
        project_type="quick",
        status="draft"
    )
    db_session.add(project)
    db_session.flush()

    # Create financial input without SDE or EBITDA
    financial = FinancialInput(
        project_id=project.id,
        year=0,
        revenue=1000000
        # No SDE or EBITDA
    )
    db_session.add(financial)
    db_session.commit()

    # Should raise ValuationError
    with pytest.raises(ValuationError) as exc_info:
        run_quick_valuation(db_session, project.id)

    assert "Either SDE or EBITDA must be provided" in str(exc_info.value)


def test_valuation_updates_project_status(db_session):
    """Test that valuation updates project status"""
    # Create client
    client = Client(name="Test Client")
    db_session.add(client)
    db_session.flush()

    # Create project
    project = Project(
        client_id=client.id,
        business_name="Test Business",
        industry_code="238220",
        project_type="quick",
        status="draft"
    )
    db_session.add(project)
    db_session.flush()

    # Create financial input
    financial = FinancialInput(
        project_id=project.id,
        year=0,
        revenue=1000000,
        sde=200000
    )
    db_session.add(financial)

    # Create industry multiple
    industry_multiple = IndustryMultiple(
        industry_code="238220",
        metric_type="SDE",
        multiple_low=Decimal("2.5"),
        multiple_mid=Decimal("3.0"),
        multiple_high=Decimal("3.5"),
        source="Test Data"
    )
    db_session.add(industry_multiple)
    db_session.commit()

    # Verify initial status
    assert project.status == "draft"

    # Run valuation
    run_quick_valuation(db_session, project.id)

    # Refresh project
    db_session.refresh(project)

    # Verify status changed
    assert project.status == "in_analysis"
