"""Logging configuration for the application."""
import logging
import sys
from typing import Optional

from app.core.config import settings


def setup_logging(level: Optional[str] = None) -> logging.Logger:
    """
    Configure application logging.

    Args:
        level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)

    Returns:
        Logger instance
    """
    log_level = level or settings.log_level

    # Create logger
    logger = logging.getLogger("engagement_tracker")
    logger.setLevel(getattr(logging, log_level.upper()))

    # Remove existing handlers to avoid duplicates
    logger.handlers.clear()

    # Create console handler with formatting
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(getattr(logging, log_level.upper()))

    # Create formatter
    if settings.is_production:
        # JSON-like format for production (easier to parse)
        formatter = logging.Formatter(
            '{"time": "%(asctime)s", "level": "%(levelname)s", "module": "%(name)s", "message": "%(message)s"}'
        )
    else:
        # Human-readable format for development
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )

    handler.setFormatter(formatter)
    logger.addHandler(handler)

    return logger


# Global logger instance
logger = setup_logging()
