from __future__ import annotations

from pathlib import Path

from app import stage6_eval


ROOT = Path(__file__).resolve().parents[2]
CASE_FILE = ROOT / "data" / "evals" / "stage6" / "stage-6-source-chain-cases.json"


def test_stage6_case_file_exists_and_has_full_income_type_coverage():
    cases = stage6_eval.load_cases(CASE_FILE)

    assert len(cases) >= 6
    assert {case["category"] for case in cases} >= {
        "source_trace_supported",
        "pair_alignment",
    }


def test_stage6_case_file_matches_current_runtime_behavior():
    cases = stage6_eval.load_cases(CASE_FILE)

    report = stage6_eval.evaluate_suite(cases, analyzer=stage6_eval.run_case_through_service)

    assert report["failed_cases"] == 0
    assert report["metrics"]["real_excerpt_rate"]["value"] == 1.0
    assert report["metrics"]["mli_fact_rate"]["value"] == 1.0
