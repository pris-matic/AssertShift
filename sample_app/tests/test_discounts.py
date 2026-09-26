"""Evolved test suite — post-Bob-analysis (Bob-assisted edits reviewed and approved).

Changes from baseline:
  - test_premium_gets_a_discount: tightened from > 0 to == Decimal("15.00")  [STALE fix]
  - test_premium_discount_is_positive: replaced with exact 30.00 assertion   [STALE fix]
  - Added test_premium_and_student_combination                                [MISSING]
  - Added test_student_only_gets_no_discount (invariant)                      [MISSING]
  - Added test_cap_premium_only                                                [MISSING]
  - Added test_cap_premium_and_student                                         [MISSING]
  - Added test_rounding_boundary_just_below_cap                               [acceptance]
  - Added test_rounding_at_cap_boundary                                        [acceptance]
  - All preserved unaffected tests kept intact.
"""

from decimal import Decimal

import pytest

from sample_app.app.discounts import calculate_discount


# ---------------------------------------------------------------------------
# Input contract (preserved, unchanged)
# ---------------------------------------------------------------------------

class TestInputContract:
    def test_zero_total_premium(self):
        result = calculate_discount(
            Decimal("0.00"), is_premium=True, is_student=False
        )
        assert result == Decimal("0.00")

    def test_zero_total_non_premium(self):
        result = calculate_discount(
            Decimal("0.00"), is_premium=False, is_student=False
        )
        assert result == Decimal("0.00")

    def test_zero_total_premium_student(self):
        result = calculate_discount(
            Decimal("0.00"), is_premium=True, is_student=True
        )
        assert result == Decimal("0.00")

    def test_negative_total_raises(self):
        with pytest.raises(ValueError):
            calculate_discount(
                Decimal("-1.00"), is_premium=True, is_student=False
            )

    def test_negative_total_non_premium_raises(self):
        with pytest.raises(ValueError):
            calculate_discount(
                Decimal("-0.01"), is_premium=False, is_student=False
            )

    def test_return_type_is_decimal(self):
        result = calculate_discount(
            Decimal("50.00"), is_premium=True, is_student=False
        )
        assert isinstance(result, Decimal)


# ---------------------------------------------------------------------------
# Non-premium: preserved invariant
# ---------------------------------------------------------------------------

class TestNonPremiumDiscount:
    def test_non_premium_no_discount(self):
        result = calculate_discount(
            Decimal("100.00"), is_premium=False, is_student=False
        )
        assert result == Decimal("0.00")

    def test_student_only_gets_no_discount(self):
        """Preserved invariant: Student-only (non-Premium) → 0%."""
        result = calculate_discount(
            Decimal("100.00"), is_premium=False, is_student=True
        )
        assert result == Decimal("0.00")

    def test_student_only_large_order_gets_no_discount(self):
        """Invariant holds even for large orders."""
        result = calculate_discount(
            Decimal("1000.00"), is_premium=False, is_student=True
        )
        assert result == Decimal("0.00")

    def test_return_two_decimal_places_non_premium(self):
        result = calculate_discount(
            Decimal("99.99"), is_premium=False, is_student=False
        )
        assert result == Decimal("0.00")


# ---------------------------------------------------------------------------
# Premium-only: 15% with cap
# ---------------------------------------------------------------------------

class TestPremiumOnlyDiscount:
    def test_premium_discount_exact_rate(self):
        """Was STALE (> 0): now pins the exact 15% rate."""
        result = calculate_discount(
            Decimal("100.00"), is_premium=True, is_student=False
        )
        assert result == Decimal("15.00")

    def test_premium_discount_200(self):
        """Was STALE (> 0): now pins exact value for $200 order."""
        result = calculate_discount(
            Decimal("200.00"), is_premium=True, is_student=False
        )
        assert result == Decimal("30.00")

    def test_cap_premium_only(self):
        """Raw discount $150 exceeds cap → returns $100.00."""
        result = calculate_discount(
            Decimal("1000.00"), is_premium=True, is_student=False
        )
        assert result == Decimal("100.00")

    def test_rounding_boundary_just_below_cap(self):
        """$499.99 × 15% = $74.9985 → rounds to $75.00 (below cap)."""
        result = calculate_discount(
            Decimal("499.99"), is_premium=True, is_student=False
        )
        assert result == Decimal("75.00")

    def test_rounding_then_cap(self):
        """$666.70 × 15% = $100.005 → ROUND_HALF_UP to $100.01 → capped at $100.00."""
        result = calculate_discount(
            Decimal("666.70"), is_premium=True, is_student=False
        )
        assert result == Decimal("100.00")


# ---------------------------------------------------------------------------
# Premium + Student: 20% with cap
# ---------------------------------------------------------------------------

class TestPremiumStudentDiscount:
    def test_premium_and_student_combination(self):
        """Was MISSING: Premium+Student → 20%."""
        result = calculate_discount(
            Decimal("100.00"), is_premium=True, is_student=True
        )
        assert result == Decimal("20.00")

    def test_cap_premium_and_student(self):
        """Was MISSING: 20% of $1000 = $200, capped at $100."""
        result = calculate_discount(
            Decimal("1000.00"), is_premium=True, is_student=True
        )
        assert result == Decimal("100.00")

    def test_premium_student_below_cap(self):
        """$400 × 20% = $80.00, below cap."""
        result = calculate_discount(
            Decimal("400.00"), is_premium=True, is_student=True
        )
        assert result == Decimal("80.00")

    def test_premium_student_at_cap_boundary(self):
        """$500 × 20% = $100.00, exactly at cap."""
        result = calculate_discount(
            Decimal("500.00"), is_premium=True, is_student=True
        )
        assert result == Decimal("100.00")
