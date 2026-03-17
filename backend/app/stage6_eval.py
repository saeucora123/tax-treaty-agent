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
        raise ValueError("Stage 6 case file must contain a JSON list.")
    return payload


def evaluate_case(case: dict, analyzer: Analyzer) -> dict:
    actual = analyzer(case)
    expected = case["expected"]
    result = actual.get("result") or {}
    source_trace = result.get("source_trace") or {}
    mli_context = result.get("mli_context") or {}
    excerpt = result.get("source_excerpt") or ""
    working_paper_ref = source_trace.get("working_paper_ref") or ""

    checks = {
        "supported": actual.get("supported") == expected.get("supported"),
        "review_state_code": actual.get("review_state", {}).get("state_code")
        == expected.get("review_state_code"),
        "article_number": result.get("article_number") == expected.get("article_number"),
        "rate": result.get("rate") == expected.get("rate"),
        "source_reference": result.get("source_reference") == expected.get("source_reference"),
        "real_excerpt": expected.get("placeholder_excerpt_allowed", False)
        or "sample" not in excerpt.lower(),
        "working_paper": working_paper_ref.endswith(expected.get("working_paper_suffix", "")),
        "mli_ppt": mli_context.get("ppt_applies") is expected.get("mli_ppt_expected"),
        "mli_summary": "PPT" in (mli_context.get("summary") or ""),
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

    report = {
        "total_cases": len(case_reports),
        "passed_cases": sum(1 for report in case_reports if report["passed"]),
        "failed_cases": sum(1 for report in case_reports if not report["passed"]),
        "category_summary": category_summary,
        "case_reports": case_reports,
    }
    report["metrics"] = build_metric_summary(report)
    return report


def run_stage6_evaluation(
    case_path: Path,
    *,
    output_path: Path | None = None,
    analyzer: Analyzer | None = None,
) -> dict:
    resolved_analyzer = analyzer or run_case_through_service
    cases = load_cases(case_path)
    report = evaluate_suite(cases, analyzer=resolved_analyzer)
    report["suite_scope_note"] = (
        "This Stage 6 evaluation replays the source-chain closure contract across the currently "
        "supported treaty pairs and income types, checking treaty rates, real excerpts, "
        "working-paper references, and fact-based MLI/PPT prompts."
    )
    report["known_limitations"] = [
        "The current pack validates source-trace completeness inside the product response, not external citation export workflows.",
        "The 15-minute human review exercise is tracked separately as a gate artifact rather than a JSON-only metric.",
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

    real_excerpt_numerator = sum(1 for report in case_reports if report["checks"]["real_excerpt"])
    mli_fact_numerator = sum(
        1
        for report in case_reports
        if report["checks"]["mli_ppt"] and report["checks"]["mli_summary"]
    )

    return {
        "real_excerpt_rate": build_metric_entry(
            numerator=real_excerpt_numerator,
            denominator=total_cases,
            definition="Cases where the source excerpt is a real treaty excerpt rather than placeholder text.",
        ),
        "mli_fact_rate": build_metric_entry(
            numerator=mli_fact_numerator,
            denominator=total_cases,
            definition="Cases where the response carries a fact-based PPT signal and explicit MLI summary.",
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
    os.environ["PYTEST_CURRENT_TEST"] = "stage6_eval"
    try:
        yield
    finally:
        if previous is None:
            os.environ.pop("PYTEST_CURRENT_TEST", None)
        else:
            os.environ["PYTEST_CURRENT_TEST"] = previous
