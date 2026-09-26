#!/usr/bin/env python3
"""scripts/run_verification_matrix.py

Executes all eight suite × candidate combinations for the AssertShift
verification matrix and writes results to verification/matrix_results.json.

Combinations (2 suites × 4 candidates):
  Suites:
    baseline  - verification_snapshots/baseline_tests/test_discounts.py
    evolved   - sample_app/tests/test_discounts.py

  Candidates:
    correct            - sample_app/app/discounts.py
    premium_still_10   - verification_mutants/premium_still_10/discounts.py
    missing_discount_cap - verification_mutants/missing_discount_cap/discounts.py
    student_without_premium - verification_mutants/student_without_premium/discounts.py

Each run uses an isolated temporary directory so that no module-cache
contamination can occur between runs.

Usage:
    python scripts/run_verification_matrix.py

Output:
    verification/matrix_results.json  - full structured results
    verification/manifest.json        - updated with run metadata
"""

import hashlib
import json
import re
import shutil
import subprocess
import sys
import tempfile
import time
from datetime import datetime, timezone
from pathlib import Path

# ---------------------------------------------------------------------------
# Paths (relative to repo root)
# ---------------------------------------------------------------------------

REPO_ROOT = Path(__file__).parent.parent.resolve()

CANDIDATES = {
    "correct": REPO_ROOT / "sample_app" / "app" / "discounts.py",
    "premium_still_10": REPO_ROOT / "verification_mutants" / "premium_still_10" / "discounts.py",
    "missing_discount_cap": REPO_ROOT / "verification_mutants" / "missing_discount_cap" / "discounts.py",
    "student_without_premium": REPO_ROOT / "verification_mutants" / "student_without_premium" / "discounts.py",
}

SUITES = {
    "baseline": REPO_ROOT / "verification_snapshots" / "baseline_tests" / "test_discounts.py",
    "evolved": REPO_ROOT / "sample_app" / "tests" / "test_discounts.py",
}

OUTPUT_DIR = REPO_ROOT / "verification"
OUTPUT_FILE = OUTPUT_DIR / "matrix_results.json"
MANIFEST_FILE = OUTPUT_DIR / "manifest.json"

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def file_sha256(path: Path) -> str:
    h = hashlib.sha256()
    h.update(path.read_bytes())
    return h.hexdigest()[:16]


def parse_pytest_output(stdout: str, stderr: str) -> dict:
    """Extract pass/fail/error counts and failing test names from pytest output."""
    counts = {"passed": 0, "failed": 0, "error": 0, "total": 0}
    failing_tests: list[str] = []
    failure_excerpts: list[str] = []

    # Attempt to parse the summary line, e.g. "5 passed, 2 failed, 1 error"
    summary_pattern = re.compile(
        r"(\d+) passed|(\d+) failed|(\d+) error",
        re.IGNORECASE,
    )
    for m in summary_pattern.finditer(stdout + stderr):
        if m.group(1):
            counts["passed"] = int(m.group(1))
        elif m.group(2):
            counts["failed"] = int(m.group(2))
        elif m.group(3):
            counts["error"] = int(m.group(3))

    counts["total"] = counts["passed"] + counts["failed"] + counts["error"]

    # Capture FAILED test IDs
    for line in (stdout + stderr).splitlines():
        if line.strip().startswith("FAILED "):
            test_id = line.strip()[len("FAILED "):].split(" - ")[0].strip()
            failing_tests.append(test_id)

    # Capture short assertion excerpts (AssertionError lines)
    in_block = False
    block_lines: list[str] = []
    for line in (stdout + stderr).splitlines():
        if line.startswith("FAILED") or ("AssertionError" in line):
            in_block = True
        if in_block:
            block_lines.append(line)
            if len(block_lines) >= 6:
                failure_excerpts.append("\n".join(block_lines))
                block_lines = []
                in_block = False

    return {
        "counts": counts,
        "failing_tests": failing_tests,
        "failure_excerpt": "\n".join(failure_excerpts)[:2000] if failure_excerpts else "",
    }


