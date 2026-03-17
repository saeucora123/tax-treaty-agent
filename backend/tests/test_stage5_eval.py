from __future__ import annotations

import json
from pathlib import Path

from app import stage5_eval


def test_evaluate_case_passes_for_supported_handoff_case():
    case = {
        "id": "stage5-supported-001",
        "category": "supported_clear",
        "scenario": "中国居民企业向荷兰支付特许权使用费",
        "expected": {
            "supported": True,
            "review_state_code": "pre_review_complete",
            "recommended_route": "standard_review",
            "record_kind": "supported",
            "article_number": "12",
            "rate_display": "10%",
            "human_disposition": "Proceed with standard human review.",
            "user_declared_facts_present": False,
        },
    }

    actual = {
        "supported": True,
        "review_state": {"state_code": "pre_review_complete"},
        "handoff_package": {
            "machine_handoff": {
                "review_state_code": "pre_review_complete",
                "recommended_route": "standard_review",
                "record_kind": "supported",
                "article_number": "12",
                "rate_display": "10%",
                "user_declared_facts": [],
            },
            "human_review_brief": {
                "disposition": "Proceed with standard human review.",
            },
        },
    }

    report = stage5_eval.evaluate_case(case, analyzer=lambda payload: actual)

    assert report["passed"] is True
    assert report["checks"]["handoff_present"] is True
    assert report["checks"]["recommended_route"] is True
    assert report["checks"]["record_kind"] is True


def test_evaluate_case_passes_for_null_article_fields_case():
    case = {
        "id": "stage5-unsupported-001",
        "category": "unsupported",
        "scenario": "中国居民企业向美国支付特许权使用费",
        "expected": {
            "supported": False,
            "review_state_code": "out_of_scope",
            "recommended_route": "out_of_scope_rewrite",
            "record_kind": "unsupported",
            "article_number": None,
            "rate_display": None,
            "human_disposition": "Rewrite the scenario inside the supported pilot scope.",
            "user_declared_facts_present": False,
        },
    }

    actual = {
        "supported": False,
        "review_state": {"state_code": "out_of_scope"},
        "handoff_package": {
            "machine_handoff": {
                "review_state_code": "out_of_scope",
                "recommended_route": "out_of_scope_rewrite",
                "record_kind": "unsupported",
                "article_number": None,
                "rate_display": None,
                "user_declared_facts": [],
            },
            "human_review_brief": {
                "disposition": "Rewrite the scenario inside the supported pilot scope.",
            },
        },
    }

    report = stage5_eval.evaluate_case(case, analyzer=lambda payload: actual)

    assert report["passed"] is True
    assert report["checks"]["article_number"] is True
    assert report["checks"]["rate_display"] is True


def test_run_stage5_evaluation_writes_report_file(tmp_path: Path):
    case_file = tmp_path / "stage5-cases.json"
    report_file = tmp_path / "stage5-report.json"
    case_file.write_text(
        json.dumps(
            [
                {
                    "id": "stage5-stage4-001",
                    "category": "stage4_bounded",
                    "scenario": "中国公司向荷兰公司支付股息",
                    "input_mode": "guided",
                    "guided_input": {
                        "payer_country": "CN",
                        "payee_country": "NL",
                        "income_type": "dividends",
                        "facts": {
                            "direct_holding_confirmed": "yes",
                            "direct_holding_threshold_met": "yes",
                            "beneficial_owner_confirmed": "yes",
                            "holding_structure_is_direct": "yes",
                        },
                    },
                    "expected": {
                        "supported": True,
                        "review_state_code": "pre_review_complete",
                        "recommended_route": "standard_review",
                        "record_kind": "supported",
                        "article_number": "10",
                        "rate_display": "5%",
                        "human_disposition": "Proceed with standard human review.",
                        "user_declared_facts_present": True,
                    },
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
            "review_state": {"state_code": "pre_review_complete"},
            "handoff_package": {
                "machine_handoff": {
                    "review_state_code": "pre_review_complete",
                    "recommended_route": "standard_review",
                    "record_kind": "supported",
                    "article_number": "10",
                    "rate_display": "5%",
                    "user_declared_facts": [{"fact_key": "direct_holding_confirmed"}],
                },
                "human_review_brief": {
                    "disposition": "Proceed with standard human review.",
                },
            },
        }

    report = stage5_eval.run_stage5_evaluation(
        case_file,
        output_path=report_file,
        analyzer=fake_analyzer,
    )

    assert report["total_cases"] == 1
    assert report["passed_cases"] == 1
    assert report["metrics"]["handoff_coverage"]["numerator"] == 1
    assert report["metrics"]["user_declared_fact_preservation"]["numerator"] == 1
    assert report_file.exists() is True
