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
