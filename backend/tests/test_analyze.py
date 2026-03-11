import json
from pathlib import Path

from fastapi.testclient import TestClient

from app.main import app
from app import service


client = TestClient(app)


def test_rejects_unsupported_country_pair():
    response = client.post(
        "/analyze",
        json={"scenario": "中国居民企业向美国支付特许权使用费"},
    )

    assert response.status_code == 200
    assert response.json() == {
        "data_source_used": "stable",
        "supported": False,
        "reason": "unsupported_country_pair",
        "message": "Current MVP supports only China-Netherlands treaty scenarios.",
        "immediate_action": "Rewrite the scenario into the supported China-Netherlands scope before running another review.",
        "missing_fields": [],
        "suggested_format": "Try a sentence like: 中国居民企业向荷兰公司支付特许权使用费",
        "suggested_examples": [
            "中国居民企业向荷兰公司支付股息",
            "中国居民企业向荷兰银行支付利息",
            "中国居民企业向荷兰公司支付特许权使用费",
        ],
    }


def test_returns_structured_result_for_supported_royalties_case():
    response = client.post(
        "/analyze",
        json={"scenario": "中国居民企业向荷兰支付特许权使用费"},
    )

    assert response.status_code == 200
    assert response.json() == {
        "data_source_used": "stable",
        "supported": True,
        "normalized_input": {
            "payer_country": "CN",
            "payee_country": "NL",
            "transaction_type": "royalties",
        },
        "result": {
            "summary": "Preliminary view: Article 12 Royalties appears relevant, with a treaty rate ceiling of 10%. Manual review is still recommended.",
            "boundary_note": "This is a first-pass treaty pre-review based on limited scenario facts. Final eligibility still depends on additional facts, documents, and analysis outside the current review scope.",
            "immediate_action": "Proceed with standard manual review before relying on the treaty position.",
            "article_number": "12",
            "article_title": "Royalties",
            "source_reference": "Article 12(1)",
            "source_language": "en",
            "source_excerpt": "Royalty treatment is governed by Article 12(1), subject to treaty conditions and factual qualification.",
            "rate": "10%",
            "extraction_confidence": 0.98,
            "auto_conclusion_allowed": True,
            "key_missing_facts": [
                "Whether the payment is truly for qualifying intellectual property use.",
                "Whether the recipient is the beneficial owner of the royalty income.",
                "Whether the contract and payment flow support treaty characterization.",
            ],
            "review_checklist": [
                "Confirm the payment is actually for the use of, or right to use, qualifying intellectual property.",
                "Confirm the recipient is the beneficial owner of the royalty income.",
                "Check the underlying contract, invoice, and payment flow for factual consistency.",
            ],
            "conditions": [
                "Treaty applicability depends on the facts of the payment."
            ],
            "notes": [
                "Beneficial ownership and factual qualification may matter."
            ],
            "human_review_required": True,
            "review_priority": "normal",
            "review_reason": "Final eligibility depends on facts outside the current review scope.",
        },
    }


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
        "Preliminary view: Article 10 Dividends appears relevant, with a treaty rate ceiling of 10%. "
        "Manual review is still recommended."
    )
    assert response.json()["result"]["boundary_note"] == (
        "This is a first-pass treaty pre-review based on limited scenario facts. Final eligibility still depends on additional facts, documents, and analysis outside the current review scope."
    )
    assert response.json()["result"]["immediate_action"] == (
        "Proceed with standard manual review before relying on the treaty position."
    )
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
    assert response.json() == {
        "data_source_used": "stable",
        "supported": False,
        "reason": "unsupported_transaction_type",
        "message": "Current MVP supports only dividends, interest, and royalties.",
        "immediate_action": "Restate the payment using a supported income type before relying on treaty review output.",
        "missing_fields": ["transaction_type"],
        "suggested_format": "Try a sentence like: 中国居民企业向荷兰公司支付特许权使用费",
        "suggested_examples": [
            "中国居民企业向荷兰公司支付股息",
            "中国居民企业向荷兰银行支付利息",
            "中国居民企业向荷兰公司支付特许权使用费",
        ],
    }


def test_rejects_incomplete_scenario_when_country_pair_cannot_be_confirmed():
    response = client.post(
        "/analyze",
        json={"scenario": "向荷兰公司支付股息"},
    )

    assert response.status_code == 200
    assert response.json() == {
        "data_source_used": "stable",
        "supported": False,
        "reason": "incomplete_scenario",
        "message": "Please provide a clearer scenario with both payer and payee country context.",
        "immediate_action": "Add the missing scenario facts before running the treaty review again.",
        "missing_fields": ["payer_country"],
        "suggested_format": "Try a sentence like: 中国居民企业向荷兰公司支付股息",
        "suggested_examples": [
            "中国居民企业向荷兰公司支付股息",
            "荷兰公司向中国公司支付利息",
        ],
    }


def test_incomplete_alias_input_gets_bridge_note_but_keeps_formal_template():
    response = client.post(
        "/analyze",
        json={"scenario": "向荷兰公司支付软件许可费"},
    )

    assert response.status_code == 200
    assert response.json() == {
        "data_source_used": "stable",
        "supported": False,
        "reason": "incomplete_scenario",
        "message": "Please provide a clearer scenario with both payer and payee country context.",
        "immediate_action": "Add the missing scenario facts before running the treaty review again.",
        "missing_fields": ["payer_country"],
        "classification_note": (
            "Current review maps `软件许可费` into the royalties lane for first-pass treaty review. "
            "Use a fuller scenario so the tool can test the treaty position under the standard treaty royalties framework."
        ),
        "suggested_format": "Try a sentence like: 中国居民企业向荷兰公司支付特许权使用费",
        "suggested_examples": [
            "中国居民企业向荷兰公司支付股息",
            "荷兰公司向中国公司支付利息",
        ],
    }


