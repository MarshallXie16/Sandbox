"""
Workflow Service for Facilitator Automation.

Manages state transitions and validates workflow rules for engagements.
"""

from typing import Dict, Set, Optional
from app.models.enums import EngagementStatus


class WorkflowService:
    """
    Service for managing engagement workflow and state machine.

    State machine:
    - draft → active
    - active → (shortlisting | outreach_in_progress | offers_in_play |
                under_agreement | closed_success | closed_no_deal | terminated)
    - shortlisting → (outreach_in_progress | active)
    - outreach_in_progress → (offers_in_play | active)
    - offers_in_play → (under_agreement | closed_success | closed_no_deal | terminated)
    - under_agreement → (closed_success | closed_no_deal | terminated)

    Terminal states: closed_success, closed_no_deal, terminated
    """

    # Define allowed state transitions
    ALLOWED_TRANSITIONS: Dict[EngagementStatus, Set[EngagementStatus]] = {
        EngagementStatus.DRAFT: {
            EngagementStatus.ACTIVE,
        },
        EngagementStatus.ACTIVE: {
            EngagementStatus.SHORTLISTING,
            EngagementStatus.OUTREACH_IN_PROGRESS,
            EngagementStatus.OFFERS_IN_PLAY,
            EngagementStatus.UNDER_AGREEMENT,
            EngagementStatus.CLOSED_SUCCESS,
            EngagementStatus.CLOSED_NO_DEAL,
            EngagementStatus.TERMINATED,
        },
        EngagementStatus.SHORTLISTING: {
            EngagementStatus.ACTIVE,
            EngagementStatus.OUTREACH_IN_PROGRESS,
            EngagementStatus.TERMINATED,
        },
        EngagementStatus.OUTREACH_IN_PROGRESS: {
            EngagementStatus.ACTIVE,
            EngagementStatus.OFFERS_IN_PLAY,
            EngagementStatus.TERMINATED,
        },
        EngagementStatus.OFFERS_IN_PLAY: {
            EngagementStatus.ACTIVE,
            EngagementStatus.UNDER_AGREEMENT,
            EngagementStatus.CLOSED_SUCCESS,
            EngagementStatus.CLOSED_NO_DEAL,
            EngagementStatus.TERMINATED,
        },
        EngagementStatus.UNDER_AGREEMENT: {
            EngagementStatus.OFFERS_IN_PLAY,  # Can go back if agreement falls through
            EngagementStatus.CLOSED_SUCCESS,
            EngagementStatus.CLOSED_NO_DEAL,
            EngagementStatus.TERMINATED,
        },
        # Terminal states - no transitions allowed
        EngagementStatus.CLOSED_SUCCESS: set(),
        EngagementStatus.CLOSED_NO_DEAL: set(),
        EngagementStatus.TERMINATED: set(),
    }

    TERMINAL_STATES: Set[EngagementStatus] = {
        EngagementStatus.CLOSED_SUCCESS,
        EngagementStatus.CLOSED_NO_DEAL,
        EngagementStatus.TERMINATED,
    }

    ACTIVE_STATES: Set[EngagementStatus] = {
        EngagementStatus.ACTIVE,
        EngagementStatus.SHORTLISTING,
        EngagementStatus.OUTREACH_IN_PROGRESS,
        EngagementStatus.OFFERS_IN_PLAY,
        EngagementStatus.UNDER_AGREEMENT,
    }

    @classmethod
    def is_transition_allowed(
        cls,
        from_status: EngagementStatus,
        to_status: EngagementStatus
    ) -> bool:
        """
        Check if a state transition is allowed.

        Args:
            from_status: Current status
            to_status: Desired status

        Returns:
            True if transition is allowed, False otherwise
        """
        # Allow staying in the same state
        if from_status == to_status:
            return True

        allowed = cls.ALLOWED_TRANSITIONS.get(from_status, set())
        return to_status in allowed

    @classmethod
    def validate_transition(
        cls,
        from_status: EngagementStatus,
        to_status: EngagementStatus
    ) -> None:
        """
        Validate a state transition, raising an error if invalid.

        Args:
            from_status: Current status
            to_status: Desired status

        Raises:
            ValueError: If transition is not allowed
        """
        if not cls.is_transition_allowed(from_status, to_status):
            raise ValueError(
                f"Invalid state transition: {from_status.value} → {to_status.value}. "
                f"Allowed transitions from {from_status.value}: "
                f"{[s.value for s in cls.ALLOWED_TRANSITIONS.get(from_status, set())]}"
            )

    @classmethod
    def is_terminal_state(cls, status: EngagementStatus) -> bool:
        """
        Check if a status is a terminal state.

        Terminal states cannot transition to any other state.

        Args:
            status: Status to check

        Returns:
            True if terminal, False otherwise
        """
        return status in cls.TERMINAL_STATES

    @classmethod
    def is_active_state(cls, status: EngagementStatus) -> bool:
        """
        Check if a status is an active state.

        Active states are those where the engagement is actively being worked on.

        Args:
            status: Status to check

        Returns:
            True if active, False otherwise
        """
        return status in cls.ACTIVE_STATES

    @classmethod
    def get_allowed_transitions(
        cls,
        from_status: EngagementStatus
    ) -> Set[EngagementStatus]:
        """
        Get all allowed transitions from a given status.

        Args:
            from_status: Current status

        Returns:
            Set of allowed target statuses
        """
        return cls.ALLOWED_TRANSITIONS.get(from_status, set()).copy()

    @classmethod
    def get_next_status_for_action(
        cls,
        current_status: EngagementStatus,
        action: str
    ) -> Optional[EngagementStatus]:
        """
        Get the next status based on an action.

        This maps common actions to status transitions.

        Args:
            current_status: Current engagement status
            action: Action being performed (e.g., "activate", "start_outreach")

        Returns:
            Next status or None if action doesn't map to a transition
        """
        action_mapping = {
            "activate": EngagementStatus.ACTIVE,
            "start_shortlist": EngagementStatus.SHORTLISTING,
            "start_outreach": EngagementStatus.OUTREACH_IN_PROGRESS,
            "offers_received": EngagementStatus.OFFERS_IN_PLAY,
            "offer_accepted": EngagementStatus.UNDER_AGREEMENT,
            "close_success": EngagementStatus.CLOSED_SUCCESS,
            "close_no_deal": EngagementStatus.CLOSED_NO_DEAL,
            "terminate": EngagementStatus.TERMINATED,
        }

        target_status = action_mapping.get(action)

        if target_status and cls.is_transition_allowed(current_status, target_status):
            return target_status

        return None

    @classmethod
    def get_workflow_description(cls, status: EngagementStatus) -> str:
        """
        Get human-readable description of a workflow status.

        Args:
            status: Engagement status

        Returns:
            Description string
        """
        descriptions = {
            EngagementStatus.DRAFT: "Engagement is in draft, not yet active",
            EngagementStatus.ACTIVE: "Engagement is active",
            EngagementStatus.SHORTLISTING: "Building shortlist of candidate buyers",
            EngagementStatus.OUTREACH_IN_PROGRESS: "Actively reaching out to buyers",
            EngagementStatus.OFFERS_IN_PLAY: "One or more offers have been received",
            EngagementStatus.UNDER_AGREEMENT: "An offer has been accepted in principle",
            EngagementStatus.CLOSED_SUCCESS: "Deal closed successfully with introduced buyer",
            EngagementStatus.CLOSED_NO_DEAL: "Engagement ended without a deal",
            EngagementStatus.TERMINATED: "Engagement terminated early",
        }
        return descriptions.get(status, "Unknown status")
