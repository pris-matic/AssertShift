# AssertShift — Analysis & Verification Report

> **Tagline:** Your code changed. Did your tests?
>
> Generated: 2026-09-26  
> Bob mode: Plan (analysis) → Agent (test edits)  
> Verification status: **VERIFIED**

---

## 1. Change summary

**Source:** [`inputs/change-request.md`](../inputs/change-request.md)

The `calculate_discount` function was updated from a flat 10% Premium discount to a differentiated rule set:

| Rule | Old behavior | New behavior |
|---|---|---|
| Premium only | 10%, no cap | **15%**, capped at $100 |
| Premium + Student | 10%, no cap | **20%**, capped at $100 |
| Non-Premium (incl. Student-only) | 0% | **0% — preserved invariant** |
| Cap | None | **$100.00** on discount amount |
| Rounding | ROUND_HALF_UP, 2dp | ROUND_HALF_UP, 2dp (unchanged) |

---

## 2. Baseline test suite

**Suite:** `verification_snapshots/baseline_tests/test_discounts.py`  
**Suite hash:** `sha256:2291368d3102775a`  
**Tests examined:** 8  
**Result on correct implementation:** ✅ 8 passed, 0 failed

The baseline suite **passes** on the correct post-change code but contains demonstrably weak assertions. This is the "green but incomplete" starting state.

---

## 3. Bob findings

Bob examined the baseline suite and identified **0 BREAKING**, **2 STALE**, and **4 MISSING** findings.

### F-001 — STALE

- **Test:** `TestPremiumDiscount::test_premium_gets_a_discount`
- **Requirement:** Premium-only → 15% (`change-request.md §3.1 rule 1`)
- **Reason:** `assert result > Decimal('0.00')` passes for both the old 10% and the new 15%. Counterexample: the `premium_still_10` mutant returns `Decimal('10.00')`, which still satisfies `> 0`.
- **Action:** Replace with `assert result == Decimal('15.00')`

### F-002 — STALE

- **Test:** `TestPremiumDiscount::test_premium_discount_is_positive`
- **Requirement:** Premium-only → 15% (`change-request.md §3.1 rule 1`)
- **Reason:** Same positivity-only assertion on a $200 order. Does not distinguish 10% ($20) from 15% ($30).
- **Action:** Replace with `assert result == Decimal('30.00')`

### F-003 — MISSING

- **Gap:** No test covers `is_premium=True, is_student=True`
- **Requirement:** Premium+Student → 20% (`change-request.md §3.1 rule 2`)
- **Evidence:** The baseline suite contains no targeted Premium+Student assertion. The evolved suite adds `test_premium_and_student_combination`, which passes against the correct implementation (`Decimal('20.00')`).
- **Limitation:** The current three-mutant matrix does not include a dedicated mutant for an incorrect Premium+Student rate. This finding is demonstrated through missing baseline coverage plus the new executable acceptance test, not through a dedicated mutant kill.
- **Action:** Add `test_premium_and_student_combination`

### F-004 — MISSING

- **Gap:** No test covers `is_premium=False, is_student=True`
- **Requirement:** Non-Premium (including Student-only) → 0% (`change-request.md §3.1 rule 3, §6`)
- **Evidence:** `student_without_premium` mutant (gives 20% to non-premium students) passes all 8 baseline tests. Evolved `test_student_only_gets_no_discount` catches it: `assert Decimal('20.00') == Decimal('0.00')`.
- **Action:** Add `test_student_only_gets_no_discount`

### F-005 — MISSING

- **Gap:** No test uses an order total large enough to produce a raw discount > $100
- **Requirement:** $100 cap on discount amount (`change-request.md §3.3`)
- **Evidence:** `missing_discount_cap` mutant (no cap) passes all 8 baseline tests. Evolved `test_cap_premium_only` catches it: `assert Decimal('150.00') == Decimal('100.00')`.
- **Action:** Add `test_cap_premium_only` and `test_cap_premium_and_student`

### F-006 — MISSING

- **Gap:** No rounding-then-cap boundary test
- **Requirement:** Rounding-then-cap behavior (`change-request.md §§3.2–3.4` — calculation order, cap, rounding)
- **Reasoning:** $666.70 × 15% = $100.005; ROUND_HALF_UP → $100.01; cap → $100.00. The correct implementation caps the rounded value; the `missing_discount_cap` mutant returns $100.01.
- **Action:** Add `test_rounding_then_cap` (`Decimal('666.70')` → `Decimal('100.00')`)

---

## 4. Evolved test suite

**Suite:** `sample_app/tests/test_discounts.py`
**Suite hash:** `sha256:78fa1c73c28ace99`
**Tests:** 19 total — all 8 baseline tests retained (2 of those 8 were tightened) + 11 new tests added
**Result on correct implementation:** ✅ 19 passed, 0 failed

