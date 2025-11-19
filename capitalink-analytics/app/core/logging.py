"""Logging configuration."""

import logging
import sys
from typing import Any, Dict

from app.core.config import settings


def setup_logging() -> None:
    """Configure application logging."""
    log_level = getattr(logging, settings.log_level.upper(), logging.INFO)

    # Configure root logger
    logging.basicConfig(
        level=log_level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[logging.StreamHandler(sys.stdout)],
    )

    # Set specific log levels for libraries
    logging.getLogger("uvicorn").setLevel(log_level)
    logging.getLogger("sqlalchemy.engine").setLevel(
        logging.WARNING if not settings.analytics_debug else logging.INFO
    )


def get_logger(name: str) -> logging.Logger:
    """Get a logger instance."""
    return logging.getLogger(name)


class AnalyticsLogger:
    """Helper class for structured analytics logging."""

    def __init__(self, logger: logging.Logger):
        self.logger = logger

    def log_snapshot_run(self, domain: str, snapshot_date: str, metrics: Dict[str, Any]) -> None:
        """Log snapshot run completion."""
        self.logger.info(
            f"Snapshot completed - Domain: {domain}, Date: {snapshot_date}, "
            f"Metrics: {len(metrics)} entries"
        )

    def log_api_call(self, endpoint: str, duration_ms: float, status_code: int) -> None:
        """Log API call."""
        self.logger.info(
            f"API call - Endpoint: {endpoint}, Duration: {duration_ms:.2f}ms, "
            f"Status: {status_code}"
        )

    def log_upstream_query(self, source: str, query_type: str, duration_ms: float) -> None:
        """Log upstream database query."""
        self.logger.debug(
            f"Upstream query - Source: {source}, Type: {query_type}, "
            f"Duration: {duration_ms:.2f}ms"
        )

    def log_error(self, operation: str, error: Exception) -> None:
        """Log error with context."""
        self.logger.error(f"Error in {operation}: {str(error)}", exc_info=True)
