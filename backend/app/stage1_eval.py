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
        raise ValueError("Stage 1 case file must contain a JSON list.")
    return payload


def run_stage1_evaluation(
    case_path: Path,
    *,
    output_path: Path | None = None,
    analyzer: Analyzer = None,
) -> dict:
    resolved_analyzer = analyzer or run_case_through_service
    cases = load_cases(case_path)
    report = evaluate_suite(cases, analyzer=resolved_analyzer)
    report["metrics"] = build_metric_summary(cases, report)
    report["hard_commitment_mapping"] = build_hard_commitment_mapping(cases)
    report["suite_scope_note"] = (
        "This Stage 1 evaluation is deterministic and disables live LLM input parsing so the "
        "same fixed case suite can be replayed without paid model calls or runtime drift."
    )
    known_limitations = [
        "The case suite is built by the project team and is not yet externally audited.",
        "Results reflect covered scenarios only and do not imply performance on all possible inputs.",
    ]
    if len(cases) < 70:
        known_limitations.insert(
            0,
            "This fixed suite is still below the current memo minimum case count.",
        )
    else:
        known_limitations.insert(
            0,
            "This fixed suite now meets the current memo minimum count, but it is still a curated internal suite rather than an external independent benchmark.",
        )
    report["known_limitations"] = known_limitations
    if output_path is not None:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(
            json.dumps(report, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
    return report


def build_metric_summary(cases: list[dict], suite_report: dict) -> dict:
    case_reports = suite_report["case_reports"]

    normalized_cases = [report for report in case_reports if "normalized_input" in _expected_for_case(cases, report["id"])]
    article_cases = [report for report in case_reports if "article_number" in _expected_for_case(cases, report["id"])]
    refused_cases = [report for report in case_reports if report["actual"].get("supported") is False]
    false_positive_refusals = [
        report
        for report in refused_cases
        if _expected_for_case(cases, report["id"]).get("supported") is True
    ]
    supported_scope_cases = [
        report
        for report in case_reports
        if _expected_for_case(cases, report["id"]).get("supported") is True
    ]
    supported_scope_refusals = [
        report for report in supported_scope_cases if report["actual"].get("supported") is False
    ]

    return {
        "input_interpretation_accuracy": build_metric_entry(
            numerator=sum(1 for report in normalized_cases if report["checks"].get("normalized_input") is True),
            denominator=len(normalized_cases),
            definition="Cases with expected normalized_input where the runtime interpretation matched exactly.",
            scope="cases_with_expected_normalized_input",
        ),
        "article_matching_accuracy": build_metric_entry(
            numerator=sum(1 for report in article_cases if report["checks"].get("article_number") is True),
            denominator=len(article_cases),
            definition="Cases with expected article_number where the runtime matched the expected article.",
            scope="cases_with_expected_article_number",
        ),
        "effective_output_rate_all_queries": build_metric_entry(
            numerator=sum(1 for report in case_reports if report["actual"].get("supported") is True),
            denominator=len(case_reports),
            definition="Queries that returned a substantive structured result.",
            scope="all_queries",
        ),
        "effective_output_rate_supported_scope_queries": build_metric_entry(
            numerator=sum(1 for report in supported_scope_cases if report["actual"].get("supported") is True),
            denominator=len(supported_scope_cases),
            definition="Queries expected to be supportable that returned a substantive structured result.",
            scope="supported_scope_queries",
        ),
        "conservative_refusal_rate_all_queries": build_metric_entry(
            numerator=len(refused_cases),
            denominator=len(case_reports),
            definition="Queries that ended in a conservative refusal state.",
            scope="all_queries",
        ),
        "conservative_refusal_rate_supported_scope_queries": build_metric_entry(
            numerator=len(supported_scope_refusals),
            denominator=len(supported_scope_cases),
            definition="Queries expected to be supportable that still ended in a refusal state.",
            scope="supported_scope_queries",
        ),
        "false_positive_refusal_rate": build_metric_entry(
            numerator=len(false_positive_refusals),
            denominator=len(refused_cases),
            definition="Refusal cases where the expected result said a structured supported result should have been possible.",
            scope="refused_queries",
        ),
        "critical_overreach_rate": build_metric_entry(
            numerator=suite_report["critical_overreach_count"],
            denominator=len(case_reports),
            definition="Critical overreach cases divided by all evaluated queries.",
            scope="all_queries",
        ),
        "major_overreach_rate": build_metric_entry(
            numerator=suite_report["major_overreach_count"],
            denominator=len(case_reports),
            definition="Major overreach cases divided by all evaluated queries.",
            scope="all_queries",
        ),
        "minor_overreach_rate": build_metric_entry(
            numerator=suite_report["minor_overreach_count"],
            denominator=len(case_reports),
            definition="Minor overreach cases divided by all evaluated queries.",
            scope="all_queries",
        ),
    }


def build_metric_entry(
    *,
    numerator: int,
    denominator: int,
    definition: str,
    scope: str,
) -> dict:
    return {
        "numerator": numerator,
        "denominator": denominator,
        "value": None if denominator == 0 else round(numerator / denominator, 4),
        "definition": definition,
        "scope": scope,
        "sample_note": "Team-authored fixed Stage 1 suite; expected outputs are human-written and replayable.",
        "bias_note": (
            "Coverage is intentionally narrow, China-Netherlands-only, and still reflects project-team "
            "scenario selection rather than external independent sampling."
        ),
        "known_limitations": [
            "Current values are computed only from the fixed Stage 1 case suite.",
            "These metrics should be read together with coverage composition and overreach counts.",
        ],
    }


def build_hard_commitment_mapping(cases: list[dict]) -> dict:
    mapping: dict[str, list[str]] = {}
    for case in cases:
        for commitment in case.get("hard_commitments", []):
            mapping.setdefault(commitment, []).append(case["id"])
    return dict(sorted(mapping.items()))


def render_markdown_summary(report: dict, *, case_path: Path, report_path: Path) -> str:
    lines = [
        "# Stage 1 Evaluation Summary",
        "",
        f"Case file: `{case_path.as_posix()}`",
        f"Report file: `{report_path.as_posix()}`",
        "",
        "## Scope",
        "",
        report["suite_scope_note"],
        "",
        "## Headline Counts",
        "",
        f"- total cases: `{report['total_cases']}`",
        f"- passed cases: `{report['passed_cases']}`",
        f"- failed cases: `{report['failed_cases']}`",
        f"- critical overreach count: `{report['critical_overreach_count']}`",
        f"- major overreach count: `{report['major_overreach_count']}`",
        f"- minor overreach count: `{report['minor_overreach_count']}`",
        "",
        "## Category Summary",
        "",
    ]

    for category, bucket in report["category_summary"].items():
        lines.append(f"- `{category}`: `{bucket['passed']} / {bucket['total']}` passed")

    lines.extend(["", "## Metrics", ""])
    for metric_name, metric in report["metrics"].items():
        lines.append(f"### `{metric_name}`")
        lines.append("")
        lines.append(f"- definition: {metric['definition']}")
        lines.append(f"- scope: `{metric['scope']}`")
        lines.append(f"- value: `{metric['numerator']} / {metric['denominator']}` (`{metric['value']}`)")
        lines.append(f"- sample note: {metric['sample_note']}")
        lines.append(f"- bias note: {metric['bias_note']}")
        lines.append("- known limitations:")
        for item in metric.get("known_limitations", []):
            lines.append(f"  - {item}")
        lines.append("")

    lines.extend(["## Hard Commitment Mapping", ""])
    for commitment, case_ids in report.get("hard_commitment_mapping", {}).items():
        lines.append(f"- `{commitment}`: {', '.join(f'`{case_id}`' for case_id in case_ids)}")

    lines.extend(["## Known Limitations", ""])
    for item in report.get("known_limitations", []):
        lines.append(f"- {item}")

    return "\n".join(lines).strip() + "\n"


def evaluate_case(case: dict, analyzer: Analyzer) -> dict:
    actual = analyzer(case)
    expected = case["expected"]
    checks: dict[str, bool] = {}

    checks["supported"] = actual.get("supported") == expected.get("supported")

    if "reason" in expected:
        checks["reason"] = actual.get("reason") == expected["reason"]

    if "normalized_input" in expected:
        checks["normalized_input"] = actual.get("normalized_input") == expected["normalized_input"]

    result_payload = actual.get("result", {})

    if "article_number" in expected:
        checks["article_number"] = result_payload.get("article_number") == expected["article_number"]

    if "rate" in expected:
        checks["rate"] = result_payload.get("rate") == expected["rate"]

    if "review_priority" in expected:
        checks["review_priority"] = result_payload.get("review_priority") == expected["review_priority"]

    if "auto_conclusion_allowed" in expected:
        checks["auto_conclusion_allowed"] = (
            result_payload.get("auto_conclusion_allowed") == expected["auto_conclusion_allowed"]
        )

    if expected.get("must_have_next_action"):
        immediate_action = actual.get("immediate_action") or result_payload.get("immediate_action")
        checks["next_action"] = bool(immediate_action)
    if expected.get("must_have_source_reference"):
        checks["source_reference"] = bool(result_payload.get("source_reference"))
    if expected.get("must_have_conditions"):
        checks["conditions"] = bool(result_payload.get("conditions"))

    passed = all(checks.values()) if checks else True
    major_overreach = bool(expected.get("supported") is False and actual.get("supported") is True)
    critical_overreach = bool(
        expected.get("supported") is True
        and "rate" in expected
        and actual.get("supported") is True
        and result_payload.get("rate") != expected["rate"]
        and result_payload.get("auto_conclusion_allowed", True) is True
    )
    minor_overreach = bool(
        expected.get("supported") is True
        and actual.get("supported") is True
        and not critical_overreach
        and (
            checks.get("review_priority") is False
            or checks.get("auto_conclusion_allowed") is False
        )
    )

    return {
        "id": case["id"],
        "category": case["category"],
        "passed": passed,
        "checks": checks,
        "actual": actual,
        "major_overreach": major_overreach,
        "critical_overreach": critical_overreach,
        "minor_overreach": minor_overreach,
    }


def evaluate_suite(cases: list[dict], analyzer: Analyzer) -> dict:
    case_reports = [evaluate_case(case, analyzer=analyzer) for case in cases]
    category_summary: dict[str, dict[str, int]] = {}

    for report in case_reports:
        bucket = category_summary.setdefault(report["category"], {"total": 0, "passed": 0})
        bucket["total"] += 1
        bucket["passed"] += int(report["passed"])

    return {
        "total_cases": len(case_reports),
        "passed_cases": sum(1 for report in case_reports if report["passed"]),
        "failed_cases": sum(1 for report in case_reports if not report["passed"]),
        "critical_overreach_count": sum(1 for report in case_reports if report["critical_overreach"]),
        "major_overreach_count": sum(1 for report in case_reports if report["major_overreach"]),
        "minor_overreach_count": sum(1 for report in case_reports if report["minor_overreach"]),
        "category_summary": category_summary,
        "case_reports": case_reports,
    }


def run_case_through_service(case: dict) -> dict:
    data_source = case.get("data_source", "stable")
    overrides = case.get("service_overrides", {})
    stable_data_path = resolve_override_path(overrides.get("stable_data_path"))
    llm_generated_data_path = resolve_override_path(overrides.get("llm_generated_data_path"))

    with disable_live_llm(), override_service_paths(
        stable_data_path=stable_data_path,
        llm_generated_data_path=llm_generated_data_path,
    ):
        return service.analyze_scenario(case["scenario"], data_source=data_source)


@contextmanager
def disable_live_llm():
    previous = os.getenv("PYTEST_CURRENT_TEST")
    os.environ["PYTEST_CURRENT_TEST"] = "stage1_eval"
    try:
        yield
    finally:
        if previous is None:
            os.environ.pop("PYTEST_CURRENT_TEST", None)
        else:
            os.environ["PYTEST_CURRENT_TEST"] = previous


@contextmanager
def override_service_paths(
    *,
    stable_data_path: str | None = None,
    llm_generated_data_path: str | None = None,
):
    original_stable = service.DATA_PATH
    original_llm = service.LLM_GENERATED_DATA_PATH

    if stable_data_path:
        service.DATA_PATH = Path(stable_data_path)
    if llm_generated_data_path:
        service.LLM_GENERATED_DATA_PATH = Path(llm_generated_data_path)

    try:
        yield
    finally:
        service.DATA_PATH = original_stable
        service.LLM_GENERATED_DATA_PATH = original_llm


def resolve_override_path(raw_path: str | None) -> str | None:
    if not raw_path:
        return None
    candidate = Path(raw_path)
    if candidate.is_absolute():
        return str(candidate)
    return str(REPO_ROOT / candidate)


def _expected_for_case(cases: list[dict], case_id: str) -> dict:
    for case in cases:
        if case["id"] == case_id:
            return case["expected"]
    raise KeyError(f"Case id not found in suite: {case_id}")
