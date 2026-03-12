from __future__ import annotations

import json
from pathlib import Path

from app import stage1_eval


def test_evaluate_case_passes_when_supported_expectations_match():
    case = {
        "id": "happy-royalties-001",
        "category": "happy_path",
        "scenario": "中国居民企业向荷兰支付特许权使用费",
        "expected": {
            "supported": True,
            "normalized_input": {
                "payer_country": "CN",
                "payee_country": "NL",
                "transaction_type": "royalties",
            },
            "article_number": "12",
            "rate": "10%",
        },
    }

    actual = {
        "supported": True,
        "normalized_input": {
            "payer_country": "CN",
            "payee_country": "NL",
            "transaction_type": "royalties",
        },
        "result": {
            "article_number": "12",
            "rate": "10%",
            "review_priority": "normal",
            "auto_conclusion_allowed": True,
            "immediate_action": "Proceed with standard manual review before relying on the treaty position.",
        },
    }

    report = stage1_eval.evaluate_case(case, analyzer=lambda payload: actual)

    assert report["passed"] is True
    assert report["major_overreach"] is False
    assert report["critical_overreach"] is False
    assert report["checks"]["supported"] is True
    assert report["checks"]["normalized_input"] is True
    assert report["checks"]["article_number"] is True
    assert report["checks"]["rate"] is True


def test_evaluate_case_checks_review_priority_and_auto_conclusion_when_expected():
    case = {
        "id": "multi-branch-001",
        "category": "multi_branch",
        "scenario": "中国公司向荷兰公司支付股息",
        "expected": {
            "supported": True,
            "article_number": "10",
            "rate": "5% / 10%",
            "review_priority": "high",
            "auto_conclusion_allowed": False,
            "must_have_next_action": True,
        },
    }

    actual = {
        "supported": True,
        "result": {
            "article_number": "10",
            "rate": "5% / 10%",
            "review_priority": "high",
            "auto_conclusion_allowed": False,
            "immediate_action": "Do not rely on this result yet.",
        },
    }

    report = stage1_eval.evaluate_case(case, analyzer=lambda payload: actual)

    assert report["passed"] is True
    assert report["checks"]["review_priority"] is True
    assert report["checks"]["auto_conclusion_allowed"] is True
    assert report["checks"]["next_action"] is True


def test_evaluate_case_can_require_source_reference_and_conditions():
    case = {
        "id": "hc4-001",
        "category": "happy_path",
        "scenario": "中国居民企业向荷兰支付特许权使用费",
        "expected": {
            "supported": True,
            "article_number": "12",
            "rate": "10%",
            "must_have_source_reference": True,
            "must_have_conditions": True,
        },
    }

    actual = {
        "supported": True,
        "result": {
            "article_number": "12",
            "rate": "10%",
            "source_reference": "Article 12(1)",
            "conditions": ["Treaty applicability depends on the facts of the payment."],
            "immediate_action": "Proceed with standard manual review before relying on the treaty position.",
        },
    }

    report = stage1_eval.evaluate_case(case, analyzer=lambda payload: actual)

    assert report["passed"] is True
    assert report["checks"]["source_reference"] is True
    assert report["checks"]["conditions"] is True


def test_evaluate_case_flags_major_overreach_when_unsupported_case_returns_substantive_result():
    case = {
        "id": "out-of-scope-country-001",
        "category": "out_of_scope",
        "scenario": "中国居民企业向美国支付特许权使用费",
        "expected": {
            "supported": False,
            "reason": "unsupported_country_pair",
        },
    }

    actual = {
        "supported": True,
        "normalized_input": {
            "payer_country": "CN",
            "payee_country": "US",
            "transaction_type": "royalties",
        },
        "result": {
            "article_number": "12",
            "rate": "10%",
            "immediate_action": "Proceed with standard manual review before relying on the treaty position.",
        },
    }

    report = stage1_eval.evaluate_case(case, analyzer=lambda payload: actual)

    assert report["passed"] is False
    assert report["major_overreach"] is True
    assert report["critical_overreach"] is False


