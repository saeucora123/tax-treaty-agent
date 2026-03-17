import json
from pathlib import Path

from fastapi.testclient import TestClient

from app.main import app
from app import service


client = TestClient(app)


def test_request_schema_no_longer_exposes_legacy_dividend_bridge():
    schema = app.openapi()
    request_schema = schema["components"]["schemas"]["AnalyzeRequest"]
    legacy_bridge_field = "_".join(["fact", "inputs"])

    assert legacy_bridge_field not in request_schema["properties"]


def assert_machine_handoff(
    payload: dict,
    *,
    record_kind: str,
    review_state_code: str,
    recommended_route: str,
) -> dict:
    assert "handoff_package" in payload
    handoff = payload["handoff_package"]
    assert payload["schema_version"] == "slice3.v1"
    assert handoff["machine_handoff"]["schema_version"] == payload["schema_version"]
    assert handoff["machine_handoff"]["record_kind"] == record_kind
    assert handoff["machine_handoff"]["review_state_code"] == review_state_code
    assert handoff["machine_handoff"]["recommended_route"] == recommended_route
    assert handoff["human_review_brief"]["brief_title"] == "Treaty Pre-Review Brief"
    assert "not a final tax opinion" in handoff["human_review_brief"]["handoff_note"]
    return handoff


def guided_cn_nl_dividend_payload(facts: dict) -> dict:
    return {
        "input_mode": "guided",
        "guided_input": {
            "payer_country": "CN",
            "payee_country": "NL",
            "income_type": "dividends",
            "facts": facts,
        },
    }


