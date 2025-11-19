"""
Tests for Fee Calculator Service.

Tests the core fee calculation logic for facilitator fees.
"""

import pytest
from decimal import Decimal
from app.services.fee_calculator import FeeCalculatorService, FeeCalculation


class TestFeeCalculator:
    """Test suite for FeeCalculatorService."""

    def test_calculate_success_fee_normal_case(self):
        """Test normal fee calculation with standard values."""
        # Given
        final_price = Decimal("2000000")  # $2M
        success_fee_rate = Decimal("0.05")  # 5%
        offer_fees_paid = Decimal("5000")  # $5k

        # When
        result = FeeCalculatorService.calculate_success_fee(
            final_price, success_fee_rate, offer_fees_paid
        )

        # Then
        assert result.final_price == Decimal("2000000")
        assert result.success_fee_rate == Decimal("0.05")
        assert result.success_fee_gross == Decimal("100000")  # 2M * 0.05
        assert result.offer_fee_credit == Decimal("5000")
        assert result.success_fee_net == Decimal("95000")  # 100k - 5k
        assert result.total_facilitator_revenue == Decimal("100000")

    def test_calculate_success_fee_multiple_offers(self):
        """Test fee calculation with multiple offer fees paid."""
        # Given
        final_price = Decimal("2000000")
        success_fee_rate = Decimal("0.05")
        offer_fees_paid = Decimal("15000")  # 3 offers × $5k

        # When
        result = FeeCalculatorService.calculate_success_fee(
            final_price, success_fee_rate, offer_fees_paid
        )

        # Then
        assert result.success_fee_gross == Decimal("100000")
        assert result.offer_fee_credit == Decimal("15000")
        assert result.success_fee_net == Decimal("85000")
        assert result.total_facilitator_revenue == Decimal("100000")

    def test_calculate_success_fee_credit_capped(self):
        """Test that credit is capped at gross amount."""
        # Given: Low-value deal where offer fees exceed gross
        final_price = Decimal("50000")  # $50k
        success_fee_rate = Decimal("0.05")  # 5%
        offer_fees_paid = Decimal("5000")  # $5k

        # When
        result = FeeCalculatorService.calculate_success_fee(
            final_price, success_fee_rate, offer_fees_paid
        )

        # Then
        assert result.success_fee_gross == Decimal("2500")  # 50k * 0.05
        assert result.offer_fee_credit == Decimal("2500")  # Capped at gross
        assert result.success_fee_net == Decimal("0")
        assert result.total_facilitator_revenue == Decimal("2500")

    def test_calculate_success_fee_no_offer_fees(self):
        """Test fee calculation when no offer fees have been paid."""
        # Given
        final_price = Decimal("1000000")
        success_fee_rate = Decimal("0.05")
        offer_fees_paid = Decimal("0")

        # When
        result = FeeCalculatorService.calculate_success_fee(
            final_price, success_fee_rate, offer_fees_paid
        )

        # Then
        assert result.success_fee_gross == Decimal("50000")
        assert result.offer_fee_credit == Decimal("0")
        assert result.success_fee_net == Decimal("50000")
        assert result.total_facilitator_revenue == Decimal("50000")

    def test_fee_calculation_to_dict(self):
        """Test conversion to dictionary for JSON serialization."""
        # Given
        final_price = Decimal("1000000")
        success_fee_rate = Decimal("0.05")
        offer_fees_paid = Decimal("5000")

        # When
        result = FeeCalculatorService.calculate_success_fee(
            final_price, success_fee_rate, offer_fees_paid
        )
        result_dict = result.to_dict()

        # Then
        assert isinstance(result_dict, dict)
        assert result_dict["final_price"] == 1000000.0
        assert result_dict["success_fee_rate"] == 0.05
        assert result_dict["success_fee_gross"] == 50000.0
        assert result_dict["offer_fee_credit"] == 5000.0
        assert result_dict["success_fee_net"] == 45000.0

    def test_validate_fee_rate_valid(self):
        """Test fee rate validation with valid values."""
        # Should not raise
        FeeCalculatorService.validate_fee_rate(Decimal("0.05"))
        FeeCalculatorService.validate_fee_rate(Decimal("0"))
        FeeCalculatorService.validate_fee_rate(Decimal("1"))

    def test_validate_fee_rate_invalid(self):
        """Test fee rate validation with invalid values."""
        with pytest.raises(ValueError, match="Fee rate must be between 0 and 1"):
            FeeCalculatorService.validate_fee_rate(Decimal("1.1"))

        with pytest.raises(ValueError):
            FeeCalculatorService.validate_fee_rate(Decimal("-0.1"))

    def test_get_default_offer_fee(self):
        """Test getting default offer fee from configuration."""
        fee = FeeCalculatorService.get_default_offer_fee()
        assert isinstance(fee, Decimal)
        assert fee >= 0

    def test_get_default_success_fee_rate(self):
        """Test getting default success fee rate from configuration."""
        rate = FeeCalculatorService.get_default_success_fee_rate()
        assert isinstance(rate, Decimal)
        assert 0 <= rate <= 1

    def test_calculate_gross_success_fee(self):
        """Test calculating gross success fee."""
        result = FeeCalculatorService.calculate_gross_success_fee(
            Decimal("1000000"),
            Decimal("0.05")
        )
        assert result == Decimal("50000")

    def test_format_currency(self):
        """Test currency formatting."""
        formatted = FeeCalculatorService.format_currency(Decimal("1234567.89"), "CAD")
        assert "CAD" in formatted
        assert "1,234,567.89" in formatted
