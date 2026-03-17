import json
from pathlib import Path

from fastapi.testclient import TestClient

from app.main import app
from app import service
from tests.support.handoff_assertions import (
    assert_machine_handoff,
    guided_cn_nl_dividend_payload,
)


client = TestClient(app)

def test_dividend_fact_completion_narrows_to_reduced_rate_when_direct_threshold_is_met():
    response = client.post(
        "/analyze",
        json={
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
        },
    )

    assert response.status_code == 200
    assert response.json()["supported"] is True
    assert response.json()["result"]["rate"] == "5%"
    assert response.json()["result"]["summary"] == (
        "Preliminary view: Article 10 Dividends appears relevant, with a treaty rate ceiling of 5%. "
        "Manual review is still recommended."
    )
    assert response.json()["review_state"] == {
        "state_code": "pre_review_complete",
        "state_label_zh": "预审完成",
        "state_summary": "系统已完成第一轮预审，请按标准复核流程继续。",
    }
    assert response.json()["fact_completion_status"] == {
        "status_code": "completed_narrowed",
        "status_label_zh": "已缩减",
        "status_summary": "系统已根据用户声明事实将股息分支缩减为单一候选税率。",
    }
    assert response.json()["change_summary"] == {
        "summary_label": "Result Change Summary",
        "state_change": "可补全 -> 预审完成",
        "rate_change": "5% / 10% -> 5%",
        "trigger_facts": [
            "Direct holding confirmed: yes",
            "Direct holding is at least 25%: yes",
            "Beneficial owner status separately confirmed: yes",
            "Holding structure is direct (no intermediate entity): yes",
        ],
    }
    assert response.json()["user_declared_facts"] == {
        "declaration_label": "User-declared facts (unverified)",
        "facts": [
            {
                "fact_key": "direct_holding_confirmed",
                "value": "yes",
                "label": "Direct holding confirmed",
            },
            {
                "fact_key": "direct_holding_threshold_met",
                "value": "yes",
                "label": "Direct holding is at least 25%",
            },
            {
                "fact_key": "beneficial_owner_confirmed",
                "value": "yes",
                "label": "Beneficial owner status separately confirmed",
            },
            {
                "fact_key": "holding_structure_is_direct",
                "value": "yes",
                "label": "Holding structure is direct (no intermediate entity)",
            },
        ],
    }
    assert response.json()["result"]["key_missing_facts"] == [
        "Whether the payment is legally a dividend rather than another type of return.",
        "Whether the recipient is the beneficial owner of the dividend income.",
        "Whether shareholding facts support relying on the treaty position.",
    ]
    assert response.json()["fact_completion"] is None
    handoff = assert_machine_handoff(
        response.json(),
        record_kind="supported",
        review_state_code="pre_review_complete",
        recommended_route="standard_review",
    )
    assert handoff["machine_handoff"]["user_declared_facts"] == [
        {
            "fact_key": "direct_holding_confirmed",
            "value": "yes",
            "label": "Direct holding confirmed",
        },
        {
            "fact_key": "direct_holding_threshold_met",
            "value": "yes",
            "label": "Direct holding is at least 25%",
        },
        {
            "fact_key": "beneficial_owner_confirmed",
            "value": "yes",
            "label": "Beneficial owner status separately confirmed",
        },
        {
            "fact_key": "holding_structure_is_direct",
            "value": "yes",
            "label": "Holding structure is direct (no intermediate entity)",
        },
    ]

