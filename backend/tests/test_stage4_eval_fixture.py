from __future__ import annotations

from pathlib import Path

from app import stage4_eval


ROOT = Path(__file__).resolve().parents[2]
CASE_FILE = ROOT / "data" / "evals" / "stage4" / "stage-4-precision-pack.json"


def test_stage4_precision_pack_exists_and_meets_current_minimum_count():
    cases = stage4_eval.load_cases(CASE_FILE)

    assert len(cases) >= 10
    assert {case["category"] for case in cases} >= {"multi_branch_dividend"}


def test_stage4_precision_pack_matches_current_runtime_behavior():
    cases = stage4_eval.load_cases(CASE_FILE)

    report = stage4_eval.evaluate_suite(cases, analyzer=stage4_eval.run_case_through_service)

    assert report["failed_cases"] == 0

