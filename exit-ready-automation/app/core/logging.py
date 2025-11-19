"""
Logging configuration for the application.
"""
import logging
import sys
from typing import Any

from app.core.config import settings


def setup_logging() -> None:
    """Configure application logging."""
    log_level = getattr(logging, settings.log_level.upper(), logging.INFO)

    # Root logger configuration
    logging.basicConfig(
        level=log_level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.StreamHandler(sys.stdout)
        ]
    )

    # Set specific loggers
    loggers = {
        "uvicorn": log_level,
        "uvicorn.access": logging.WARNING if not settings.debug else log_level,
        "sqlalchemy.engine": logging.WARNING if not settings.debug else log_level,
        "httpx": logging.WARNING,
    }

    for logger_name, level in loggers.items():
        logging.getLogger(logger_name).setLevel(level)


def get_logger(name: str) -> logging.Logger:
    """Get a logger instance with the given name."""
    return logging.getLogger(name)