def test_dividend_fact_completion_narrows_to_general_rate_when_direct_threshold_is_not_met():
    response = client.post(
        "/analyze",
        json={
            "input_mode": "guided",
            "guided_input": {
                "payer_country": "CN",
                "payee_country": "NL",
                "income_type": "dividends",
                "facts": {
                    "direct_holding_confirmed": "yes",
                    "direct_holding_threshold_met": "no",
                    "holding_structure_is_direct": "yes",
                },
            },
        },
    )

    assert response.status_code == 200
    assert response.json()["supported"] is True
    assert response.json()["result"]["rate"] == "10%"
    assert response.json()["result"]["summary"] == (
        "Preliminary view: Article 10 Dividends appears relevant, with a treaty rate ceiling of 10%. "
        "Manual review is still recommended."
    )
    assert response.json()["fact_completion_status"] == {
        "status_code": "completed_narrowed",
        "status_label_zh": "已缩减",
        "status_summary": "系统已根据用户声明事实将股息分支缩减为单一候选税率。",
    }
    assert response.json()["change_summary"] == {
        "summary_label": "Result Change Summary",
        "state_change": "可补全 -> 预审完成",
        "rate_change": "5% / 10% -> 10%",
        "trigger_facts": [
            "Direct holding confirmed: yes",
            "Direct holding is at least 25%: no",
            "Holding structure is direct (no intermediate entity): yes",
        ],
    }
    assert response.json()["user_declared_facts"] == {
        "declaration_label": "User-declared facts (unverified)",
        "facts": [
            {
                "fact_key": "direct_holding_confirmed",
                "value": "yes",
                "label": "Direct holding confirmed",
            },
            {
                "fact_key": "direct_holding_threshold_met",
                "value": "no",
                "label": "Direct holding is at least 25%",
            },
            {
                "fact_key": "holding_structure_is_direct",
                "value": "yes",
                "label": "Holding structure is direct (no intermediate entity)",
            },
        ],
    }
    assert response.json()["fact_completion"] is None

def test_dividend_fact_completion_stops_when_key_facts_remain_unknown():
    response = client.post(
        "/analyze",
        json={
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
        },
    )

    assert response.status_code == 200
    assert response.json()["supported"] is True
    assert response.json()["result"]["rate"] == "5% / 10%"
    assert response.json()["review_state"] == {
        "state_code": "needs_human_intervention",
        "state_label_zh": "需要人工介入",
        "state_summary": "当前结果已触发保守停止，应转入人工处理而不是继续自动推进。",
    }
    assert response.json()["fact_completion_status"] == {
        "status_code": "terminated_unknown_facts",
        "status_label_zh": "停止自动缩减",
        "status_summary": "关键事实仍未确认，系统结束当前补事实流程并建议先在线下核实。",
    }
    assert response.json()["change_summary"] == {
        "summary_label": "Result Change Summary",
        "state_change": "可补全 -> 需要人工介入",
        "rate_change": "5% / 10% -> 5% / 10%",
        "trigger_facts": [
            "Direct holding confirmed: yes",
            "Direct holding is at least 25%: unknown",
            "Holding structure is direct (no intermediate entity): yes",
        ],
    }
    assert response.json()["next_actions"] == [
        {
            "priority": "high",
            "action": "先在线下确认直接持股比例和持股方式，再重新发起预审或转交人工复核。",
            "reason": "当前关键分支事实仍未确认，系统不会继续自动缩减股息税率分支。",
        }
    ]
    assert response.json()["fact_completion"] is None
    assert response.json()["user_declared_facts"] == {
        "declaration_label": "User-declared facts (unverified)",
        "facts": [
            {
                "fact_key": "direct_holding_confirmed",
                "value": "yes",
                "label": "Direct holding confirmed",
            },
            {
                "fact_key": "direct_holding_threshold_met",
                "value": "unknown",
                "label": "Direct holding is at least 25%",
            },
            {
                "fact_key": "holding_structure_is_direct",
                "value": "yes",
                "label": "Holding structure is direct (no intermediate entity)",
            },
        ],
    }

def test_dividend_fact_completion_stops_when_pe_exclusion_is_triggered():
    response = client.post(
        "/analyze",
        json={
            "input_mode": "guided",
            "guided_input": {
                "payer_country": "CN",
                "payee_country": "NL",
                "income_type": "dividends",
                "facts": {
                    "pe_effectively_connected": "yes",
                    "holding_structure_is_direct": "unknown",
                },
            },
        },
    )

    assert response.status_code == 200
    assert response.json()["supported"] is True
    assert response.json()["result"]["rate"] == "5% / 10%"
    assert response.json()["review_state"] == {
        "state_code": "needs_human_intervention",
        "state_label_zh": "需要人工介入",
        "state_summary": "当前结果已触发保守停止，应转入人工处理而不是继续自动推进。",
    }
    assert response.json()["fact_completion_status"] == {
        "status_code": "terminated_pe_exclusion",
        "status_label_zh": "转入排除情形复核",
        "status_summary": "当前场景触发了与中国常设机构或固定基地实际联系的排除提醒，系统结束 Article 10 分支自动缩减。",
    }
    assert response.json()["change_summary"] == {
        "summary_label": "Result Change Summary",
        "state_change": "可补全 -> 需要人工介入",
        "rate_change": "5% / 10% -> Article 10 branch excluded",
        "trigger_facts": [
            "Dividend effectively connected with a China PE / fixed base: yes",
            "Holding structure is direct (no intermediate entity): unknown",
        ],
    }
    assert response.json()["next_actions"] == [
        {
            "priority": "high",
            "action": "停止依赖当前股息分支自动缩减，并确认荷兰收款方是否在中国存在与该股息实际联系的常设机构或固定基地。",
            "reason": "如果该排除情形成立，当前场景可能需要转入其他条款并进行人工复核，而不是继续沿用 Article 10 分支结果。",
        }
    ]
    assert response.json()["fact_completion"] is None
    assert response.json()["user_declared_facts"] == {
        "declaration_label": "User-declared facts (unverified)",
        "facts": [
            {
                "fact_key": "pe_effectively_connected",
                "value": "yes",
                "label": "Dividend effectively connected with a China PE / fixed base",
            },
            {
                "fact_key": "holding_structure_is_direct",
                "value": "unknown",
                "label": "Holding structure is direct (no intermediate entity)",
            },
        ],
    }

