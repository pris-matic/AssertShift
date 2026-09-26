# AssertShift — Final Cleanup Before Submission Assets

> **Purpose:** Apply the remaining technical and documentation cleanup to AssertShift **before** working on public URLs, deployment, video recording, or Bob screenshots/session media.
>
> This is a narrow cleanup pass. Do not redesign the project, add new features, expand the mutant set, or change the core experiment unless a cleanup item below requires it.

---

# 1. Fix the canonical change-request rounding example

## Current inconsistency

The evolved test suite and final report correctly use:

```text
$666.70 × 15% = $100.005
ROUND_HALF_UP → $100.01
cap → $100.00
```

However, the canonical requirements file still contains the older `$666.67` boundary example.

Because `inputs/change-request.md` is the source of truth, it must match the actual test and report.

## Required change

In:

```text
inputs/change-request.md
```

replace the acceptance-example row using:

```text
666.67
```

with:

```text
666.70
```

and describe it accurately:

```text
$666.70 × 15% = $100.005
ROUND_HALF_UP → $100.01
cap → $100.00
```

## Acceptance criteria

- `inputs/change-request.md` uses `$666.70`.
- `sample_app/tests/test_discounts.py` uses `$666.70`.
- `artifacts/assertshift-report.json` uses `$666.70`.
- `artifacts/assertshift-report.md` uses `$666.70`.
- No final documentation still presents `$666.67` as the example intended to round above `$100.00`.

---

# 2. Update Bob session notes to match the final implementation

## Current inconsistencies

`bob_sessions/README.md` still refers to the old test name:

```text
test_rounding_at_cap_boundary
```

The final evolved test is:

```text
test_rounding_then_cap
```

The Bob session notes also summarize only a subset of the newly created tests, while the final project reports:

```text
tests_updated = 2
tests_created = 11
```

## Required changes

Update:

```text
bob_sessions/README.md
```

so it reflects the final repository state.

At minimum:

- Rename the referenced test to `test_rounding_then_cap`.
- State that Bob tightened **2 existing tests**.
- State that the final evolved suite contains **11 newly added tests**.
- If listing tests individually, list all 11 accurately.
- If a concise summary is preferable, say:

```text
Bob tightened 2 stale assertions and added 11 tests covering:
- Premium + Student behavior
- Student-only preserved invariant
- cap behavior
- rounding/cap boundaries
- additional input-contract and boundary coverage
```

Do not claim screenshots or exported UI evidence exist yet. Those will be handled later.

## Acceptance criteria

- No obsolete test name remains.
- Counts agree with the final test files and reports.
- The notes remain truthful about what Bob actually did.

---

# 3. Clarify the human-readable evolved-suite arithmetic

## Current wording

The Markdown report currently contains wording equivalent to:

```text
19 tests (8 preserved + 2 tightened + 11 added)
```

That wording can be read as:

```text
8 + 2 + 11 = 21
```

even though the 2 tightened tests are part of the original 8.

## Required change

In:

```text
artifacts/assertshift-report.md
```

rewrite the suite summary to something unambiguous:

```text
19 total tests:
- all 8 baseline tests retained;
- 2 of those 8 were tightened;
- 11 new tests were added.
```

or:

```text
19 total: 8 baseline tests retained (including 2 tightened) + 11 new tests.
```

Check the root `README.md` and viewer text for similar wording.

## Acceptance criteria

- No document implies 21 total tests.
- All artifacts consistently report:
  - baseline tests: 8
  - updated existing tests: 2
  - newly created tests: 11
  - evolved total: 19

---

# 4. Harden defect-specific mutant validation

## Goal

A mutant must not count as caught merely because:

1. a test with a relevant name failed; or
2. one generic number appeared somewhere in pytest output.

A valid catch should be tied to the mutant's **specific named defect**.

## Required inspection

Review:

```text
scripts/run_verification_matrix.py
```

especially:

```text
EXPECTED_DEFECT_EVIDENCE
is_relevant_failure(...)
derive_verification_status(...)
```

## Required behavior

For each mutant, `caught_by_evolved = true` only when all of the following are true:

```text
1. evolved run result == BEHAVIORAL_FAIL
2. correct evolved implementation == PASS
3. at least one mapped relevant test failed
4. no infrastructure/setup error invalidates the run
5. captured failure evidence is consistent with the mutant's named defect
```

### Recommended evidence rules

#### `premium_still_10`

Require evidence that distinguishes the incorrect rate from the approved rate.

For example:

```text
actual contains 10.00
expected contains 15.00
```

from a mapped Premium-only rate test.

