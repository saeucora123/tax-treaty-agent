from fastapi.testclient import TestClient

from app.main import app


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
            "article_number": "12",
            "article_title": "Royalties",
            "rate": "10%",
            "conditions": [
                "Treaty applicability depends on the facts of the payment."
            ],
            "notes": [
                "Beneficial ownership and factual details may affect the final conclusion."
            ],
            "human_review_required": True,
            "review_reason": "Final eligibility depends on facts beyond v1 scope.",
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
    assert response.json()["result"]["article_number"] == "10"
    assert response.json()["result"]["article_title"] == "Dividends"


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
    }