def test_dividend_fact_completion_stops_when_beneficial_owner_prerequisite_is_not_confirmed():
    response = client.post(
        "/analyze",
        json={
            "input_mode": "guided",
            "guided_input": {
                "payer_country": "CN",
                "payee_country": "NL",
                "income_type": "dividends",
                "facts": {
                    "direct_holding_confirmed": "yes",
                    "direct_holding_threshold_met": "yes",
                    "beneficial_owner_confirmed": "no",
                    "holding_structure_is_direct": "yes",
                },
            },
        },
    )

    assert response.status_code == 200
    assert response.json()["supported"] is True
    assert response.json()["result"]["rate"] == "5% / 10%"
    assert response.json()["review_state"] == {
        "state_code": "needs_human_intervention",
        "state_label_zh": "需要人工介入",
        "state_summary": "当前结果已触发保守停止，应转入人工处理而不是继续自动推进。",
    }
    assert response.json()["fact_completion_status"] == {
        "status_code": "terminated_beneficial_owner_unconfirmed",
        "status_label_zh": "受益所有人前提未确认",
        "status_summary": "协定优惠前提中的受益所有人身份尚未被单独确认，系统结束当前股息分支自动缩减。",
    }
    assert response.json()["change_summary"] == {
        "summary_label": "Result Change Summary",
        "state_change": "可补全 -> 需要人工介入",
        "rate_change": "5% -> treaty rate cannot be relied on yet",
        "trigger_facts": [
            "Direct holding confirmed: yes",
            "Direct holding is at least 25%: yes",
            "Beneficial owner status separately confirmed: no",
            "Holding structure is direct (no intermediate entity): yes",
        ],
    }
    assert response.json()["next_actions"] == [
        {
            "priority": "high",
            "action": "先单独确认受益所有人身份及其支持材料，在未确认前不要依赖当前协定优惠税率分支。",
            "reason": "受益所有人是协定优惠适用的前提条件；系统不会仅凭当前输入替你判断这一点是否成立。",
        }
    ]
    assert response.json()["fact_completion"] is None
    assert response.json()["user_declared_facts"] == {
        "declaration_label": "User-declared facts (unverified)",
        "facts": [
            {
                "fact_key": "direct_holding_confirmed",
                "value": "yes",
                "label": "Direct holding confirmed",
            },
            {
                "fact_key": "direct_holding_threshold_met",
                "value": "yes",
                "label": "Direct holding is at least 25%",
            },
            {
                "fact_key": "beneficial_owner_confirmed",
                "value": "no",
                "label": "Beneficial owner status separately confirmed",
            },
            {
                "fact_key": "holding_structure_is_direct",
                "value": "yes",
                "label": "Holding structure is direct (no intermediate entity)",
            },
        ],
    }

