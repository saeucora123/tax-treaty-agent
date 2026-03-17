from __future__ import annotations

import json
import os
from contextlib import contextmanager
from pathlib import Path
from typing import Callable

from app import service


Analyzer = Callable[[dict], dict]
REPO_ROOT = Path(__file__).resolve().parents[2]


def load_cases(path: Path) -> list[dict]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, list):
        raise ValueError("Stage 2 case file must contain a JSON list.")
    return payload


def evaluate_case(case: dict, analyzer: Analyzer) -> dict:
    actual = analyzer(case)
    expected = case["expected"]
    checks = {
        "supported": actual.get("supported") == expected.get("supported"),
        "reason": actual.get("reason") == expected.get("reason"),
        "review_state_code": actual.get("review_state", {}).get("state_code")
        == expected.get("review_state_code"),
        "article_number": actual.get("result", {}).get("article_number")
        == expected.get("article_number"),
        "rate": actual.get("result", {}).get("rate") == expected.get("rate"),
        "data_source_used": actual.get("data_source_used") == expected.get("data_source_used"),
        "direction": actual.get("confirmed_scope", {}).get("payment_direction")
        == expected.get("payment_direction"),
    }
    return {
        "id": case["id"],
        "category": case["category"],
        "passed": all(checks.values()),
        "checks": checks,
        "actual": actual,
    }


def evaluate_suite(cases: list[dict], analyzer: Analyzer) -> dict:
    case_reports = [evaluate_case(case, analyzer=analyzer) for case in cases]
    category_summary: dict[str, dict[str, int]] = {}

    for report in case_reports:
        bucket = category_summary.setdefault(report["category"], {"total": 0, "passed": 0})
        bucket["total"] += 1
        bucket["passed"] += int(report["passed"])

    total_cases = len(case_reports)
    passed_cases = sum(1 for report in case_reports if report["passed"])
    return {
        "total_cases": total_cases,
        "passed_cases": passed_cases,
        "failed_cases": total_cases - passed_cases,
        "pass_rate": None if total_cases == 0 else round(passed_cases / total_cases, 4),
        "category_summary": category_summary,
        "case_reports": case_reports,
    }


def run_stage2_evaluation(
    case_path: Path,
    *,
    output_path: Path | None = None,
    analyzer: Analyzer | None = None,
) -> dict:
    resolved_analyzer = analyzer or run_case_through_service
    cases = load_cases(case_path)
    report = evaluate_suite(cases, analyzer=resolved_analyzer)
    report["metrics"] = build_metric_summary(report)
    report["suite_scope_note"] = (
        "This Stage 2 evaluation replays stable-lane CN-SG onboarding behavior and one "
        "controlled llm_generated rejection without changing the public request contract."
    )
    report["known_limitations"] = [
        "The Stage 2 pack focuses on the stable pilot pair and does not expand llm_generated support beyond CN-NL.",
        "The current pack tests runtime reuse, not full treaty-source completeness.",
    ]
    if output_path is not None:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(
            json.dumps(report, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
    return report


def build_metric_summary(report: dict) -> dict:
    total_cases = report["total_cases"]
    passed_cases = report["passed_cases"]
    return {
        "overall_pass_rate": {
            "numerator": passed_cases,
            "denominator": total_cases,
            "value": None if total_cases == 0 else round(passed_cases / total_cases, 4),
            "definition": "Share of Stage 2 replay cases that match the expected runtime behavior.",
        },
        "g2_1_threshold": {
            "threshold": 0.9,
            "actual": None if total_cases == 0 else round(passed_cases / total_cases, 4),
            "met": total_cases > 0 and (passed_cases / total_cases) >= 0.9,
        },
    }


def run_case_through_service(case: dict) -> dict:
    with disable_live_llm():
        return service.analyze_scenario(
            case["scenario"],
            data_source=case.get("data_source", "stable"),
            input_mode=case.get("input_mode"),
            guided_input=case.get("guided_input"),
        )


@contextmanager
def disable_live_llm():
    previous = os.getenv("PYTEST_CURRENT_TEST")
    os.environ["PYTEST_CURRENT_TEST"] = "stage2_eval"
    try:
        yield
    finally:
        if previous is None:
            os.environ.pop("PYTEST_CURRENT_TEST", None)
        else:
            os.environ["PYTEST_CURRENT_TEST"] = previous
