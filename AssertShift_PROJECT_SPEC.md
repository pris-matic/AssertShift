# AssertShift — IBM Bob 2.0 Hackathon Build Specification (v4)

> **Tagline:** Your code changed. Did your tests?
>
> **Core idea:** After a behavior change, IBM Bob examines the change request, implementation, and existing tests; identifies failing, stale, and missing tests; helps evolve the suite; and produces executable evidence that the new tests protect the intended behavior.

## 0. Purpose and priority

This is the source of truth for a **small, reproducible hackathon prototype**, not a specification for a universal testing product. The centerpiece is a real Bob-assisted test-evolution session and the test output it produces. A static website only displays its resulting evidence; it does not run Bob or analyze arbitrary repositories.

**Build priority:** working sample and truthful baseline → Bob analysis → reviewed test edits → executable verification matrix → saved Bob/session evidence → JSON/Markdown report → interactive public viewer → presentation polish. If time runs short, report unfinished items rather than representing them as complete.

**What changed since v3:** clarified the three classification labels and the green-suite demo; separated a manual-time benchmark from the baseline test suite; made PDF and Bob configuration optional when not supported; required per-mutant relevant failures and correct-implementation controls; removed prefilled success values and the mandatory empty repository skeleton; and made the public report viewer minimally interactive.

## 1. Project and problem

**Project title:** AssertShift  
**Short description:** AssertShift uses IBM Bob 2.0 to find and address stale or missing tests after software behavior changes, then checks the improved tests against correct and deliberately incorrect implementations.

A passing test suite does not guarantee that its assertions still represent the intended behavior. A test such as `assert discount > 0` remains green for many incorrect positive discounts. A new branch may have no relevant test at all. A legitimately obsolete exact-value test may fail and require updating **only after the new requirement and implementation are checked**.

The product's differentiator is **test-suite co-evolution**, particularly tests that remain green but no longer constrain the changed behavior. Bob is the analysis and editing partner; `pytest` supplies executable evidence. Do not claim automatic proof of correctness or generalized coverage for arbitrary codebases.

### Finding labels

- `BREAKING`: An existing test fails because it asserts the old behavior. Confirm the implementation actually matches the approved change request before changing the test. An implementation defect is **not** automatically a legitimately breaking test.
- `STALE`: An existing test passes but its assertion is insufficient to check the documented new behavior. Give a concrete counterexample that would still pass.
- `MISSING`: A documented acceptance case has no relevant test. This includes a **preserved invariant**, such as non-Premium Students continuing to receive no premium discount; it does not imply the behavior itself is new.
- `UNRESOLVED`: Use this in notes or the report when there is insufficient evidence to assign a trustworthy label. Do not guess a result to make the dashboard look complete.

A label is an assessment by Bob supported by source locations and test evidence, not a claim that every possible bug has been found.

## 2. Scope and scenario

Build **one** Python/pytest discount service. It uses the same public function signature before and after the change:

```python
from decimal import Decimal

def calculate_discount(
    order_total: Decimal,
    *,
    is_premium: bool,
    is_student: bool,
) -> Decimal:
    ...
```

The function returns the **discount amount**, not the final order price. Supply `order_total` as a finite, nonnegative US-dollar `Decimal` with at most two fractional digits. Negative totals raise `ValueError`; zero returns `Decimal("0.00")`. Avoid floats in application code and tests. Output has two fractional digits using `ROUND_HALF_UP`. This input contract is intentionally narrow; unsupported input types or higher-precision money are out of scope.

### Original behavior

- Premium: 10% of the order total, with no $100 cap.
- Non-Premium: 0%, whether Student or not.
- Student status has no effect.
- The function already follows the input, zero, negative-total, and return-value contract above.

### Approved post-change behavior

1. Premium only: 15%.
2. Premium **and** Student: 20%, instead of 15%.
3. Non-Premium, including Student-only: 0%; this is a preserved invariant.
4. After calculating the percentage discount, cap the **discount amount** at `Decimal("100.00")` and round to two decimals using `ROUND_HALF_UP`.
5. Preserve the input, zero, and negative-total behavior.

