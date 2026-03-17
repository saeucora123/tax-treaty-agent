from __future__ import annotations

import json
from pathlib import Path

from app import stage4_eval


def test_evaluate_case_passes_for_awaiting_facts_stage4_case():
    case = {
        "id": "stage4-awaiting-001",
        "category": "multi_branch_dividend",
        "scenario": "中国公司向荷兰公司支付股息",
        "expected": {
            "supported": True,
            "review_state_code": "can_be_completed",
            "rate": "5% / 10%",
            "fact_completion_status_code": "awaiting_user_facts",
            "fact_completion_present": True,
            "change_summary_present": False,
            "user_declared_facts_present": False,
        },
    }

    actual = {
        "supported": True,
        "review_state": {"state_code": "can_be_completed"},
        "fact_completion_status": {"status_code": "awaiting_user_facts"},
        "fact_completion": {"flow_type": "bounded_form"},
        "change_summary": None,
        "user_declared_facts": None,
        "result": {"rate": "5% / 10%"},
    }

    report = stage4_eval.evaluate_case(case, analyzer=lambda payload: actual)

    assert report["passed"] is True
    assert report["checks"]["review_state_code"] is True
    assert report["checks"]["fact_completion_status_code"] is True
    assert report["checks"]["fact_completion_present"] is True


def test_evaluate_case_passes_for_terminated_stage4_case():
    case = {
        "id": "stage4-terminated-001",
        "category": "multi_branch_dividend",
        "scenario": "中国公司向荷兰公司支付股息",
        "input_mode": "guided",
        "guided_input": {
            "payer_country": "CN",
            "payee_country": "NL",
            "income_type": "dividends",
            "facts": {
                "direct_holding_confirmed": "yes",
                "direct_holding_threshold_met": "unknown",
                "holding_structure_is_direct": "yes",
            },
        },
        "expected": {
            "supported": True,
            "review_state_code": "needs_human_intervention",
            "rate": "5% / 10%",
            "fact_completion_status_code": "terminated_unknown_facts",
            "fact_completion_present": False,
            "change_summary_present": True,
            "user_declared_facts_present": True,
        },
    }

    actual = {
        "supported": True,
        "review_state": {"state_code": "needs_human_intervention"},
        "fact_completion_status": {"status_code": "terminated_unknown_facts"},
        "fact_completion": None,
        "change_summary": {"summary_label": "Result Change Summary"},
        "user_declared_facts": {"declaration_label": "User-declared facts (unverified)"},
        "result": {"rate": "5% / 10%"},
    }

    report = stage4_eval.evaluate_case(case, analyzer=lambda payload: actual)

    assert report["passed"] is True
    assert report["checks"]["change_summary_present"] is True
    assert report["checks"]["user_declared_facts_present"] is True


