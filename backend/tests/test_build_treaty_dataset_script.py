from __future__ import annotations

import importlib.util
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT_PATH = REPO_ROOT / "scripts" / "build_treaty_dataset.py"
CN_SG_SOURCE_PATH = REPO_ROOT / "data" / "source_documents" / "cn-sg-main-treaty.json"


spec = importlib.util.spec_from_file_location("build_treaty_dataset_script", SCRIPT_PATH)
module = importlib.util.module_from_spec(spec)
assert spec is not None and spec.loader is not None
spec.loader.exec_module(module)


def test_generic_builder_preserves_second_pair_metadata():
    payload = module.load_source_document(CN_SG_SOURCE_PATH)

    dataset = module.build_dataset(payload)

    assert dataset["treaty"]["treaty_id"] == "cn-sg"
    assert dataset["treaty"]["jurisdictions"] == ["CN", "SG"]
    assert dataset["treaty"]["title"] == "China-Singapore Tax Treaty"
    assert "pair-agnostic" in dataset["treaty"]["notes"][0]


def test_generic_builder_keeps_second_pair_article_structure():
    payload = module.load_source_document(CN_SG_SOURCE_PATH)

    dataset = module.build_dataset(payload)

    assert [article["income_type"] for article in dataset["articles"]] == [
        "dividends",
        "interest",
        "royalties",
    ]
    assert dataset["articles"][0]["paragraphs"][0]["source_reference"] == "CN-SG Article 10(2)(b)"
    assert dataset["articles"][1]["paragraphs"][1]["rules"][0]["rate"] == "7%"


def test_generic_builder_preserves_optional_source_trace_metadata():
    payload = module.load_source_document(CN_SG_SOURCE_PATH)

    dataset = module.build_dataset(payload)

    assert dataset["treaty"]["source_trace"]["language_version"] == "en"
    assert "iras-cn-sg-dta-full-text-pdf" in dataset["treaty"]["source_trace"]["official_source_ids"]
    assert dataset["treaty"]["mli_context"]["ppt_applies"] is True
