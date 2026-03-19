import json
import importlib.util
from pathlib import Path

import pytest

from app import llm_document_extractor, source_ingest


REPO_ROOT = Path(__file__).resolve().parents[2]
SOURCE_INGEST_SCRIPT_PATH = REPO_ROOT / "scripts" / "run_source_ingest.py"


class FakeHTTPResponse:
    def __init__(self, payload: dict):
        self._payload = json.dumps(payload).encode("utf-8")

    def read(self) -> bytes:
        return self._payload

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False


def load_source_ingest_script_module():
    spec = importlib.util.spec_from_file_location("run_source_ingest_script", SOURCE_INGEST_SCRIPT_PATH)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_llm_document_extractor_generates_pair_agnostic_rule_ids(monkeypatch):
    config = llm_document_extractor.LLMInputParserConfig(
        api_key="test-key",
        base_url="https://example.com",
        model="deepseek-chat",
        timeout_seconds=5,
    )
    monkeypatch.setattr(
        llm_document_extractor.request,
        "urlopen",
        lambda req, timeout: FakeHTTPResponse(
            {
                "choices": [
                    {
                        "message": {
                            "content": json.dumps(
                                {
                                    "parsed_articles": [
                                        {
                                            "article_number": "12",
                                            "article_title": "Royalties",
                                            "income_type": "royalties",
                                            "summary": "Treaty treatment for royalties.",
                                            "article_notes": [],
                                            "paragraphs": [
                                                {
                                                    "paragraph_number": "2",
                                                    "source_reference": "Article 12(2)",
                                                    "text": "However, such royalties may also be taxed in the first-mentioned State, but the tax so charged shall not exceed 10 per cent of the gross amount of the royalties.",
                                                    "rules": [
                                                        {
                                                            "rule_type": "source_tax_limit",
                                                            "rate": "10%",
                                                            "direction": "payer_to_payee",
                                                            "conditions": [
                                                                "General royalties branch."
                                                            ],
                                                            "review_reason": "General royalties branch.",
                                                            "extraction_confidence": 0.97,
                                                        }
                                                    ],
                                                }
                                            ],
                                        }
                                    ]
                                }
                            )
                        }
                    }
                ]
            }
        ),
    )

    payload = llm_document_extractor.extract_source_payload_from_text(
        raw_text=(
            "Article 12 Royalties\n"
            "2. However, such royalties may also be taxed in the first-mentioned State, "
            "but the tax so charged shall not exceed 10 per cent of the gross amount of the royalties."
        ),
        document_id="cn-kr-main-treaty",
        title="China-Korea Tax Treaty",
        document_type="treaty_text",
        jurisdictions=["CN", "KR"],
        source_language="en",
        config=config,
    )

    rule = payload["parsed_articles"][0]["paragraphs"][0]["extracted_rules"][0]
    assert rule["rule_id"] == "cn-kr-art12-p2-r1"


