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
        "/internal/analyze",
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
        "/internal/analyze",
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
        "/internal/analyze",
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