#### `missing_discount_cap`

Require evidence from a mapped cap-related test showing an uncapped value versus `$100.00`.

Examples:

```text
150.00 vs 100.00
```

or:

```text
100.01 vs 100.00
```

#### `student_without_premium`

Require evidence from a mapped Student-only invariant test showing:

```text
20.00 vs 0.00
```

## Important implementation note

Do **not** make the validator depend on an overly fragile exact full pytest string.

Prefer a small mutant-specific validation function or structured checks.

For example:

```python
def has_defect_evidence(run: dict, mutant_id: str) -> bool:
    output = (
        run.get("failure_excerpt", "")
        + run.get("stdout_excerpt", "")
        + run.get("stderr_excerpt", "")
    )

    if mutant_id == "premium_still_10":
        return "10.00" in output and "15.00" in output

    if mutant_id == "missing_discount_cap":
        return (
            ("150.00" in output and "100.00" in output)
            or ("100.01" in output and "100.00" in output)
        )

    if mutant_id == "student_without_premium":
        return "20.00" in output and "0.00" in output

    return False
```

This is only a suggested structure; use whichever implementation is clearest and least brittle.

## Acceptance criteria

- Relevant test name alone is insufficient.
- One generic fragment alone is insufficient.
- The captured evidence must match the mutant's named behavior.
- All three final mutants still qualify as caught after the rerun.

---

# 5. Treat pytest execution errors conservatively

## Goal

A test run containing a pytest/setup error should not be accepted as a clean behavioral-failure run.

## Required inspection

Review:

```text
classify_result(...)
parse_pytest_output(...)
```

## Required behavior

A conservative classification order should be:

```text
if any known infrastructure/collection/setup problem:
    INFRA_ERROR
elif pytest error count > 0:
    INFRA_ERROR
elif exit code == 0 and failures == 0:
    PASS
elif failures > 0 and errors == 0:
    BEHAVIORAL_FAIL
else:
    INFRA_ERROR
```

In other words:

```text
failed assertions + pytest errors
```

should **not** automatically become a valid `BEHAVIORAL_FAIL`.

The current successful run has zero errors, so this is harness hardening rather than a claim that the current evidence is invalid.

## Acceptance criteria

- Any required matrix run with `error > 0` becomes `INFRA_ERROR`.
- A mixed failed/error run cannot produce `VERIFIED`.
- Pure assertion failures continue to classify as `BEHAVIORAL_FAIL`.

---

# 6. Keep documentation synchronized after harness changes

If Sections 4 or 5 change:

```text
scripts/run_verification_matrix.py
```

rerun:

```bash
python scripts/run_verification_matrix.py
```

Then regenerate or refresh:

```text
verification/manifest.json
verification/matrix_results.json
artifacts/assertshift-report.json
artifacts/assertshift-report.md
docs/data/assertshift-report.json
```

Do not retain old:

- hashes;
- timestamps;
- counts;
- failure excerpts;
- suite IDs;
- verification status

after changing test or verification logic.

## Acceptance criteria

Final matrix must still show:

```text
correct / baseline = PASS
correct / evolved = PASS

premium_still_10 / evolved = relevant BEHAVIORAL_FAIL
missing_discount_cap / evolved = relevant BEHAVIORAL_FAIL
student_without_premium / evolved = relevant BEHAVIORAL_FAIL

infra errors = 0
verification status = VERIFIED
```

Record actual results rather than assuming these outcomes.

---

# 7. Verify report JSON and viewer data are identical

The public viewer loads:

```text
docs/data/assertshift-report.json
```

The source report is:

```text
artifacts/assertshift-report.json
```

After the final cleanup/rerun, confirm they are byte-for-byte identical or are generated/copied from the same source.

Recommended check:

```python
from pathlib import Path
import hashlib

paths = [
    Path("artifacts/assertshift-report.json"),
    Path("docs/data/assertshift-report.json"),
]

for path in paths:
    print(path, hashlib.sha256(path.read_bytes()).hexdigest())
```

## Acceptance criteria

- Both hashes match.
- The viewer is not displaying stale data from an earlier run.

---

# 8. Repository hygiene

Before the final commit, inspect `.gitignore`.

It should ignore at least:

```gitignore
.pytest_cache/
__pycache__/
*.pyc
```

Also remove already tracked cache files if necessary.

Possible commands:

```bash
git rm -r --cached .pytest_cache
git rm -r --cached "**/__pycache__"
```

Use commands appropriate for the current shell/platform and only if those paths are already tracked.

Do not delete legitimate source files.

## Acceptance criteria

