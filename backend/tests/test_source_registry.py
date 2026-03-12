import json
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
REGISTRY_PATH = REPO_ROOT / "data" / "source_registry" / "cn-nl-official-sources.json"
USAGE_MAP_PATH = REPO_ROOT / "data" / "source_registry" / "cn-nl-source-usage-map.json"


def test_cn_nl_source_registry_covers_primary_treaty_and_mli_sources():
    registry = json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))

    assert registry["registry_id"] == "cn-nl-official-sources"
    assert registry["jurisdiction_pair"] == ["CN", "NL"]

    sources = registry["sources"]
    source_ids = {source["source_id"] for source in sources}
    issuing_authorities = {source["issuing_authority"] for source in sources}
    source_types = {source["source_type"] for source in sources}
    preferred_uses = {source["preferred_use"] for source in sources}

    assert "sat-cn-nl-2013-zh-pdf" in source_ids
    assert "sat-cn-nl-2013-en-pdf" in source_ids
    assert "sat-cn-nl-mli-en-pdf" in source_ids
    assert "nl-2013-consolidated-text" in source_ids
    assert "State Taxation Administration of the PRC" in issuing_authorities
    assert "Kingdom of the Netherlands Treaty Database" in issuing_authorities
    assert "treaty_text" in source_types
    assert "mli_synthesized_text" in source_types
    assert "primary_runtime_basis" in preferred_uses
    assert "mli_context_only" in preferred_uses

    for source in sources:
        assert source["status"] in {"confirmed", "needs_manual_open"}
        assert source["official_url"].startswith("http")


def test_cn_nl_source_usage_map_references_known_sources_and_existing_artifacts():
    registry = json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))
    usage_map = json.loads(USAGE_MAP_PATH.read_text(encoding="utf-8"))

    known_source_ids = {source["source_id"] for source in registry["sources"]}

    assert usage_map["registry_id"] == registry["registry_id"]

    for artifact in usage_map["artifacts"]:
        artifact_path = REPO_ROOT / artifact["artifact_path"]
        assert artifact_path.exists(), artifact["artifact_path"]
        assert artifact["governance_status"] in {
            "curated_subset",
            "verified_excerpt",
            "llm_generated_demo_artifact",
        }
        for source_id in artifact["derived_from_source_ids"]:
            assert source_id in known_source_ids
