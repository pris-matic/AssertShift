# AssertShift

> **Your code changed. Did your tests?**

AssertShift uses IBM Bob 2.0 to find stale and missing tests after software behavior changes, then verifies the improved suite with reproducible executable evidence — not just a green badge.

---

## What this demonstrates

A test suite that passes is not necessarily a test suite that *constrains* the intended behavior. AssertShift shows:

1. A **baseline suite** that is green on the correct post-change code but contains weak (stale) assertions and is missing coverage for new acceptance cases.
2. **Bob's analysis** — Plan mode reads the change request, implementation, and tests; identifies STALE and MISSING findings with concrete counterexamples.
3. **Bob's test edits** — Agent mode tightens stale assertions and adds missing tests.
4. A **verification matrix** — 8 isolated pytest runs (2 suites × 4 candidates) proving the evolved suite catches three single-defect mutants that escape the baseline suite.

---

## Repository layout

```
assertshift/
├── inputs/change-request.md               # Canonical approved change request
├── sample_app/
│   ├── app/discounts.py                   # Correct post-change implementation
│   └── tests/test_discounts.py            # Bob-evolved test suite (19 tests)
├── verification_snapshots/
│   └── baseline_tests/test_discounts.py   # Immutable baseline (8 tests, green but weak)
├── verification_mutants/
│   ├── premium_still_10/discounts.py      # Mutant: 10% instead of 15%
│   ├── missing_discount_cap/discounts.py  # Mutant: no $100 cap
│   └── student_without_premium/discounts.py # Mutant: student-only gets 20%
├── verification/
│   ├── manifest.json                      # Suite hashes + last run status
│   └── matrix_results.json                # Full 8-run output (generated)
├── scripts/
│   └── run_verification_matrix.py         # Runs all 8 matrix combinations
├── artifacts/
│   ├── assertshift-report.json            # Structured report (real results)
│   └── assertshift-report.md              # Human-readable report
├── docs/
│   ├── index.html                         # Static report viewer
│   └── data/assertshift-report.json       # Copy of artifacts report (for viewer)
├── bob_sessions/README.md                 # Bob session evidence and workflow notes
├── submission/README.md                   # Submission checklist and placeholders
└── AssertShift_PROJECT_SPEC.md            # Project specification (v4)
```

---

## Prerequisites

- Python 3.9+ (tested on 3.13)
- `pytest` (`pip install pytest`)

No other dependencies.

---

## How to reproduce

### 1. Confirm the green-suite run (baseline passes on correct code)

```bash
pytest verification_snapshots/baseline_tests/test_discounts.py -v
```

Expected: **8 passed**. Note the two stale `> 0` assertions in `TestPremiumDiscount`.

### 2. Confirm the evolved suite passes on correct code

```bash
pytest sample_app/tests/test_discounts.py -v
```

Expected: **19 passed**.

### 3. Run the verification matrix (all 8 combinations)

```bash
python scripts/run_verification_matrix.py
```

Expected output:
```
Running [baseline × correct                 ] ... PASS          (8P / 0F / 0E)
Running [baseline × premium_still_10        ] ... PASS          (8P / 0F / 0E)  ← escapes
Running [baseline × missing_discount_cap    ] ... PASS          (8P / 0F / 0E)  ← escapes
Running [baseline × student_without_premium ] ... PASS          (8P / 0F / 0E)  ← escapes
Running [evolved  × correct                 ] ... PASS          (19P / 0F / 0E)
Running [evolved  × premium_still_10        ] ... BEHAVIORAL_FAIL (15P / 4F / 0E)  ← caught
Running [evolved  × missing_discount_cap    ] ... BEHAVIORAL_FAIL (16P / 3F / 0E)  ← caught
Running [evolved  × student_without_premium ] ... BEHAVIORAL_FAIL (17P / 2F / 0E)  ← caught

Verification status: VERIFIED
```

Results are written to `verification/matrix_results.json` and `verification/manifest.json`.

### 4. Inspect the reports

- **JSON:** `artifacts/assertshift-report.json`
- **Markdown:** `artifacts/assertshift-report.md`

### 5. Open the report viewer

Open `docs/index.html` in a browser (or serve it via GitHub Pages).  
The viewer loads `docs/data/assertshift-report.json` automatically. You can also load any compatible JSON report via the file input.

> **Note:** The viewer requires `docs/data/assertshift-report.json` to be accessible at a relative path. For local viewing, serve the `docs/` directory with a local HTTP server:
> ```bash
> python -m http.server 8080 --directory docs
> # then open http://localhost:8080
> ```

---

## Bob's role vs the viewer's role

| Component | Role |
|---|---|
| IBM Bob (Plan mode) | Reads change request, code, and tests; identifies STALE/MISSING/BREAKING findings |
| IBM Bob (Agent mode) | Tightens stale assertions; adds missing test cases |
| `scripts/run_verification_matrix.py` | Executes 8 isolated pytest runs; records pass/fail/error counts |
| `docs/index.html` | **Displays** the already-generated report; does not run Bob or analyze code |

The semantic findings (STALE/MISSING classifications) are produced by Bob's analysis, not hardcoded in any script or in the viewer.

---

## Actual measurements (observed results)

| Metric | Value |
|---|---|
| Baseline tests | 8 |
| Stale findings (Bob) | 2 |
| Missing findings (Bob) | 4 |
| Breaking findings (Bob) | 0 |
| Tests updated | 2 |
| Tests added | 11 |
| Evolved tests | 19 |
| Mutants caught by evolved suite | 3 / 3 |
| Mutants escaped by baseline suite | 3 / 3 |
| Infrastructure errors | 0 |
| Verification status | **VERIFIED** |

---

## Scope and limitations

- Verification covers three controlled behavioral defects and demonstrates improved detection for those defects; it does not claim exhaustive correctness.
- Premium+Student behavior is covered by executable tests, but the current matrix does not include a dedicated mutant for an incorrect Premium+Student rate.
- The evaluation measures test-strength improvement rather than developer-time savings.

`BREAKING = 0` because the baseline suite still passes on the correct post-change implementation; the demonstrated problem is stale and missing test intent rather than failing legacy tests.

IBM Bob audit evidence and IDE screenshots are available in `bob_sessions/`.

---

## Submission placeholders

```
PUBLIC_REPOSITORY_URL=TBD
APPLICATION_URL=TBD
VIDEO_URL=TBD
BOB_SESSION_EVIDENCE=bob_sessions/README.md
```

See `submission/README.md` for the full checklist.