def test_build_source_document_from_manifest_merges_raw_and_pdf_sources(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
):
    raw_input_path = tmp_path / "cn-kr-article10.txt"
    pdf_input_path = tmp_path / "cn-kr-article11-12.pdf"
    raw_input_path.write_text("Article 10 text", encoding="utf-8")
    pdf_input_path.write_bytes(b"%PDF-1.4 stub")

    raw_parsed_output_path = tmp_path / "raw.parsed.json"
    pdf_raw_text_output_path = tmp_path / "pdf.extracted.txt"
    pdf_parsed_output_path = tmp_path / "pdf.parsed.json"
    output_source_document = tmp_path / "cn-kr-main-treaty.json"
    build_report_output = tmp_path / "cn-kr-main-treaty.build.report.json"

    manifest = {
        "pair_id": "cn-kr",
        "jurisdictions": ["CN", "KR"],
        "target_articles": ["10", "11", "12"],
        "document": {
            "document_id": "cn-kr-main-treaty",
            "title": "China-Korea Tax Treaty",
            "document_type": "treaty_text",
            "source_trace": {
                "treaty_full_name": "China-Korea Tax Treaty",
                "version_note": "Test source trace.",
                "source_document_title": "China-Korea Tax Treaty",
                "language_version": "en",
                "official_source_ids": ["nts-cn-kr-treaty-text"],
                "working_papers": {
                    "dividends": "docs/test-dividends.md",
                    "interest": "docs/test-interest.md",
                    "royalties": "docs/test-royalties.md",
                },
            },
            "mli_context": {
                "covered_tax_agreement": False,
                "ppt_applies": False,
                "summary": "MLI review signal only.",
                "human_review_note": "Keep manual review.",
                "official_source_ids": ["oecd-mli-signatories-and-parties"],
            },
            "notes": ["Generated during source-build test."],
        },
        "sources": [
            {
                "source_id": "nts-cn-kr-treaty-text",
                "source_type": "raw_text",
                "input_path": str(raw_input_path),
                "parsed_output_path": str(raw_parsed_output_path),
                "document_id": "cn-kr-article10-text",
                "title": "China-Korea Treaty Article 10 Text",
                "document_type": "treaty_text",
                "language": "en",
            },
            {
                "source_id": "unts-cn-kr-treaty-pdf",
                "source_type": "pdf_text",
                "input_path": str(pdf_input_path),
                "raw_text_output_path": str(pdf_raw_text_output_path),
                "parsed_output_path": str(pdf_parsed_output_path),
                "document_id": "cn-kr-article11-12-pdf",
                "title": "China-Korea Treaty PDF",
                "document_type": "treaty_text",
                "language": "en",
            },
        ],
        "output_source_document": str(output_source_document),
        "build_report_output": str(build_report_output),
    }
    manifest_path = tmp_path / "cn-kr-main-treaty.build.json"
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    raw_payload = {
        "document": {
            "document_id": "cn-kr-article10-text",
            "title": "China-Korea Treaty Article 10 Text",
            "document_type": "treaty_text",
            "jurisdictions": ["CN", "KR"],
            "notes": ["Generated by constrained LLM document extraction."],
        },
        "parsed_articles": [
            {
                "article_number": "10",
                "article_title": "Dividends",
                "article_label": "Article 10",
                "income_type": "dividends",
                "summary": "Dividends article.",
                "article_notes": [],
                "paragraphs": [
                    {
                        "paragraph_id": "art10-p2",
                        "paragraph_label": "Article 10(2)",
                        "source_reference": "Article 10(2)",
                        "source_language": "en",
                        "source_segments": [
                            {
                                "segment_id": "art10-p2-s1",
                                "segment_order": 1,
                                "page_hint": None,
                                "source_kind": "article_paragraph",
                                "text_quality": "clean",
                                "normalization_status": "verbatim",
                                "text": "Dividend paragraph.",
                            }
                        ],
                        "extracted_rules": [
                            {
                                "rule_id": "cn-kr-art10-p2-r1",
                                "rule_type": "source_tax_limit",
                                "rate": "10%",
                                "direction": "bidirectional",
                                "candidate_rank": 1,
                                "is_primary_candidate": True,
                                "extraction_confidence": 0.97,
                                "derived_from_segments": ["art10-p2-s1"],
                                "conditions": ["General dividends branch."],
                                "human_review_required": True,
                                "review_reason": "General dividends branch.",
                            }
                        ],
                    }
                ],
            }
        ],
    }
    pdf_payload = {
        "document": {
            "document_id": "cn-kr-article11-12-pdf",
            "title": "China-Korea Treaty PDF",
            "document_type": "treaty_text",
            "jurisdictions": ["CN", "KR"],
            "notes": ["Generated by constrained LLM document extraction."],
        },
        "parsed_articles": [
            {
                "article_number": "11",
                "article_title": "Interest",
                "article_label": "Article 11",
                "income_type": "interest",
                "summary": "Interest article.",
                "article_notes": [],
                "paragraphs": [
                    {
                        "paragraph_id": "art11-p2",
                        "paragraph_label": "Article 11(2)",
                        "source_reference": "Article 11(2)",
                        "source_language": "en",
                        "source_segments": [
                            {
                                "segment_id": "art11-p2-s1",
                                "segment_order": 1,
                                "page_hint": 4,
                                "source_kind": "article_paragraph",
                                "text_quality": "clean",
                                "normalization_status": "verbatim",
                                "text": "Interest paragraph.",
                            }
                        ],
                        "extracted_rules": [
                            {
                                "rule_id": "cn-kr-art11-p2-r1",
                                "rule_type": "source_tax_limit",
                                "rate": "10%",
                                "direction": "bidirectional",
                                "candidate_rank": 1,
                                "is_primary_candidate": True,
                                "extraction_confidence": 0.97,
                                "derived_from_segments": ["art11-p2-s1"],
                                "conditions": ["General interest branch."],
                                "human_review_required": True,
                                "review_reason": "General interest branch.",
                            }
                        ],
                    }
                ],
            },
            {
                "article_number": "12",
                "article_title": "Royalties",
                "article_label": "Article 12",
                "income_type": "royalties",
                "summary": "Royalties article.",
                "article_notes": [],
                "paragraphs": [
                    {
                        "paragraph_id": "art12-p2",
                        "paragraph_label": "Article 12(2)",
                        "source_reference": "Article 12(2)",
                        "source_language": "en",
                        "source_segments": [
                            {
                                "segment_id": "art12-p2-s1",
                                "segment_order": 1,
                                "page_hint": 5,
                                "source_kind": "article_paragraph",
                                "text_quality": "clean",
                                "normalization_status": "verbatim",
                                "text": "Royalties paragraph.",
                            }
                        ],
                        "extracted_rules": [
                            {
                                "rule_id": "cn-kr-art12-p2-r1",
                                "rule_type": "source_tax_limit",
                                "rate": "10%",
                                "direction": "bidirectional",
                                "candidate_rank": 1,
                                "is_primary_candidate": True,
                                "extraction_confidence": 0.97,
                                "derived_from_segments": ["art12-p2-s1"],
                                "conditions": ["General royalties branch."],
                                "human_review_required": True,
                                "review_reason": "General royalties branch.",
                            }
                        ],
                    }
                ],
            },
        ],
    }

    monkeypatch.setattr(
        source_ingest,
        "extract_source_payload_from_text",
        lambda raw_text, **kwargs: raw_payload
        if kwargs["document_id"] == "cn-kr-article10-text"
        else pdf_payload,
    )
    monkeypatch.setattr(
        source_ingest,
        "load_known_source_ids",
        lambda pair_id: {"nts-cn-kr-treaty-text", "unts-cn-kr-treaty-pdf"},
    )
    monkeypatch.setattr(
        source_ingest,
        "extract_pdf_text",
        lambda path: "Article 11 Interest\nArticle 12 Royalties",
    )

    result = source_ingest.run_source_build(manifest_path)

    assert result["status"] == "ok"
    assert output_source_document.exists()
    built_source = json.loads(output_source_document.read_text(encoding="utf-8"))
    assert built_source["document"]["document_id"] == "cn-kr-main-treaty"
    assert built_source["document"]["source_trace"]["official_source_ids"] == [
        "nts-cn-kr-treaty-text"
    ]
    assert [article["article_number"] for article in built_source["parsed_articles"]] == [
        "10",
        "11",
        "12",
    ]
    assert raw_parsed_output_path.exists()
    assert pdf_parsed_output_path.exists()
    assert pdf_raw_text_output_path.exists()
    report = json.loads(build_report_output.read_text(encoding="utf-8"))
    assert report["status"] == "ok"
    assert report["article_count"] == 3
    assert report["missing_target_articles"] == []


