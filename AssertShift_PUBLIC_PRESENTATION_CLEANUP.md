# AssertShift — Public Presentation Cleanup

> **Purpose:** Make the public-facing AssertShift presentation cleaner and more judge-friendly without changing the experiment, verification evidence, or core implementation.
>
> This pass is **presentation-only**.

---

# Files to change

Only update:

```text
docs/index.html
README.md
```

Do **not** modify:

```text
artifacts/assertshift-report.json
artifacts/assertshift-report.md
verification/manifest.json
verification/matrix_results.json
scripts/run_verification_matrix.py
sample_app/
verification_snapshots/
verification_mutants/
bob_sessions/README.md
```

The detailed evidence artifacts should remain technical and unchanged.

---

# 1. Clean up the summary area in `docs/index.html`

## Current issue

The public viewer currently shows the suite hashes prominently:

```text
Baseline suite: sha256:2291368d3102775a
Evolved suite: sha256:78fa1c73c28ace99
```

These hashes are useful for reproducibility, but they are too technical to emphasize in the main public summary.

## Required change

Replace the prominent hash line with a clearer summary:

```text
Baseline: 8 tests
Evolved: 19 tests
```

or visually equivalent wording.

Keep the hashes available, but move them into a collapsed/expandable section titled:

```text
Reproducibility details
```

Inside that section, show:

```text
Baseline suite hash: sha256:2291368d3102775a
Evolved suite hash: sha256:78fa1c73c28ace99
```

If the values are already loaded from JSON, continue loading them from JSON rather than hardcoding them.

## Acceptance criteria

- The main summary emphasizes test counts, not hashes.
- Hashes remain accessible for reproducibility.
- No verification data is removed.
- Hashes are still loaded from the report data where possible.

---

# 2. Simplify the public limitations section in `docs/index.html`

## Goal

Keep the project honest, but avoid making the public page feel like an internal audit document.

The public viewer should show only the limitations that materially affect interpretation of the result.

## Replace the current public limitations with these three scope notes

### Scope & limitations

1. **Controlled defect scope**

```text
Verification covers three controlled behavioral defects and does not claim exhaustive correctness.
```

2. **Premium+Student mutant scope**

```text
Premium+Student behavior is covered by executable tests, but the current matrix does not include a dedicated incorrect-rate mutant for that case.
```

3. **Evaluation focus**

```text
The evaluation measures test-strength improvement rather than developer-time savings.
```

## Remove from the public website

Do not show these as public limitations:

```text
PDF document reading was not demonstrated.
```

```text
Bob session screenshots were not committed.
```

That screenshot statement is now outdated.

Also remove the long public explanation of:

```text
BREAKING = 0
```

The result itself may remain visible in the findings/summary, but it does not need to be presented as a limitation.

## Important

Do not delete those detailed notes from the evidence artifacts.

This cleanup affects only the public website presentation.

---

# 3. Update the root `README.md`

## A. Keep the technical evidence

The README may continue to show:

- suite hashes;
- verification status;
- matrix results;
- exact counts;
- reproduction instructions.

Do not remove reproducibility information from the README.

## B. Update the limitations section

Replace the current long/public-facing limitations wording with a cleaner version such as:

```markdown
## Scope and limitations

- Verification covers three controlled behavioral defects and demonstrates improved detection for those defects; it does not claim exhaustive correctness.
- Premium+Student behavior is covered by executable tests, but the current matrix does not include a dedicated mutant for an incorrect Premium+Student rate.
- The evaluation measures test-strength improvement rather than developer-time savings.
```

## C. Fix the outdated screenshot statement

Remove or replace any line equivalent to:

```text
live IDE screenshots were not committed
```

because IBM Bob audit screenshots are now committed.

Replace it with:

```text
IBM Bob audit evidence and IDE screenshots are available in `bob_sessions/`.
```

or equivalent wording.

## D. Keep BREAKING = 0 factual, not defensive

It is fine for the README to report:

```text
BREAKING findings: 0
```

Do not present this as a project weakness.

If a short explanation is needed:

```text
BREAKING = 0 because the baseline suite still passes on the correct post-change implementation; the demonstrated problem is stale and missing test intent rather than failing legacy tests.
```

Keep this explanation concise.

---

# 4. Do not change the evidence model

This presentation cleanup must **not** change:

```text
8 baseline tests
19 evolved tests
2 STALE
4 MISSING
0 BREAKING
2 updated tests
11 added tests
3 / 3 mutants escape baseline
3 / 3 mutants caught by evolved
0 infrastructure errors
VERIFIED
```

Do not rerun the verification matrix unless an executable file is modified accidentally.

---

# 5. Final public presentation target

The website should communicate this story quickly:

```text
Your code changed. Did your tests?

Baseline: 8 tests
Evolved: 19 tests

0 BREAKING
2 STALE
4 MISSING

3 / 3 controlled mutants escaped baseline
3 / 3 were caught by the evolved suite

VERIFIED
```

Technical hashes and lower-level details should remain available, but secondary.

---

# Definition of Done

- [ ] `docs/index.html` emphasizes `8 baseline` and `19 evolved` rather than suite hashes.
- [ ] Suite hashes remain available under `Reproducibility details`.
- [ ] Public limitations are reduced to the 3 concise scope notes.
- [ ] Outdated screenshot-not-committed wording is removed.
- [ ] PDF-reading note is removed from the public viewer.
- [ ] Long BREAKING=0 defensive wording is removed from the public viewer.
- [ ] Root `README.md` uses the same 3 scope/limitation points.
- [ ] Root README states that Bob screenshots are available in `bob_sessions/`.
- [ ] Raw evidence artifacts remain unchanged.
- [ ] Verification files remain unchanged.
- [ ] No executable code is modified.
- [ ] No matrix rerun is required unless executable files are accidentally changed.

---

# Suggested Bob Prompt

```text
Read AssertShift_PUBLIC_PRESENTATION_CLEANUP.md and apply only this presentation cleanup.

Modify only:
- docs/index.html
- README.md

For docs/index.html:
1. Replace the prominent suite-hash line with a clearer public summary:
   Baseline: 8 tests
   Evolved: 19 tests
2. Keep the suite hashes inside a collapsed "Reproducibility details" section.
3. Reduce the public limitations to these three points:
   - verification covers three controlled behavioral defects and does not claim exhaustive correctness;
   - Premium+Student behavior is covered by executable tests, but there is no dedicated incorrect-rate mutant for that case;
   - evaluation measures test-strength improvement rather than developer-time savings.
4. Remove the public PDF-reading note.
5. Remove the outdated statement that Bob screenshots were not committed.
6. Remove the long BREAKING=0 explanation from the public limitations area.

For README.md:
1. Keep technical reproducibility information.
2. Replace the limitations section with the same concise three-point scope framing.
3. Replace any "screenshots were not committed" wording with:
   IBM Bob audit evidence and IDE screenshots are available in `bob_sessions/`.
4. Keep BREAKING = 0 as a factual observed result, not a limitation.

Do not modify reports, verification JSON, scripts, tests, mutants, implementation, or Bob session evidence.

Do not rerun the matrix unless an executable file is accidentally changed.

At the end, report:
- files changed;
- presentation changes made;
- confirmation that no evidence or executable files were modified.
```
