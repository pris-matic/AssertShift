"""Mutant: premium_still_10

Named defect: Premium-only customers receive 10% instead of the approved 15%.
All other post-change rules (cap, Premium+Student 20%, invariants) are correct.

This is a controlled known-bad fixture — NOT a bug found in the real code.
"""

from decimal import ROUND_HALF_UP, Decimal

_CAP = Decimal("100.00")
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
        rate = Decimal("0.20")  # Premium + Student: correct 20%
    else:
        rate = Decimal("0.10")  # DEFECT: should be 0.15, uses old 0.10 instead

    raw = order_total * rate
    discount = raw.quantize(_TWO_PLACES, rounding=ROUND_HALF_UP)

    if discount > _CAP:
        return _CAP

    return discount