def test_evaluate_suite_counts_categories_and_overreach():
    cases = [
        {
            "id": "happy-001",
            "category": "happy_path",
            "scenario": "中国居民企业向荷兰支付特许权使用费",
            "expected": {"supported": True, "article_number": "12"},
        },
        {
            "id": "out-of-scope-001",
            "category": "out_of_scope",
            "scenario": "中国居民企业向美国支付特许权使用费",
            "expected": {"supported": False, "reason": "unsupported_country_pair"},
        },
    ]

    def fake_analyzer(case: dict) -> dict:
        if case["id"] == "happy-001":
            return {
                "supported": True,
                "result": {"article_number": "12", "rate": "10%", "immediate_action": "review"},
            }
        return {
            "supported": True,
            "result": {"article_number": "12", "rate": "10%", "immediate_action": "review"},
        }

    report = stage1_eval.evaluate_suite(cases, analyzer=fake_analyzer)

    assert report["total_cases"] == 2
    assert report["passed_cases"] == 1
    assert report["failed_cases"] == 1
    assert report["major_overreach_count"] == 1
    assert report["critical_overreach_count"] == 0
    assert report["category_summary"]["happy_path"] == {"total": 1, "passed": 1}
    assert report["category_summary"]["out_of_scope"] == {"total": 1, "passed": 0}


def test_run_case_through_service_disables_live_llm_and_restores_paths(monkeypatch, tmp_path: Path):
    captured: dict[str, object] = {}
    stable_original = stage1_eval.service.DATA_PATH
    llm_original = stage1_eval.service.LLM_GENERATED_DATA_PATH

    custom_stable = tmp_path / "custom-stable.json"
    custom_stable.write_text("{}", encoding="utf-8")

    def fake_analyze(scenario: str, data_source: str = "stable") -> dict:
        captured["scenario"] = scenario
        captured["data_source"] = data_source
        captured["disable_env"] = stage1_eval.os.getenv("PYTEST_CURRENT_TEST")
        captured["stable_path"] = stage1_eval.service.DATA_PATH
        captured["llm_path"] = stage1_eval.service.LLM_GENERATED_DATA_PATH
        return {"supported": False, "reason": "unsupported_country_pair"}

    monkeypatch.setattr(stage1_eval.service, "analyze_scenario", fake_analyze)

    result = stage1_eval.run_case_through_service(
        {
            "scenario": "中国居民企业向美国支付特许权使用费",
            "data_source": "stable",
            "service_overrides": {
                "stable_data_path": str(custom_stable),
            },
        }
    )

    assert result == {"supported": False, "reason": "unsupported_country_pair"}
    assert captured["disable_env"] == "stage1_eval"
    assert captured["stable_path"] == custom_stable
    assert captured["llm_path"] == llm_original
    assert stage1_eval.service.DATA_PATH == stable_original
    assert stage1_eval.service.LLM_GENERATED_DATA_PATH == llm_original


def test_run_case_through_service_resolves_repo_relative_override_paths(monkeypatch):
    captured: dict[str, object] = {}

    def fake_analyze(scenario: str, data_source: str = "stable") -> dict:
        captured["stable_path"] = stage1_eval.service.DATA_PATH
        return {"supported": False, "reason": "unsupported_country_pair"}

    monkeypatch.setattr(stage1_eval.service, "analyze_scenario", fake_analyze)

    stage1_eval.run_case_through_service(
        {
            "scenario": "中国居民企业向美国支付特许权使用费",
            "service_overrides": {
                "stable_data_path": "data/treaties/cn-nl.v3.json",
            },
        }
    )

    assert captured["stable_path"] == stage1_eval.REPO_ROOT / "data" / "treaties" / "cn-nl.v3.json"