def classify_result(exit_code: int, counts: dict, stdout: str, stderr: str) -> str:
    """Return PASS, BEHAVIORAL_FAIL, or INFRA_ERROR.

    Conservative classification order (per spec):
    1. Any known infrastructure/collection/setup text → INFRA_ERROR
    2. pytest error count > 0 → INFRA_ERROR  (errors are not behavioral failures)
    3. exit code 0 and failures == 0 → PASS
    4. failures > 0 and errors == 0 → BEHAVIORAL_FAIL
    5. everything else → INFRA_ERROR
    """
    combined = stdout + stderr

    # Infrastructure indicators: no tests collected, import errors, syntax errors
    infra_markers = [
        "no tests ran",
        "collected 0 items",
        "ERROR collecting",
        "ImportError",
        "ModuleNotFoundError",
        "SyntaxError",
        "no module named",
    ]
    for marker in infra_markers:
        if marker.lower() in combined.lower():
            return "INFRA_ERROR"

    # Any pytest fixture/setup error is infrastructure, not a behavioral failure
    if counts["error"] > 0:
        return "INFRA_ERROR"

    if exit_code == 0 and counts["failed"] == 0:
        return "PASS"
    if counts["failed"] > 0 and counts["error"] == 0:
        return "BEHAVIORAL_FAIL"
    # Nonzero exit with no clear failure counts (e.g. collection error)
    return "INFRA_ERROR"


# ---------------------------------------------------------------------------
# Single isolated run
# ---------------------------------------------------------------------------

def run_single(suite_id: str, suite_path: Path, candidate_id: str, candidate_path: Path) -> dict:
    """Run pytest for one suite/candidate pair in an isolated temp directory."""
    with tempfile.TemporaryDirectory(prefix="assertshift_") as tmp:
        tmp_path = Path(tmp)

        # Recreate the import structure: sample_app/app/discounts.py
        app_dir = tmp_path / "sample_app" / "app"
        app_dir.mkdir(parents=True)
        (tmp_path / "sample_app" / "__init__.py").write_text("")
        (app_dir / "__init__.py").write_text("")

        # Place the selected candidate at the expected import path
        shutil.copy(candidate_path, app_dir / "discounts.py")

        # Place the selected test file
        tests_dir = tmp_path / "tests"
        tests_dir.mkdir()
        (tests_dir / "__init__.py").write_text("")
        shutil.copy(suite_path, tests_dir / "test_discounts.py")

        # Build the pytest command
        cmd = [
            sys.executable, "-m", "pytest",
            str(tests_dir / "test_discounts.py"),
            "-v", "--tb=short", "--no-header",
        ]

        start = time.monotonic()
        try:
            proc = subprocess.run(
                cmd,
                cwd=str(tmp_path),
                capture_output=True,
                text=True,
                timeout=60,
            )
            exit_code = proc.returncode
            stdout = proc.stdout
            stderr = proc.stderr
        except subprocess.TimeoutExpired:
            return {
                "suite": suite_id,
                "candidate": candidate_id,
                "result": "INFRA_ERROR",
                "exit_code": -1,
                "counts": {"passed": 0, "failed": 0, "error": 0, "total": 0},
                "failing_tests": [],
                "failure_excerpt": "Timeout after 60s",
                "stdout_excerpt": "",
                "stderr_excerpt": "Timeout after 60s",
                "duration_s": round(time.monotonic() - start, 3),
                "candidate_hash": file_sha256(candidate_path),
                "suite_hash": file_sha256(suite_path),
                "command": " ".join(cmd),
            }

        duration = round(time.monotonic() - start, 3)
        parsed = parse_pytest_output(stdout, stderr)
        result = classify_result(exit_code, parsed["counts"], stdout, stderr)

        return {
            "suite": suite_id,
            "candidate": candidate_id,
            "result": result,
            "exit_code": exit_code,
            "counts": parsed["counts"],
            "failing_tests": parsed["failing_tests"],
            "failure_excerpt": parsed["failure_excerpt"],
            "stdout_excerpt": stdout[-3000:] if len(stdout) > 3000 else stdout,
            "stderr_excerpt": stderr[-1000:] if len(stderr) > 1000 else stderr,
            "duration_s": duration,
            "candidate_hash": file_sha256(candidate_path),
            "suite_hash": file_sha256(suite_path),
            "command": " ".join(cmd),
        }