The canonical source is `inputs/change-request.md`. It must explicitly state the invariant and calculations. If a PDF is used to demonstrate document reading, generate it from that Markdown source; never edit the copies independently. If time or tooling makes PDF conversion unreliable, show Bob reading the Markdown document and remove any PDF-specific claim from the submission.

| Input | Correct discount | Purpose |
| --- | ---: | --- |
| $100.00, Premium only | $15.00 | Distinguishes 15% from 10%. |
| $100.00, Premium + Student | $20.00 | Checks combination and precedence. |
| $100.00, Student only | $0.00 | Checks preserved invariant. |
| $1,000.00, Premium only | $100.00 | Checks the cap: raw discount is $150. |
| $1,000.00, Premium + Student | $100.00 | Checks the cap for the 20% branch. |
| $0.00, any valid flags | $0.00 | Checks zero input. |
| Negative total | `ValueError` | Checks invalid input. |

Include one small rounding case and a case just below/at the cap if feasible. Tests should assert `Decimal` amounts, not formatted strings. The examples describe intended behavior; only executed tests count as implementation evidence.

## 3. The green-suite demo

Create a pre-evolution test suite that **passes on the correct post-change implementation** but contains at least one weak Premium assertion and lacks targeted tests for Premium + Student, Student-only, and the cap. Preserve a few relevant unaffected tests. Example stale assertion:

```python
assert calculate_discount(
    Decimal("100.00"), is_premium=True, is_student=False
) > Decimal("0.00")
```

This passes for both the required $15.00 and an incorrect $10.00. The Bob-evolved version should assert `Decimal("15.00")` for the same inputs.

**Do not mix incompatible test states.** The primary green-suite demo uses `BREAKING = 0` unless a real baseline test fails. A separate legitimately obsolete test can illustrate `BREAKING` if there is time, but never say “all existing tests pass” in the same run that contains a failing test. Bob may describe all three categories while **only claiming to have detected the categories actually present**.

The production implementation must already reflect the post-change request before the baseline-vs-evolved test comparison. Bob's main remediation changes **tests**; do not quietly make Bob fix production code and then present that as the same test-evolution experiment. If Bob discovers a genuine implementation defect, document the distinct fix and rerun the controlled comparison.

## 4. Bob-assisted workflow

### A. Plan without edits

Ask Bob in Plan mode to read this spec, the canonical change request, the original-to-new production-code diff, and the baseline tests. Capture the plan and identify what can be independently inspected. Do not edit the baseline tests yet.

### B. Focused investigation

Where supported by the installed Bob version, use focused subagents or independent tasks for:

1. **Change Analyst:** Identify behavior deltas and relevant implementation locations.
2. **Test Mapper:** Map existing assertions to behavior; identify weak assertions and uncovered cases.
3. **Intent Analyst:** Extract the approved rules, including unchanged invariants, from the change request.

Run independent tasks in parallel only where the current Bob tooling actually permits it. If a feature is unavailable, document what was used rather than claiming parallel execution.

### C. Live classification

Bob consolidates the findings in the IDE/session. Every `BREAKING`, `STALE`, or `MISSING` finding must have an ID, source requirement, file/test reference or explicit absence of one, explanation, proposed action, and confidence/limitation. Keep a copy of the genuine Bob output. **Do not hardcode Bob's semantic classification in Python, JavaScript, canned report fixtures, or the viewer.** A deterministic script may validate a report's shape or execute tests, but it must not invent the findings.

### D. Reviewed remediation

Review and approve Bob's test-edit plan. In Agent mode, Bob updates stale assertions and adds missing cases. Preserve unaffected tests. Update a genuinely obsolete test only if the approved requirement and correct implementation justify doing so. Record changed files and the actual Bob session evidence.

### E. Verification and reporting

A separate Verification Subagent reviews the tests and the executed verification matrix, challenges exact values and boundaries, and explains survivors or invalid runs. Its opinion alone is **not** the verification result: the commands and behavioral failures are the evidence. Allow at most **one** verify → improve tests → verify-again cycle in the recorded demo; if unresolved, report the limitation.

