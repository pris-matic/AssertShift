# AssertShift — Final Report Reference Sync

> **Purpose:** Apply three wording/reference corrections so the report artifacts and public viewer match the finalized section numbering and calculation order in `inputs/change-request.md`.
>
> This is a **documentation/data synchronization pass only**. Do not change executable code, tests, mutants, verification logic, or the experiment.

---

# Files to update

Update only:

```text
artifacts/assertshift-report.json
artifacts/assertshift-report.md
docs/data/assertshift-report.json
```

Do **not** modify:

```text
sample_app/
verification_snapshots/
verification_mutants/
scripts/run_verification_matrix.py
verification/matrix_results.json
verification/manifest.json
inputs/change-request.md
README.md
bob_sessions/
docs/index.html
```

---

# 1. Fix F-005 section reference

## Current issue

F-005 refers to the `$100 cap` as:

```text
inputs/change-request.md §3.2
```

But the finalized change request now uses:

```text
§3.2 = Calculation order
§3.3 = Cap
§3.4 = Rounding
```

## Required change

For F-005, change the requirement reference to:

```text
inputs/change-request.md §3.3
```

This applies wherever F-005's requirement/reference text appears in:

```text
artifacts/assertshift-report.json
artifacts/assertshift-report.md
docs/data/assertshift-report.json
```

## Acceptance criteria

- F-005 cites `§3.3`.
- F-005 no longer cites `§3.2` as the cap section.
- No other F-005 wording is changed unnecessarily.

---

# 2. Fix F-006 section reference

## Current issue

F-006 currently cites:

```text
inputs/change-request.md §3.3
```

for the rounding-boundary behavior.

The finalized requirement is broader because the demonstrated behavior depends on:

```text
§3.2 Calculation order
§3.3 Cap
§3.4 Rounding
```

## Required change

For F-006, change the requirement reference to:

```text
inputs/change-request.md §§3.2–3.4
```

or an equivalent explicit wording such as:

```text
inputs/change-request.md §§3.2–3.4 (calculation order, cap, rounding)
```

Use the same wording consistently across all three report files.

## Acceptance criteria

- F-006 no longer cites only `§3.3`.
- F-006 clearly references the full calculation-order / rounding / cap behavior.
- The three report files use the same reference wording.

---

# 3. Clarify the behavior-change wording for the cap

## Current wording

The report currently includes wording equivalent to:

```text
New $100 cap on discount amount (after percentage calculation)
```

That wording is now less precise than the finalized specification.

## Required change

Replace it with:

```text
New $100 cap on the rounded discount amount
```

This should appear in the behavior-change summary wherever that exact report entry is used.

Recommended final behavior-change list:

```text
Premium-only discount rate changed from 10% to 15%
New Premium+Student combination discount: 20%
New $100 cap on the rounded discount amount
Round-half-up to two decimal places (unchanged, now made explicit)
```

## Acceptance criteria

- The report says the cap applies to the **rounded discount amount**.
- No report text implies cap-before-rounding.
- The wording matches the finalized canonical calculation order.

---

# 4. Keep the three report copies synchronized

After the wording fixes, make sure:

```text
artifacts/assertshift-report.json
docs/data/assertshift-report.json
```

remain identical.

If `docs/data/assertshift-report.json` is intended to be a direct copy of the artifact report, copy it from the final artifact JSON after editing.

Recommended verification:

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

Both hashes should match.

---

# 5. Do not rerun the verification matrix

These changes affect only:

```text
section references
report wording
public report data
```

They do not change:

```text
implementation
test behavior
mutants
verification harness
matrix outcomes
suite hashes
verification status
```

Therefore:

```text
python scripts/run_verification_matrix.py
```

is **not required** for this pass.

Do not change timestamps, hashes, counts, or matrix results merely because wording changed unless the project's report-generation logic specifically requires that.

---

# Final Definition of Done

- [ ] F-005 cites `inputs/change-request.md §3.3`.
- [ ] F-006 cites `inputs/change-request.md §§3.2–3.4`.
- [ ] Behavior-change wording says `$100 cap on the rounded discount amount`.
- [ ] `artifacts/assertshift-report.json` is updated.
- [ ] `artifacts/assertshift-report.md` is updated.
- [ ] `docs/data/assertshift-report.json` is updated.
- [ ] Artifact JSON and viewer JSON are identical.
- [ ] No executable files are modified.
- [ ] No tests or mutants are modified.
- [ ] No verification files are regenerated.
- [ ] No matrix rerun is performed.
- [ ] Existing observed results remain unchanged:
  - 8 baseline tests
  - 19 evolved tests
  - 0 BREAKING
  - 2 STALE
  - 4 MISSING
  - 2 tests updated
  - 11 tests added
  - 3/3 mutants escape baseline
  - 3/3 mutants caught by evolved
  - 0 infrastructure errors
  - VERIFIED

---

# Suggested Bob Prompt

```text
Read AssertShift_FINAL_REPORT_REFERENCE_SYNC.md and apply only the three report synchronization fixes.

Modify only:
- artifacts/assertshift-report.json
- artifacts/assertshift-report.md
- docs/data/assertshift-report.json

Make these exact corrections:
1. F-005 requirement reference:
   change inputs/change-request.md §3.2
   to inputs/change-request.md §3.3

2. F-006 requirement reference:
   change the single-section reference
   to inputs/change-request.md §§3.2–3.4
   because the behavior depends on calculation order, rounding, and cap.

3. Behavior-change wording:
   change "New $100 cap on discount amount (after percentage calculation)"
   to "New $100 cap on the rounded discount amount".

Keep the artifact JSON and docs/data JSON identical.

Do not modify executable code, tests, mutants, verification logic, matrix results, manifest, README, change request, Bob session evidence, or docs/index.html.

Do not rerun the verification matrix.

At the end, report:
- files changed;
- exact wording/reference corrections made;
- confirmation that artifact JSON and docs/data JSON are identical;
- confirmation that no executable or verification files were changed.
```
