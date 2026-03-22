from pathlib import Path

from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def _guided_royalties_payload() -> dict:
    return {
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
    }


def test_create_case_persists_guided_snapshot_and_returns_dual_tokens(
    tmp_path: Path,
    monkeypatch,
):
    monkeypatch.setenv("TAX_TREATY_AGENT_CASE_DB_PATH", str(tmp_path / "cases.sqlite3"))

    response = client.post("/cases", json=_guided_royalties_payload())

    assert response.status_code == 200
    payload = response.json()
    assert payload["case_id"].startswith("case_")
    assert payload["saved_at"]
    assert payload["creator_token"]
    assert payload["reviewer_token"]
    assert payload["creator_token"] != payload["reviewer_token"]
    assert payload["analyze_response_snapshot"]["supported"] is True
    assert (
        payload["analyze_response_snapshot"]["handoff_package"]["authority_memo"]["status"]
        == "available"
    )


def test_create_case_rejects_legacy_free_text_payload(
    tmp_path: Path,
    monkeypatch,
):
    monkeypatch.setenv("TAX_TREATY_AGENT_CASE_DB_PATH", str(tmp_path / "cases.sqlite3"))

    response = client.post(
        "/cases",
        json={"scenario": "中国居民企业向荷兰支付特许权使用费"},
    )

    assert response.status_code == 400
    assert "guided" in response.json()["detail"].lower()


def test_get_case_returns_creator_and_reviewer_views_with_same_saved_snapshot(
    tmp_path: Path,
    monkeypatch,
):
    monkeypatch.setenv("TAX_TREATY_AGENT_CASE_DB_PATH", str(tmp_path / "cases.sqlite3"))

    create_response = client.post("/cases", json=_guided_royalties_payload())
    create_payload = create_response.json()

    creator_response = client.get(
        f"/cases/{create_payload['case_id']}",
        params={"token": create_payload["creator_token"]},
    )
    reviewer_response = client.get(
        f"/cases/{create_payload['case_id']}",
        params={"token": create_payload["reviewer_token"]},
    )

    assert creator_response.status_code == 200
    assert reviewer_response.status_code == 200

    creator_payload = creator_response.json()
    reviewer_payload = reviewer_response.json()

    assert creator_payload["view_role"] == "creator"
    assert creator_payload["reviewer_share_ready"] is True
    assert reviewer_payload["view_role"] == "reviewer"
    assert reviewer_payload["reviewer_share_ready"] is False
    assert creator_payload["request_snapshot"]["guided_input"]["income_type"] == "royalties"
    assert reviewer_payload["request_snapshot"]["guided_input"]["income_type"] == "royalties"
    assert creator_payload["response_snapshot"]["handoff_package"]["authority_memo"]["status"] == "available"
    assert reviewer_payload["response_snapshot"]["handoff_package"]["authority_memo"]["status"] == "available"


def test_get_case_returns_same_not_found_for_unknown_case_and_invalid_token(
    tmp_path: Path,
    monkeypatch,
):
    monkeypatch.setenv("TAX_TREATY_AGENT_CASE_DB_PATH", str(tmp_path / "cases.sqlite3"))

    create_response = client.post("/cases", json=_guided_royalties_payload())
    create_payload = create_response.json()

    invalid_token_response = client.get(
        f"/cases/{create_payload['case_id']}",
        params={"token": "not-a-real-token"},
    )
    unknown_case_response = client.get(
        "/cases/case_missing",
        params={"token": create_payload["creator_token"]},
    )

    assert invalid_token_response.status_code == 404
    assert unknown_case_response.status_code == 404
    assert invalid_token_response.json() == unknown_case_response.json()


def test_workpaper_html_contains_saved_workflow_authority_and_boundary_sections(
    tmp_path: Path,
    monkeypatch,
):
    monkeypatch.setenv("TAX_TREATY_AGENT_CASE_DB_PATH", str(tmp_path / "cases.sqlite3"))

    create_response = client.post("/cases", json=_guided_royalties_payload())
    create_payload = create_response.json()

    response = client.get(
        f"/cases/{create_payload['case_id']}/workpaper",
        params={"token": create_payload["reviewer_token"]},
    )

    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]
    assert response.headers["content-disposition"] == (
        f'inline; filename="{create_payload["case_id"]}-workpaper.html"'
    )
    assert "READ-ONLY WORKPAPER" in response.text
    assert "Tax Treaty Agent Pre-Review Workpaper" in response.text
    assert create_payload["case_id"] in response.text
    assert "Case Summary" in response.text
    assert "Reviewer Risk Summary" in response.text
    assert "Saved Facts / Scenario Snapshot" in response.text
    assert "Source Chain" in response.text
    assert "BO precheck (no_initial_flag)" in response.text
    assert "beneficial_owner (DATA_MISSING)" in response.text
    assert "domestic_law (DATA_MISSING)" in response.text
    assert "Has the recipient&#x27;s beneficial-owner status for the royalty income been separately confirmed?" in response.text
    assert "Facts To Verify" in response.text
    assert "Workflow Handoff" in response.text
    assert "Authority Memo" in response.text
    assert "Coverage Gaps" in response.text
    assert "This is a first-pass treaty pre-review based on limited scenario facts." in response.text
