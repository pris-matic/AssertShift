# AssertShift — Required Corrections Before Submission

> **Purpose:** This file contains only the corrections required after auditing the current AssertShift implementation against `AssertShift_PROJECT_SPEC_v4.md`.
>
> Treat this as a focused patch brief. Do **not** redesign the project or expand scope. Fix the items below, rerun the required verification, and update only the artifacts affected by those fixes.

---

# 1. Fix the rounding/cap boundary test

## Problem

The current evolved test suite includes a test/comment equivalent to:

```text
$666.67 × 15% = $100.0005 → rounds to $100.01 → capped at $100.00
```

That arithmetic is incorrect.

With `ROUND_HALF_UP` to two decimal places:

```text
100.0005 → 100.00
```

Therefore the current example does **not** demonstrate a value rounding above the cap before the cap is applied.

## Required change

Replace the current boundary input with one that really produces a rounded value greater than `$100.00`.

Recommended case:

```text
$666.70 × 15% = $100.005
ROUND_HALF_UP → $100.01
cap → $100.00
```

Recommended test:

```python
def test_rounding_then_cap():
    result = calculate_discount(
        Decimal("666.70"),
        is_premium=True,
        is_student=False,
    )
    assert result == Decimal("100.00")
```

## Acceptance criteria

- The comment/docstring uses mathematically correct values.
- The test passes on the correct implementation.
- The test fails on the `missing_discount_cap` mutant for the expected cap-related reason.
- The test is not counted as evidence for a different mutant.

---

# 2. Correct finding F-003 in the generated report

## Problem

The current report's `F-003` finding is about the missing:

```text
Premium + Student → 20%
```

case.

However, its evidence currently refers to the `student_without_premium` mutant and implies that `test_premium_and_student_combination` catches that mutant.

That is incorrect.

The `student_without_premium` mutant's named defect is:

```text
Non-Premium Student incorrectly receives 20%
```

Its Premium + Student behavior remains correct.

## Required change

Update F-003 so it states only evidence actually supported by the implementation and matrix.

Recommended wording:

```text
Classification: MISSING

Requirement:
Premium + Student receives 20%.

Gap:
No baseline test covers is_premium=True, is_student=True.

Evidence:
The baseline suite contains no targeted Premium + Student assertion.
The evolved suite adds test_premium_and_student_combination, which passes against the correct post-change implementation.

Limitation:
The current three-mutant verification matrix does not include a dedicated mutant for an incorrect Premium + Student rate, so this finding is demonstrated through missing baseline coverage plus the new executable acceptance test, not through a dedicated mutant kill.
```

## Acceptance criteria

- F-003 no longer claims the `student_without_premium` mutant validates the Premium + Student rule.
- The report clearly distinguishes:
  - missing baseline coverage;
  - the evolved acceptance test;
  - the lack of a dedicated mutant for this specific rule.
- Do **not** add another mutant unless there is substantial time remaining. The current three-mutant scope is sufficient.

---

# 3. Recalculate `tests_created`

## Problem

The current report says:

```json
"tests_updated": 2,
"tests_created": 7
```

But the recorded suite sizes are:

```text
Baseline: 8 tests
Evolved:  19 tests
```

The two stale Premium tests were tightened/updated, while the evolved suite contains additional tests beyond the baseline.

The report count must reconcile with the actual test diff.

## Required change

Determine the count from the actual baseline/evolved test files rather than from memory or the file header.

If:

- 2 baseline tests were modified in place; and
- all 8 original tests remain represented; and
- the evolved suite has 19 tests;

then the expected count is:

```json
"tests_updated": 2,
"tests_created": 11
```

However, verify this from the actual diff before writing the value.

## Acceptance criteria

- `tests_updated` matches actual changed existing test cases.
- `tests_created` matches actual newly added test cases.
- The JSON report, Markdown report, README, and viewer show the same numbers.
- No count is manually copied into one artifact without checking the actual files.

---

# 4. Strengthen relevant-mutant failure validation

## Problem

The verification harness currently checks whether a failing test's **name** belongs to the configured relevant-test list for a mutant.

