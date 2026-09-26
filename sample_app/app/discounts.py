"""Discount service — post-change implementation.

Approved change request: inputs/change-request.md
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
    """Return the discount amount for an order.

    Args:
        order_total: A finite, nonnegative US-dollar Decimal with at most two
            fractional digits.
        is_premium: Whether the customer holds Premium status.
        is_student: Whether the customer holds Student status.

    Returns:
        The discount amount as a Decimal with two fractional digits, capped at
        Decimal("100.00") and rounded using ROUND_HALF_UP.

    Raises:
        ValueError: If order_total is negative.
    """
    if order_total < Decimal("0"):
        raise ValueError(f"order_total must be nonnegative; got {order_total!r}")

    if order_total == Decimal("0"):
        return Decimal("0.00")

    if not is_premium:
        # Preserved invariant: non-Premium customers (including Student-only)
        # always receive a 0% discount.
        return Decimal("0.00")

    # Premium branch
    if is_student:
        rate = Decimal("0.20")  # Premium + Student: 20%
    else:
        rate = Decimal("0.15")  # Premium only: 15%

    raw = order_total * rate
    discount = raw.quantize(_TWO_PLACES, rounding=ROUND_HALF_UP)

    if discount > _CAP:
        return _CAP

    return discount
