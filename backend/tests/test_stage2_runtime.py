import json
from pathlib import Path

from fastapi.testclient import TestClient

from app.main import app
from app import service


client = TestClient(app)


def test_returns_cn_sg_dividend_branch_candidates_from_stable_dataset():
    response = client.post(
        "/analyze",
        json={"scenario": "中国公司向新加坡公司支付股息"},
    )

    assert response.status_code == 200
    assert response.json()["supported"] is True
    assert response.json()["normalized_input"] == {
        "payer_country": "CN",
        "payee_country": "SG",
        "transaction_type": "dividends",
    }
    assert response.json()["result"]["article_number"] == "10"
    assert response.json()["result"]["rate"] == "5% / 10%"
    assert response.json()["result"]["auto_conclusion_allowed"] is False
    assert response.json()["result"]["alternative_rate_candidates"] == [
        {
            "source_reference": "CN-SG Article 10(2)(a)",
            "rate": "5%",
            "conditions": [
                "The beneficial owner is a company (other than a partnership) which holds directly at least 25 per cent of the capital of the company paying the dividends."
            ],
        }
    ]
    assert "sample" not in response.json()["result"]["source_excerpt"].lower()
    assert response.json()["result"]["source_trace"]["language_version"] == "en"
    assert "iras-cn-sg-dta-full-text-pdf" in response.json()["result"]["source_trace"]["official_source_ids"]
    assert response.json()["result"]["source_trace"]["working_paper_ref"].endswith(
        "cn-sg-dividends-working-paper.md"
    )
    assert response.json()["result"]["mli_context"]["covered_tax_agreement"] is True
    assert response.json()["result"]["mli_context"]["ppt_applies"] is True
    assert "PPT" in response.json()["result"]["mli_context"]["summary"]
    assert response.json()["review_state"] == {
        "state_code": "can_be_completed",
        "state_label_zh": "可补全",
        "state_summary": "系统已缩小范围；补充少量关键事实后，可进一步明确结果。",
    }
    assert "fact_completion" not in response.json()
    assert response.json()["handoff_package"]["machine_handoff"] == {
        "schema_version": "slice3.v1",
        "record_kind": "supported",
        "review_state_code": "can_be_completed",
        "recommended_route": "complete_facts_then_rerun",
        "applicable_treaty": "中国-新加坡税收协定",
        "payment_direction": "CN -> SG",
        "income_type": "dividends",
        "article_number": "10",
        "article_title": "Dividends",
        "rate_display": "5% / 10%",
        "auto_conclusion_allowed": False,
        "human_review_required": True,
        "data_source_used": "stable",
        "source_reference": "CN-SG Article 10(2)(b)",
        "source_excerpt": response.json()["result"]["source_excerpt"],
        "treaty_version": response.json()["result"]["source_trace"]["version_note"],
        "mli_summary": response.json()["result"]["mli_context"]["summary"],
        "review_priority": "high",
        "blocking_facts": [
            "Whether the payment is legally a dividend rather than another type of return.",
            "Whether the recipient is the beneficial owner of the dividend income.",
            "Whether shareholding facts support relying on the treaty position.",
        ],
        "next_actions": [
            {
                "priority": "high",
                "action": "先核实股息分支所需的关键事实，再判断候选税率分支。",
                "reason": "当前存在多个可信税率分支，系统不会自动替你选择其一。",
            }
        ],
        "user_declared_facts": [],
        "bo_precheck": {
            "status": "insufficient_facts",
            "reason_code": "legacy_free_text_missing_bo_fact",
            "reason_summary": "The current free-text path does not provide a structured BO fact, so the system cannot emit a stronger BO workflow signal.",
            "facts_considered": [],
            "review_note": "Confirm BO evidence before relying on treaty benefits.",
        },
        "guided_conflict": None,
    }


def test_returns_cn_sg_interest_branch_candidates_from_stable_dataset():
    response = client.post(
        "/analyze",
        json={"scenario": "中国企业向新加坡银行支付利息"},
    )

    assert response.status_code == 200
    assert response.json()["supported"] is True
    assert response.json()["normalized_input"] == {
        "payer_country": "CN",
        "payee_country": "SG",
        "transaction_type": "interest",
    }
    assert response.json()["result"]["article_number"] == "11"
    assert response.json()["result"]["rate"] == "7% / 10%"
    assert response.json()["result"]["auto_conclusion_allowed"] is False
    assert "sample" not in response.json()["result"]["source_excerpt"].lower()
    assert response.json()["result"]["source_trace"]["working_paper_ref"].endswith(
        "cn-sg-interest-working-paper.md"
    )
    assert "fact_completion" not in response.json()


def test_returns_cn_sg_royalties_single_rate_from_stable_dataset():
    response = client.post(
        "/analyze",
        json={"scenario": "中国居民企业向新加坡公司支付特许权使用费"},
    )

    assert response.status_code == 200
    assert response.json()["supported"] is True
    assert response.json()["normalized_input"] == {
        "payer_country": "CN",
        "payee_country": "SG",
        "transaction_type": "royalties",
    }
    assert response.json()["result"]["article_number"] == "12"
    assert response.json()["result"]["rate"] == "10%"
    assert "sample" not in response.json()["result"]["source_excerpt"].lower()
    assert response.json()["result"]["source_trace"]["working_paper_ref"].endswith(
        "cn-sg-royalties-working-paper.md"
    )
    assert response.json()["review_state"] == {
        "state_code": "pre_review_complete",
        "state_label_zh": "预审完成",
        "state_summary": "系统已完成第一轮预审，请按标准复核流程继续。",
    }


