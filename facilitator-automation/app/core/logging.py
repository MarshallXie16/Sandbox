"""
Logging configuration for Facilitator Automation.
Provides structured logging with configurable levels.
"""

import logging
import sys
from typing import Any, Dict

from app.core.config import settings


def setup_logging() -> None:
    """
    Configure application logging.
    Sets up formatters, handlers, and log levels.
    """
    log_level = getattr(logging, settings.log_level.upper(), logging.INFO)

    # Create formatter
    formatter = logging.Formatter(
        fmt="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    console_handler.setLevel(log_level)

    # Root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    root_logger.addHandler(console_handler)

    # Set third-party loggers to WARNING to reduce noise
    logging.getLogger("sqlalchemy").setLevel(logging.WARNING)
    logging.getLogger("asyncpg").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("uvicorn").setLevel(logging.INFO)


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance for a specific module.

    Args:
        name: Logger name (typically __name__)

    Returns:
        Configured logger instance
    """
    return logging.getLogger(name)


class StructuredLogger:
    """
    Wrapper for structured logging with consistent formatting.
    Useful for event tracking and audit trails.
    """

    def __init__(self, name: str):
        self.logger = logging.getLogger(name)

    def log_event(
        self,
        event_type: str,
        level: str = "INFO",
        **kwargs: Any
    ) -> None:
        """
        Log a structured event.

        Args:
            event_type: Type of event (e.g., "engagement_created")
            level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
            **kwargs: Additional event data
        """
        log_level = getattr(logging, level.upper(), logging.INFO)
        message = self._format_event(event_type, kwargs)
        self.logger.log(log_level, message)

    def _format_event(self, event_type: str, data: Dict[str, Any]) -> str:
        """Format event data as a readable string."""
        parts = [f"EVENT: {event_type}"]
        for key, value in data.items():
            parts.append(f"{key}={value}")
        return " | ".join(parts)
