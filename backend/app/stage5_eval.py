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
        raise ValueError("Stage 5 case file must contain a JSON list.")
    return payload


def evaluate_case(case: dict, analyzer: Analyzer) -> dict:
    actual = analyzer(case)
    expected = case["expected"]
    handoff = actual.get("handoff_package") or {}
    machine_handoff = handoff.get("machine_handoff") or {}
    human_review_brief = handoff.get("human_review_brief") or {}
    handoff_present = bool(handoff)
    actual_review_state_code = actual.get("review_state", {}).get("state_code")

    checks = {
        "supported": actual.get("supported") == expected.get("supported"),
        "review_state_code": actual_review_state_code == expected.get("review_state_code"),
        "handoff_present": handoff_present,
        "review_state_echo": machine_handoff.get("review_state_code") == actual_review_state_code,
        "recommended_route": machine_handoff.get("recommended_route")
        == expected.get("recommended_route"),
        "record_kind": machine_handoff.get("record_kind") == expected.get("record_kind"),
        "article_number": machine_handoff.get("article_number") == expected.get("article_number"),
        "rate_display": machine_handoff.get("rate_display") == expected.get("rate_display"),
        "human_disposition": human_review_brief.get("disposition")
        == expected.get("human_disposition"),
        "user_declared_facts_present": bool(machine_handoff.get("user_declared_facts"))
        is expected.get("user_declared_facts_present", False),
    }
    return {
        "id": case["id"],
        "category": case["category"],
        "passed": all(checks.values()),
        "checks": checks,
        "expected": expected,
        "actual": actual,
    }


def evaluate_suite(cases: list[dict], analyzer: Analyzer) -> dict:
    case_reports = [evaluate_case(case, analyzer=analyzer) for case in cases]
    category_summary: dict[str, dict[str, int]] = {}

    for report in case_reports:
        bucket = category_summary.setdefault(report["category"], {"total": 0, "passed": 0})
        bucket["total"] += 1
        bucket["passed"] += int(report["passed"])

    report = {
        "total_cases": len(case_reports),
        "passed_cases": sum(1 for report in case_reports if report["passed"]),
        "failed_cases": sum(1 for report in case_reports if not report["passed"]),
        "category_summary": category_summary,
        "case_reports": case_reports,
    }
    report["metrics"] = build_metric_summary(report)
    return report


def run_stage5_evaluation(
    case_path: Path,
    *,
    output_path: Path | None = None,
    analyzer: Analyzer | None = None,
) -> dict:
    resolved_analyzer = analyzer or run_case_through_service
    cases = load_cases(case_path)
    report = evaluate_suite(cases, analyzer=resolved_analyzer)
    report["suite_scope_note"] = (
        "This Stage 5 evaluation replays the deterministic handoff contract across supported, "
        "incomplete, unsupported, unavailable-data-source, and bounded Stage 4 outputs without "
        "changing the public request shape."
    )
    report["known_limitations"] = [
        "The current pack validates the response-level handoff contract, not external transport or workflow orchestration.",
        "Frontend renderability is still validated through the existing UI test suite rather than this JSON report alone.",
    ]
    if output_path is not None:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(
            json.dumps(report, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
    return report


def build_metric_summary(report: dict) -> dict:
    case_reports = report["case_reports"]
    total_cases = len(case_reports)

    handoff_coverage_numerator = sum(
        1 for report in case_reports if report["checks"]["handoff_present"]
    )
    route_match_numerator = sum(
        1
        for report in case_reports
        if report["checks"]["recommended_route"] and report["checks"]["review_state_echo"]
    )
    null_field_cases = [
        report
        for report in case_reports
        if report["actual"].get("handoff_package", {})
        .get("machine_handoff", {})
        .get("record_kind")
        in {"unsupported", "incomplete"}
    ]
    null_field_numerator = sum(
        1
        for report in null_field_cases
        if report["checks"]["article_number"] and report["checks"]["rate_display"]
    )
    user_declared_cases = [
        report
        for report in case_reports
        if report["expected"].get("user_declared_facts_present", False)
    ]

    return {
        "handoff_coverage": build_metric_entry(
            numerator=handoff_coverage_numerator,
            denominator=total_cases,
            definition="Cases where the response includes a handoff_package.",
        ),
        "route_match_rate": build_metric_entry(
            numerator=route_match_numerator,
            denominator=total_cases,
            definition="Cases where recommended_route matches the expected route and echoes the response review_state.",
        ),
        "null_field_behavior": build_metric_entry(
            numerator=null_field_numerator,
            denominator=len(null_field_cases),
            definition="Cases requiring null treaty/article fields that return explicit null values instead of fabricated data.",
        ),
        "user_declared_fact_preservation": build_metric_entry(
            numerator=sum(
                1 for report in user_declared_cases if report["checks"]["user_declared_facts_present"]
            ),
            denominator=len(user_declared_cases),
            definition="Cases that preserve user-declared facts inside machine_handoff when such facts exist.",
        ),
    }


def build_metric_entry(*, numerator: int, denominator: int, definition: str) -> dict:
    return {
        "numerator": numerator,
        "denominator": denominator,
        "value": None if denominator == 0 else round(numerator / denominator, 4),
        "definition": definition,
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
    os.environ["PYTEST_CURRENT_TEST"] = "stage5_eval"
    try:
        yield
    finally:
        if previous is None:
            os.environ.pop("PYTEST_CURRENT_TEST", None)
        else:
            os.environ["PYTEST_CURRENT_TEST"] = previous
