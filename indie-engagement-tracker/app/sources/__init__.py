"""Event sources for fetching engagement data."""
from app.sources.base import EventSource, StandardEvent
from app.sources.email_engine_source import EmailEngineSource
from app.sources.indie_crm_source import IndieCrmActivitySource
from app.sources.manager import SourceManager

__all__ = [
    "EventSource",
    "StandardEvent",
    "EmailEngineSource",
    "IndieCrmActivitySource",
    "SourceManager",
]