Generate structured JSON and readable Markdown reports from the same observed results. Never convert an infrastructure failure into a “caught” mutant, and never claim a discovered gap or improvement without evidence.

## 5. Reproducible verification matrix

### Immutable test states

- Save the pre-evolution suite as `verification_snapshots/baseline_tests/` **before Bob edits it**, and commit it or record its content hash. This is the green but incomplete suite on the correct post-change implementation.
- Keep Bob's approved evolved suite in `sample_app/tests/` and commit it after changes. Record the baseline snapshot hash/commit and the evolved suite commit in `verification/manifest.json`.
- The words **baseline suite** here mean *old tests against the correct new code*. They do **not** mean a manual-review time benchmark or a run against the old production implementation.
- Do not edit the snapshot to improve the comparison. If you must regenerate it, disclose and update its recorded identity before rerunning all comparisons.

### Candidates

Use the correct post-change implementation plus three deterministic, interface-compatible alternatives:

1. `premium_still_10`: Premium-only receives 10% rather than 15%; all unrelated post-change rules stay correct.
2. `missing_discount_cap`: Correct rates, but no $100 cap; unrelated behavior stays correct.
3. `student_without_premium`: Student-only incorrectly gets 20%; unrelated behavior stays correct.

Each mutant should contain **only its named behavioral defect**. Test it on a representative input before running the matrix; if it is equivalent to the correct implementation on that input or introduces a second defect, fix the fixture and rerun the complete matrix. Label these as controlled known-bad fixtures, not bugs Bob discovered in the real code.

### Harness

`scripts/run_verification_matrix.py` executes all **eight** suite/candidate combinations: two test states × (one correct implementation + three mutants). Each run uses an isolated temporary directory or equivalent clean environment, puts the selected candidate at the *same import path*, and runs the selected tests without modifying the working repository. Do not let Python module caches, fixture names, environment variables, or unrelated tests contaminate another run.

For each run, record candidate and suite IDs; their hashes/commits; exact command; process exit code; pass/fail/error counts; failing test and assertion excerpt when applicable; duration; and one of `PASS`, `BEHAVIORAL_FAIL`, or `INFRA_ERROR`. Preserve stdout/stderr or a reviewable excerpt. Avoid relying on a nonzero exit code alone: pytest's no-tests-collected, syntax, and import failures must be invalid results, not catches.

| Candidate | Baseline suite | Evolved suite |
| --- | --- | --- |
| Correct post-change implementation | Must pass for the green-suite claim | Must pass for verification. |
| Premium still 10% | Record actual outcome. | Targeted 15% assertion should fail. |
| No $100 cap | Record actual outcome. | Targeted capped-discount assertion should fail. |
| Student-only gets 20% | Record actual outcome. | Targeted invariant assertion should fail. |

A mutant is **caught** only if its evolved-suite run fails on a test relevant to its *named defect* and the correct-implementation control passes. A failure on an unrelated requirement or setup problem is not a valid catch for that mutant. A mutant **escapes** if the test run completes and passes. Report a mutant caught by the baseline suite honestly; do not promise all three will escape it.

`verification.status` is:

- `VERIFIED`: both correct-implementation runs pass, and each of the three mutant/evolved-suite runs has a relevant behavioral failure, with no infrastructure errors in the required matrix.
- `FAILED`: runs execute validly, but a correct control fails or at least one required mutant survives or fails only for an unrelated behavior.
- `INVALID`: any required run has an infrastructure/setup error or missing trustworthy evidence; fix the harness and rerun before claiming results.

This is evidence against **three chosen faults**, not proof the program or test suite is perfect.

## 6. Report contract

Generate `artifacts/assertshift-report.json` and `artifacts/assertshift-report.md` from observed Bob findings, reviewed changes, and matrix runs. Do not preload example counts, `VERIFIED`, or `0` unverified behaviors as if they were real results.

Minimum JSON fields:

```json
{
  "project": "AssertShift",
  "change_request": "inputs/change-request.md",
  "analysis": {
    "behavior_changes": [],
    "preserved_invariants": [],
    "tests_examined": null,
    "breaking_tests": null,
    "stale_tests": null,
    "missing_tests": null
  },
  "findings": [],
  "actions": {"tests_updated": null, "tests_created": null},
  "verification": {
    "baseline_suite_id": null,
    "evolved_suite_id": null,
    "correct_baseline_passes": null,
    "correct_evolved_passes": null,
    "matrix_results": [],
    "mutants_escaped_baseline": null,
    "mutants_caught_evolved": null,
    "infra_errors": null,
    "unverified_behaviors": null,
    "status": null
  },
  "bob_evidence": [],
  "limitations": []
}
```

`null` indicates **not yet measured**, not a real report outcome. Replace it with observed values when writing final artifacts. Every finding should include `id`, `classification`, `requirement`, `test_or_gap`, `reason`, `evidence`, and `recommended_action`. Every matrix entry should include IDs, command, exit code, counts, result, relevant test/failure excerpt, and identifiers or hashes. The Markdown report should state what the evidence proves and what it does **not** prove. Validate that counts match the actual findings, matrix, and captured test outputs; the viewer must not fabricate them.

## 7. Public viewer and submission

A small static HTML/CSS/JavaScript viewer under `docs/` is the preferred low-risk public presentation. GitHub Pages may host it if the event accepts that URL. Its default view loads a **real, checked-in** copy of the generated JSON report. Provide at least one genuine interaction: inspect individual findings/matrix rows or load another compatible report using a local JSON file input. Label the page **Report viewer — Bob analysis runs in the IDE**, not “live Bob scanner.” Use safe text rendering for report contents; do not insert uploaded JSON as raw HTML.

Confirm the event-specific public URL and repository requirements before submission. A working viewer does not replace the actual Bob session/export evidence or a short video showing the IDE workflow. If hosting is unavailable, disclose the limitation rather than giving a nonworking URL.

### Minimal repository layout

```text
assertshift/
├── PROJECT_SPEC.md
├── README.md
├── sample_app/app/discounts.py
├── sample_app/tests/test_discounts.py
├── inputs/change-request.md
├── verification_snapshots/baseline_tests/
├── verification_mutants/
├── verification/manifest.json
├── scripts/run_verification_matrix.py
├── artifacts/assertshift-report.json
├── artifacts/assertshift-report.md
├── docs/index.html
├── docs/data/assertshift-report.json
├── bob_sessions/
└── submission/
```

Create the first four working assets and the relevant evidence directories early; create later files **when their contents exist**. Do not spend the first minutes committing empty `.gitkeep` folders to imply completion. `docs/data/assertshift-report.json` is a copy of the generated report: document the copy/update step and verify the two files match before deployment. Add a project-level Bob rule or reusable skill **only in the syntax supported by the installed version**, and only if it improves repeatability. Avoid unnecessary framework, backend, or external-LLM dependencies.

The README must explain how to reproduce the green-suite run, invoke the Bob workflow, run the eight-cell matrix, inspect the reports, identify real Bob session evidence, and open the viewer. Include genuine limitations and actual measurements. Do not commit credentials, private customer data, or fabricated screenshots. Capture exports/screenshots as work happens; label them with task and timestamp.

## 8. Measurement and demo

Keep two distinct comparisons:

1. **Test-strength comparison:** the immutable baseline suite versus Bob's evolved suite, each run on the correct implementation and all three mutants. This measures detection of the chosen faults, **not developer time saved**.
2. **Time/effort comparison (optional if not fairly measurable):** a manual attempt and a Bob-assisted attempt on the **same task**, with start/end conditions, participant familiarity, and number of manual actions disclosed. Do not equate the baseline suite's execution time with manual-review time or claim productivity gains from one uncontrolled run.

Record actual findings, tests changed/created, suite results, and duration. If a fair manual comparison is not possible, report the test-strength comparison and omit a speed claim.

