# Change Request: Discount Service — New Premium/Student Rules

**Date:** 2025-01-01  
**Status:** Approved  
**Scope:** `calculate_discount` function in `sample_app/app/discounts.py`

---

## 1. Background

The current discount service applies a flat 10% discount to Premium customers and 0% to everyone else. Student status has no effect. This change introduces differentiated rates, a Premium+Student combination discount, and a per-order cap.

---

## 2. Current (pre-change) behavior

| Condition | Discount rate | Notes |
|---|---:|---|
| Premium only | 10% of `order_total` | No cap |
| Non-Premium (any Student status) | 0% | Student flag ignored |
| Student only | 0% | No student discount without Premium |

---

## 3. Approved new behavior

### 3.1 Discount rates

1. **Premium only** (`is_premium=True`, `is_student=False`): **15%** of `order_total`.
2. **Premium and Student** (`is_premium=True`, `is_student=True`): **20%** of `order_total`.
3. **Non-Premium** (including Student-only; `is_premium=False`): **0%** — _preserved invariant_.

### 3.2 Cap

After calculating the percentage, **cap the discount amount at `Decimal("100.00")`**. If the raw percentage discount exceeds $100.00, return exactly `Decimal("100.00")`.

### 3.3 Rounding

Round the final result to two decimal places using **`ROUND_HALF_UP`**.

---

## 4. Input contract (unchanged)

- `order_total`: a finite, nonnegative US-dollar `Decimal` with at most two fractional digits.
- Negative `order_total` raises `ValueError`.
- `order_total == Decimal("0.00")` returns `Decimal("0.00")` regardless of flags.
- `is_premium` and `is_student` are plain `bool` values.
- Do not use `float` in application code or tests; use `Decimal` throughout.

---

## 5. Return contract (unchanged)

- Returns a `Decimal` with exactly two fractional digits (`Decimal("X.XX")`).
- Negative return values are not possible under valid input.

---

## 6. Preserved invariant

> **Non-Premium customers — including those with `is_student=True` — receive a 0% discount.**
> This invariant is unchanged by this request. Any test that verified 0% for non-Premium must continue to pass.

---

## 7. Acceptance examples

| `order_total` | `is_premium` | `is_student` | Expected discount | Rationale |
|---:|:---:|:---:|---:|---|
| `100.00` | ✓ | ✗ | `15.00` | Distinguishes 15% from old 10% |
| `100.00` | ✓ | ✓ | `20.00` | Premium+Student combination |
| `100.00` | ✗ | ✓ | `0.00` | Preserved invariant: Student-only → 0% |
| `100.00` | ✗ | ✗ | `0.00` | Preserved invariant: Non-Premium → 0% |
| `1000.00` | ✓ | ✗ | `100.00` | Cap: raw 15% = $150, capped to $100 |
| `1000.00` | ✓ | ✓ | `100.00` | Cap: raw 20% = $200, capped to $100 |
| `0.00` | ✓ | ✓ | `0.00` | Zero input → zero output |
| Negative | any | any | `ValueError` | Invalid input |
| `666.70` | ✓ | ✗ | `100.00` | Rounding-then-cap: 15% = $100.005 → ROUND_HALF_UP → $100.01 → cap |
| `499.99` | ✓ | ✗ | `75.00` | Below cap: 15% of $499.99 = $74.9985 → $75.00 |

---

## 8. Out of scope

- Floats, `str`, `int`, or high-precision `Decimal` inputs.
- Stacking multiple discount types beyond the Premium+Student combination.
- Other customer segments or order types.