def test_dividend_fact_completion_stops_when_user_declared_facts_conflict():
    response = client.post(
        "/analyze",
        json={
            "input_mode": "guided",
            "guided_input": {
                "payer_country": "CN",
                "payee_country": "NL",
                "income_type": "dividends",
                "facts": {
                    "direct_holding_confirmed": "no",
                    "direct_holding_threshold_met": "yes",
                    "holding_structure_is_direct": "yes",
                },
            },
        },
    )

    assert response.status_code == 200
    assert response.json()["supported"] is True
    assert response.json()["result"]["rate"] == "5% / 10%"
    assert response.json()["review_state"] == {
        "state_code": "needs_human_intervention",
        "state_label_zh": "需要人工介入",
        "state_summary": "当前结果已触发保守停止，应转入人工处理而不是继续自动推进。",
    }
    assert response.json()["fact_completion_status"] == {
        "status_code": "terminated_conflicting_user_facts",
        "status_label_zh": "用户声明事实冲突",
        "status_summary": "已提交的补事实答案彼此冲突，系统结束当前股息分支自动缩减。",
    }
    assert response.json()["change_summary"] == {
        "summary_label": "Result Change Summary",
        "state_change": "可补全 -> 需要人工介入",
        "rate_change": "5% / 10% -> treaty rate cannot be narrowed due to conflicting facts",
        "trigger_facts": [
            "Direct holding confirmed: no",
            "Direct holding is at least 25%: yes",
            "Holding structure is direct (no intermediate entity): yes",
        ],
    }
    assert response.json()["next_actions"] == [
        {
            "priority": "high",
            "action": "先核对直接持股方式和持股比例的真实情况；当前答案彼此冲突，系统不会继续自动缩减股息税率分支。",
            "reason": "例如，在未直接持股的情况下不能同时把直接持股门槛判断为已满足；请先在线下核实后再重新预审。",
        }
    ]
    assert response.json()["fact_completion"] is None
    assert response.json()["user_declared_facts"] == {
        "declaration_label": "User-declared facts (unverified)",
        "facts": [
            {
                "fact_key": "direct_holding_confirmed",
                "value": "no",
                "label": "Direct holding confirmed",
            },
            {
                "fact_key": "direct_holding_threshold_met",
                "value": "yes",
                "label": "Direct holding is at least 25%",
            },
            {
                "fact_key": "holding_structure_is_direct",
                "value": "yes",
                "label": "Holding structure is direct (no intermediate entity)",
            },
        ],
    }

