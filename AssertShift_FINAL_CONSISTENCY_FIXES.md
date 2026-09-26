# AssertShift — Final Consistency Fixes

> **Purpose:** Apply the last two consistency fixes found during the final cleanup audit.
>
> `.gitignore` has already been fixed manually and is **out of scope** for this pass.
>
> Do not redesign AssertShift, change the verification model, add new mutants, or work on URLs/video/screenshots yet.

---

# 1. Fix the test-count/list inconsistency in `bob_sessions/README.md`

## Current issue

`bob_sessions/README.md` correctly states:

```text
Bob tightened 2 existing tests and added 11 new tests.
```

However, the section labeled:

```text
11 newly added tests
```

currently contains **12 numbered entries**.

The source of the mismatch is:

```text
test_premium_discount_exact_rate
```

This should be treated as the renamed/tightened replacement of the original stale test:

```text
test_premium_gets_a_discount
```

rather than as an additional newly created test.

Likewise:

```text
test_premium_discount_is_positive
```

became:

```text
test_premium_discount_200
```

as part of the two tightened existing tests.

## Required change

Rewrite the tightened-test section so the rename/replacement is explicit.

Recommended wording:

```text
2 tightened existing tests:

1. test_premium_gets_a_discount
   → test_premium_discount_exact_rate
   Assertion changed from:
   > 0
   to:
   == Decimal("15.00")

2. test_premium_discount_is_positive
   → test_premium_discount_200
   Assertion changed from:
   > 0
   to:
   == Decimal("30.00")
```

Then remove:

```text
test_premium_discount_exact_rate
```

from the list of newly added tests.

The final new-test list should contain exactly **11** tests.

## Final count that must remain true

```text
Baseline suite: 8 tests

Of those 8:
- 2 were tightened/renamed
- the remaining baseline coverage was preserved

New tests added: 11

Final evolved suite: 19 tests
```

## Acceptance criteria

- `bob_sessions/README.md` says **2 tightened** and **11 added**.
- The “newly added” section contains exactly 11 entries.
- `test_premium_discount_exact_rate` is documented as the evolved form of `test_premium_gets_a_discount`, not as an additional new test.
- `test_premium_discount_200` is documented as the evolved form of `test_premium_discount_is_positive`.
- Counts remain consistent with:
  - `artifacts/assertshift-report.json`
  - `artifacts/assertshift-report.md`
  - root `README.md`

---

# 2. Make the discount calculation order explicit in `inputs/change-request.md`

## Current issue

The change request currently states:

```text
Cap the discount after calculating the percentage.
```

and separately states:

```text
Round the final result to two decimal places using ROUND_HALF_UP.
```

The acceptance example now correctly demonstrates:

```text
$666.70 × 15%
= $100.005
→ ROUND_HALF_UP
= $100.01
→ cap
= $100.00
```

Therefore the intended operation order is:

```text
percentage calculation
→ rounding
→ cap
```

The requirements document should state this explicitly so there is no ambiguity between:

```text
percentage → cap → round
```

and:

```text
percentage → round → cap
```

## Required change

In:

```text
inputs/change-request.md
```

add an explicit calculation-order section or rewrite Sections 3.2–3.3 so the order is unambiguous.

Recommended wording:

```markdown
### 3.2 Calculation order

Apply the discount in this order:

1. Select the applicable discount rate.
2. Calculate the raw discount amount from `order_total`.
3. Round the discount amount to two decimal places using `ROUND_HALF_UP`.
4. Cap the rounded discount at `Decimal("100.00")`.

### 3.3 Cap

After rounding, if the discount amount exceeds `Decimal("100.00")`,
return exactly `Decimal("100.00")`.

### 3.4 Rounding

Round the calculated discount amount to two decimal places using
`ROUND_HALF_UP` before applying the cap.
```

The section numbering may be adjusted differently if that is cleaner, but the final document must clearly express the same order.

## Acceptance example that must remain correct

```text
order_total = Decimal("666.70")
is_premium = True
is_student = False

raw discount = 666.70 × 0.15
             = 100.005

rounded      = 100.01

capped       = 100.00
```

## Acceptance criteria

- The canonical change request explicitly states:

```text
rate selection
→ raw discount
→ ROUND_HALF_UP to 2 decimals
→ $100 cap
```

- The `$666.70` acceptance example remains unchanged and consistent with that order.
- No section elsewhere in the change request implies that the cap occurs before rounding.
- The requirement remains consistent with:
  - `sample_app/app/discounts.py`
  - `sample_app/tests/test_discounts.py`
  - `artifacts/assertshift-report.json`
  - `artifacts/assertshift-report.md`

---

# 3. Scope control

Do **not** change the following during this pass unless necessary to repair a direct reference to the two fixes above:

- `scripts/run_verification_matrix.py`
- mutant files
- baseline tests
- evolved test behavior
- verification logic
- public viewer
- repository structure
- `.gitignore`
- URLs
- deployment
- demo video
- Bob screenshots/session media

These fixes are documentation consistency fixes only.

Because neither fix changes executable code or test behavior, a full verification-matrix rerun is **not required** unless an executable file is changed accidentally.

---

# Final Definition of Done

- [ ] `bob_sessions/README.md` contains exactly 2 tightened existing tests.
- [ ] The two tightened tests show their old → evolved names clearly.
- [ ] `bob_sessions/README.md` contains exactly 11 newly added tests.
- [ ] No test is double-counted as both tightened and newly added.
- [ ] Final total remains 19 evolved tests.
- [ ] `inputs/change-request.md` explicitly defines the calculation order.
- [ ] The order is raw percentage → ROUND_HALF_UP → cap.
- [ ] `$666.70 → $100.005 → $100.01 → $100.00` remains the canonical rounding/cap example.
- [ ] No executable logic was changed.
- [ ] `.gitignore` is left untouched because it was already corrected manually.
- [ ] URLs, deployment, video, and screenshots remain out of scope.

---

# Suggested Bob Prompt

```text
Read AssertShift_FINAL_CONSISTENCY_FIXES.md and apply only the two documentation fixes described there.

1. Fix bob_sessions/README.md so the final accounting is exactly:
   - 2 existing tests tightened/renamed
   - 11 genuinely new tests added
   - 19 evolved tests total
   Do not double-count test_premium_discount_exact_rate as both a tightened replacement and a new test.

2. Make inputs/change-request.md explicitly define the calculation order as:
   raw percentage calculation → ROUND_HALF_UP to two decimals → $100 cap.

Keep the $666.70 example and its correct arithmetic.

Do not modify .gitignore; it has already been corrected manually.
Do not change executable logic, mutants, tests, verification behavior, URLs, deployment, video, or screenshots.

At the end, report exactly which documentation lines/sections changed and confirm that no executable files were modified.
```
