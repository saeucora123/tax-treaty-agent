from __future__ import annotations

from pathlib import Path

from app import stage2_eval


ROOT = Path(__file__).resolve().parents[2]
CASE_FILE = ROOT / "data" / "evals" / "stage2" / "stage-2-cn-sg-cases.json"


def test_stage2_case_file_exists_and_has_minimum_replay_set():
    cases = stage2_eval.load_cases(CASE_FILE)

    assert len(cases) >= 10
    assert {case["category"] for case in cases} >= {
        "stable_supported",
        "generated_unavailable",
        "guardrail_regression",
    }


def test_stage2_case_file_matches_current_runtime_behavior():
    cases = stage2_eval.load_cases(CASE_FILE)

    report = stage2_eval.evaluate_suite(cases, analyzer=stage2_eval.run_case_through_service)

    assert report["failed_cases"] == 0
    assert report["pass_rate"] >= 0.9
