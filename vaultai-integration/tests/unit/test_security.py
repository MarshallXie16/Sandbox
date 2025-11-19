"""
Unit tests for security and PII redaction.
"""

import pytest
from app.core.security import PIIRedactor, detect_pii, redact_pii


def test_redact_email():
    """Test email redaction."""
    redactor = PIIRedactor(enabled=True, patterns=["email"])

    text = "Contact us at support@example.com for help."
    redacted = redactor.redact(text)

    assert "support@example.com" not in redacted
    assert "[REDACTED_EMAIL]" in redacted


def test_redact_ssn():
    """Test SSN redaction."""
    redactor = PIIRedactor(enabled=True, patterns=["ssn"])

    text = "My SSN is 123-45-6789."
    redacted = redactor.redact(text)

    assert "123-45-6789" not in redacted
    assert "[REDACTED_SSN]" in redacted


def test_redact_phone():
    """Test phone number redaction."""
    redactor = PIIRedactor(enabled=True, patterns=["phone"])

    test_cases = [
        "Call me at 555-123-4567",
        "Phone: (555) 123-4567",
        "Contact: 5551234567",
    ]

    for text in test_cases:
        redacted = redactor.redact(text)
        assert "[REDACTED_PHONE]" in redacted


def test_redact_credit_card():
    """Test credit card redaction."""
    redactor = PIIRedactor(enabled=True, patterns=["credit_card"])

    text = "Card number: 1234-5678-9012-3456"
    redacted = redactor.redact(text)

    assert "1234-5678-9012-3456" not in redacted
    assert "[REDACTED_CREDIT_CARD]" in redacted


def test_redact_multiple_patterns():
    """Test redaction of multiple PII types."""
    redactor = PIIRedactor(enabled=True, patterns=["email", "phone", "ssn"])

    text = """
    Contact John at john@example.com or call 555-123-4567.
    SSN: 123-45-6789
    """

    redacted = redactor.redact(text)

    assert "john@example.com" not in redacted
    assert "555-123-4567" not in redacted
    assert "123-45-6789" not in redacted
    assert "[REDACTED_EMAIL]" in redacted
    assert "[REDACTED_PHONE]" in redacted
    assert "[REDACTED_SSN]" in redacted


def test_redact_disabled():
    """Test that redaction can be disabled."""
    redactor = PIIRedactor(enabled=False, patterns=["email"])

    text = "Email: test@example.com"
    redacted = redactor.redact(text)

    # Should not redact when disabled
    assert text == redacted


def test_detect_pii():
    """Test PII detection without redaction."""
    redactor = PIIRedactor(enabled=True, patterns=["email", "phone"])

    text = """
    Email: support@example.com
    Another email: contact@test.com
    Phone: 555-123-4567
    """

    detections = redactor.detect(text)

    assert detections["email"] == 2
    assert detections["phone"] == 1


def test_detect_no_pii():
    """Test detection when no PII present."""
    redactor = PIIRedactor(enabled=True, patterns=["email", "phone", "ssn"])

    text = "This is a clean text with no PII."

    detections = redactor.detect(text)

    assert len(detections) == 0


def test_global_redact_function():
    """Test global redact_pii function."""
    text = "Contact: test@example.com"
    redacted = redact_pii(text)

    # Should use global redactor settings
    assert isinstance(redacted, str)


def test_global_detect_function():
    """Test global detect_pii function."""
    text = "Email: test@example.com, Phone: 555-1234"
    detections = detect_pii(text)

    assert isinstance(detections, dict)


def test_preserves_text_structure():
    """Test that redaction preserves text structure."""
    redactor = PIIRedactor(enabled=True, patterns=["email"])

    text = """
    Dear Customer,

    Please contact us at support@example.com.

    Best regards,
    Team
    """

    redacted = redactor.redact(text)

    # Structure should be preserved
    assert "Dear Customer," in redacted
    assert "Best regards," in redacted
    assert "[REDACTED_EMAIL]" in redacted


def test_redact_unknown_pattern():
    """Test handling of unknown pattern names."""
    redactor = PIIRedactor(enabled=True, patterns=["email", "unknown_pattern"])

    text = "Email: test@example.com"

    # Should not crash, just log warning
    redacted = redactor.redact(text)

    assert "[REDACTED_EMAIL]" in redacted


def test_case_insensitive_email():
    """Test that email detection is case-insensitive."""
    redactor = PIIRedactor(enabled=True, patterns=["email"])

    text = "Contact: Test@Example.COM"
    redacted = redactor.redact(text)

    assert "[REDACTED_EMAIL]" in redacted


def test_multiple_occurrences():
    """Test redaction of multiple occurrences of same PII."""
    redactor = PIIRedactor(enabled=True, patterns=["email"])

    text = "test@example.com and test@example.com again"
    redacted = redactor.redact(text)

    # Both occurrences should be redacted
    assert text.count("test@example.com") == 2
    assert redacted.count("[REDACTED_EMAIL]") == 2
