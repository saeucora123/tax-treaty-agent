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
