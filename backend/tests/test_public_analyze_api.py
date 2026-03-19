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

SUPPORTED_SCOPE_EXAMPLES = [
    "中国居民企业向韩国公司支付股息",
    "中国居民企业向韩国银行支付利息",
    "中国居民企业向韩国公司支付特许权使用费",
    "中国居民企业向荷兰公司支付股息",
    "中国居民企业向荷兰银行支付利息",
    "中国居民企业向荷兰公司支付特许权使用费",
    "中国居民企业向新加坡公司支付股息",
    "中国居民企业向新加坡银行支付利息",
    "中国居民企业向新加坡公司支付特许权使用费",
]

INCOMPLETE_SCOPE_EXAMPLES = [
    "中国居民企业向韩国公司支付股息",
    "中国居民企业向韩国银行支付利息",
]

def test_public_openapi_hides_data_source_but_internal_contract_keeps_it():
    schema = app.openapi()
    analyze_schema = schema["components"]["schemas"]["AnalyzeRequest"]
    internal_schema = schema["components"]["schemas"]["InternalAnalyzeRequest"]

    assert "data_source" not in analyze_schema["properties"]
    assert internal_schema["properties"]["data_source"]["default"] == "stable"

def test_guided_facts_endpoint_returns_backend_canonical_schema():
    response = client.get("/guided-facts")

    assert response.status_code == 200
    payload = response.json()
    assert payload["schema_version"] == "slice3.v1"
    assert payload["income_types"]["dividends"][0] == {
        "fact_key": "direct_holding_percentage",
        "prompt": "What is the recipient's direct shareholding percentage in the paying company as of the payment date?",
        "input_type": "text",
        "allowed_values_format": 'numeric string or "unknown"',
        "deprecated": False,
    }
    assert payload["income_types"]["interest"][1]["fact_key"] == "beneficial_owner_status"

def test_request_schema_no_longer_exposes_legacy_dividend_bridge():
    schema = app.openapi()
    request_schema = schema["components"]["schemas"]["AnalyzeRequest"]
    legacy_bridge_field = "_".join(["fact", "inputs"])

    assert legacy_bridge_field not in request_schema["properties"]

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
    assert payload["suggested_examples"] == SUPPORTED_SCOPE_EXAMPLES
    assert payload["review_state"] == {
        "state_code": "out_of_scope",
        "state_label_zh": "不在支持范围",
        "state_summary": "当前查询超出本产品的国家对或收入类型支持范围。",
    }
    assert payload["next_actions"] == [
        {
            "priority": "high",
            "action": "改写为当前试点国家对列表内、且属于股息、利息或特许权使用费的查询后再重试。",
            "reason": "当前场景属于产品边界之外；目前稳定数据源只支持 China-Korea, China-Netherlands, China-Singapore 试点国家对。",
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
    assert payload["suggested_examples"] == INCOMPLETE_SCOPE_EXAMPLES
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
    assert payload["suggested_examples"] == INCOMPLETE_SCOPE_EXAMPLES

def test_rejects_ambiguous_payer_country_instead_of_guessing():
    response = client.post(
        "/analyze",
        json={"scenario": "中国公司和荷兰公司向荷兰公司支付股息"},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["reason"] == "incomplete_scenario"
    assert payload["missing_fields"] == ["payer_country"]
    assert payload["suggested_examples"] == INCOMPLETE_SCOPE_EXAMPLES

def test_rejects_ambiguous_payee_country_instead_of_guessing():
    response = client.post(
        "/analyze",
        json={"scenario": "中国居民企业向荷兰公司或美国公司支付特许权使用费"},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["reason"] == "incomplete_scenario"
    assert payload["missing_fields"] == ["payee_country"]
    assert payload["suggested_examples"] == INCOMPLETE_SCOPE_EXAMPLES

def test_rejects_unsupported_country_pair_with_supported_scope_examples():
    response = client.post(
        "/analyze",
        json={"scenario": "中国居民企业向美国支付特许权使用费"},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["reason"] == "unsupported_country_pair"
    assert payload["message"] == (
        "Current pilot scope supports only China-Korea, China-Netherlands, China-Singapore treaty scenarios."
    )
    assert payload["suggested_examples"] == SUPPORTED_SCOPE_EXAMPLES

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
        "Current pilot scope supports only China-Korea, China-Netherlands, China-Singapore treaty scenarios."
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
    assert payload["suggested_examples"] == INCOMPLETE_SCOPE_EXAMPLES
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
            "reason": "当前场景属于产品边界之外；目前稳定数据源只支持 China-Korea, China-Netherlands, China-Singapore 试点国家对。",
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