def test_run_stage1_evaluation_writes_report_file(tmp_path: Path):
    case_file = tmp_path / "cases.json"
    report_file = tmp_path / "report.json"
    case_file.write_text(
        json.dumps(
            [
                {
                    "id": "happy-001",
                    "category": "happy_path",
                    "scenario": "中国居民企业向荷兰支付特许权使用费",
                    "expected": {"supported": True, "article_number": "12"},
                }
            ],
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )

    def fake_analyzer(case: dict) -> dict:
        return {
            "supported": True,
            "result": {
                "article_number": "12",
                "rate": "10%",
                "immediate_action": "Proceed with standard manual review before relying on the treaty position.",
            },
        }

    report = stage1_eval.run_stage1_evaluation(
        case_file,
        output_path=report_file,
        analyzer=fake_analyzer,
    )

    assert report["total_cases"] == 1
    assert report["suite_scope_note"].startswith("This Stage 1 evaluation")
    assert "known_limitations" in report
    assert report["metrics"]["effective_output_rate_all_queries"]["known_limitations"]
    assert report_file.exists() is True
    assert json.loads(report_file.read_text(encoding="utf-8"))["passed_cases"] == 1


def test_build_metric_summary_reports_core_stage1_counts():
    cases = [
        {
            "id": "happy-001",
            "category": "happy_path",
            "scenario": "中国居民企业向荷兰支付特许权使用费",
            "expected": {
                "supported": True,
                "normalized_input": {
                    "payer_country": "CN",
                    "payee_country": "NL",
                    "transaction_type": "royalties",
                },
                "article_number": "12",
            },
        },
        {
            "id": "out-of-scope-001",
            "category": "out_of_scope",
            "scenario": "中国居民企业向美国支付特许权使用费",
            "expected": {
                "supported": False,
                "reason": "unsupported_country_pair",
            },
        },
    ]

    def fake_analyzer(case: dict) -> dict:
        if case["id"] == "happy-001":
            return {
                "supported": True,
                "normalized_input": {
                    "payer_country": "CN",
                    "payee_country": "NL",
                    "transaction_type": "royalties",
                },
                "result": {
                    "article_number": "12",
                    "rate": "10%",
                    "immediate_action": "Proceed with standard manual review before relying on the treaty position.",
                },
            }
        return {
            "supported": False,
            "reason": "unsupported_country_pair",
            "immediate_action": "Rewrite the scenario into the supported China-Netherlands scope before running another review.",
        }

    suite_report = stage1_eval.evaluate_suite(cases, analyzer=fake_analyzer)
    metrics = stage1_eval.build_metric_summary(cases, suite_report)

    assert metrics["input_interpretation_accuracy"]["numerator"] == 1
    assert metrics["input_interpretation_accuracy"]["denominator"] == 1
    assert metrics["article_matching_accuracy"]["numerator"] == 1
    assert metrics["article_matching_accuracy"]["denominator"] == 1
    assert metrics["effective_output_rate_all_queries"]["numerator"] == 1
    assert metrics["effective_output_rate_all_queries"]["denominator"] == 2
    assert metrics["conservative_refusal_rate_all_queries"]["numerator"] == 1
    assert metrics["conservative_refusal_rate_all_queries"]["denominator"] == 2
    assert metrics["false_positive_refusal_rate"]["numerator"] == 0
    assert metrics["false_positive_refusal_rate"]["denominator"] == 1


def test_build_metric_summary_includes_scope_bias_notes_and_split_denominators():
    cases = [
        {
            "id": "happy-001",
            "category": "happy_path",
            "scenario": "中国居民企业向荷兰支付特许权使用费",
            "expected": {
                "supported": True,
                "normalized_input": {
                    "payer_country": "CN",
                    "payee_country": "NL",
                    "transaction_type": "royalties",
                },
                "article_number": "12",
            },
        },
        {
            "id": "out-of-scope-001",
            "category": "out_of_scope",
            "scenario": "中国居民企业向美国支付特许权使用费",
            "expected": {
                "supported": False,
                "reason": "unsupported_country_pair",
            },
        },
        {
            "id": "incomplete-001",
            "category": "incomplete",
            "scenario": "向荷兰公司支付股息",
            "expected": {
                "supported": False,
                "reason": "incomplete_scenario",
            },
        },
    ]

    def fake_analyzer(case: dict) -> dict:
        if case["id"] == "happy-001":
            return {
                "supported": True,
                "normalized_input": {
                    "payer_country": "CN",
                    "payee_country": "NL",
                    "transaction_type": "royalties",
                },
                "result": {
                    "article_number": "12",
                    "rate": "10%",
                    "immediate_action": "Proceed with standard manual review before relying on the treaty position.",
                },
            }
        return {
            "supported": False,
            "reason": case["expected"]["reason"],
            "immediate_action": "Add the missing scenario facts before running the treaty review again.",
        }

    suite_report = stage1_eval.evaluate_suite(cases, analyzer=fake_analyzer)
    metrics = stage1_eval.build_metric_summary(cases, suite_report)

    assert metrics["effective_output_rate_all_queries"]["scope"] == "all_queries"
    assert metrics["effective_output_rate_supported_scope_queries"]["scope"] == "supported_scope_queries"
    assert metrics["effective_output_rate_supported_scope_queries"]["numerator"] == 1
    assert metrics["effective_output_rate_supported_scope_queries"]["denominator"] == 1
    assert metrics["conservative_refusal_rate_supported_scope_queries"]["numerator"] == 0
    assert metrics["conservative_refusal_rate_supported_scope_queries"]["denominator"] == 1
    assert "bias_note" in metrics["input_interpretation_accuracy"]
    assert "sample_note" in metrics["input_interpretation_accuracy"]
    assert metrics["minor_overreach_rate"]["numerator"] == 0
    assert metrics["minor_overreach_rate"]["denominator"] == 3


def test_evaluate_case_flags_minor_overreach_when_confidence_language_is_weaker_than_expected():
    case = {
        "id": "minor-overreach-001",
        "category": "happy_path",
        "scenario": "中国居民企业向荷兰支付特许权使用费",
        "expected": {
            "supported": True,
            "article_number": "12",
            "rate": "10%",
            "review_priority": "normal",
            "auto_conclusion_allowed": True,
        },
    }

    actual = {
        "supported": True,
        "result": {
            "article_number": "12",
            "rate": "10%",
            "review_priority": "high",
            "auto_conclusion_allowed": False,
            "immediate_action": "Do not rely on this result yet.",
        },
    }

    report = stage1_eval.evaluate_case(case, analyzer=lambda payload: actual)

    assert report["passed"] is False
    assert report["critical_overreach"] is False
    assert report["major_overreach"] is False
    assert report["minor_overreach"] is True


def test_render_markdown_summary_includes_scope_metrics_and_limitations():
    report = {
        "total_cases": 8,
        "passed_cases": 8,
        "failed_cases": 0,
        "critical_overreach_count": 0,
        "major_overreach_count": 0,
        "minor_overreach_count": 0,
        "category_summary": {
            "happy_path": {"total": 2, "passed": 2},
            "out_of_scope": {"total": 2, "passed": 2},
        },
        "metrics": {
            "effective_output_rate_all_queries": {
                "numerator": 5,
                "denominator": 8,
                "value": 0.625,
                "definition": "Queries that returned a substantive structured result.",
                "scope": "all_queries",
                "sample_note": "Team-authored initial fixed suite.",
                "bias_note": "Coverage is still narrow.",
                "known_limitations": [
                    "Current values are computed only from the fixed Stage 1 case suite."
                ],
            },
            "critical_overreach_rate": {
                "numerator": 0,
                "denominator": 8,
                "value": 0.0,
                "definition": "Critical overreach cases divided by all evaluated queries.",
                "scope": "all_queries",
                "sample_note": "Team-authored initial fixed suite.",
                "bias_note": "Coverage is still narrow.",
                "known_limitations": [
                    "Current values are computed only from the fixed Stage 1 case suite."
                ],
            },
        },
        "suite_scope_note": "This Stage 1 evaluation is deterministic.",
        "known_limitations": [
            "This is an initial fixed suite, not the full memo minimum case count."
        ],
    }

    markdown = stage1_eval.render_markdown_summary(
        report,
        case_path=Path("data/evals/stage1/stage-1-initial-cases.json"),
        report_path=Path("docs/superpowers/research/stage-1-evidence/2026-03-12-stage-1-initial-report.json"),
    )

    assert "# Stage 1 Evaluation Summary" in markdown
    assert "This Stage 1 evaluation is deterministic." in markdown
    assert "`5 / 8` (`0.625`)" in markdown
    assert "`0 / 8` (`0.0`)" in markdown
    assert "scope: `all_queries`" in markdown
    assert "sample note: Team-authored initial fixed suite." in markdown
    assert "bias note: Coverage is still narrow." in markdown
    assert "Current values are computed only from the fixed Stage 1 case suite." in markdown
    assert "data/evals/stage1/stage-1-initial-cases.json" in markdown