That is useful, but slightly weaker than the project specification.

A mutant must count as `CAUGHT` only if it fails because of its **named behavioral defect**.

For example:

```text
premium_still_10
```

should be considered caught because an exact Premium-rate assertion shows:

```text
actual:   10.00
expected: 15.00
```

A relevant test failing because of an unrelated exception must not count.

## Required change

Keep the existing `RELEVANT_TESTS` mapping, but add behavioral-evidence validation.

At minimum, each mutant must have:

```text
1. evolved result == BEHAVIORAL_FAIL
2. at least one relevant test name failed
3. no infrastructure error
4. correct implementation passes evolved suite
5. captured assertion/failure excerpt is consistent with the mutant's named defect
```

### Recommended implementation approach

Create expected evidence metadata for each mutant.

Example:

```python
EXPECTED_DEFECT_EVIDENCE = {
    "premium_still_10": {
        "tests": [
            "test_premium_discount_exact_rate",
            "test_premium_discount_200",
        ],
        "expected_fragments": [
            "10.00",
            "15.00",
        ],
    },
    "missing_discount_cap": {
        "tests": [
            "test_cap_premium_only",
            "test_cap_premium_and_student",
            "test_rounding_then_cap",
        ],
        "expected_fragments": [
            "150.00",
            "100.00",
        ],
    },
    "student_without_premium": {
        "tests": [
            "test_student_only_gets_no_discount",
            "test_student_only_large_order_gets_no_discount",
        ],
        "expected_fragments": [
            "20.00",
            "0.00",
        ],
    },
}
```

The exact implementation may differ, but the harness must not rely only on test names.

## Important limitation

Do not make assertion-string parsing so brittle that harmless pytest formatting changes make the matrix invalid.

A practical solution is acceptable:

- relevant test name;
- `BEHAVIORAL_FAIL`;
- no infrastructure errors;
- expected values or defect-specific text visible in captured failure output.

## Acceptance criteria

For every mutant marked `caught_by_evolved = true`:

- the correct evolved suite passes;
- at least one mapped test fails;
- the failure evidence corresponds to the mutant's named defect;
- the result is not an import/setup/syntax/fixture failure.

---

# 5. Fix the manifest encoding issue

## Problem

The current manifest description contains mojibake:

```text
Verification manifest â€” records suite identities and last matrix run.
```

## Required change

Replace it with UTF-8-safe text such as:

```text
Verification manifest - records suite identities and last matrix run.
```

or:

```text
Verification manifest — records suite identities and last matrix run.
```

only if the repository/file encoding is verified as UTF-8.

## Acceptance criteria

- `verification/manifest.json` contains no mojibake.
- JSON remains valid UTF-8.

---

# 6. Fix the inaccurate limitation about a BREAKING example

## Problem

The current report limitation states that a legitimately obsolete/BREAKING example is documented in the baseline-suite header.

The audited baseline test file documents:

- STALE tests;
- MISSING coverage;
- preserved unaffected tests;

but does not actually contain a separate BREAKING example.

## Required change

Remove or rewrite that limitation.

Recommended replacement:

```text
The main controlled scenario has BREAKING = 0 because the baseline suite passes on the correct post-change implementation. The project supports the BREAKING classification conceptually, but no separate BREAKING example was included in the recorded main run.
```

## Acceptance criteria

- The final report makes no claim that a BREAKING example exists unless one actually exists in the repository/session evidence.
- Keep `BREAKING = 0` for the main controlled demo unless a genuine breaking test is added separately.

---

# 7. Rerun the verification matrix after all code/test changes

Because Section 1 changes an evolved test, the existing suite hash and recorded matrix output are no longer authoritative.

After completing all fixes:

```bash
python scripts/run_verification_matrix.py
```

Run the full eight-cell matrix again.

## Required eight runs

```text
Baseline × correct
Baseline × premium_still_10
Baseline × missing_discount_cap
Baseline × student_without_premium

Evolved × correct
Evolved × premium_still_10
Evolved × missing_discount_cap
Evolved × student_without_premium
```

## Required result checks

The final status can be `VERIFIED` only if:

