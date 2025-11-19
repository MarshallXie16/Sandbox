"""
VaultAI Integration Layer - Security & Redaction
PII detection and redaction for sensitive data protection.
"""

import re
from typing import Dict, List, Pattern

from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)

# Regex patterns for common PII
PII_PATTERNS: Dict[str, Pattern] = {
    "ssn": re.compile(r"\b\d{3}-\d{2}-\d{4}\b"),
    "email": re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b"),
    "phone": re.compile(r"\b(\+\d{1,2}\s?)?(\(?\d{3}\)?[\s.-]?)?\d{3}[\s.-]?\d{4}\b"),
    "credit_card": re.compile(r"\b\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}\b"),
    "ip_address": re.compile(r"\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b"),
}


class PIIRedactor:
    """Redacts personally identifiable information from text."""

    def __init__(self, enabled: bool = True, patterns: List[str] | None = None):
        """
        Initialize PII redactor.

        Args:
            enabled: Whether redaction is enabled.
            patterns: List of pattern names to use (e.g., ["email", "ssn"]).
                     If None, uses all available patterns.
        """
        self.enabled = enabled
        self.patterns = patterns or list(PII_PATTERNS.keys())

    def redact(self, text: str) -> str:
        """
        Redact PII from text.

        Args:
            text: Input text potentially containing PII.

        Returns:
            Text with PII replaced by [REDACTED_{type}].
        """
        if not self.enabled:
            return text

        redacted_text = text
        redactions_count = 0

        for pattern_name in self.patterns:
            if pattern_name not in PII_PATTERNS:
                logger.warning(f"Unknown PII pattern: {pattern_name}")
                continue

            pattern = PII_PATTERNS[pattern_name]
            matches = pattern.findall(redacted_text)

            if matches:
                redactions_count += len(matches)
                redacted_text = pattern.sub(f"[REDACTED_{pattern_name.upper()}]", redacted_text)

        if redactions_count > 0:
            logger.info(f"Redacted {redactions_count} PII instances from text")

        return redacted_text

    def detect(self, text: str) -> Dict[str, int]:
        """
        Detect PII in text without redacting.

        Args:
            text: Input text to analyze.

        Returns:
            Dictionary mapping PII type to count of occurrences.
        """
        detections: Dict[str, int] = {}

        for pattern_name in self.patterns:
            if pattern_name not in PII_PATTERNS:
                continue

            pattern = PII_PATTERNS[pattern_name]
            matches = pattern.findall(text)

            if matches:
                detections[pattern_name] = len(matches)

        return detections


# Global redactor instance
pii_redactor = PIIRedactor(
    enabled=settings.ENABLE_PII_REDACTION,
    patterns=settings.redaction_patterns_list,
)


def redact_pii(text: str) -> str:
    """
    Convenience function to redact PII from text.

    Args:
        text: Input text.

    Returns:
        Redacted text.
    """
    return pii_redactor.redact(text)


def detect_pii(text: str) -> Dict[str, int]:
    """
    Convenience function to detect PII in text.

    Args:
        text: Input text.

    Returns:
        Dictionary of detected PII types and counts.
    """
    return pii_redactor.detect(text)
