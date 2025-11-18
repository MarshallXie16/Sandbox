"""
Pytest configuration and fixtures.
"""

import pytest
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from app.models.base import Base
from app.schemas.buyer import BuyerProfile
from app.schemas.listing import ListingProfile


@pytest.fixture
def sample_buyer() -> BuyerProfile:
    """Sample buyer profile for testing."""
    return BuyerProfile(
        id=1,
        email="buyer@example.com",
        first_name="John",
        last_name="Doe",
        industry_preferences=["software", "technology"],
        region_preferences=["BC", "Western Canada"],
        min_deal_size=500000,
        max_deal_size=2000000,
        deal_types=["asset"],
        experience_level="experienced",
        engagement_score=75.0,
    )


@pytest.fixture
def sample_listing() -> ListingProfile:
    """Sample listing profile for testing."""
    return ListingProfile(
        id=101,
        name="Tech SaaS Company",
        company_id=1,
        company_name="Example Tech Inc",
        amount=1000000,
        status="Active",
        stage="Active",
        industry="software",
        region="BC",
        revenue=2000000,
        ebitda=400000,
        deal_size_band="mid",
        tags=["saas", "recurring revenue"],
        description="Growing SaaS company with strong MRR",
    )


@pytest.fixture
def mismatched_listing() -> ListingProfile:
    """Listing that doesn't match sample buyer."""
    return ListingProfile(
        id=102,
        name="Restaurant Business",
        company_id=2,
        company_name="Food Co",
        amount=10000000,  # Way outside buyer budget
        status="Active",
        stage="Active",
        industry="food_beverage",  # Different industry
        region="Ontario",  # Different region
        revenue=5000000,
        ebitda=500000,
        deal_size_band="large",
        tags=["restaurant"],
        description="Established restaurant chain",
    )


@pytest.fixture
def multiple_buyers() -> list[BuyerProfile]:
    """Multiple buyer profiles for batch testing."""
    return [
        BuyerProfile(
            id=1,
            email="buyer1@example.com",
            first_name="Alice",
            last_name="Smith",
            industry_preferences=["software"],
            region_preferences=["BC"],
            min_deal_size=500000,
            max_deal_size=2000000,
            experience_level="experienced",
            engagement_score=80.0,
        ),
        BuyerProfile(
            id=2,
            email="buyer2@example.com",
            first_name="Bob",
            last_name="Johnson",
            industry_preferences=["manufacturing"],
            region_preferences=["Alberta"],
            min_deal_size=1000000,
            max_deal_size=5000000,
            experience_level="first_time",
            engagement_score=50.0,
        ),
    ]


@pytest.fixture
def multiple_listings() -> list[ListingProfile]:
    """Multiple listing profiles for batch testing."""
    return [
        ListingProfile(
            id=101,
            name="SaaS Company A",
            company_id=1,
            amount=1000000,
            status="Active",
            industry="software",
            region="BC",
            revenue=2000000,
        ),
        ListingProfile(
            id=102,
            name="Manufacturing Plant B",
            company_id=2,
            amount=3000000,
            status="Active",
            industry="manufacturing",
            region="Alberta",
            revenue=10000000,
        ),
    ]