```text
correct / baseline       = PASS
correct / evolved        = PASS

premium_still_10 / evolved
  = relevant behavioral failure

missing_discount_cap / evolved
  = relevant behavioral failure

student_without_premium / evolved
  = relevant behavioral failure

required matrix infrastructure errors
  = 0
```

The three mutants escaping the baseline is desirable for the demo but must be recorded from actual output, not assumed.

---

# 8. Regenerate dependent artifacts from the new run

After the matrix rerun, update/regenerate:

```text
verification/manifest.json
verification/matrix_results.json
artifacts/assertshift-report.json
artifacts/assertshift-report.md
docs/data/assertshift-report.json
```

If the public viewer derives data from the copied report, verify:

```text
artifacts/assertshift-report.json
==
docs/data/assertshift-report.json
```

before deployment.

Do not manually preserve old hashes, run times, counts, or `VERIFIED` values.

---

# 9. Validate the final report against actual evidence

Before considering this correction task complete, confirm:

```text
Breaking count  = actual Bob findings
Stale count     = actual Bob findings
Missing count   = actual Bob findings

Tests examined  = actual baseline count
Tests updated   = actual diff
Tests created   = actual diff

Baseline suite hash = newly recorded baseline hash
Evolved suite hash  = newly recorded evolved hash

Mutant evidence = actual rerun
Verification    = derived from rerun
```

Also verify that:

- F-001 and F-002 correctly describe the two stale Premium assertions.
- F-003 no longer makes a false mutant claim.
- F-004 maps to Student-only invariant evidence.
- F-005 maps to cap-mutant evidence.
- F-006 uses mathematically correct rounding/cap language.

---

# 10. Do not change these parts

The following parts already support the intended AssertShift demo and should not be redesigned during this correction pass:

- the correct post-change `calculate_discount(...)` implementation;
- the immutable baseline suite concept;
- the three-mutant scope;
- the eight-run verification matrix;
- the `BREAKING / STALE / MISSING / UNRESOLVED` classification model;
- the green-baseline demo;
- the distinction between test-strength evidence and developer-time claims;
- the static report viewer architecture;
- the rule that Bob performs semantic analysis while Python executes deterministic verification.

Keep this correction pass narrow.

---

# 11. Final correction checklist

- [ ] Fix rounding/cap boundary arithmetic and test input.
- [ ] Confirm new boundary test passes on correct implementation.
- [ ] Confirm new boundary test fails appropriately on no-cap mutant.
- [ ] Correct F-003 evidence.
- [ ] Recalculate tests-created/tests-updated counts from actual diff.
- [ ] Strengthen mutant catch validation beyond test-name-only matching.
- [ ] Fix manifest text encoding.
- [ ] Remove/rewrite unsupported BREAKING-example limitation.
- [ ] Rerun all eight matrix combinations.
- [ ] Confirm correct implementation passes both suites.
- [ ] Confirm each evolved mutant failure is relevant to its named defect.
- [ ] Confirm zero required infrastructure errors.
- [ ] Regenerate manifest and matrix results.
- [ ] Regenerate JSON and Markdown reports.
- [ ] Refresh the viewer's report copy.
- [ ] Confirm all hashes/counts/results reflect the latest run.
- [ ] Do not fabricate or preserve superseded evidence.

---

# Suggested Bob Prompt

```text
Read REQUIRED_CORRECTIONS.md and apply only the corrections described there.

Do not redesign AssertShift or expand scope.

First inspect the current implementation and explain how you will address each correction. Then make the changes.

After changing any evolved test or verification logic, rerun the full eight-cell verification matrix and regenerate every dependent artifact from the new results.

Pay particular attention to:
1. the corrected ROUND_HALF_UP/cap boundary arithmetic;
2. F-003's incorrect mutant evidence;
3. reconciling tests_created/tests_updated with the real diff;
4. ensuring a mutant counts as caught only when a relevant test fails for that mutant's named behavioral defect;
5. preserving correct-implementation controls and separating infrastructure failures from behavioral failures.

Do not hardcode successful output or preserve stale hashes/results from the previous run.
```
