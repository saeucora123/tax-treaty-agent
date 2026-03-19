from fastapi.testclient import TestClient

from app.main import app
from app import main as main_module


client = TestClient(app)


def test_internal_onboarding_manifests_endpoint_lists_available_manifests(monkeypatch):
    monkeypatch.setattr(
        main_module,
        "list_onboarding_manifests",
        lambda: [
            {
                "manifest_path": "D:/repo/data/onboarding/manifests/cn-kr.initial-oecd.json",
                "pair_id": "cn-kr",
                "mode": "initial_onboarding",
                "jurisdictions": ["CN", "KR"],
                "target_articles": ["10", "11", "12"],
                "baseline_enabled": True,
                "source_build_manifest_path": "D:/repo/data/source_documents/manifests/cn-kr-main-treaty.build.json",
                "source_build_available": True,
            }
        ],
    )

    response = client.get("/internal/onboarding/manifests")

    assert response.status_code == 200
    payload = response.json()
    assert payload["manifests"][0]["pair_id"] == "cn-kr"
    assert payload["manifests"][0]["mode"] == "initial_onboarding"


def test_internal_onboarding_workspace_endpoint_returns_workspace_snapshot(monkeypatch):
    monkeypatch.setattr(
        main_module,
        "build_workspace",
        lambda manifest: {
            "manifest": {
                "manifest_path": manifest,
                "pair_id": "cn-kr",
                "mode": "initial_onboarding",
                "source_build_available": True,
            },
            "source_build": {"status": "ok", "report": {"article_count": 3}},
            "compile": {
                "status": "ok",
                "report": {"rule_count": 4},
                "delta_report": {"delta_item_count": 4, "high_materiality_count": 2},
                "delta_analysis": [{"summary": "Delta item"}],
            },
            "review": {"status": "ready_for_approval", "report": {"status": "ready_for_approval"}},
            "approval": {"status": None, "record": None},
            "promotion": {"status": None, "record": None},
            "timing": {
                "status": "not_started",
                "durations": {"review_seconds": None, "end_to_end_seconds": None},
                "review_session_active": False,
            },
            "reviewed_source": {"path": "D:/repo/reviewed.source.json", "content": "{\"ok\": true}"},
        },
    )

    response = client.get(
        "/internal/onboarding/workspace",
        params={"manifest": "D:/repo/data/onboarding/manifests/cn-kr.initial-oecd.json"},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["manifest"]["pair_id"] == "cn-kr"
    assert payload["compile"]["delta_report"]["delta_item_count"] == 4
    assert payload["timing"]["status"] == "not_started"
    assert payload["reviewed_source"]["content"] == "{\"ok\": true}"


def test_internal_onboarding_review_endpoint_persists_editor_content_before_review(monkeypatch):
    calls: list[tuple[str, str]] = []

    monkeypatch.setattr(
        main_module,
        "save_reviewed_source_json",
        lambda manifest, reviewed_source_json: calls.append((manifest, reviewed_source_json)),
    )
    monkeypatch.setattr(main_module, "run_review", lambda manifest: None)
    monkeypatch.setattr(
        main_module,
        "build_workspace",
        lambda manifest: {
            "manifest": {"manifest_path": manifest, "pair_id": "cn-kr"},
            "review": {"status": "ready_for_approval", "report": {"status": "ready_for_approval"}},
            "reviewed_source": {"path": "D:/repo/reviewed.source.json", "content": "{\"reviewed\": true}"},
        },
    )

    response = client.post(
        "/internal/onboarding/review",
        json={
            "manifest": "D:/repo/data/onboarding/manifests/cn-kr.initial-oecd.json",
            "reviewed_source_json": "{\"reviewed\": true}",
        },
    )

    assert response.status_code == 200
    assert calls == [
        (
            "D:/repo/data/onboarding/manifests/cn-kr.initial-oecd.json",
            "{\"reviewed\": true}",
        )
    ]
    assert response.json()["review"]["status"] == "ready_for_approval"


def test_internal_onboarding_approve_endpoint_records_reviewer_and_returns_workspace(monkeypatch):
    calls: list[tuple[str, str, str]] = []

    monkeypatch.setattr(
        main_module,
        "run_approve",
        lambda manifest, reviewer_name, note: calls.append((manifest, reviewer_name, note)),
    )
    monkeypatch.setattr(
        main_module,
        "build_workspace",
        lambda manifest: {
            "manifest": {"manifest_path": manifest, "pair_id": "cn-kr"},
            "approval": {"status": "approved", "record": {"reviewer_name": "Tax Reviewer"}},
        },
    )

    response = client.post(
        "/internal/onboarding/approve",
        json={
            "manifest": "D:/repo/data/onboarding/manifests/cn-kr.initial-oecd.json",
            "reviewer_name": "Tax Reviewer",
            "note": "Approved after source-chain review.",
        },
    )

    assert response.status_code == 200
    assert calls == [
        (
            "D:/repo/data/onboarding/manifests/cn-kr.initial-oecd.json",
            "Tax Reviewer",
            "Approved after source-chain review.",
        )
    ]
    assert response.json()["approval"]["status"] == "approved"


def test_internal_onboarding_start_review_endpoint_records_reviewer_and_returns_workspace(monkeypatch):
    calls: list[tuple[str, str, str]] = []

    monkeypatch.setattr(
        main_module,
        "start_review_session",
        lambda manifest, reviewer_name, note: calls.append((manifest, reviewer_name, note)),
    )
    monkeypatch.setattr(
        main_module,
        "build_workspace",
        lambda manifest: {
            "manifest": {"manifest_path": manifest, "pair_id": "cn-kr"},
            "timing": {
                "status": "active_review_session",
                "durations": {"review_seconds": None, "end_to_end_seconds": None},
                "review_session_active": True,
            },
        },
    )

    response = client.post(
        "/internal/onboarding/start-review",
        json={
            "manifest": "D:/repo/data/onboarding/manifests/cn-kr.initial-oecd.json",
            "reviewer_name": "Timing Reviewer",
            "note": "Measured pilot started.",
        },
    )

    assert response.status_code == 200
    assert calls == [
        (
            "D:/repo/data/onboarding/manifests/cn-kr.initial-oecd.json",
            "Timing Reviewer",
            "Measured pilot started.",
        )
    ]
    assert response.json()["timing"]["status"] == "active_review_session"
