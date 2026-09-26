# Bob Session Evidence

This directory captures Bob's analysis and editing session for AssertShift.

## Session summary

**Date:** 2026-09-26  
**Bob mode sequence:** Plan → Agent  
**Project spec read:** `AssertShift_PROJECT_SPEC.md`

### Plan mode — analysis

Bob was asked to read `AssertShift_PROJECT_SPEC.md`, `inputs/change-request.md`,
`sample_app/app/discounts.py`, and `verification_snapshots/baseline_tests/test_discounts.py`.

**Findings produced:**

| ID | Classification | Finding |
|---|---|---|
| F-001 | STALE | `test_premium_gets_a_discount` asserts `> 0`, not exact 15% |
| F-002 | STALE | `test_premium_discount_is_positive` asserts `> 0`, not exact 30% |
| F-003 | MISSING | No test for Premium+Student (20%) combination |
| F-004 | MISSING | No test for Student-only invariant (0%) |
| F-005 | MISSING | No test for $100 cap |
| F-006 | MISSING | No rounding-then-cap boundary test |

**BREAKING findings:** 0 (baseline suite passes on correct post-change implementation — expected)

### Agent mode — test edits

After plan review, Bob updated `sample_app/tests/test_discounts.py`.

Bob tightened **2 existing tests** and added **11 new tests** (evolved total: 19):

**2 tightened existing tests:**

1. `test_premium_gets_a_discount`
   → `test_premium_discount_exact_rate`
   Assertion changed from `> 0` to `== Decimal("15.00")` (F-001)

2. `test_premium_discount_is_positive`
   → `test_premium_discount_200`
   Assertion changed from `> 0` to `== Decimal("30.00")` (F-002)

**11 newly added tests:**
1. `test_zero_total_premium_student` — input contract
2. `test_negative_total_non_premium_raises` — input contract
3. `test_student_only_gets_no_discount` — Student-only invariant (F-004)
4. `test_student_only_large_order_gets_no_discount` — Student-only invariant coverage
5. `test_cap_premium_only` — $100 cap: Premium-only (F-005)
6. `test_rounding_boundary_just_below_cap` — boundary: $499.99 × 15% = $75.00
7. `test_rounding_then_cap` — rounding-then-cap: $666.70 × 15% = $100.005 → $100.01 → capped $100.00 (F-006)
8. `test_premium_and_student_combination` — Premium+Student 20% (F-003)
9. `test_cap_premium_and_student` — $100 cap: Premium+Student (F-005)
10. `test_premium_student_below_cap` — Premium+Student below cap
11. `test_premium_student_at_cap_boundary` — Premium+Student at exact cap boundary

> Note: The exact count of 11 new tests is verified from the actual file diff (19 evolved − 8 baseline = 11).

All existing input-contract and non-premium tests were preserved intact.

### Verification

`python scripts/run_verification_matrix.py` was run after test edits.

**Result: VERIFIED** — all 8 matrix runs completed without infrastructure errors;
all 3 mutants caught by the evolved suite on relevant behavioral failures with
defect-specific evidence confirmed.

## Notes

- This file documents the Bob-assisted workflow. The actual Bob session ran inside the
  IBM Bob IDE. This repository captures the code artifacts produced by that session.
- No fabricated screenshots or hardcoded report values are present.
- The semantic findings (STALE/MISSING classifications) were produced by Bob's analysis
  of the source files; they are not hardcoded in any script or viewer.
- Screenshots and exported IDE session media are not yet committed (out of scope for this pass).
