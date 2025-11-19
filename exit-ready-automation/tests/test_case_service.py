"""
Tests for CaseService.
"""
import pytest
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from app.core.db import Base
from app.services import CaseService
from app.schemas.case import CaseCreate
from app.core.workflow import CaseStatus


@pytest.fixture
async def db_session():
    """Create a test database session."""
    # Use in-memory SQLite for tests
    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        echo=False,
    )

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async_session = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )

    async with async_session() as session:
        yield session

    await engine.dispose()


@pytest.mark.asyncio
async def test_create_case(db_session):
    """Test creating a new case."""
    service = CaseService(db_session)

    case_data = CaseCreate(
        owner_name="Test Owner",
        owner_email="test@example.com",
        company_name="Test Company",
        industry="Technology",
        region="US-West",
    )

    case = await service.create_case(case_data)

    assert case.id is not None
    assert case.case_code.startswith("ER-")
    assert case.status == CaseStatus.CREATED.value
    assert case.owner_name == "Test Owner"
    assert case.company_name == "Test Company"


@pytest.mark.asyncio
async def test_get_case(db_session):
    """Test retrieving a case."""
    service = CaseService(db_session)

    # Create a case
    case_data = CaseCreate(
        owner_name="Test Owner",
        owner_email="test@example.com",
        company_name="Test Company",
    )

    created_case = await service.create_case(case_data)

    # Retrieve the case
    retrieved_case = await service.get_case(created_case.id)

    assert retrieved_case is not None
    assert retrieved_case.id == created_case.id
    assert retrieved_case.case_code == created_case.case_code


@pytest.mark.asyncio
async def test_list_cases(db_session):
    """Test listing cases."""
    service = CaseService(db_session)

    # Create multiple cases
    for i in range(3):
        case_data = CaseCreate(
            owner_name=f"Owner {i}",
            owner_email=f"owner{i}@example.com",
            company_name=f"Company {i}",
        )
        await service.create_case(case_data)

    # List cases
    cases, total = await service.list_cases(page=1, page_size=10)

    assert len(cases) == 3
    assert total == 3


@pytest.mark.asyncio
async def test_update_status(db_session):
    """Test updating case status."""
    service = CaseService(db_session)

    # Create a case
    case_data = CaseCreate(
        owner_name="Test Owner",
        owner_email="test@example.com",
        company_name="Test Company",
    )

    case = await service.create_case(case_data)

    # Update status
    updated_case = await service.update_status(
        case.id,
        CaseStatus.INTAKE_PENDING
    )

    assert updated_case.status == CaseStatus.INTAKE_PENDING.value