def test_rejects_unsupported_country_pair():
    response = client.post(
        "/analyze",
        json={"scenario": "中国居民企业向美国支付特许权使用费"},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["data_source_used"] == "stable"
    assert payload["supported"] is False
    assert payload["reason"] == "unsupported_country_pair"
    assert payload["message"] == (
        "Current pilot scope supports only China-Netherlands, China-Singapore treaty scenarios."
    )
    assert payload["immediate_action"] == (
        "Rewrite the scenario into the supported pilot treaty pair list before running another review."
    )
    assert payload["missing_fields"] == []
    assert payload["suggested_format"] == "Try a sentence like: 中国居民企业向新加坡公司支付特许权使用费"
    assert payload["suggested_examples"] == [
        "中国居民企业向荷兰公司支付股息",
        "中国居民企业向荷兰银行支付利息",
        "中国居民企业向荷兰公司支付特许权使用费",
        "中国居民企业向新加坡公司支付股息",
        "中国居民企业向新加坡银行支付利息",
        "中国居民企业向新加坡公司支付特许权使用费",
    ]
    assert payload["review_state"] == {
        "state_code": "out_of_scope",
        "state_label_zh": "不在支持范围",
        "state_summary": "当前查询超出本产品的国家对或收入类型支持范围。",
    }
    assert payload["next_actions"] == [
        {
            "priority": "high",
            "action": "改写为当前试点国家对列表内、且属于股息、利息或特许权使用费的查询后再重试。",
            "reason": "当前场景属于产品边界之外；目前稳定数据源只支持 China-Netherlands, China-Singapore 两个试点国家对。",
        }
    ]
    handoff = assert_machine_handoff(
        payload,
        record_kind="unsupported",
        review_state_code="out_of_scope",
        recommended_route="out_of_scope_rewrite",
    )
    assert handoff["machine_handoff"]["article_number"] is None
    assert handoff["machine_handoff"]["rate_display"] is None
    assert handoff["human_review_brief"]["disposition"] == "Rewrite the scenario inside the supported pilot scope."


def test_returns_structured_result_for_supported_royalties_case():
    response = client.post(
        "/analyze",
        json={"scenario": "中国居民企业向荷兰支付特许权使用费"},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["data_source_used"] == "stable"
    assert payload["supported"] is True
    assert payload["normalized_input"] == {
        "payer_country": "CN",
        "payee_country": "NL",
        "transaction_type": "royalties",
    }
    assert payload["result"]["treaty_id"] == "cn-nl"
    assert payload["result"]["treaty_title"] == "China-Netherlands Tax Treaty"
    assert payload["result"]["article_number"] == "12"
    assert payload["result"]["article_title"] == "Royalties"
    assert payload["result"]["rate"] == "10%"
    assert payload["result"]["source_reference"] == "Article 12(2)"
    assert "sample" not in payload["result"]["source_excerpt"].lower()
    assert payload["result"]["source_trace"]["language_version"] == "en"
    assert "2013" in payload["result"]["source_trace"]["version_note"]
    assert "sat-cn-nl-2013-en-pdf" in payload["result"]["source_trace"]["official_source_ids"]
    assert payload["result"]["source_trace"]["working_paper_ref"].endswith(
        "cn-nl-royalties-alignment-check.md"
    )
    assert payload["result"]["mli_context"]["covered_tax_agreement"] is True
    assert payload["result"]["mli_context"]["ppt_applies"] is True
    assert "PPT" in payload["result"]["mli_context"]["summary"]
    assert "人工复核" not in payload["result"]["mli_context"]["summary"]
    assert payload["review_state"] == {
        "state_code": "pre_review_complete",
        "state_label_zh": "预审完成",
        "state_summary": "系统已完成第一轮预审，请按标准复核流程继续。",
    }
    assert payload["confirmed_scope"] == {
        "applicable_treaty": "中国-荷兰税收协定",
        "applicable_article": "Article 12 - Royalties",
        "payment_direction": "CN -> NL",
        "income_type": "royalties",
    }
    assert payload["next_actions"] == [
        {
            "priority": "medium",
            "action": "按标准人工复核流程确认条款适用条件与受益所有人事实。",
            "reason": "当前结果属于第一轮预审完成，不等于最终税务结论。",
        }
    ]
    handoff = assert_machine_handoff(
        payload,
        record_kind="supported",
        review_state_code="pre_review_complete",
        recommended_route="standard_review",
    )
    assert handoff["machine_handoff"]["applicable_treaty"] == "中国-荷兰税收协定"
    assert handoff["machine_handoff"]["payment_direction"] == "CN -> NL"
    assert handoff["machine_handoff"]["article_number"] == "12"
    assert handoff["machine_handoff"]["rate_display"] == "10%"
    assert handoff["machine_handoff"]["source_excerpt"] == payload["result"]["source_excerpt"]
    assert handoff["machine_handoff"]["treaty_version"] == payload["result"]["source_trace"]["version_note"]
    assert handoff["machine_handoff"]["mli_summary"] == payload["result"]["mli_context"]["summary"]
    assert handoff["human_review_brief"]["disposition"] == "Proceed with standard human review."
    assert any("2013" in line for line in handoff["human_review_brief"]["summary_lines"])
    assert any("PPT" in line for line in handoff["human_review_brief"]["summary_lines"])
    if "input_interpretation" in payload:
        assert payload["input_interpretation"]["parser_source"] == "llm"


def test_returns_structured_result_for_supported_dividends_case():
    response = client.post(
        "/analyze",
        json={"scenario": "中国公司向荷兰公司支付股息"},
    )

    assert response.status_code == 200
    assert response.json()["supported"] is True
    assert response.json()["normalized_input"] == {
        "payer_country": "CN",
        "payee_country": "NL",
        "transaction_type": "dividends",
    }
    assert response.json()["result"]["summary"] == (
        "Preliminary view: Article 10 Dividends appears relevant, but multiple treaty rate branches "
        "(5% / 10%) are possible and this version should not issue an automatic conclusion."
    )
    assert response.json()["result"]["boundary_note"] == (
        "This is a first-pass treaty pre-review based on limited scenario facts. Final eligibility still depends on additional facts, documents, and analysis outside the current review scope."
    )
    assert response.json()["result"]["immediate_action"] == (
        "Do not rely on this result yet. Resolve the missing facts and supporting documents before any treaty conclusion."
    )
    assert response.json()["result"]["rate"] == "5% / 10%"
    assert response.json()["result"]["auto_conclusion_allowed"] is False
    assert response.json()["result"]["key_missing_facts"] == [
        "Whether the payment is legally a dividend rather than another type of return.",
        "Whether the recipient is the beneficial owner of the dividend income.",
        "Whether shareholding facts support relying on the treaty position.",
    ]
    assert response.json()["result"]["article_number"] == "10"
    assert response.json()["result"]["article_title"] == "Dividends"
    assert response.json()["result"]["review_checklist"] == [
        "Confirm the payment is legally characterized as a dividend rather than another return.",
        "Confirm the recipient is the beneficial owner of the dividend income.",
        "Check shareholding facts and supporting corporate records before relying on the treaty rate.",
    ]
    assert response.json()["review_state"] == {
        "state_code": "can_be_completed",
        "state_label_zh": "可补全",
        "state_summary": "系统已缩小范围；补充少量关键事实后，可进一步明确结果。",
    }
    assert response.json()["next_actions"] == [
        {
            "priority": "high",
            "action": "先核实股息分支所需的关键事实，再判断候选税率分支。",
            "reason": "当前存在多个可信税率分支，系统不会自动替你选择其一。",
        }
    ]
    assert response.json()["fact_completion"] == {
        "flow_type": "bounded_form",
        "session_type": "pseudo_multiturn",
        "user_declaration_note": "Facts entered here are user-declared and not independently verified.",
        "facts": [
            {
                "fact_key": "direct_holding_percentage",
                "prompt": "What is the recipient's direct shareholding percentage in the paying company as of the payment date?",
                "input_type": "text",
            },
            {
                "fact_key": "payment_date",
                "prompt": "What is the dividend payment date (or declared payment date)?",
                "input_type": "text",
            },
            {
                "fact_key": "holding_period_months",
                "prompt": "How many months has the recipient continuously held the shares as of the payment date?",
                "input_type": "text",
            },
            {
                "fact_key": "beneficial_owner_confirmed",
                "prompt": "Has beneficial-owner status been separately confirmed outside this tool?",
                "input_type": "single_select",
                "options": ["yes", "no", "unknown"],
            },
            {
                "fact_key": "pe_effectively_connected",
                "prompt": "Is the dividend effectively connected with a permanent establishment or fixed base of the Dutch recipient in China?",
                "input_type": "single_select",
                "options": ["yes", "no", "unknown"],
            },
            {
                "fact_key": "holding_structure_is_direct",
                "prompt": "Is the holding structure confirmed to be direct with no intermediate holding entity between the recipient and the paying company?",
                "input_type": "single_select",
                "options": ["yes", "no", "unknown"],
            },
            {
                "fact_key": "mli_ppt_risk_flag",
                "prompt": "Has a principal purpose test (PPT) risk assessment been performed for this dividend payment under the MLI?",
                "input_type": "single_select",
                "options": ["yes", "no", "unknown"],
            },
        ],
    }


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


def test_returns_structured_result_for_supported_reverse_direction_case():
    response = client.post(
        "/analyze",
        json={"scenario": "荷兰公司向中国母公司支付股息"},
    )

    assert response.status_code == 200
    assert response.json()["supported"] is True
    assert response.json()["normalized_input"] == {
        "payer_country": "NL",
        "payee_country": "CN",
        "transaction_type": "dividends",
    }
    assert response.json()["result"]["article_number"] == "10"
    assert response.json()["result"]["article_title"] == "Dividends"


def test_analysis_respects_direction_specific_rule_branches(tmp_path: Path, monkeypatch):
    payload = {
        "treaty": {
            "treaty_id": "cn-nl",
            "jurisdictions": ["CN", "NL"],
            "title": "China-Netherlands Tax Treaty",
            "version": "v3-generated",
            "source_type": "import_stub_from_source_documents",
            "source_documents": [],
            "notes": [],
        },
        "articles": [
            {
                "article_number": "12",
                "article_title": "Royalties",
                "article_label": "Article 12",
                "income_type": "royalties",
                "summary": "Treaty treatment for royalties.",
                "notes": [],
                "paragraphs": [
                    {
                        "paragraph_id": "art12-p1",
                        "paragraph_label": "Article 12(2)",
                        "source_reference": "Article 12(2)",
                        "source_language": "en",
                        "source_excerpt": "Forward branch.",
                        "source_segments": [],
                        "provenance_summary": {},
                        "rules": [
                            {
                                "rule_id": "cn-nl-art12-p1-forward",
                                "rule_type": "rate_limitation",
                                "rate": "5%",
                                "direction": "payer_to_payee",
                                "candidate_rank": 1,
                                "is_primary_candidate": True,
                                "extraction_confidence": 0.98,
                                "derived_from_segments": [],
                                "conditions": ["Only when payer is CN and payee is NL."],
                                "human_review_required": True,
                                "review_reason": "Forward branch.",
                            }
                        ],
                    },
                    {
                        "paragraph_id": "art12-p2",
                        "paragraph_label": "Article 12(2)",
                        "source_reference": "Article 12(2)",
                        "source_language": "en",
                        "source_excerpt": "Reverse branch.",
                        "source_segments": [],
                        "provenance_summary": {},
                        "rules": [
                            {
                                "rule_id": "cn-nl-art12-p2-reverse",
                                "rule_type": "rate_limitation",
                                "rate": "15%",
                                "direction": "payee_to_payer",
                                "candidate_rank": 1,
                                "is_primary_candidate": True,
                                "extraction_confidence": 0.98,
                                "derived_from_segments": [],
                                "conditions": ["Only when payer is NL and payee is CN."],
                                "human_review_required": True,
                                "review_reason": "Reverse branch.",
                            }
                        ],
                    },
                ],
            }
        ],
    }

    temp_data_path = tmp_path / "cn-nl.directional-royalties.json"
    temp_data_path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    monkeypatch.setattr(service, "DATA_PATH", temp_data_path)

    response = client.post(
        "/analyze",
        json={"scenario": "荷兰公司向中国公司支付特许权使用费"},
    )

    assert response.status_code == 200
    assert response.json()["supported"] is True
    assert response.json()["result"]["source_reference"] == "Article 12(2)"
    assert response.json()["result"]["rate"] == "15%"
    assert response.json()["result"]["conditions"] == [
        "Only when payer is NL and payee is CN."
    ]


def test_treats_common_royalty_like_labels_as_supported_royalties_case():
    response = client.post(
        "/analyze",
        json={"scenario": "中国居民企业向荷兰公司支付软件许可费"},
    )

    assert response.status_code == 200
    assert response.json()["supported"] is True
    assert response.json()["normalized_input"] == {
        "payer_country": "CN",
        "payee_country": "NL",
        "transaction_type": "royalties",
    }
    assert response.json()["result"]["article_number"] == "12"
    assert response.json()["result"]["article_title"] == "Royalties"


def test_rejects_supported_country_pair_with_unknown_transaction_type():
    response = client.post(
        "/analyze",
        json={"scenario": "中国居民企业向荷兰支付服务费"},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["data_source_used"] == "stable"
    assert payload["supported"] is False
    assert payload["reason"] == "unsupported_transaction_type"
    assert payload["missing_fields"] == ["transaction_type"]
    assert payload["suggested_format"] == "Try a sentence like: 中国居民企业向新加坡公司支付特许权使用费"
    assert payload["suggested_examples"] == [
        "中国居民企业向荷兰公司支付股息",
        "中国居民企业向荷兰银行支付利息",
        "中国居民企业向荷兰公司支付特许权使用费",
        "中国居民企业向新加坡公司支付股息",
        "中国居民企业向新加坡银行支付利息",
        "中国居民企业向新加坡公司支付特许权使用费",
    ]
    assert payload["review_state"] == {
        "state_code": "out_of_scope",
        "state_label_zh": "不在支持范围",
        "state_summary": "当前查询超出本产品的国家对或收入类型支持范围。",
    }
    assert payload["next_actions"] == [
        {
            "priority": "high",
            "action": "改写为当前试点国家对列表内、且属于股息、利息或特许权使用费的查询后再重试。",
            "reason": "当前场景属于产品边界之外；目前稳定数据源只支持 China-Netherlands, China-Singapore 两个试点国家对。",
        }
    ]


def test_rejects_incomplete_scenario_when_country_pair_cannot_be_confirmed():
    response = client.post(
        "/analyze",
        json={"scenario": "向荷兰公司支付股息"},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["data_source_used"] == "stable"
    assert payload["supported"] is False
    assert payload["reason"] == "incomplete_scenario"
    assert payload["missing_fields"] == ["payer_country"]
    assert payload["suggested_format"] == "Try a sentence like: 中国居民企业向荷兰公司支付股息"
    assert payload["suggested_examples"] == [
        "中国居民企业向荷兰公司支付股息",
        "中国居民企业向荷兰银行支付利息",
    ]
    assert payload["review_state"] == {
        "state_code": "can_be_completed",
        "state_label_zh": "可补全",
        "state_summary": "系统仍在当前预审范围内，但需要补充缺失事实后才能继续缩小结果。",
    }
    assert payload["next_actions"] == [
        {
            "priority": "high",
            "action": "补充付款方国家或付款方主体信息后重新提交查询。",
            "reason": "当前缺少足够的付款方事实，系统无法确认交易方向。",
        }
    ]


def test_incomplete_alias_input_gets_bridge_note_but_keeps_formal_template():
    response = client.post(
        "/analyze",
        json={"scenario": "向荷兰公司支付软件许可费"},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["reason"] == "incomplete_scenario"
    assert payload["missing_fields"] == ["payer_country"]
    assert payload["classification_note"] == (
        "Current review maps `软件许可费` into the royalties lane for first-pass treaty review. "
        "Use a fuller scenario so the tool can test the treaty position under the standard treaty royalties framework."
    )
    assert payload["suggested_format"] == "Try a sentence like: 中国居民企业向荷兰公司支付特许权使用费"
    assert payload["suggested_examples"] == [
        "中国居民企业向荷兰公司支付股息",
        "中国居民企业向荷兰银行支付利息",
    ]


def test_rejects_ambiguous_payer_country_instead_of_guessing():
    response = client.post(
        "/analyze",
        json={"scenario": "中国公司和荷兰公司向荷兰公司支付股息"},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["reason"] == "incomplete_scenario"
    assert payload["missing_fields"] == ["payer_country"]
    assert payload["suggested_examples"] == [
        "中国居民企业向荷兰公司支付股息",
        "中国居民企业向荷兰银行支付利息",
    ]


def test_rejects_ambiguous_payee_country_instead_of_guessing():
    response = client.post(
        "/analyze",
        json={"scenario": "中国居民企业向荷兰公司或美国公司支付特许权使用费"},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["reason"] == "incomplete_scenario"
    assert payload["missing_fields"] == ["payee_country"]
    assert payload["suggested_examples"] == [
        "中国居民企业向荷兰公司支付股息",
        "中国居民企业向荷兰银行支付利息",
    ]


def test_rejects_unsupported_country_pair_with_supported_scope_examples():
    response = client.post(
        "/analyze",
        json={"scenario": "中国居民企业向美国支付特许权使用费"},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["reason"] == "unsupported_country_pair"
    assert payload["message"] == (
        "Current pilot scope supports only China-Netherlands, China-Singapore treaty scenarios."
    )
    assert payload["suggested_examples"] == [
        "中国居民企业向荷兰公司支付股息",
        "中国居民企业向荷兰银行支付利息",
        "中国居民企业向荷兰公司支付特许权使用费",
        "中国居民企业向新加坡公司支付股息",
        "中国居民企业向新加坡银行支付利息",
        "中国居民企业向新加坡公司支付特许权使用费",
    ]


def test_medium_confidence_match_is_escalated_to_priority_review(tmp_path: Path, monkeypatch):
    payload = json.loads(Path(service.DATA_PATH).read_text(encoding="utf-8"))
    payload["articles"][2]["paragraphs"][0]["rules"][0]["extraction_confidence"] = 0.88

    temp_data_path = tmp_path / "cn-nl.medium-confidence.json"
    temp_data_path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    monkeypatch.setattr(service, "DATA_PATH", temp_data_path)

    response = client.post(
        "/analyze",
        json={"scenario": "中国居民企业向荷兰支付特许权使用费"},
    )

    assert response.status_code == 200
    assert response.json()["result"]["review_priority"] == "high"
    assert response.json()["result"]["auto_conclusion_allowed"] is True
    assert response.json()["result"]["summary"] == (
        "Preliminary view: Article 12 Royalties appears relevant, with a treaty rate ceiling of 10%. "
        "Prioritize manual review before relying on this result."
    )
    assert response.json()["result"]["boundary_note"] == (
        "This is a first-pass treaty pre-review based on limited scenario facts. Final eligibility still depends on additional facts, documents, and analysis outside the current review scope."
    )
    assert response.json()["result"]["immediate_action"] == (
        "Escalate this case for priority manual review before using the treaty result."
    )
    assert "prioritize manual verification" in response.json()["result"]["review_reason"]
    assert "v1 scope" not in response.json()["result"]["review_reason"]


def test_very_low_confidence_match_is_held_from_auto_conclusion(tmp_path: Path, monkeypatch):
    payload = json.loads(Path(service.DATA_PATH).read_text(encoding="utf-8"))
    payload["articles"][2]["paragraphs"][0]["rules"][0]["extraction_confidence"] = 0.72

    temp_data_path = tmp_path / "cn-nl.very-low-confidence.json"
    temp_data_path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    monkeypatch.setattr(service, "DATA_PATH", temp_data_path)

    response = client.post(
        "/analyze",
        json={"scenario": "中国居民企业向荷兰支付特许权使用费"},
    )

    assert response.status_code == 200
    assert response.json()["result"]["review_priority"] == "high"
    assert response.json()["result"]["auto_conclusion_allowed"] is False
    assert response.json()["result"]["summary"] == (
        "Preliminary view: Article 12 Royalties appears relevant, but this version should not issue an automatic conclusion. "
        "The current indicative treaty rate is 10%."
    )
    assert response.json()["result"]["boundary_note"] == (
        "This is a first-pass treaty pre-review based on limited scenario facts. Final eligibility still depends on additional facts, documents, and analysis outside the current review scope."
    )
    assert response.json()["result"]["immediate_action"] == (
        "Do not rely on this result yet. Resolve the missing facts and supporting documents before any treaty conclusion."
    )
    assert "not suitable for an automatic treaty conclusion" in response.json()["result"]["review_reason"]
    assert "v1 scope" not in response.json()["result"]["review_reason"]


def test_analysis_prefers_rate_bearing_rule_over_earlier_narrative_paragraph(tmp_path: Path, monkeypatch):
    payload = {
        "treaty": {
            "treaty_id": "cn-nl",
            "jurisdictions": ["CN", "NL"],
            "title": "China-Netherlands Tax Treaty",
            "version": "v3-generated",
            "source_type": "import_stub_from_source_documents",
            "source_documents": [],
            "notes": [],
        },
        "articles": [
            {
                "article_number": "12",
                "article_title": "Royalties",
                "article_label": "Article 12",
                "income_type": "royalties",
                "summary": "Treaty treatment for royalties.",
                "notes": [],
                "paragraphs": [
                    {
                        "paragraph_id": "art12-p1",
                        "paragraph_label": "Article 12(2)",
                        "source_reference": "Article 12(2)",
                        "source_language": "en",
                        "source_excerpt": "Royalties arising in one of the States and paid to a resident of the other State may be taxed in that other State.",
                        "source_segments": [],
                        "provenance_summary": {},
                        "rules": [
                            {
                                "rule_id": "cn-nl-art12-p1-r1",
                                "rule_type": "taxation_right",
                                "rate": "N/A",
                                "direction": "bidirectional",
                                "candidate_rank": 1,
                                "is_primary_candidate": True,
                                "extraction_confidence": 0.95,
                                "derived_from_segments": [],
                                "conditions": [],
                                "human_review_required": True,
                                "review_reason": "Narrative treaty paragraph retained for context.",
                            }
                        ],
                    },
                    {
                        "paragraph_id": "art12-p2",
                        "paragraph_label": "Article 12(2)",
                        "source_reference": "Article 12(2)",
                        "source_language": "en",
                        "source_excerpt": "However, such royalties may also be taxed in the first-mentioned State, but the tax so charged shall not exceed 10 per cent of the gross amount of the royalties.",
                        "source_segments": [],
                        "provenance_summary": {},
                        "rules": [
                            {
                                "rule_id": "cn-nl-art12-p2-r1",
                                "rule_type": "rate_limitation",
                                "rate": "10%",
                                "direction": "payer_to_payee",
                                "candidate_rank": 1,
                                "is_primary_candidate": True,
                                "extraction_confidence": 0.98,
                                "derived_from_segments": [],
                                "conditions": [
                                    "Treaty applicability depends on the facts of the payment."
                                ],
                                "human_review_required": True,
                                "review_reason": "Final eligibility depends on facts outside the current review scope.",
                            }
                        ],
                    },
                ],
            }
        ],
    }

    temp_data_path = tmp_path / "cn-nl.phase2-like.json"
    temp_data_path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    monkeypatch.setattr(service, "DATA_PATH", temp_data_path)

    response = client.post(
        "/analyze",
        json={"scenario": "中国居民企业向荷兰支付特许权使用费"},
    )

    assert response.status_code == 200
    assert response.json()["supported"] is True
    assert response.json()["result"]["source_reference"] == "Article 12(2)"
    assert response.json()["result"]["rate"] == "10%"


def test_llm_input_parser_can_route_more_natural_language_into_supported_case(monkeypatch):
    monkeypatch.setattr(
        service,
        "try_llm_normalize_input",
        lambda scenario: {
            "country_pair": ("CN", "NL"),
            "payer_country": "CN",
            "payee_country": "NL",
            "transaction_type": "royalties",
            "matched_transaction_label": "软件授权",
            "reason": "ok",
        },
    )

    response = client.post(
        "/analyze",
        json={"scenario": "我是北京的独立开发者，把软件授权给阿姆斯特丹的公司"},
    )

    assert response.status_code == 200
    assert response.json()["supported"] is True
    assert response.json()["normalized_input"] == {
        "payer_country": "CN",
        "payee_country": "NL",
        "transaction_type": "royalties",
    }
    assert response.json()["input_interpretation"] == {
        "parser_source": "llm",
        "payer_country": "CN",
        "payee_country": "NL",
        "transaction_type": "royalties",
        "matched_transaction_label": "软件授权",
    }
    assert response.json()["result"]["article_number"] == "12"


def test_llm_input_parser_returns_incomplete_when_it_flags_missing_core_fact(monkeypatch):
    monkeypatch.setattr(
        service,
        "try_llm_normalize_input",
        lambda scenario: {
            "country_pair": None,
            "payer_country": "CN",
            "payee_country": None,
            "transaction_type": "royalties",
            "matched_transaction_label": "软件授权",
            "reason": "incomplete_scenario",
        },
    )

    response = client.post(
        "/analyze",
        json={"scenario": "我是北京的独立开发者，把软件授权给欧洲公司"},
    )

    assert response.status_code == 200
    assert response.json()["supported"] is False
    assert response.json()["reason"] == "incomplete_scenario"
    assert response.json()["missing_fields"] == ["payee_country"]
    assert response.json()["input_interpretation"] == {
        "parser_source": "llm",
        "payer_country": "CN",
        "payee_country": None,
        "transaction_type": "royalties",
        "matched_transaction_label": "软件授权",
    }


def test_llm_input_parser_can_route_out_of_scope_country_pair_into_unsupported(monkeypatch):
    monkeypatch.setattr(
        service,
        "try_llm_normalize_input",
        lambda scenario: {
            "country_pair": ("CN", "US"),
            "payer_country": "CN",
            "payee_country": "US",
            "transaction_type": "dividends",
            "matched_transaction_label": "股息",
            "parser_source": "llm",
            "reason": "ok",
        },
    )

    response = client.post(
        "/analyze",
        json={"scenario": "中国公司向美国公司支付股息"},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["reason"] == "unsupported_country_pair"
    assert payload["input_interpretation"] == {
        "parser_source": "llm",
        "payer_country": "CN",
        "payee_country": "US",
        "transaction_type": "dividends",
        "matched_transaction_label": "股息",
    }
    assert payload["message"] == (
        "Current pilot scope supports only China-Netherlands, China-Singapore treaty scenarios."
    )


def test_llm_input_parser_rejects_non_tax_smalltalk_as_incomplete(monkeypatch):
    monkeypatch.setattr(
        service,
        "try_llm_normalize_input",
        lambda scenario: {
            "country_pair": None,
            "payer_country": None,
            "payee_country": None,
            "transaction_type": "unknown",
            "matched_transaction_label": None,
            "parser_source": "llm",
            "reason": "incomplete_scenario",
        },
    )

    response = client.post(
        "/analyze",
        json={"scenario": "今天天气不错"},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["reason"] == "incomplete_scenario"
    assert payload["missing_fields"] == [
        "payer_country",
        "payee_country",
        "transaction_type",
    ]
    assert payload["suggested_examples"] == [
        "中国居民企业向荷兰公司支付股息",
        "中国居民企业向荷兰银行支付利息",
    ]
    assert payload["input_interpretation"] == {
        "parser_source": "llm",
        "payer_country": None,
        "payee_country": None,
        "transaction_type": "unknown",
        "matched_transaction_label": None,
    }


def test_llm_input_parser_is_cross_checked_before_supported_result(monkeypatch):
    monkeypatch.setattr(
        service,
        "parse_scenario_to_json",
        lambda scenario: {
            "payer_country": "CN",
            "payee_country": "NL",
            "transaction_type": "royalties",
            "matched_transaction_label": "royalties",
            "needs_clarification": False,
        },
    )

    response = client.post(
        "/analyze",
        json={"scenario": "今天天气不错，顺便聊聊欧洲"},
    )

    assert response.status_code == 200
    assert response.json()["supported"] is False
    assert response.json()["reason"] == "incomplete_scenario"
    assert response.json()["input_interpretation"] == {
        "parser_source": "llm",
        "payer_country": None,
        "payee_country": None,
        "transaction_type": "unknown",
        "matched_transaction_label": "royalties",
    }


def test_llm_input_parser_normalizes_country_names_from_model_output(monkeypatch):
    monkeypatch.setattr(
        service,
        "parse_scenario_to_json",
        lambda scenario: {
            "payer_country": "China",
            "payee_country": "Netherlands",
            "transaction_type": "royalties",
            "matched_transaction_label": "software license",
            "needs_clarification": False,
        },
    )

    normalized = service.try_llm_normalize_input(
        "I am a Beijing developer licensing software to an Amsterdam company"
    )

    assert normalized == {
        "country_pair": ("CN", "NL"),
        "payer_country": "CN",
        "payee_country": "NL",
        "transaction_type": "royalties",
        "matched_transaction_label": "software license",
        "parser_source": "llm",
        "reason": "ok",
    }


def test_llm_input_parser_accepts_supported_country_aliases_when_evidence_is_present(
    monkeypatch,
):
    monkeypatch.setattr(
        service,
        "parse_scenario_to_json",
        lambda scenario: {
            "payer_country": "PRC",
            "payee_country": "Dutch",
            "transaction_type": "royalties",
            "matched_transaction_label": "royalties",
            "needs_clarification": False,
        },
    )

    response = client.post(
        "/analyze",
        json={"scenario": "PRC company pays Dutch company royalties"},
    )

    assert response.status_code == 200
    assert response.json()["supported"] is True
    assert response.json()["normalized_input"] == {
        "payer_country": "CN",
        "payee_country": "NL",
        "transaction_type": "royalties",
    }
    assert response.json()["input_interpretation"] == {
        "parser_source": "llm",
        "payer_country": "CN",
        "payee_country": "NL",
        "transaction_type": "royalties",
        "matched_transaction_label": "royalties",
    }


def test_analyze_uses_llm_generated_dataset_when_requested(tmp_path: Path, monkeypatch):
    stable_payload = json.loads(Path(service.DATA_PATH).read_text(encoding="utf-8"))
    llm_payload = json.loads(Path(service.DATA_PATH).read_text(encoding="utf-8"))

    stable_payload["articles"][2]["paragraphs"][0]["source_reference"] = "Article 12(2)"
    stable_payload["articles"][2]["paragraphs"][0]["rules"][0]["rate"] = "10%"

    llm_payload["articles"][2]["paragraphs"][0]["source_reference"] = "Article 12(2)"
    llm_payload["articles"][2]["paragraphs"][0]["rules"][0]["rate"] = "7%"

    stable_path = tmp_path / "cn-nl.stable.json"
    llm_path = tmp_path / "cn-nl.llm-generated.json"
    stable_path.write_text(
        json.dumps(stable_payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    llm_path.write_text(
        json.dumps(llm_payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    monkeypatch.setattr(service, "DATA_PATH", stable_path)
    monkeypatch.setattr(service, "LLM_GENERATED_DATA_PATH", llm_path)

    default_response = client.post(
        "/analyze",
        json={"scenario": "中国居民企业向荷兰支付特许权使用费"},
    )
    llm_response = client.post(
        "/analyze",
        json={
            "scenario": "中国居民企业向荷兰支付特许权使用费",
            "data_source": "llm_generated",
        },
    )

    assert default_response.status_code == 200
    assert default_response.json()["data_source_used"] == "stable"
    assert default_response.json()["result"]["source_reference"] == "Article 12(2)"
    assert default_response.json()["result"]["rate"] == "10%"

    assert llm_response.status_code == 200
    assert llm_response.json()["data_source_used"] == "llm_generated"
    assert llm_response.json()["result"]["source_reference"] == "Article 12(2)"
    assert llm_response.json()["result"]["rate"] == "7%"


def test_analyze_rejects_unknown_data_source():
    response = client.post(
        "/analyze",
        json={
            "scenario": "中国居民企业向荷兰支付特许权使用费",
            "data_source": "mystery",
        },
    )

    assert response.status_code == 422


def test_analyze_returns_controlled_failure_when_llm_generated_dataset_is_missing(
    tmp_path: Path, monkeypatch
):
    missing_path = tmp_path / "missing-llm-dataset.json"
    monkeypatch.setattr(service, "LLM_GENERATED_DATA_PATH", missing_path)

    response = client.post(
        "/analyze",
        json={
            "scenario": "中国居民企业向荷兰支付特许权使用费",
            "data_source": "llm_generated",
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert {key: value for key, value in payload.items() if key != "handoff_package"} == {
        "schema_version": "slice3.v1",
        "input_mode_used": "free_text",
        "data_source_used": "llm_generated",
        "supported": False,
        "reason": "unavailable_data_source",
        "message": "The requested treaty dataset is not currently available.",
        "immediate_action": "Retry with the stable curated dataset or regenerate the requested treaty dataset before reviewing this scenario.",
        "missing_fields": [],
        "suggested_format": "Try again with the stable dataset or regenerate the LLM-generated treaty dataset before reviewing this scenario.",
        "suggested_examples": [
            "Use the default stable dataset for a normal review run.",
            "Regenerate the LLM-derived treaty dataset, then retry the same scenario.",
        ],
        "review_state": {
            "state_code": "needs_human_intervention",
            "state_label_zh": "需要人工介入",
            "state_summary": "当前结果无法在现有自动化边界内继续推进，应转入人工处理。",
        },
        "next_actions": [
            {
                "priority": "high",
                "action": "切回稳定数据源，或在人工确认数据已生成后再重试。",
                "reason": "当前请求的数据集不可用，系统不会伪造协定结论。",
            }
        ],
    }
    handoff = assert_machine_handoff(
        payload,
        record_kind="unsupported",
        review_state_code="needs_human_intervention",
        recommended_route="manual_review",
    )
    assert handoff["machine_handoff"]["data_source_used"] == "llm_generated"
    assert handoff["human_review_brief"]["disposition"] == "Escalate this scenario for manual review."


def test_analysis_escalates_when_multiple_rate_branches_exist_under_one_article(
    tmp_path: Path, monkeypatch
):
    payload = {
        "treaty": {
            "treaty_id": "cn-nl",
            "jurisdictions": ["CN", "NL"],
            "title": "China-Netherlands Tax Treaty",
            "version": "v3-generated",
            "source_type": "import_stub_from_source_documents",
            "source_documents": [],
            "notes": [],
        },
        "articles": [
            {
                "article_number": "10",
                "article_title": "Dividends",
                "article_label": "Article 10",
                "income_type": "dividends",
                "summary": "Treaty treatment for dividends.",
                "notes": [],
                "paragraphs": [
                    {
                        "paragraph_id": "art10-p1",
                        "paragraph_label": "Article 10(1)",
                        "source_reference": "Article 10(1)",
                        "source_language": "en",
                        "source_excerpt": "Dividends may be taxed in the residence State.",
                        "source_segments": [],
                        "provenance_summary": {},
                        "rules": [
                            {
                                "rule_id": "cn-nl-art10-p1-r1",
                                "rule_type": "taxation_right",
                                "rate": "10%",
                                "direction": "bidirectional",
                                "candidate_rank": 1,
                                "is_primary_candidate": True,
                                "extraction_confidence": 0.98,
                                "derived_from_segments": [],
                                "conditions": [
                                    "Applies where no lower-rate branch is established."
                                ],
                                "human_review_required": True,
                                "review_reason": "General dividend branch.",
                            }
                        ],
                    },
                    {
                        "paragraph_id": "art10-p2",
                        "paragraph_label": "Article 10(2)",
                        "source_reference": "Article 10(2)",
                        "source_language": "en",
                        "source_excerpt": "A lower rate may apply if the ownership threshold is met.",
                        "source_segments": [],
                        "provenance_summary": {},
                        "rules": [
                            {
                                "rule_id": "cn-nl-art10-p2-r1",
                                "rule_type": "source_tax_limit",
                                "rate": "5%",
                                "direction": "payer_to_payee",
                                "candidate_rank": 1,
                                "is_primary_candidate": True,
                                "extraction_confidence": 0.98,
                                "derived_from_segments": [],
                                "conditions": [
                                    "A reduced rate may apply if the ownership threshold is satisfied."
                                ],
                                "human_review_required": True,
                                "review_reason": "Reduced-rate dividend branch.",
                            }
                        ],
                    },
                ],
            }
        ],
    }

    temp_data_path = tmp_path / "cn-nl.dividend-branches.json"
    temp_data_path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    monkeypatch.setattr(service, "DATA_PATH", temp_data_path)

    response = client.post(
        "/analyze",
        json={"scenario": "中国公司向荷兰公司支付股息"},
    )

    assert response.status_code == 200
    assert response.json()["supported"] is True
    assert response.json()["result"]["review_priority"] == "high"
    assert response.json()["result"]["auto_conclusion_allowed"] is False
    assert response.json()["result"]["rate"] == "5% / 10%"
    assert response.json()["result"]["summary"] == (
        "Preliminary view: Article 10 Dividends appears relevant, but multiple treaty rate branches "
        "(5% / 10%) are possible and this version should not issue an automatic conclusion."
    )
    assert response.json()["result"]["alternative_rate_candidates"] == [
        {
            "source_reference": "Article 10(2)",
            "rate": "5%",
            "conditions": [
                "A reduced rate may apply if the ownership threshold is satisfied."
            ],
        }
    ]
    assert "Multiple treaty rate branches were found" in response.json()["result"]["review_reason"]
    assert response.json()["review_state"] == {
        "state_code": "can_be_completed",
        "state_label_zh": "可补全",
        "state_summary": "系统已缩小范围；补充少量关键事实后，可进一步明确结果。",
    }
    assert response.json()["next_actions"] == [
        {
            "priority": "high",
            "action": "先核实股息分支所需的关键事实，再判断候选税率分支。",
            "reason": "当前存在多个可信税率分支，系统不会自动替你选择其一。",
        }
    ]


def test_analysis_escalates_when_one_paragraph_contains_multiple_rate_rules(
    tmp_path: Path, monkeypatch
):
    payload = {
        "treaty": {
            "treaty_id": "cn-nl",
            "jurisdictions": ["CN", "NL"],
            "title": "China-Netherlands Tax Treaty",
            "version": "v3-generated",
            "source_type": "import_stub_from_source_documents",
            "source_documents": [],
            "notes": [],
        },
        "articles": [
            {
                "article_number": "10",
                "article_title": "Dividends",
                "article_label": "Article 10",
                "income_type": "dividends",
                "summary": "Treaty treatment for dividends.",
                "notes": [],
                "paragraphs": [
                    {
                        "paragraph_id": "art10-p2",
                        "paragraph_label": "Article 10(2)",
                        "source_reference": "Article 10(2)",
                        "source_language": "en",
                        "source_excerpt": "Dividends may be taxed in the source State at 10%, or 5% if the ownership threshold is met.",
                        "source_segments": [],
                        "provenance_summary": {},
                        "rules": [
                            {
                                "rule_id": "cn-nl-art10-p2-r1",
                                "rule_type": "source_tax_limit",
                                "rate": "10%",
                                "direction": "payer_to_payee",
                                "candidate_rank": 1,
                                "is_primary_candidate": True,
                                "extraction_confidence": 0.98,
                                "derived_from_segments": [],
                                "conditions": [
                                    "General dividend branch when no lower-rate condition is established."
                                ],
                                "human_review_required": True,
                                "review_reason": "General dividend branch.",
                            },
                            {
                                "rule_id": "cn-nl-art10-p2-r2",
                                "rule_type": "source_tax_limit",
                                "rate": "5%",
                                "direction": "payer_to_payee",
                                "candidate_rank": 2,
                                "is_primary_candidate": False,
                                "extraction_confidence": 0.98,
                                "derived_from_segments": [],
                                "conditions": [
                                    "Reduced rate branch if the ownership threshold is satisfied."
                                ],
                                "human_review_required": True,
                                "review_reason": "Reduced-rate dividend branch.",
                            },
                        ],
                    }
                ],
            }
        ],
    }

    temp_data_path = tmp_path / "cn-nl.same-paragraph-dividend-branches.json"
    temp_data_path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    monkeypatch.setattr(service, "DATA_PATH", temp_data_path)

    response = client.post(
        "/analyze",
        json={"scenario": "中国公司向荷兰公司支付股息"},
    )

    assert response.status_code == 200
    assert response.json()["supported"] is True
    assert response.json()["result"]["review_priority"] == "high"
    assert response.json()["result"]["auto_conclusion_allowed"] is False
    assert response.json()["result"]["rate"] == "5% / 10%"
    assert response.json()["result"]["summary"] == (
        "Preliminary view: Article 10 Dividends appears relevant, but multiple treaty rate branches "
        "(5% / 10%) are possible and this version should not issue an automatic conclusion."
    )
    assert response.json()["result"]["alternative_rate_candidates"] == [
        {
            "source_reference": "Article 10(2)",
            "rate": "5%",
            "conditions": [
                "Reduced rate branch if the ownership threshold is satisfied."
            ],
        }
    ]
    assert response.json()["review_state"] == {
        "state_code": "can_be_completed",
        "state_label_zh": "可补全",
        "state_summary": "系统已缩小范围；补充少量关键事实后，可进一步明确结果。",
    }
    assert response.json()["next_actions"] == [
        {
            "priority": "high",
            "action": "先核实股息分支所需的关键事实，再判断候选税率分支。",
            "reason": "当前存在多个可信税率分支，系统不会自动替你选择其一。",
        }
    ]


def test_stage3_state_contract_marks_supported_clear_case_as_pre_review_complete():
    response = client.post(
        "/analyze",
        json={"scenario": "中国居民企业向荷兰支付特许权使用费"},
    )

    assert response.status_code == 200
    assert response.json()["review_state"] == {
        "state_code": "pre_review_complete",
        "state_label_zh": "预审完成",
        "state_summary": "系统已完成第一轮预审，请按标准复核流程继续。",
    }
    assert response.json()["confirmed_scope"] == {
        "applicable_treaty": "中国-荷兰税收协定",
        "applicable_article": "Article 12 - Royalties",
        "payment_direction": "CN -> NL",
        "income_type": "royalties",
    }
    assert response.json()["next_actions"] == [
        {
            "priority": "medium",
            "action": "按标准人工复核流程确认条款适用条件与受益所有人事实。",
            "reason": "当前结果属于第一轮预审完成，不等于最终税务结论。",
        }
    ]


def test_stage3_state_contract_marks_incomplete_case_as_can_be_completed():
    response = client.post(
        "/analyze",
        json={"scenario": "向荷兰公司支付股息"},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["review_state"] == {
        "state_code": "can_be_completed",
        "state_label_zh": "可补全",
        "state_summary": "系统仍在当前预审范围内，但需要补充缺失事实后才能继续缩小结果。",
    }
    assert payload["next_actions"] == [
        {
            "priority": "high",
            "action": "补充付款方国家或付款方主体信息后重新提交查询。",
            "reason": "当前缺少足够的付款方事实，系统无法确认交易方向。",
        }
    ]
    handoff = assert_machine_handoff(
        payload,
        record_kind="incomplete",
        review_state_code="can_be_completed",
        recommended_route="complete_facts_then_rerun",
    )
    assert handoff["machine_handoff"]["article_number"] is None
    assert handoff["machine_handoff"]["rate_display"] is None
    assert handoff["human_review_brief"]["disposition"] == "Complete the missing facts and rerun the pre-review."


def test_stage3_state_contract_marks_priority_review_case_as_partial_review(
    tmp_path: Path, monkeypatch
):
    payload = json.loads(Path(service.DATA_PATH).read_text(encoding="utf-8"))
    payload["articles"][2]["paragraphs"][0]["rules"][0]["extraction_confidence"] = 0.88

    temp_data_path = tmp_path / "cn-nl.stage3-partial-review.json"
    temp_data_path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    monkeypatch.setattr(service, "DATA_PATH", temp_data_path)

    response = client.post(
        "/analyze",
        json={"scenario": "中国居民企业向荷兰支付特许权使用费"},
    )

    assert response.status_code == 200
    assert response.json()["review_state"] == {
        "state_code": "partial_review",
        "state_label_zh": "预审部分完成",
        "state_summary": "系统已完成结构化缩减，但当前结果仍需优先人工复核。",
    }
    assert response.json()["next_actions"] == [
        {
            "priority": "high",
            "action": "优先核验条款适用条件、来源质量和关键事实后再引用该结果。",
            "reason": "当前来源置信度不足以支持常规依赖，但已完成条款缩减。",
        }
    ]


def test_stage3_state_contract_marks_low_confidence_hold_as_human_intervention(
    tmp_path: Path, monkeypatch
):
    payload = json.loads(Path(service.DATA_PATH).read_text(encoding="utf-8"))
    payload["articles"][2]["paragraphs"][0]["rules"][0]["extraction_confidence"] = 0.72

    temp_data_path = tmp_path / "cn-nl.stage3-human-intervention.json"
    temp_data_path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    monkeypatch.setattr(service, "DATA_PATH", temp_data_path)

    response = client.post(
        "/analyze",
        json={"scenario": "中国居民企业向荷兰支付特许权使用费"},
    )

    assert response.status_code == 200
    assert response.json()["review_state"] == {
        "state_code": "needs_human_intervention",
        "state_label_zh": "需要人工介入",
        "state_summary": "当前结果已触发保守停止，应转入人工处理而不是继续自动推进。",
    }
    assert response.json()["next_actions"] == [
        {
            "priority": "high",
            "action": "停止自动结论流程，并将当前条款、来源和待核事实交给人工复核。",
            "reason": "当前来源置信度过低，系统不应继续自动推进。",
        }
    ]


def test_stage3_state_contract_marks_unsupported_scope_as_out_of_scope():
    response = client.post(
        "/analyze",
        json={"scenario": "中国居民企业向美国支付特许权使用费"},
    )

    assert response.status_code == 200
    assert response.json()["review_state"] == {
        "state_code": "out_of_scope",
        "state_label_zh": "不在支持范围",
        "state_summary": "当前查询超出本产品的国家对或收入类型支持范围。",
    }
    assert response.json()["next_actions"] == [
        {
            "priority": "high",
            "action": "改写为当前试点国家对列表内、且属于股息、利息或特许权使用费的查询后再重试。",
            "reason": "当前场景属于产品边界之外；目前稳定数据源只支持 China-Netherlands, China-Singapore 两个试点国家对。",
        }
    ]


def test_guided_royalties_request_returns_schema_version_and_bo_precheck():
    response = client.post(
        "/analyze",
        json={
            "input_mode": "guided",
            "guided_input": {
                "payer_country": "CN",
                "payee_country": "NL",
                "income_type": "royalties",
                "facts": {
                    "royalty_character_confirmed": "yes",
                    "beneficial_owner_status": "yes",
                    "contract_payment_flow_consistent": "yes",
                },
                "scenario_text": "中国居民企业向荷兰公司支付特许权使用费",
            },
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["schema_version"] == payload["handoff_package"]["machine_handoff"]["schema_version"]
    assert payload["supported"] is True
    assert payload["input_mode_used"] == "guided"
    assert payload["normalized_input"] == {
        "payer_country": "CN",
        "payee_country": "NL",
        "transaction_type": "royalties",
    }
    assert payload["bo_precheck"] == {
        "status": "no_initial_flag",
        "reason_code": "beneficial_owner_confirmed",
        "reason_summary": "The guided beneficial-owner fact is marked confirmed, so the system does not raise an initial BO workflow flag.",
        "facts_considered": [
            {
                "fact_key": "beneficial_owner_status",
                "value": "yes",
            }
        ],
        "review_note": "Beneficial-owner status still requires human verification outside this tool.",
    }
    handoff = assert_machine_handoff(
        payload,
        record_kind="supported",
        review_state_code="pre_review_complete",
        recommended_route="standard_review",
    )
    assert handoff["machine_handoff"]["bo_precheck"] == payload["bo_precheck"]


def test_guided_interest_request_uses_preapproved_fields_without_changing_interest_logic():
    response = client.post(
        "/analyze",
        json={
            "input_mode": "guided",
            "guided_input": {
                "payer_country": "CN",
                "payee_country": "SG",
                "income_type": "interest",
                "facts": {
                    "interest_character_confirmed": "yes",
                    "beneficial_owner_status": "unknown",
                    "lending_documents_consistent": "yes",
                },
            },
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["supported"] is True
    assert payload["input_mode_used"] == "guided"
    assert payload["normalized_input"] == {
        "payer_country": "CN",
        "payee_country": "SG",
        "transaction_type": "interest",
    }
    assert payload["result"]["article_title"] == "Interest"
    assert payload["bo_precheck"]["status"] == "insufficient_facts"
    assert payload["bo_precheck"]["reason_code"] == "beneficial_owner_unknown"
    assert payload["bo_precheck"]["facts_considered"] == [
        {
            "fact_key": "beneficial_owner_status",
            "value": "unknown",
        }
    ]


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