# ---------------------------------------------------------------------------
# Matrix
# ---------------------------------------------------------------------------

def run_matrix() -> list[dict]:
    results = []
    ordered = [
        ("baseline", "correct"),
        ("baseline", "premium_still_10"),
        ("baseline", "missing_discount_cap"),
        ("baseline", "student_without_premium"),
        ("evolved", "correct"),
        ("evolved", "premium_still_10"),
        ("evolved", "missing_discount_cap"),
        ("evolved", "student_without_premium"),
    ]

    for suite_id, candidate_id in ordered:
        suite_path = SUITES[suite_id]
        candidate_path = CANDIDATES[candidate_id]
        print(f"  Running [{suite_id:8s} × {candidate_id:25s}] ...", end=" ", flush=True)
        result = run_single(suite_id, suite_path, candidate_id, candidate_path)
        status_label = result["result"]
        counts = result["counts"]
        print(f"{status_label}  ({counts['passed']}P / {counts['failed']}F / {counts['error']}E, {result['duration_s']}s)")
        results.append(result)

    return results


# ---------------------------------------------------------------------------
# Verification status derivation
# ---------------------------------------------------------------------------

MUTANTS = ["premium_still_10", "missing_discount_cap", "student_without_premium"]

# Relevant-test names for each mutant (first gate: test-name match)
MUTANT_RELEVANT_TESTS = {
    "premium_still_10": [
        "test_premium_discount_exact_rate",
        "test_premium_discount_200",
    ],
    "missing_discount_cap": [
        "test_cap_premium_only",
        "test_cap_premium_and_student",
        "test_rounding_then_cap",
    ],
    "student_without_premium": [
        "test_student_only_gets_no_discount",
        "test_student_only_large_order_gets_no_discount",
    ],
}


def has_defect_evidence(run: dict, mutant_id: str) -> bool:
    """Return True only when the failure output contains evidence specifically
    consistent with the mutant's named behavioral defect.

    Requirements (must all hold):
    1. at least one relevant test name failed
    2. the captured output contains paired values that match the named defect
       (not a single generic number that could appear for any reason)

    Paired-value checks (robust to minor pytest formatting changes):
      premium_still_10      : "10.00" AND "15.00" in output
      missing_discount_cap  : ("150.00" AND "100.00") OR ("100.01" AND "100.00") in output
      student_without_premium: "20.00" AND "0.00" in output
    """
    relevant_tests = MUTANT_RELEVANT_TESTS.get(mutant_id, [])

    # Gate 1: at least one mapped test name must appear among failing tests
    relevant_test_failed = any(
        rt in ft
        for ft in run.get("failing_tests", [])
        for rt in relevant_tests
    )
    if not relevant_test_failed:
        return False

    # Gate 2: defect-specific paired-value evidence in captured output
    output = (
        run.get("failure_excerpt", "")
        + run.get("stdout_excerpt", "")
        + run.get("stderr_excerpt", "")
    )

    if mutant_id == "premium_still_10":
        # Wrong rate: actual 10.00, expected 15.00
        return "10.00" in output and "15.00" in output

    if mutant_id == "missing_discount_cap":
        # Missing cap: uncapped value vs capped 100.00
        return (
            ("150.00" in output and "100.00" in output)
            or ("100.01" in output and "100.00" in output)
        )

    if mutant_id == "student_without_premium":
        # Invariant broken: student-only got 20.00 but expected 0.00
        return "20.00" in output and "0.00" in output

    return False


def is_relevant_failure(run: dict, mutant_id: str) -> bool:
    """Alias kept for compatibility; delegates to has_defect_evidence."""
    return has_defect_evidence(run, mutant_id)


