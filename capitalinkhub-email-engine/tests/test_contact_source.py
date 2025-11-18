"""
Tests for contact source functionality.
"""
import pytest
import tempfile
from pathlib import Path

from app.utils.contact_source import CSVContactSource
from app.models import RecipientSegment


@pytest.fixture
def sample_csv_file():
    """Create a temporary CSV file with sample data."""
    content = """email,name,segment,company_name,industry
john@example.com,John Smith,buyer,Smith Corp,Technology
sarah@example.com,Sarah Johnson,seller,Johnson Inc,Retail
invalid-email,Mike Williams,buyer,,
,No Email,seller,,
valid@test.com,,,Extra Company,Finance
"""
    temp_file = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.csv')
    temp_file.write(content)
    temp_file.close()

    yield temp_file.name

    # Cleanup
    Path(temp_file.name).unlink()


def test_csv_contact_source_basic(sample_csv_file):
    """Test basic CSV loading functionality."""
    source = CSVContactSource(
        file_path=sample_csv_file,
        email_column="email",
        name_column="name",
        segment_column="segment"
    )

    contacts = source.load_contacts()

    # Should load 3 valid contacts (2 with invalid/missing emails are skipped)
    assert len(contacts) == 3

    # Check first contact
    assert contacts[0]["email"] == "john@example.com"
    assert contacts[0]["name"] == "John Smith"
    assert contacts[0]["segment"] == RecipientSegment.BUYER
    assert contacts[0]["details"]["company_name"] == "Smith Corp"
    assert contacts[0]["details"]["industry"] == "Technology"


def test_csv_contact_source_default_segment(sample_csv_file):
    """Test CSV loading with default segment."""
    source = CSVContactSource(
        file_path=sample_csv_file,
        email_column="email",
        name_column="name",
        segment_column="segment",
        default_segment=RecipientSegment.COLD_LEAD
    )

    contacts = source.load_contacts()

    # Find the contact with no segment specified
    contact_with_default = next((c for c in contacts if c["email"] == "valid@test.com"), None)
    assert contact_with_default is not None
    # Should use default since segment column is empty
    assert contact_with_default["segment"] == RecipientSegment.COLD_LEAD


def test_csv_contact_source_skip_invalid_emails(sample_csv_file):
    """Test that contacts with invalid emails are skipped."""
    source = CSVContactSource(
        file_path=sample_csv_file,
        email_column="email",
        name_column="name"
    )

    contacts = source.load_contacts()

    # Should skip 'invalid-email' and empty email
    emails = [c["email"] for c in contacts]
    assert "invalid-email" not in emails
    assert "" not in emails


def test_csv_contact_source_extra_fields(sample_csv_file):
    """Test that extra fields are included in details."""
    source = CSVContactSource(
        file_path=sample_csv_file,
        email_column="email",
        name_column="name",
        extra_columns=["company_name", "industry"]
    )

    contacts = source.load_contacts()

    # Check that extra fields are in details
    first_contact = contacts[0]
    assert "company_name" in first_contact["details"]
    assert "industry" in first_contact["details"]


def test_csv_contact_source_missing_file():
    """Test error handling for missing CSV file."""
    with pytest.raises(FileNotFoundError):
        CSVContactSource(
            file_path="nonexistent.csv",
            email_column="email"
        )


def test_csv_contact_source_missing_required_column():
    """Test error handling for missing required column."""
    content = """name,segment
John Smith,buyer
"""
    temp_file = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.csv')
    temp_file.write(content)
    temp_file.close()

    try:
        source = CSVContactSource(
            file_path=temp_file.name,
            email_column="email"  # This column doesn't exist
        )

        with pytest.raises(ValueError, match="Required column"):
            source.load_contacts()
    finally:
        Path(temp_file.name).unlink()


def test_csv_contact_source_empty_name():
    """Test handling of contacts with empty names."""
    content = """email,name,segment
test@example.com,,buyer
"""
    temp_file = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.csv')
    temp_file.write(content)
    temp_file.close()

    try:
        source = CSVContactSource(
            file_path=temp_file.name,
            email_column="email",
            name_column="name"
        )

        contacts = source.load_contacts()

        assert len(contacts) == 1
        assert contacts[0]["name"] is None  # Empty name becomes None
    finally:
        Path(temp_file.name).unlink()
