"""
Workflow state machine for Exit Ready cases.
"""
from enum import Enum
from typing import Dict, List, Optional, Set
from datetime import datetime

from app.core.logging import get_logger

logger = get_logger(__name__)


class CaseStatus(str, Enum):
    """Exit Ready case statuses."""
    CREATED = "created"
    INTAKE_PENDING = "intake_pending"
    INTAKE_DONE = "intake_done"
    DOCS_COLLECTING = "docs_collecting"
    FINANCIALS_READY = "financials_ready"
    VALUATION_DONE = "valuation_done"
    DRAFTS_GENERATED = "drafts_generated"
    UNDER_REVIEW = "under_review"
    REPORT_READY = "report_ready"
    DELIVERED = "delivered"
    CLOSED = "closed"


class WorkflowError(Exception):
    """Base exception for workflow errors."""
    pass


class InvalidTransitionError(WorkflowError):
    """Raised when an invalid state transition is attempted."""
    pass


class WorkflowService:
    """
    Manages the state machine for Exit Ready cases.

    Enforces valid transitions and provides workflow validation.
    """

    # Define allowed transitions
    TRANSITIONS: Dict[CaseStatus, List[CaseStatus]] = {
        CaseStatus.CREATED: [CaseStatus.INTAKE_PENDING],
        CaseStatus.INTAKE_PENDING: [CaseStatus.INTAKE_DONE],
        CaseStatus.INTAKE_DONE: [CaseStatus.DOCS_COLLECTING],
        CaseStatus.DOCS_COLLECTING: [CaseStatus.FINANCIALS_READY],
        CaseStatus.FINANCIALS_READY: [CaseStatus.VALUATION_DONE],
        CaseStatus.VALUATION_DONE: [CaseStatus.DRAFTS_GENERATED],
        CaseStatus.DRAFTS_GENERATED: [CaseStatus.UNDER_REVIEW],
        CaseStatus.UNDER_REVIEW: [
            CaseStatus.REPORT_READY,
            CaseStatus.DRAFTS_GENERATED  # Allow going back to regenerate drafts
        ],
        CaseStatus.REPORT_READY: [CaseStatus.DELIVERED],
        CaseStatus.DELIVERED: [CaseStatus.CLOSED],
        CaseStatus.CLOSED: [],  # Terminal state
    }

    # Status descriptions for display
    STATUS_DESCRIPTIONS: Dict[CaseStatus, str] = {
        CaseStatus.CREATED: "Case created, ready to send intake",
        CaseStatus.INTAKE_PENDING: "Intake form sent, awaiting response",
        CaseStatus.INTAKE_DONE: "Intake received, ready to collect documents",
        CaseStatus.DOCS_COLLECTING: "Collecting required documents",
        CaseStatus.FINANCIALS_READY: "Financials normalized, ready for valuation",
        CaseStatus.VALUATION_DONE: "Valuation completed, ready to generate drafts",
        CaseStatus.DRAFTS_GENERATED: "Drafts generated, awaiting review",
        CaseStatus.UNDER_REVIEW: "Drafts under human review",
        CaseStatus.REPORT_READY: "Final report ready for delivery",
        CaseStatus.DELIVERED: "Report delivered to seller",
        CaseStatus.CLOSED: "Case closed",
    }

    @classmethod
    def validate_transition(
        cls,
        from_status: CaseStatus,
        to_status: CaseStatus,
        admin_override: bool = False
    ) -> bool:
        """
        Validate if a transition is allowed.

        Args:
            from_status: Current status
            to_status: Desired status
            admin_override: If True, allow any transition (use with caution)

        Returns:
            True if transition is valid

        Raises:
            InvalidTransitionError: If transition is not allowed
        """
        if admin_override:
            logger.warning(
                f"Admin override: Forcing transition from {from_status} to {to_status}"
            )
            return True

        allowed_statuses = cls.TRANSITIONS.get(from_status, [])

        if to_status not in allowed_statuses:
            raise InvalidTransitionError(
                f"Invalid transition from {from_status} to {to_status}. "
                f"Allowed transitions: {', '.join(s.value for s in allowed_statuses)}"
            )

        return True

    @classmethod
    def get_next_statuses(cls, current_status: CaseStatus) -> List[CaseStatus]:
        """
        Get list of valid next statuses from current status.

        Args:
            current_status: Current case status

        Returns:
            List of allowed next statuses
        """
        return cls.TRANSITIONS.get(current_status, [])

    @classmethod
    def get_status_description(cls, status: CaseStatus) -> str:
        """
        Get human-readable description of a status.

        Args:
            status: Case status

        Returns:
            Description string
        """
        return cls.STATUS_DESCRIPTIONS.get(status, "Unknown status")

    @classmethod
    def can_transition_to(cls, from_status: CaseStatus, to_status: CaseStatus) -> bool:
        """
        Check if a transition is allowed without raising an exception.

        Args:
            from_status: Current status
            to_status: Desired status

        Returns:
            True if transition is allowed, False otherwise
        """
        try:
            cls.validate_transition(from_status, to_status)
            return True
        except InvalidTransitionError:
            return False

    @classmethod
    def is_terminal_status(cls, status: CaseStatus) -> bool:
        """
        Check if a status is terminal (no further transitions).

        Args:
            status: Case status to check

        Returns:
            True if status is terminal
        """
        return len(cls.TRANSITIONS.get(status, [])) == 0

    @classmethod
    def get_all_statuses(cls) -> List[CaseStatus]:
        """Get all possible case statuses."""
        return list(CaseStatus)

    @classmethod
    def get_workflow_path(cls) -> List[CaseStatus]:
        """
        Get the typical workflow path (happy path).

        Returns:
            Ordered list of statuses in typical flow
        """
        return [
            CaseStatus.CREATED,
            CaseStatus.INTAKE_PENDING,
            CaseStatus.INTAKE_DONE,
            CaseStatus.DOCS_COLLECTING,
            CaseStatus.FINANCIALS_READY,
            CaseStatus.VALUATION_DONE,
            CaseStatus.DRAFTS_GENERATED,
            CaseStatus.UNDER_REVIEW,
            CaseStatus.REPORT_READY,
            CaseStatus.DELIVERED,
            CaseStatus.CLOSED,
        ]

    @classmethod
    def get_status_stage(cls, status: CaseStatus) -> str:
        """
        Get the general stage of a status (for grouping).

        Returns:
            Stage name: 'intake', 'preparation', 'valuation', 'drafting', 'delivery', 'complete'
        """
        stage_mapping = {
            CaseStatus.CREATED: "intake",
            CaseStatus.INTAKE_PENDING: "intake",
            CaseStatus.INTAKE_DONE: "preparation",
            CaseStatus.DOCS_COLLECTING: "preparation",
            CaseStatus.FINANCIALS_READY: "valuation",
            CaseStatus.VALUATION_DONE: "valuation",
            CaseStatus.DRAFTS_GENERATED: "drafting",
            CaseStatus.UNDER_REVIEW: "drafting",
            CaseStatus.REPORT_READY: "delivery",
            CaseStatus.DELIVERED: "delivery",
            CaseStatus.CLOSED: "complete",
        }
        return stage_mapping.get(status, "unknown")
