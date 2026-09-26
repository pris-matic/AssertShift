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
- Final IBM Bob audit screenshots are included under `bob_sessions/screenshots/`.

## Final read-only audit evidence

After the implementation, test evolution, verification harness, reports, and documentation were finalized, Bob performed one final **read-only consistency audit** using three focused analyst tasks in parallel:

1. **Requirements Analyst** — compared `inputs/change-request.md` with `sample_app/app/discounts.py`.
2. **Test Analyst** — compared `verification_snapshots/baseline_tests/test_discounts.py` with `sample_app/tests/test_discounts.py`.
3. **Verification Analyst** — cross-checked `verification/matrix_results.json`, `verification/manifest.json`, `artifacts/assertshift-report.json`, `artifacts/assertshift-report.md`, and the root `README.md`.

Bob then consolidated the three analyst results into one final audit summary. No executable files were modified during this audit.

### Screenshots

#### 1. Audit prompt and parallel analysts running

![Audit prompt and parallel analysts running](screenshots/01-audit-prompt-running.png)

The final read-only audit prompt is shown with the Requirements Analyst, Test Analyst, and Verification Analyst running as separate focused tasks.

#### 2. Parallel audits completed

![Parallel audits completed](screenshots/02-parallel-audits-complete.png)

All three analyst tasks completed before Bob produced the consolidated report.

#### 3. Requirements audit

![Requirements audit](screenshots/03-requirements-audit.png)

The Requirements Analyst verified the approved discount rates, calculation order, cap behavior, preserved non-Premium invariant, input contract, and return contract against the implementation. **Verdict: PASS.**

#### 4. Test-evolution audit

![Test-evolution audit](screenshots/04-test-audit.png)

The Test Analyst verified the baseline/evolved suite accounting and findings:

- 8 baseline tests
- 19 evolved tests
- 0 BREAKING findings
- 2 STALE tests tightened
- 4 MISSING coverage areas
- 11 new tests added
- all 8 baseline tests retained, with 2 renamed/tightened

**Verdict: PASS.**

#### 5. Verification audit

![Verification audit](screenshots/05-verification-audit.png)

The Verification Analyst cross-checked the generated matrix, manifest, reports, and README and confirmed:

- 8 matrix runs
- 0 infrastructure errors
- all 3 mutants escape the baseline suite
- all 3 mutants are caught by the evolved suite
- `VERIFIED` status is consistent
- suite/candidate hashes are consistent
- test and finding counts agree across artifacts

**Verdict: PASS.**

#### 6. Consolidated final result

![Overall audit result](screenshots/06-overall-audit-pass.png)

Bob consolidated the three analyst results:

```text
Requirements Analyst: PASS
Test Analyst: PASS
Verification Analyst: PASS

OVERALL: PASS — No inconsistencies found. No files modified.
```

These screenshots are direct captures of the IBM Bob session and are included as workflow evidence rather than reconstructed or fabricated results.