def test_build_source_document_from_manifest_rejects_missing_target_article_coverage(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
):
    input_path = tmp_path / "cn-kr-article10.txt"
    input_path.write_text("Article 10 text", encoding="utf-8")
    manifest = {
        "pair_id": "cn-kr",
        "jurisdictions": ["CN", "KR"],
        "target_articles": ["10", "11", "12"],
        "document": {
            "document_id": "cn-kr-main-treaty",
            "title": "China-Korea Tax Treaty",
            "document_type": "treaty_text",
            "source_trace": {
                "treaty_full_name": "China-Korea Tax Treaty",
                "version_note": "Test source trace.",
                "source_document_title": "China-Korea Tax Treaty",
                "language_version": "en",
                "official_source_ids": ["nts-cn-kr-treaty-text"],
                "working_papers": {
                    "dividends": "docs/test-dividends.md",
                    "interest": "docs/test-interest.md",
                    "royalties": "docs/test-royalties.md",
                },
            },
            "mli_context": {
                "covered_tax_agreement": False,
                "ppt_applies": False,
                "summary": "MLI review signal only.",
                "human_review_note": "Keep manual review.",
                "official_source_ids": ["oecd-mli-signatories-and-parties"],
            },
            "notes": [],
        },
        "sources": [
            {
                "source_id": "nts-cn-kr-treaty-text",
                "source_type": "raw_text",
                "input_path": str(input_path),
                "parsed_output_path": str(tmp_path / "raw.parsed.json"),
                "document_id": "cn-kr-article10-text",
                "title": "China-Korea Treaty Article 10 Text",
                "document_type": "treaty_text",
                "language": "en",
            }
        ],
        "output_source_document": str(tmp_path / "cn-kr-main-treaty.json"),
        "build_report_output": str(tmp_path / "cn-kr-main-treaty.build.report.json"),
    }
    manifest_path = tmp_path / "cn-kr-main-treaty.build.json"
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    monkeypatch.setattr(
        source_ingest,
        "extract_source_payload_from_text",
        lambda raw_text, **kwargs: {
            "document": {
                "document_id": "cn-kr-article10-text",
                "title": "China-Korea Treaty Article 10 Text",
                "document_type": "treaty_text",
                "jurisdictions": ["CN", "KR"],
                "notes": [],
            },
            "parsed_articles": [
                {
                    "article_number": "10",
                    "article_title": "Dividends",
                    "article_label": "Article 10",
                    "income_type": "dividends",
                    "summary": "Dividends article.",
                    "article_notes": [],
                    "paragraphs": [
                        {
                            "paragraph_id": "art10-p2",
                            "paragraph_label": "Article 10(2)",
                            "source_reference": "Article 10(2)",
                            "source_language": "en",
                            "source_segments": [
                                {
                                    "segment_id": "art10-p2-s1",
                                    "segment_order": 1,
                                    "page_hint": None,
                                    "source_kind": "article_paragraph",
                                    "text_quality": "clean",
                                    "normalization_status": "verbatim",
                                    "text": "Dividend paragraph.",
                                }
                            ],
                            "extracted_rules": [
                                {
                                    "rule_id": "cn-kr-art10-p2-r1",
                                    "rule_type": "source_tax_limit",
                                    "rate": "10%",
                                    "direction": "bidirectional",
                                    "candidate_rank": 1,
                                    "is_primary_candidate": True,
                                    "extraction_confidence": 0.97,
                                    "derived_from_segments": ["art10-p2-s1"],
                                    "conditions": ["General dividends branch."],
                                    "human_review_required": True,
                                    "review_reason": "General dividends branch.",
                                }
                            ],
                        }
                    ],
                }
            ],
        },
    )
    monkeypatch.setattr(
        source_ingest,
        "load_known_source_ids",
        lambda pair_id: {"nts-cn-kr-treaty-text"},
    )

    with pytest.raises(source_ingest.SourceBuildError, match="Missing target articles"):
        source_ingest.run_source_build(manifest_path)


def test_run_source_ingest_script_supports_manifest_mode(monkeypatch: pytest.MonkeyPatch, tmp_path: Path):
    module = load_source_ingest_script_module()
    manifest_path = tmp_path / "cn-kr-main-treaty.build.json"
    manifest_path.write_text("{}", encoding="utf-8")

    monkeypatch.setattr(
        module,
        "parse_args",
        lambda: type(
            "Args",
            (),
            {
                "manifest": manifest_path,
                "catalog": None,
                "summary_output": None,
            },
        )(),
    )
    monkeypatch.setattr(
        module.formal_source_ingest,
        "run_source_build",
        lambda path: {
            "status": "ok",
            "article_count": 3,
            "missing_target_articles": [],
        },
    )

    assert module.main() == 0