def test_guided_dividend_narrowing_keeps_bo_precheck_present():
    response = client.post(
        "/analyze",
        json={
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
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["supported"] is True
    assert payload["input_mode_used"] == "guided"
    assert payload["result"]["rate"] == "5%"
    assert payload["bo_precheck"] is not None
    assert payload["bo_precheck"]["status"] is not None
    assert payload["bo_precheck"]["reason_code"] == "beneficial_owner_confirmed"
    assert payload["bo_precheck"]["facts_considered"] == [
        {
            "fact_key": "beneficial_owner_confirmed",
            "value": "yes",
        },
        {
            "fact_key": "holding_structure_is_direct",
            "value": "yes",
        },
    ]

def test_dividend_percentage_27_narrows_to_reduced_rate():
    response = client.post(
        "/analyze",
        json=guided_cn_nl_dividend_payload(
            {
                "direct_holding_percentage": "27",
                "payment_date": "2026-03-01",
                "holding_period_months": "18",
                "beneficial_owner_confirmed": "yes",
                "holding_structure_is_direct": "yes",
            }
        ),
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["result"]["rate"] == "5%"
    assert payload["fact_completion_status"]["status_code"] == "completed_narrowed"
    assert payload["handoff_package"]["machine_handoff"]["determining_condition_priority"] == 12
    assert payload["handoff_package"]["machine_handoff"]["calculated_threshold_met"] is True

def test_dividend_percentage_20_narrows_to_general_rate():
    response = client.post(
        "/analyze",
        json=guided_cn_nl_dividend_payload(
            {
                "direct_holding_percentage": "20",
                "payment_date": "2026-03-01",
                "holding_period_months": "18",
                "beneficial_owner_confirmed": "yes",
                "holding_structure_is_direct": "yes",
            }
        ),
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["result"]["rate"] == "10%"
    assert payload["fact_completion_status"]["status_code"] == "completed_narrowed"
    assert payload["handoff_package"]["machine_handoff"]["determining_condition_priority"] == 4
    assert payload["handoff_package"]["machine_handoff"]["calculated_threshold_met"] is False

def test_dividend_percentage_25_boundary_still_qualifies_for_reduced_rate():
    response = client.post(
        "/analyze",
        json=guided_cn_nl_dividend_payload(
            {
                "direct_holding_percentage": "25.0",
                "payment_date": "2026-03-01",
                "holding_period_months": "18",
                "beneficial_owner_confirmed": "yes",
                "holding_structure_is_direct": "yes",
            }
        ),
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["result"]["rate"] == "5%"
    assert payload["handoff_package"]["machine_handoff"]["calculated_threshold_met"] is True
    assert payload["handoff_package"]["machine_handoff"]["determining_condition_priority"] == 12

def test_dividend_unknown_percentage_terminates_as_insufficient_facts():
    response = client.post(
        "/analyze",
        json=guided_cn_nl_dividend_payload(
            {
                "direct_holding_percentage": "unknown",
                "payment_date": "unknown",
                "holding_period_months": "unknown",
                "beneficial_owner_confirmed": "yes",
                "holding_structure_is_direct": "yes",
            }
        ),
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["fact_completion_status"]["status_code"] == "terminated_unknown_facts"
    assert payload["handoff_package"]["machine_handoff"]["determining_condition_priority"] == 5
    assert payload["handoff_package"]["machine_handoff"]["calculated_threshold_met"] is None

def test_dividend_short_holding_period_under_12_months_requires_review_signal():
    response = client.post(
        "/analyze",
        json=guided_cn_nl_dividend_payload(
            {
                "direct_holding_percentage": "27",
                "payment_date": "2026-03-01",
                "holding_period_months": "8",
                "beneficial_owner_confirmed": "yes",
                "holding_structure_is_direct": "yes",
            }
        ),
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["result"]["rate"] == "5%"
    assert payload["handoff_package"]["machine_handoff"]["short_holding_period_review_required"] is True

def test_dividend_long_holding_period_clears_review_signal():
    response = client.post(
        "/analyze",
        json=guided_cn_nl_dividend_payload(
            {
                "direct_holding_percentage": "27",
                "payment_date": "2026-03-01",
                "holding_period_months": "18",
                "beneficial_owner_confirmed": "yes",
                "holding_structure_is_direct": "yes",
            }
        ),
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["result"]["rate"] == "5%"
    assert payload["handoff_package"]["machine_handoff"]["short_holding_period_review_required"] is False

def test_dividend_unknown_holding_period_defaults_to_review_required():
    response = client.post(
        "/analyze",
        json=guided_cn_nl_dividend_payload(
            {
                "direct_holding_percentage": "27",
                "payment_date": "2026-03-01",
                "holding_period_months": "unknown",
                "beneficial_owner_confirmed": "yes",
                "holding_structure_is_direct": "yes",
            }
        ),
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["result"]["rate"] == "5%"
    assert payload["handoff_package"]["machine_handoff"]["short_holding_period_review_required"] is True

def test_dividend_missing_payment_date_sets_handoff_audit_signal():
    response = client.post(
        "/analyze",
        json=guided_cn_nl_dividend_payload(
            {
                "direct_holding_percentage": "27",
                "holding_period_months": "18",
                "beneficial_owner_confirmed": "yes",
                "holding_structure_is_direct": "yes",
            }
        ),
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["result"]["rate"] == "5%"
    assert payload["handoff_package"]["machine_handoff"]["payment_date_unconfirmed"] is True

def test_dividend_deprecated_threshold_yes_bridge_still_narrows_correctly():
    response = client.post(
        "/analyze",
        json=guided_cn_nl_dividend_payload(
            {
                "direct_holding_confirmed": "yes",
                "direct_holding_threshold_met": "yes",
                "beneficial_owner_confirmed": "yes",
                "holding_structure_is_direct": "yes",
            }
        ),
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["result"]["rate"] == "5%"
    assert payload["handoff_package"]["machine_handoff"]["calculated_threshold_met"] is None

def test_dividend_deprecated_threshold_no_bridge_still_narrows_to_general_rate():
    response = client.post(
        "/analyze",
        json=guided_cn_nl_dividend_payload(
            {
                "direct_holding_confirmed": "yes",
                "direct_holding_threshold_met": "no",
                "holding_structure_is_direct": "yes",
            }
        ),
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["result"]["rate"] == "10%"
    assert payload["handoff_package"]["machine_handoff"]["calculated_threshold_met"] is None

def test_dividend_holding_structure_no_blocks_reduced_rate_even_when_threshold_is_met():
    response = client.post(
        "/analyze",
        json={
            "input_mode": "guided",
            "guided_input": {
                "payer_country": "CN",
                "payee_country": "NL",
                "income_type": "dividends",
                "facts": {
                    "direct_holding_confirmed": "yes",
                    "direct_holding_threshold_met": "yes",
                    "beneficial_owner_confirmed": "yes",
                    "holding_structure_is_direct": "no",
                },
            },
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["supported"] is True
    assert payload["result"]["rate"] == "10%"
    assert payload["fact_completion_status"]["status_code"] == "completed_narrowed"
    assert payload["handoff_package"]["machine_handoff"]["determining_condition_priority"] == 10

def test_dividend_holding_structure_unknown_terminates_as_insufficient_facts():
    response = client.post(
        "/analyze",
        json={
            "input_mode": "guided",
            "guided_input": {
                "payer_country": "CN",
                "payee_country": "NL",
                "income_type": "dividends",
                "facts": {
                    "direct_holding_confirmed": "yes",
                    "direct_holding_threshold_met": "yes",
                    "beneficial_owner_confirmed": "yes",
                    "holding_structure_is_direct": "unknown",
                },
            },
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["supported"] is True
    assert payload["fact_completion_status"]["status_code"] == "terminated_unknown_facts"
    assert payload["handoff_package"]["machine_handoff"]["determining_condition_priority"] == 11

def test_dividend_holding_structure_yes_allows_reduced_rate_when_other_conditions_are_met():
    response = client.post(
        "/analyze",
        json={
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
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["supported"] is True
    assert payload["result"]["rate"] == "5%"
    assert payload["handoff_package"]["machine_handoff"]["determining_condition_priority"] == 12

def test_dividend_mli_ppt_flag_no_requires_handoff_review_signal_for_reduced_rate():
    response = client.post(
        "/analyze",
        json={
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
                    "mli_ppt_risk_flag": "no",
                },
            },
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["result"]["rate"] == "5%"
    assert payload["handoff_package"]["machine_handoff"]["mli_ppt_review_required"] is True

def test_dividend_mli_ppt_flag_yes_clears_handoff_review_signal_for_reduced_rate():
    response = client.post(
        "/analyze",
        json={
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
                    "mli_ppt_risk_flag": "yes",
                },
            },
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["result"]["rate"] == "5%"
    assert payload["handoff_package"]["machine_handoff"]["mli_ppt_review_required"] is False

def test_guided_input_conflict_escalates_conservatively_without_overriding_structured_facts():
    response = client.post(
        "/analyze",
        json={
            "input_mode": "guided",
            "guided_input": {
                "payer_country": "CN",
                "payee_country": "NL",
                "income_type": "dividends",
                "facts": {
                    "direct_holding_confirmed": "no",
                    "direct_holding_threshold_met": "yes",
                    "beneficial_owner_confirmed": "unknown",
                    "holding_structure_is_direct": "yes",
                },
                "scenario_text": "中国公司向荷兰公司支付股息，且已满足 25% 直接持股门槛，可以适用协定优惠。",
            },
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["supported"] is True
    assert payload["input_mode_used"] == "guided"
    assert payload["review_state"] == {
        "state_code": "needs_human_intervention",
        "state_label_zh": "需要人工介入",
        "state_summary": "当前结果已触发保守停止，应转入人工处理而不是继续自动推进。",
    }
    assert payload["guided_conflict"] == {
        "status": "conflict_detected",
        "reason_code": "supplemental_text_conflicts_with_structured_facts",
        "reason_summary": "Supplemental scenario text conflicts with the structured guided facts, so the system preserved the structured facts and escalated for manual review.",
        "structured_facts_win": True,
        "conflicting_claims": [
            "scenario_text claims the reduced dividend branch can be used, but the structured facts do not support that branch",
        ],
    }
    assert payload["bo_precheck"]["status"] == "insufficient_facts"
    assert payload["bo_precheck"]["facts_considered"] == [
        {
            "fact_key": "beneficial_owner_confirmed",
            "value": "unknown",
        },
        {
            "fact_key": "holding_structure_is_direct",
            "value": "yes",
        },
    ]
    assert payload["handoff_package"]["machine_handoff"]["determining_condition_priority"] == 13
    assert payload["handoff_package"]["machine_handoff"]["guided_conflict"] == payload["guided_conflict"]