def derive_verification_status(results: list[dict]) -> dict:
    by_key = {(r["suite"], r["candidate"]): r for r in results}

    correct_baseline = by_key.get(("baseline", "correct"), {})
    correct_evolved = by_key.get(("evolved", "correct"), {})

    infra_errors = [r for r in results if r["result"] == "INFRA_ERROR"]

    correct_baseline_passes = correct_baseline.get("result") == "PASS"
    correct_evolved_passes = correct_evolved.get("result") == "PASS"

    mutants_escaped_baseline = []
    mutants_caught_evolved = []
    mutant_details = {}

    for m in MUTANTS:
        baseline_run = by_key.get(("baseline", m), {})
        evolved_run = by_key.get(("evolved", m), {})

        baseline_result = baseline_run.get("result", "INFRA_ERROR")
        evolved_result = evolved_run.get("result", "INFRA_ERROR")

        caught_evolved = (
            evolved_result == "BEHAVIORAL_FAIL"
            and is_relevant_failure(evolved_run, m)
            and correct_evolved_passes
        )

        escaped_baseline = baseline_result == "PASS"

        mutant_details[m] = {
            "baseline_result": baseline_result,
            "evolved_result": evolved_result,
            "caught_by_evolved": caught_evolved,
            "escaped_baseline": escaped_baseline,
            "relevant_failure_in_evolved": is_relevant_failure(evolved_run, m),
        }

        if escaped_baseline:
            mutants_escaped_baseline.append(m)
        if caught_evolved:
            mutants_caught_evolved.append(m)

    # Determine overall status
    if infra_errors:
        status = "INVALID"
    elif (
        correct_baseline_passes
        and correct_evolved_passes
        and len(mutants_caught_evolved) == len(MUTANTS)
    ):
        status = "VERIFIED"
    else:
        status = "FAILED"

    return {
        "correct_baseline_passes": correct_baseline_passes,
        "correct_evolved_passes": correct_evolved_passes,
        "mutants_escaped_baseline": mutants_escaped_baseline,
        "mutants_caught_evolved": mutants_caught_evolved,
        "mutant_details": mutant_details,
        "infra_errors": [r["suite"] + "/" + r["candidate"] for r in infra_errors],
        "status": status,
    }


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    print("=" * 70)
    print("AssertShift Verification Matrix")
    print(f"Started: {datetime.now(timezone.utc).isoformat()}")
    print("=" * 70)
    print()

    # Verify all source files exist
    missing = []
    for cid, cpath in CANDIDATES.items():
        if not cpath.exists():
            missing.append(f"candidate {cid!r}: {cpath}")
    for sid, spath in SUITES.items():
        if not spath.exists():
            missing.append(f"suite {sid!r}: {spath}")
    if missing:
        print("ERROR: Missing files:")
        for m in missing:
            print(f"  {m}")
        sys.exit(1)

    results = run_matrix()
    verification = derive_verification_status(results)

    print()
    print("=" * 70)
    print(f"Verification status: {verification['status']}")
    print(f"  Correct/baseline passes:  {verification['correct_baseline_passes']}")
    print(f"  Correct/evolved passes:   {verification['correct_evolved_passes']}")
    print(f"  Mutants caught (evolved): {verification['mutants_caught_evolved']}")
    print(f"  Mutants escaped baseline: {verification['mutants_escaped_baseline']}")
    print(f"  Infra errors:             {verification['infra_errors']}")
    print("=" * 70)

    OUTPUT_DIR.mkdir(exist_ok=True)

    output = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "verification": verification,
        "runs": results,
    }
    OUTPUT_FILE.write_text(json.dumps(output, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"\nResults written to: {OUTPUT_FILE.relative_to(REPO_ROOT)}")

    # Update manifest
    manifest = {}
    if MANIFEST_FILE.exists():
        try:
            manifest = json.loads(MANIFEST_FILE.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            pass

    manifest["last_matrix_run"] = datetime.now(timezone.utc).isoformat()
    manifest["verification_status"] = verification["status"]
    manifest["baseline_suite_hash"] = file_sha256(SUITES["baseline"])
    manifest["evolved_suite_hash"] = file_sha256(SUITES["evolved"])
    manifest["candidate_hashes"] = {k: file_sha256(v) for k, v in CANDIDATES.items()}
    MANIFEST_FILE.write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Manifest updated:   {MANIFEST_FILE.relative_to(REPO_ROOT)}")


if __name__ == "__main__":
    main()
