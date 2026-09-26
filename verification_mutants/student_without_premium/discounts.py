"""Mutant: student_without_premium

Named defect: Student-only customers (is_premium=False, is_student=True)
incorrectly receive a 20% discount, violating the preserved invariant.
All other post-change rules (Premium rates, cap, non-student non-premium) are correct.

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

    # DEFECT: Student-only case is evaluated before the non-premium guard,
    # incorrectly granting 20% to non-premium students.
    if is_student and not is_premium:
        rate = Decimal("0.20")
        raw = order_total * rate
        discount = raw.quantize(_TWO_PLACES, rounding=ROUND_HALF_UP)
        if discount > _CAP:
            return _CAP
        return discount

    if not is_premium:
        return Decimal("0.00")

    if is_student:
        rate = Decimal("0.20")
    else:
        rate = Decimal("0.15")

    raw = order_total * rate
    discount = raw.quantize(_TWO_PLACES, rounding=ROUND_HALF_UP)

    if discount > _CAP:
        return _CAP

    return discount
