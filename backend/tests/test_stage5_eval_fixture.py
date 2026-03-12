from __future__ import annotations

from pathlib import Path

from app import stage5_eval


ROOT = Path(__file__).resolve().parents[2]
CASE_FILE = ROOT / "data" / "evals" / "stage5" / "stage-5-handoff-cases.json"


def test_stage5_case_file_exists_and_has_minimum_handoff_coverage():
    cases = stage5_eval.load_cases(CASE_FILE)

    assert len(cases) >= 6
    assert {case["category"] for case in cases} >= {
        "supported_clear",
        "supported_ambiguous",
        "stage4_bounded",
        "unsupported",
        "incomplete",
        "unavailable_data_source",
    }


def test_stage5_case_file_matches_current_runtime_behavior():
    cases = stage5_eval.load_cases(CASE_FILE)

    report = stage5_eval.evaluate_suite(cases, analyzer=stage5_eval.run_case_through_service)

    assert report["failed_cases"] == 0
    assert report["metrics"]["handoff_coverage"]["value"] == 1.0
    assert report["metrics"]["route_match_rate"]["value"] == 1.0