def test_rejects_ambiguous_payer_country_instead_of_guessing():
    response = client.post(
        "/analyze",
        json={"scenario": "中国公司和荷兰公司向荷兰公司支付股息"},
    )

    assert response.status_code == 200
    assert response.json() == {
        "data_source_used": "stable",
        "supported": False,
        "reason": "incomplete_scenario",
        "message": "Please provide a clearer scenario with both payer and payee country context.",
        "immediate_action": "Add the missing scenario facts before running the treaty review again.",
        "missing_fields": ["payer_country"],
        "suggested_format": "Try a sentence like: 中国居民企业向荷兰公司支付股息",
        "suggested_examples": [
            "中国居民企业向荷兰公司支付股息",
            "荷兰公司向中国公司支付利息",
        ],
    }


def test_rejects_ambiguous_payee_country_instead_of_guessing():
    response = client.post(
        "/analyze",
        json={"scenario": "中国居民企业向荷兰公司或美国公司支付特许权使用费"},
    )

    assert response.status_code == 200
    assert response.json() == {
        "data_source_used": "stable",
        "supported": False,
        "reason": "incomplete_scenario",
        "message": "Please provide a clearer scenario with both payer and payee country context.",
        "immediate_action": "Add the missing scenario facts before running the treaty review again.",
        "missing_fields": ["payee_country"],
        "suggested_format": "Try a sentence like: 中国居民企业向荷兰公司支付特许权使用费",
        "suggested_examples": [
            "中国居民企业向荷兰公司支付股息",
            "荷兰公司向中国公司支付利息",
        ],
    }


def test_rejects_unsupported_country_pair_with_supported_scope_examples():
    response = client.post(
        "/analyze",
        json={"scenario": "中国居民企业向美国支付特许权使用费"},
    )

    assert response.status_code == 200
    assert response.json() == {
        "data_source_used": "stable",
        "supported": False,
        "reason": "unsupported_country_pair",
        "message": "Current MVP supports only China-Netherlands treaty scenarios.",
        "immediate_action": "Rewrite the scenario into the supported China-Netherlands scope before running another review.",
        "missing_fields": [],
        "suggested_format": "Try a sentence like: 中国居民企业向荷兰公司支付特许权使用费",
        "suggested_examples": [
            "中国居民企业向荷兰公司支付股息",
            "中国居民企业向荷兰银行支付利息",
            "中国居民企业向荷兰公司支付特许权使用费",
        ],
    }


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
                        "paragraph_label": "Article 12(1)",
                        "source_reference": "Article 12(1)",
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
    assert response.json() == {
        "data_source_used": "stable",
        "supported": False,
        "reason": "unsupported_country_pair",
        "message": "Current MVP supports only China-Netherlands treaty scenarios.",
        "immediate_action": "Rewrite the scenario into the supported China-Netherlands scope before running another review.",
        "missing_fields": [],
        "suggested_format": "Try a sentence like: 中国居民企业向荷兰公司支付特许权使用费",
        "suggested_examples": [
            "中国居民企业向荷兰公司支付股息",
            "中国居民企业向荷兰银行支付利息",
            "中国居民企业向荷兰公司支付特许权使用费",
        ],
        "input_interpretation": {
            "parser_source": "llm",
            "payer_country": "CN",
            "payee_country": "US",
            "transaction_type": "dividends",
            "matched_transaction_label": "股息",
        },
    }


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
    assert response.json() == {
        "data_source_used": "stable",
        "supported": False,
        "reason": "incomplete_scenario",
        "message": "Please provide a clearer scenario with both payer and payee country context.",
        "immediate_action": "Add the missing scenario facts before running the treaty review again.",
        "missing_fields": [
            "payer_country",
            "payee_country",
            "transaction_type",
        ],
        "suggested_format": "Try a sentence like: 中国居民企业向荷兰公司支付特许权使用费",
        "suggested_examples": [
            "中国居民企业向荷兰公司支付股息",
            "荷兰公司向中国公司支付利息",
        ],
        "input_interpretation": {
            "parser_source": "llm",
            "payer_country": None,
            "payee_country": None,
            "transaction_type": "unknown",
            "matched_transaction_label": None,
        },
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


def test_analyze_uses_llm_generated_dataset_when_requested(tmp_path: Path, monkeypatch):
    stable_payload = json.loads(Path(service.DATA_PATH).read_text(encoding="utf-8"))
    llm_payload = json.loads(Path(service.DATA_PATH).read_text(encoding="utf-8"))

    stable_payload["articles"][2]["paragraphs"][0]["source_reference"] = "Article 12(1)"
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
    assert default_response.json()["result"]["source_reference"] == "Article 12(1)"
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
    assert response.json()["result"]["rate"] == "10%"
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
    assert response.json()["result"]["alternative_rate_candidates"] == [
        {
            "source_reference": "Article 10(2)",
            "rate": "5%",
            "conditions": [
                "Reduced rate branch if the ownership threshold is satisfied."
            ],
        }
    ]
