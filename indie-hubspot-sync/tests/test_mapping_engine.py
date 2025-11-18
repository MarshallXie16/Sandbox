"""
Unit tests for field mapping engine.
"""

import pytest
from datetime import datetime
from pathlib import Path

from app.mappings.engine import MappingEngine
from app.models.tracking import EntityType


@pytest.fixture
def mapping_engine():
    """Create a mapping engine instance."""
    return MappingEngine()


def test_load_mappings(mapping_engine):
    """Test that mappings are loaded correctly."""
    assert mapping_engine.mappings is not None
    assert "contacts" in mapping_engine.mappings
    assert "companies" in mapping_engine.mappings
    assert "deals" in mapping_engine.mappings


def test_get_entity_mappings(mapping_engine):
    """Test retrieving mappings for specific entity types."""
    contact_mappings = mapping_engine.get_entity_mappings(EntityType.CONTACT)
    assert "first_name" in contact_mappings
    assert "primary_email" in contact_mappings
    assert contact_mappings["first_name"]["indie_field"] == "first_name"
    assert contact_mappings["first_name"]["hubspot_property"] == "firstname"


def test_indie_to_hubspot_contact(mapping_engine):
    """Test mapping IndieStack contact to HubSpot properties."""
    indie_contact = {
        "id": 123,
        "first_name": "John",
        "last_name": "Doe",
        "primary_email": "john@example.com",
        "phone": "+1234567890",
        "category": "lead",
        "details": {"engagement_score": 85},
        "created_at": datetime(2024, 1, 1, 12, 0, 0),
    }

    hubspot_props = mapping_engine.indie_to_hubspot(EntityType.CONTACT, indie_contact)

    assert hubspot_props["firstname"] == "John"
    assert hubspot_props["lastname"] == "Doe"
    assert hubspot_props["email"] == "john@example.com"
    assert hubspot_props["phone"] == "+1234567890"
    assert hubspot_props["cl_category"] == "lead"
    assert hubspot_props["cl_engagement_score"] == 85


def test_indie_to_hubspot_company(mapping_engine):
    """Test mapping IndieStack company to HubSpot properties."""
    indie_company = {
        "id": 456,
        "name": "Acme Corp",
        "website": "acme.com",
        "industry": "Technology",
        "revenue": 1000000,
        "employee_count": 50,
    }

    hubspot_props = mapping_engine.indie_to_hubspot(EntityType.COMPANY, indie_company)

    assert hubspot_props["name"] == "Acme Corp"
    assert hubspot_props["domain"] == "acme.com"
    assert hubspot_props["industry"] == "Technology"
    assert hubspot_props["annualrevenue"] == 1000000
    assert hubspot_props["numberofemployees"] == 50


def test_hubspot_to_indie_contact(mapping_engine):
    """Test mapping HubSpot contact to IndieStack payload."""
    hubspot_contact = {
        "id": "123",
        "properties": {
            "firstname": "Jane",
            "lastname": "Smith",
            "email": "jane@example.com",
            "phone": "+9876543210",
            "lifecyclestage": "customer",
        },
    }

    indie_payload = mapping_engine.hubspot_to_indie(EntityType.CONTACT, hubspot_contact)

    assert indie_payload["first_name"] == "Jane"
    assert indie_payload["last_name"] == "Smith"
    assert indie_payload["primary_email"] == "jane@example.com"
    assert indie_payload["phone"] == "+9876543210"
    assert indie_payload["lifecycle_stage"] == "customer"


def test_get_bidirectional_fields(mapping_engine):
    """Test retrieving bidirectional fields."""
    bidirectional = mapping_engine.get_bidirectional_fields(EntityType.CONTACT)

    assert "first_name" in bidirectional
    assert "last_name" in bidirectional
    assert "primary_email" in bidirectional
    # category should not be in the list (it's indie_to_hubspot only)
    assert "category" not in bidirectional


def test_datetime_transformation(mapping_engine):
    """Test datetime to timestamp transformation."""
    indie_contact = {
        "id": 123,
        "first_name": "Test",
        "created_at": datetime(2024, 1, 1, 12, 0, 0),
    }

    hubspot_props = mapping_engine.indie_to_hubspot(EntityType.CONTACT, indie_contact)

    # Should have createdate as timestamp in milliseconds
    assert "createdate" in hubspot_props
    assert isinstance(hubspot_props["createdate"], int)
    # 2024-01-01 12:00:00 UTC = 1704110400000 ms
    assert hubspot_props["createdate"] == 1704110400000


def test_nested_field_extraction(mapping_engine):
    """Test extracting nested JSON fields."""
    indie_contact = {
        "id": 123,
        "details": {"engagement_score": 95, "other_field": "value"},
    }

    hubspot_props = mapping_engine.indie_to_hubspot(EntityType.CONTACT, indie_contact)

    assert hubspot_props["cl_engagement_score"] == 95


def test_direction_filtering(mapping_engine):
    """Test that direction filtering works correctly."""
    indie_contact = {
        "id": 123,
        "first_name": "John",
        "category": "lead",  # indie_to_hubspot only
    }

    # With direction filter for indie_to_hubspot
    hubspot_props = mapping_engine.indie_to_hubspot(
        EntityType.CONTACT,
        indie_contact,
        direction_filter="indie_to_hubspot",
    )

    # Should include both bidirectional and indie_to_hubspot fields
    assert "firstname" in hubspot_props
    assert "cl_category" in hubspot_props


def test_missing_values_handled(mapping_engine):
    """Test that missing values are handled gracefully."""
    indie_contact = {
        "id": 123,
        "first_name": "John",
        # Missing last_name, email, etc.
    }

    hubspot_props = mapping_engine.indie_to_hubspot(EntityType.CONTACT, indie_contact)

    # Should only include fields that have values
    assert "firstname" in hubspot_props
    assert "lastname" not in hubspot_props
    assert "email" not in hubspot_props
