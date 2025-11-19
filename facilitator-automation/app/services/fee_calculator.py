"""
Fee Calculator Service for Facilitator Automation.

Implements the fee structure:
- Fixed offer fee: $5,000 (default) when an introduced buyer makes an offer
- Success fee: 5% (default) of final price when deal closes with introduced buyer
- Credit: Offer fees already paid are credited against success fee
"""

from decimal import Decimal
from typing import Dict, Any
from dataclasses import dataclass

from app.core.config import settings


@dataclass
class FeeCalculation:
    """
    Result of fee calculation.

    Attributes:
        success_fee_rate: Rate applied (e.g., 0.05 for 5%)
        final_price: Final transaction price
        success_fee_gross: Gross success fee (final_price * rate)
        offer_fee_credit: Credit for offer fees already paid
        success_fee_net: Net success fee after credit
        total_facilitator_revenue: Total revenue (credit + net)
    """

    success_fee_rate: Decimal
    final_price: Decimal
    success_fee_gross: Decimal
    offer_fee_credit: Decimal
    success_fee_net: Decimal
    total_facilitator_revenue: Decimal

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "success_fee_rate": float(self.success_fee_rate),
            "final_price": float(self.final_price),
            "success_fee_gross": float(self.success_fee_gross),
            "offer_fee_credit": float(self.offer_fee_credit),
            "success_fee_net": float(self.success_fee_net),
            "total_facilitator_revenue": float(self.total_facilitator_revenue),
        }


class FeeCalculatorService:
    """
    Service for calculating facilitator fees.

    This implements the core fee logic:
    1. Offer fee: Fixed amount (default $5k) when buyer makes an offer
    2. Success fee: Percentage (default 5%) of final price when deal closes
    3. Credit: Offer fees paid are credited against success fee (capped at gross)

    Legal context: Fees are only calculated for Introduced Buyers.
    This is a facilitator/finder agreement, not a brokerage agreement.
    """

    @staticmethod
    def calculate_success_fee(
        final_price: Decimal,
        success_fee_rate: Decimal,
        offer_fees_paid: Decimal
    ) -> FeeCalculation:
        """
        Calculate success fee with offer fee credit.

        Args:
            final_price: Final transaction price
            success_fee_rate: Success fee rate (e.g., 0.05 for 5%)
            offer_fees_paid: Total offer fees already paid for this buyer

        Returns:
            FeeCalculation with all fee components

        Example:
            final_price = $2,000,000
            success_fee_rate = 0.05 (5%)
            offer_fees_paid = $5,000

            success_fee_gross = $2,000,000 * 0.05 = $100,000
            offer_fee_credit = min($5,000, $100,000) = $5,000
            success_fee_net = $100,000 - $5,000 = $95,000
            total_revenue = $5,000 + $95,000 = $100,000
        """
        # Calculate gross success fee
        success_fee_gross = final_price * success_fee_rate

        # Credit is capped at gross amount (can't be negative)
        offer_fee_credit = min(offer_fees_paid, success_fee_gross)

        # Net success fee after credit
        success_fee_net = success_fee_gross - offer_fee_credit

        # Total revenue (what was already paid + what's due now)
        total_revenue = offer_fee_credit + success_fee_net

        return FeeCalculation(
            success_fee_rate=success_fee_rate,
            final_price=final_price,
            success_fee_gross=success_fee_gross,
            offer_fee_credit=offer_fee_credit,
            success_fee_net=success_fee_net,
            total_facilitator_revenue=total_revenue
        )

    @staticmethod
    def get_default_offer_fee() -> Decimal:
        """Get default offer fee from configuration."""
        return Decimal(str(settings.default_offer_fee_fixed))

    @staticmethod
    def get_default_success_fee_rate() -> Decimal:
        """Get default success fee rate from configuration."""
        return Decimal(str(settings.default_success_fee_rate))

    @staticmethod
    def validate_fee_rate(rate: Decimal) -> None:
        """
        Validate that fee rate is between 0 and 1.

        Args:
            rate: Fee rate to validate

        Raises:
            ValueError: If rate is out of range
        """
        if not 0 <= rate <= 1:
            raise ValueError(f"Fee rate must be between 0 and 1, got {rate}")

    @staticmethod
    def calculate_gross_success_fee(
        final_price: Decimal,
        success_fee_rate: Decimal
    ) -> Decimal:
        """
        Calculate gross success fee without credit.

        Args:
            final_price: Final transaction price
            success_fee_rate: Success fee rate

        Returns:
            Gross success fee amount
        """
        return final_price * success_fee_rate

    @staticmethod
    def format_currency(amount: Decimal, currency: str = "CAD") -> str:
        """
        Format amount as currency string.

        Args:
            amount: Amount to format
            currency: Currency code

        Returns:
            Formatted string (e.g., "CAD $100,000.00")
        """
        return f"{currency} ${amount:,.2f}"
