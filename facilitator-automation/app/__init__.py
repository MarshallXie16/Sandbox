"""
Facilitator Automation - Phase 2 Facilitator Service Module.

This module implements a structured, compliant, non-broker, non-fiduciary
coordination layer for tracking buyer introductions and facilitator fees.

Legal context: This is a facilitator/finder workflow system, NOT a brokerage system.
- No fiduciary duty
- No agency role
- No automated price advice or negotiation agent behavior
- Success fees only calculated for Introduced Buyers

Core functionality:
- Track facilitator engagements with sellers/listings
- Record introduced buyers and their lifecycle
- Track offers and deal outcomes
- Calculate facilitator fees (fixed $5k at offer + 5% success fee with credit)
"""

__version__ = "1.0.0"
__author__ = "Capital Link"
__description__ = "Facilitator Automation - Phase 2 Facilitator Service"
