"""
Pydantic schemas for Exit Ready Automation API.
"""
from app.schemas.case import (
    CaseBase,
    CaseCreate,
    CaseUpdate,
    CaseStatusUpdate,
    CaseIntakeData,
    CaseResponse,
    CaseSummary,
    CaseList,
    CaseStats,
)
from app.schemas.document import (
    DocBase,
    DocCreate,
    DocUpdate,
    DocStatusUpdate,
    DocResponse,
    DocChecklist,
    BulkDocCreate,
)
from app.schemas.event import (
    EventCreate,
    EventResponse,
    EventList,
    EventTypeStats,
)
from app.schemas.valuation import (
    YearlyFinancials,
    AddbackItem,
    NormalizedFinancials,
    ValuationRequest,
    ValuationMultiples,
    ValuationRange,
    ValuationResponse,
    ValuationStubResponse,
)

__all__ = [
    # Case schemas
    "CaseBase",
    "CaseCreate",
    "CaseUpdate",
    "CaseStatusUpdate",
    "CaseIntakeData",
    "CaseResponse",
    "CaseSummary",
    "CaseList",
    "CaseStats",
    # Document schemas
    "DocBase",
    "DocCreate",
    "DocUpdate",
    "DocStatusUpdate",
    "DocResponse",
    "DocChecklist",
    "BulkDocCreate",
    # Event schemas
    "EventCreate",
    "EventResponse",
    "EventList",
    "EventTypeStats",
    # Valuation schemas
    "YearlyFinancials",
    "AddbackItem",
    "NormalizedFinancials",
    "ValuationRequest",
    "ValuationMultiples",
    "ValuationRange",
    "ValuationResponse",
    "ValuationStubResponse",
]