def test_returns_cn_kr_dividend_branch_candidates_from_stable_dataset():
    response = client.post(
        "/analyze",
        json={"scenario": "中国公司向韩国公司支付股息"},
    )

    assert response.status_code == 200
    assert response.json()["supported"] is True
    assert response.json()["normalized_input"] == {
        "payer_country": "CN",
        "payee_country": "KR",
        "transaction_type": "dividends",
    }
    assert response.json()["result"]["article_number"] == "10"
    assert response.json()["result"]["rate"] == "5% / 10%"
    assert response.json()["result"]["auto_conclusion_allowed"] is False


def test_returns_cn_kr_interest_single_rate_from_stable_dataset():
    response = client.post(
        "/analyze",
        json={"scenario": "中国企业向韩国银行支付利息"},
    )

    assert response.status_code == 200
    assert response.json()["supported"] is True
    assert response.json()["normalized_input"] == {
        "payer_country": "CN",
        "payee_country": "KR",
        "transaction_type": "interest",
    }
    assert response.json()["result"]["article_number"] == "11"
    assert response.json()["result"]["rate"] == "10%"


def test_returns_cn_kr_royalties_single_rate_from_stable_dataset():
    response = client.post(
        "/analyze",
        json={"scenario": "中国居民企业向韩国公司支付特许权使用费"},
    )

    assert response.status_code == 200
    assert response.json()["supported"] is True
    assert response.json()["normalized_input"] == {
        "payer_country": "CN",
        "payee_country": "KR",
        "transaction_type": "royalties",
    }
    assert response.json()["result"]["article_number"] == "12"
    assert response.json()["result"]["rate"] == "10%"


def test_supports_reverse_direction_sg_to_cn_case():
    response = client.post(
        "/analyze",
        json={"scenario": "新加坡公司向中国公司支付利息"},
    )

    assert response.status_code == 200
    assert response.json()["supported"] is True
    assert response.json()["normalized_input"] == {
        "payer_country": "SG",
        "payee_country": "CN",
        "transaction_type": "interest",
    }
    assert response.json()["confirmed_scope"] == {
        "applicable_treaty": "中国-新加坡税收协定",
        "applicable_article": "Article 11 - Interest",
        "payment_direction": "SG -> CN",
        "income_type": "interest",
    }


def test_returns_controlled_unavailable_data_source_for_cn_sg_llm_generated_request():
    response = client.post(
        "/internal/analyze",
        json={
            "scenario": "中国居民企业向新加坡公司支付特许权使用费",
            "data_source": "llm_generated",
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert {
        key: value
        for key, value in payload.items()
        if key not in {"handoff_package", "input_interpretation"}
    } == {
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
            "input_mode_used": "free_text",
        "schema_version": "slice3.v1",
    }
    if "input_interpretation" in payload:
        assert payload["input_interpretation"]["parser_source"] == "llm"
    assert payload["handoff_package"]["machine_handoff"]["recommended_route"] == "manual_review"
    assert payload["handoff_package"]["human_review_brief"]["disposition"] == (
        "Escalate this scenario for manual review."
    )


def test_detects_singapore_aliases_and_supported_pair_examples():
    response = client.post(
        "/analyze",
        json={"scenario": "中国居民企业向美国支付特许权使用费"},
    )

    assert response.status_code == 200
    assert response.json()["suggested_examples"] == [
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
    assert "supported pilot treaty pair list" in response.json()["immediate_action"].lower()


def test_normalize_country_code_recognizes_singapore_aliases():
    assert service.normalize_country_code("Singapore") == "SG"
    assert service.normalize_country_code("Singaporean") == "SG"
    assert service.detect_country("新加坡公司", country_codes=["SG"]) == "SG"


def test_runtime_registry_routes_to_pair_specific_dataset(tmp_path, monkeypatch):
    cn_nl_payload = json.loads(Path(service.DATA_PATH).read_text(encoding="utf-8"))
    cn_sg_payload = json.loads(
        (
            Path(__file__).resolve().parents[2]
            / "data"
            / "pressure_tests"
            / "cn-sg.stage3.hand-encoded.json"
        ).read_text(encoding="utf-8")
    )

    cn_nl_path = tmp_path / "cn-nl.v3.json"
    cn_sg_path = tmp_path / "cn-sg.v3.json"
    cn_nl_path.write_text(
        json.dumps(cn_nl_payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    cn_sg_path.write_text(
        json.dumps(cn_sg_payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    monkeypatch.setattr(
        service,
        "STABLE_TREATY_REGISTRY",
        {
            ("CN", "NL"): cn_nl_path,
            ("CN", "SG"): cn_sg_path,
        },
    )

    cn_nl_response = client.post(
        "/analyze",
        json={"scenario": "中国居民企业向荷兰支付特许权使用费"},
    )
    cn_sg_response = client.post(
        "/analyze",
        json={"scenario": "中国居民企业向新加坡支付特许权使用费"},
    )

    assert cn_nl_response.status_code == 200
    assert cn_nl_response.json()["supported"] is True
    assert cn_nl_response.json()["result"]["source_reference"] == "Article 12(2)"

    assert cn_sg_response.status_code == 200
    assert cn_sg_response.json()["supported"] is True
    assert cn_sg_response.json()["result"]["source_reference"] == "CN-SG Article 12(2)"