The final public repository should not contain:

```text
.pytest_cache/
__pycache__/
*.pyc
```

unless there is a documented exceptional reason.

---

# 9. Check project-spec naming consistency

The root currently uses:

```text
AssertShift_PROJECT_SPEC.md
```

That is acceptable.

Do **not** rename it merely for cosmetic reasons if doing so would create broken references.

Instead:

1. search the repository for references to:
   - `AssertShift_PROJECT_SPEC.md`
   - `PROJECT_SPEC.md`
2. choose one actual filename;
3. make every README/session reference match it.

The final name itself is less important than consistency.

## Acceptance criteria

- No documentation links to a nonexistent spec filename.
- Bob session notes refer to the actual file Bob read.

---

# 10. Audit final claims for evidence

Search the final repository for claims such as:

```text
VERIFIED
2 STALE
4 MISSING
11 tests added
19 tests
3/3 mutants caught
3/3 mutants escaped baseline
0 infrastructure errors
```

Every numeric or success claim must be supported by the final matrix/report.

Also search for and remove/rewrite stale claims involving:

```text
test_rounding_at_cap_boundary
666.67 as the round-above-cap example
tests_created = 7
a BREAKING example being present in the main run
PDF analysis being demonstrated
manual time saved
```

unless that fact becomes true later and is backed by evidence.

## Acceptance criteria

The README, reports, Bob notes, and viewer all tell the same factual story.

---

# 11. Do not work on these yet

This cleanup pass intentionally excludes:

- public repository URL;
- GitHub Pages/public application URL;
- deployment verification;
- demo video;
- LabLab form submission;
- Bob IDE screenshots;
- Bob session screenshot selection;
- presentation/pitch deck;
- cover image;
- final video script;
- final submission copy tied to real URLs.

Leave URL placeholders as `TBD`.

Do not mark screenshot/video/deployment checklist items complete.

---

# 12. Cleanup Definition of Done

This cleanup pass is complete when:

- [ ] `inputs/change-request.md` uses `$666.70` for the rounding-above-cap acceptance example.
- [ ] No final artifact presents `$666.67` as that example.
- [ ] `bob_sessions/README.md` uses `test_rounding_then_cap`.
- [ ] Bob session notes accurately describe 2 tightened tests and 11 new tests.
- [ ] Human-readable report explains 19 total tests unambiguously.
- [ ] Mutant validation requires defect-specific behavioral evidence, not only relevant test names.
- [ ] Mutant evidence checks are not satisfied by only one generic fragment.
- [ ] Any pytest error count produces `INFRA_ERROR`.
- [ ] Full 8-cell matrix is rerun after harness/test/document changes that affect evidence.
- [ ] Correct implementation passes both suites.
- [ ] All three mutants are caught by relevant evolved-suite behavioral failures.
- [ ] Required matrix has zero infrastructure errors.
- [ ] Final verification status is derived from the new run.
- [ ] Manifest contains the latest suite hashes/status.
- [ ] JSON and Markdown reports reflect the latest run.
- [ ] `docs/data/assertshift-report.json` matches the final artifact JSON.
- [ ] `.pytest_cache/`, `__pycache__/`, and `*.pyc` are ignored/not committed.
- [ ] All references to the project-spec filename are consistent.
- [ ] No stale numerical or success claims remain.
- [ ] URLs, video, deployment, and Bob screenshots remain intentionally unfinished.

---

# Suggested Bob Prompt

```text
Read AssertShift_FINAL_CLEANUP.md and perform only this cleanup pass.

Do not redesign AssertShift, add new mutants, add new product features, deploy anything, create URLs, record video, or fabricate/capture screenshots.

First inspect the current files and state which cleanup items actually require changes.

Then apply the required fixes.

If you modify the evolved tests or verification harness, rerun the complete eight-cell matrix and regenerate every dependent artifact from the actual new results.

Pay special attention to:
- changing the canonical rounding-above-cap example from 666.67 to 666.70;
- updating bob_sessions/README.md to the final test name/counts;
- making the 19-test arithmetic unambiguous;
- requiring mutant-specific behavioral evidence rather than a relevant test name or one generic fragment;
- treating any pytest error count as INFRA_ERROR;
- keeping artifacts/assertshift-report.json and docs/data/assertshift-report.json synchronized;
- repository cache hygiene.

At the end, audit the repository against the Cleanup Definition of Done and report:
1. files changed,
2. commands run,
3. final matrix result,
4. final suite hashes,
5. any cleanup item intentionally left unresolved.

Do not work on URLs, deployment, video, screenshots, or submission media yet.
```
