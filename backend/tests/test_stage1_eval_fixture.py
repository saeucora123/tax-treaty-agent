from __future__ import annotations

from pathlib import Path

from app import stage1_eval


ROOT = Path(__file__).resolve().parents[2]
CASE_FILE = ROOT / "data" / "evals" / "stage1" / "stage-1-initial-cases.json"

MINIMUM_COUNTS = {
    "happy_path": 18,
    "boundary_input": 12,
    "out_of_scope": 12,
    "incomplete": 10,
    "adversarial": 10,
    "multi_branch": 8,
}


def test_stage1_initial_case_file_exists_and_covers_all_current_categories():
    cases = stage1_eval.load_cases(CASE_FILE)

    assert len(cases) >= 6
    assert {case["category"] for case in cases} >= {
        "happy_path",
        "boundary_input",
        "out_of_scope",
        "incomplete",
        "adversarial",
        "multi_branch",
    }


def test_stage1_initial_case_file_matches_current_runtime_behavior():
    cases = stage1_eval.load_cases(CASE_FILE)

    report = stage1_eval.evaluate_suite(cases, analyzer=stage1_eval.run_case_through_service)

    assert report["failed_cases"] == 0
    assert report["critical_overreach_count"] == 0
    assert report["major_overreach_count"] == 0


def test_stage1_initial_case_file_meets_stage1_memo_minimum_counts():
    cases = stage1_eval.load_cases(CASE_FILE)
    counts: dict[str, int] = {}
    for case in cases:
        counts[case["category"]] = counts.get(case["category"], 0) + 1

    assert len(cases) >= sum(MINIMUM_COUNTS.values())
    for category, minimum in MINIMUM_COUNTS.items():
        assert counts.get(category, 0) >= minimum