def test_evaluate_suite_tracks_multiple_termination_codes():
    cases = [
        {
            "id": "stage4-terminated-001",
            "category": "multi_branch_dividend",
            "scenario": "中国公司向荷兰公司支付股息",
            "expected": {
                "supported": True,
                "review_state_code": "needs_human_intervention",
                "rate": "5% / 10%",
                "fact_completion_status_code": "terminated_unknown_facts",
                "fact_completion_present": False,
                "change_summary_present": True,
                "user_declared_facts_present": True,
            },
        },
        {
            "id": "stage4-terminated-002",
            "category": "multi_branch_dividend",
            "scenario": "中国公司向荷兰公司支付股息",
            "expected": {
                "supported": True,
                "review_state_code": "needs_human_intervention",
                "rate": "5% / 10%",
                "fact_completion_status_code": "terminated_pe_exclusion",
                "fact_completion_present": False,
                "change_summary_present": True,
                "user_declared_facts_present": True,
            },
        },
        {
            "id": "stage4-terminated-003",
            "category": "multi_branch_dividend",
            "scenario": "中国公司向荷兰公司支付股息",
            "expected": {
                "supported": True,
                "review_state_code": "needs_human_intervention",
                "rate": "5% / 10%",
                "fact_completion_status_code": "terminated_beneficial_owner_unconfirmed",
                "fact_completion_present": False,
                "change_summary_present": True,
                "user_declared_facts_present": True,
            },
        },
        {
            "id": "stage4-terminated-004",
            "category": "multi_branch_dividend",
            "scenario": "中国公司向荷兰公司支付股息",
            "expected": {
                "supported": True,
                "review_state_code": "needs_human_intervention",
                "rate": "5% / 10%",
                "fact_completion_status_code": "terminated_conflicting_user_facts",
                "fact_completion_present": False,
                "change_summary_present": True,
                "user_declared_facts_present": True,
            },
        },
    ]

    actual_map = {
        "stage4-terminated-001": {
            "supported": True,
            "review_state": {"state_code": "needs_human_intervention"},
            "fact_completion_status": {"status_code": "terminated_unknown_facts"},
            "fact_completion": None,
            "change_summary": {"summary_label": "Result Change Summary"},
            "user_declared_facts": {"declaration_label": "User-declared facts (unverified)"},
            "result": {"rate": "5% / 10%"},
        },
        "stage4-terminated-002": {
            "supported": True,
            "review_state": {"state_code": "needs_human_intervention"},
            "fact_completion_status": {"status_code": "terminated_pe_exclusion"},
            "fact_completion": None,
            "change_summary": {"summary_label": "Result Change Summary"},
            "user_declared_facts": {"declaration_label": "User-declared facts (unverified)"},
            "result": {"rate": "5% / 10%"},
        },
        "stage4-terminated-003": {
            "supported": True,
            "review_state": {"state_code": "needs_human_intervention"},
            "fact_completion_status": {
                "status_code": "terminated_beneficial_owner_unconfirmed"
            },
            "fact_completion": None,
            "change_summary": {"summary_label": "Result Change Summary"},
            "user_declared_facts": {"declaration_label": "User-declared facts (unverified)"},
            "result": {"rate": "5% / 10%"},
        },
        "stage4-terminated-004": {
            "supported": True,
            "review_state": {"state_code": "needs_human_intervention"},
            "fact_completion_status": {
                "status_code": "terminated_conflicting_user_facts"
            },
            "fact_completion": None,
            "change_summary": {"summary_label": "Result Change Summary"},
            "user_declared_facts": {"declaration_label": "User-declared facts (unverified)"},
            "result": {"rate": "5% / 10%"},
        },
    }

    report = stage4_eval.evaluate_suite(
        cases,
        analyzer=lambda case: actual_map[case["id"]],
    )

    assert report["failed_cases"] == 0
    assert report["termination_summary"] == {
        "terminated_unknown_facts": 1,
        "terminated_pe_exclusion": 1,
        "terminated_beneficial_owner_unconfirmed": 1,
        "terminated_conflicting_user_facts": 1,
    }


def test_run_stage4_evaluation_writes_report_file(tmp_path: Path):
    case_file = tmp_path / "stage4-cases.json"
    report_file = tmp_path / "stage4-report.json"
    case_file.write_text(
        json.dumps(
            [
                {
                    "id": "stage4-awaiting-001",
                    "category": "multi_branch_dividend",
                    "scenario": "中国公司向荷兰公司支付股息",
                    "expected": {
                        "supported": True,
                        "review_state_code": "can_be_completed",
                        "rate": "5% / 10%",
                        "fact_completion_status_code": "awaiting_user_facts",
                        "fact_completion_present": True,
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
            "review_state": {"state_code": "can_be_completed"},
            "fact_completion_status": {"status_code": "awaiting_user_facts"},
            "fact_completion": {"flow_type": "bounded_form"},
            "change_summary": None,
            "user_declared_facts": None,
            "result": {"rate": "5% / 10%"},
        }

    report = stage4_eval.run_stage4_evaluation(
        case_file,
        output_path=report_file,
        analyzer=fake_analyzer,
    )

    assert report["total_cases"] == 1
    assert report["passed_cases"] == 1
    assert report["metrics"]["awaiting_user_facts_cases"]["numerator"] == 1
    assert report_file.exists() is True