### Five-minute demo outline

1. **Problem:** Show the actual baseline green test output and weak assertion; never display an invented “24 tests passed” count.
2. **Change:** Show the old/new discount rules and preserved Student-only invariant.
3. **Bob:** Show the real Plan analysis, focused investigations when available, findings, and approved test changes. In the main scenario, `BREAKING` may legitimately be zero.
4. **Proof:** Show the evolved suite passing on correct code and relevant behavioral failures for each mutant, plus a recorded comparison with the baseline suite. Explain any exceptions.
5. **Evidence:** Open the report/viewer and Bob session exports; state the limited claim and any outstanding failures.

Avoid promising reduced errors, rework, or time unless those outcomes were actually measured. The pitch is: **a green suite can still be weak; Bob helps find the gaps, and executable counterexamples test whether the revised suite is stronger.**

## 9. Definition of done

### Core workflow (must work before presentation polish)

- [ ] Canonical change request states old/new behavior, preserved invariant, cap, and money contract.
- [ ] Correct post-change implementation and original-to-new diff exist.
- [ ] The baseline suite passes on correct post-change code and contains a demonstrably stale assertion plus missing acceptance cases.
- [ ] Baseline tests are preserved before Bob edits them; snapshot/commit identities are recorded.
- [ ] Real Bob session inspects the documents, code, and tests; reports cited `STALE`/`MISSING` findings and any genuine `BREAKING` findings.
- [ ] Bob-assisted test edits are reviewed, saved, and committed; unaffected tests remain intact.
- [ ] Evolved suite passes on the correct code; full pytest output is retained.
- [ ] Three single-defect mutants and all eight isolated matrix runs are executed with relevant failure evidence and infrastructure errors separated.
- [ ] Verification status and limitations accurately reflect the observed matrix.
- [ ] JSON and Markdown reports match the commands, findings, and actual results.
- [ ] Real Bob session/export evidence is captured; no results or screenshots are fabricated.

### Submission readiness

- [ ] README reproduces the workflow and explains Bob's role versus the viewer's role.
- [ ] Public repository contains code, reports, and allowable session evidence, without secrets.
- [ ] Public viewer loads actual data, has meaningful interaction, and works without private credentials.
- [ ] Submission fields and URLs are checked against the current event form.
- [ ] Video or presentation shows the real Bob workflow and empirical test evidence.
- [ ] Any manual productivity comparison follows the stated methodology; otherwise speed claims are omitted.

## 10. Suggested first Bob prompt

```text
Read PROJECT_SPEC.md completely. Start in Plan mode and inspect the current repository before editing. Produce the smallest end-to-end implementation plan for AssertShift.

Show the exact change request, old-to-new code diff, immutable baseline-test snapshot step, live Breaking/Stale/Missing analysis, reviewed test edits, three single-defect mutants, eight isolated pytest runs, evidence report, and public viewer. Explain how the harness distinguishes relevant behavioral failures from infrastructure errors and how you will preserve real session evidence.

Do not hardcode the semantic findings or report outcomes. Do not claim a Bob feature, a deployment, a benchmark, or a test result unless you actually demonstrate it. Prioritize the working Bob/test workflow over optional PDF conversion, dashboard styling, or extra scaffolding.
```

## 11. Submission placeholders and references

Fill these only after the resources exist:

```text
PUBLIC_REPOSITORY_URL=TBD
APPLICATION_URL=TBD
VIDEO_URL=TBD
BOB_SESSION_EVIDENCE=TBD
```

Useful references from the prior build brief:

- [IBM Bob 2.0 hackathon](https://lablab.ai/ai-hackathons/ibm-bob-2-hackathon)
- [LabLab submission guidelines](https://lablab.ai/delivering-your-hackathon-solution)
- [IBM Bob subagent documentation](https://bob.ibm.com/docs/ide/features/subagents)

**Final message:** AssertShift uses IBM Bob 2.0 to help developers evolve tests after behavior changes—and backs the improvement with reproducible tests, not just a green badge or an AI-generated explanation.