| Action | Tests |
|---|---|
| Assertions tightened (updated) | `test_premium_gets_a_discount` → exact 15.00; `test_premium_discount_is_positive` → exact 30.00 |
| Added: combination | `test_premium_and_student_combination`, `test_premium_student_below_cap`, `test_premium_student_at_cap_boundary` |
| Added: invariant | `test_student_only_gets_no_discount`, `test_student_only_large_order_gets_no_discount` |
| Added: cap | `test_cap_premium_only`, `test_cap_premium_and_student` |
| Added: boundary | `test_rounding_boundary_just_below_cap`, `test_rounding_then_cap` |
| Added: input contract | `test_zero_total_premium_student`, `test_negative_total_non_premium_raises` |
| Preserved intact | All other input-contract and non-premium tests |

**tests_updated: 2 | tests_created: 11** (19 evolved − 8 baseline = 11 new)

---

## 5. Verification matrix

**Command:** `python scripts/run_verification_matrix.py`  
**All 8 runs completed without infrastructure errors.**

| Suite | Candidate | Result | Passed | Failed |
|---|---|:---:|:---:|:---:|
| baseline | correct | ✅ PASS | 8 | 0 |
| baseline | premium\_still\_10 | ⚠️ PASS (escapes) | 8 | 0 |
| baseline | missing\_discount\_cap | ⚠️ PASS (escapes) | 8 | 0 |
| baseline | student\_without\_premium | ⚠️ PASS (escapes) | 8 | 0 |
| evolved | correct | ✅ PASS | 19 | 0 |
| evolved | premium\_still\_10 | 🔴 BEHAVIORAL\_FAIL (caught) | 15 | 4 |
| evolved | missing\_discount\_cap | 🔴 BEHAVIORAL\_FAIL (caught) | 16 | 3 |
| evolved | student\_without\_premium | 🔴 BEHAVIORAL\_FAIL (caught) | 17 | 2 |

### Relevant behavioral failures (evolved suite)

**`premium_still_10` — caught by:**
```
TestPremiumOnlyDiscount::test_premium_discount_exact_rate
  AssertionError: assert Decimal('10.00') == Decimal('15.00')
```

**`missing_discount_cap` — caught by:**
```
TestPremiumOnlyDiscount::test_cap_premium_only
  AssertionError: assert Decimal('150.00') == Decimal('100.00')

TestPremiumOnlyDiscount::test_rounding_then_cap
  AssertionError: assert Decimal('100.01') == Decimal('100.00')
```
*(The `test_rounding_then_cap` failure proves the rounding-then-cap interaction: $666.70 × 15% = $100.005 → $100.01 uncapped, vs correct $100.00.)*

**`student_without_premium` — caught by:**
```
TestNonPremiumDiscount::test_student_only_gets_no_discount
  AssertionError: assert Decimal('20.00') == Decimal('0.00')
```

---

## 6. Verification status: VERIFIED

- ✅ Correct implementation passes both baseline (8/8) and evolved (19/19) suites.
- ✅ All three mutants escape the baseline suite (green suite is weak).
- ✅ All three mutants are caught by the evolved suite on their relevant tests.
- ✅ Fragment-based defect evidence confirmed for every caught mutant.
- ✅ Zero infrastructure errors across all 8 runs.

---

## 7. What this evidence proves and does not prove

**Proves:**
- The baseline suite is demonstrably weak — it cannot distinguish 15% from 10%, cannot detect a missing cap (including a rounded-above-cap case), and cannot detect a broken Student-only invariant.
- Bob's evolved suite detects each of those three specific behavioral defects on inputs directly relevant to the defect.
- The evolved suite still passes on the correct implementation (no false failures introduced).

**Does not prove:**
- That the implementation or test suite has no other defects.
- That all possible test inputs are covered.
- That F-003 (Premium+Student rate) is caught by a dedicated mutant — it is covered by an acceptance test only.
- Any productivity or time-saved claim (no controlled manual comparison was conducted).

---

## 8. Limitations

1. Verification measures detection of exactly **three chosen single-defect mutants**, not exhaustive correctness.
2. No manual-time benchmark was conducted; speed claims are omitted.
3. `BREAKING = 0` — the main controlled scenario has no legitimately breaking tests. The baseline suite was designed to pass on the correct post-change code. The BREAKING classification is supported conceptually but no separate BREAKING example was included in the recorded run.
4. F-003 (Premium+Student coverage) is demonstrated through missing baseline coverage and the new evolved acceptance test. The current three-mutant scope does not include a dedicated mutant for an incorrect Premium+Student rate.
5. Bob session evidence is captured in `bob_sessions/README.md`; live IDE screenshots were not committed.
6. PDF document reading was not demonstrated; Bob read `inputs/change-request.md` directly.

---

*Report viewer: [`docs/index.html`](../docs/index.html) — Bob analysis runs in the IDE, not the viewer.*
