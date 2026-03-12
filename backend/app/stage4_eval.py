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
        raise ValueError("Stage 4 case file must contain a JSON list.")
    return payload


def run_stage4_evaluation(
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
        "This Stage 4 evaluation is deterministic and replays bounded pseudo-multiturn "
        "dividend scenarios without enabling live LLM parsing."
    )
    report["known_limitations"] = [
        "The current Stage 4 pack is still concentrated in the CN-NL dividends lane.",
        "This report measures bounded pseudo-multiturn behavior, not true multi-turn interaction.",
    ]
    if output_path is not None:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(
            json.dumps(report, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
    return report


def evaluate_case(case: dict, analyzer: Analyzer) -> dict:
    actual = analyzer(case)
    expected = case["expected"]
    checks = {
        "supported": actual.get("supported") == expected.get("supported"),
        "review_state_code": actual.get("review_state", {}).get("state_code")
        == expected.get("review_state_code"),
        "rate": actual.get("result", {}).get("rate") == expected.get("rate"),
        "fact_completion_status_code": actual.get("fact_completion_status", {}).get("status_code")
        == expected.get("fact_completion_status_code"),
        "fact_completion_present": bool(actual.get("fact_completion"))
        is expected.get("fact_completion_present", False),
        "change_summary_present": bool(actual.get("change_summary"))
        is expected.get("change_summary_present", False),
        "user_declared_facts_present": bool(actual.get("user_declared_facts"))
        is expected.get("user_declared_facts_present", False),
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
    termination_summary: dict[str, int] = {}

    for report in case_reports:
        bucket = category_summary.setdefault(report["category"], {"total": 0, "passed": 0})
        bucket["total"] += 1
        bucket["passed"] += int(report["passed"])

        status_code = report["actual"].get("fact_completion_status", {}).get("status_code")
        if status_code and status_code.startswith("terminated_"):
            termination_summary[status_code] = termination_summary.get(status_code, 0) + 1

    return {
        "total_cases": len(case_reports),
        "passed_cases": sum(1 for report in case_reports if report["passed"]),
        "failed_cases": sum(1 for report in case_reports if not report["passed"]),
        "category_summary": category_summary,
        "termination_summary": termination_summary,
        "case_reports": case_reports,
    }


def build_metric_summary(report: dict) -> dict:
    case_reports = report["case_reports"]

    return {
        "awaiting_user_facts_cases": build_metric_entry(
            numerator=sum(
                1
                for report in case_reports
                if report["actual"].get("fact_completion_status", {}).get("status_code")
                == "awaiting_user_facts"
            ),
            denominator=len(case_reports),
            definition="Cases that correctly remain in the bounded fact-completion state.",
        ),
        "completed_narrowed_cases": build_metric_entry(
            numerator=sum(
                1
                for report in case_reports
                if report["actual"].get("fact_completion_status", {}).get("status_code")
                == "completed_narrowed"
            ),
            denominator=len(case_reports),
            definition="Cases that narrow the dividend branch into a single treaty-rate candidate.",
        ),
        "terminated_cases": build_metric_entry(
            numerator=sum(
                1
                for report in case_reports
                if str(report["actual"].get("fact_completion_status", {}).get("status_code", "")).startswith(
                    "terminated_"
                )
            ),
            denominator=len(case_reports),
            definition="Cases that end in a bounded guided stop instead of continuing pseudo-multiturn narrowing.",
        ),
        "g4_1_case_threshold": {
            "threshold": 10,
            "actual": len(case_reports),
            "met": len(case_reports) >= 10,
        },
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
            fact_inputs=case.get("fact_inputs"),
        )


@contextmanager
def disable_live_llm():
    previous = os.getenv("PYTEST_CURRENT_TEST")
    os.environ["PYTEST_CURRENT_TEST"] = "stage4_eval"
    try:
        yield
    finally:
        if previous is None:
            os.environ.pop("PYTEST_CURRENT_TEST", None)
        else:
            os.environ["PYTEST_CURRENT_TEST"] = previous
