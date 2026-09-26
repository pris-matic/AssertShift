"""Mutant: missing_discount_cap

Named defect: The $100 cap is not applied — discount amount is unbounded.
All other post-change rules (15% / 20% rates, invariants, rounding) are correct.

This is a controlled known-bad fixture — NOT a bug found in the real code.
"""

from decimal import ROUND_HALF_UP, Decimal

_TWO_PLACES = Decimal("0.01")


def calculate_discount(
    order_total: Decimal,
    *,
    is_premium: bool,
    is_student: bool,
) -> Decimal:
    if order_total < Decimal("0"):
        raise ValueError(f"order_total must be nonnegative; got {order_total!r}")

    if order_total == Decimal("0"):
        return Decimal("0.00")

    if not is_premium:
        return Decimal("0.00")

    if is_student:
        rate = Decimal("0.20")
    else:
        rate = Decimal("0.15")

    raw = order_total * rate
    # DEFECT: cap is intentionally omitted
    return raw.quantize(_TWO_PLACES, rounding=ROUND_HALF_UP)
