import json
import subprocess
import sys
from pathlib import Path

from app import service


REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT_PATH = REPO_ROOT / "scripts" / "build_treaty_dataset.py"
SOURCE_PATH = REPO_ROOT / "data" / "source_documents" / "cn-nl-main-treaty.json"
RAW_PARSE_SCRIPT_PATH = REPO_ROOT / "scripts" / "experimental" / "parse_cn_nl_raw_text_stub.py"
RAW_INGEST_SCRIPT_PATH = REPO_ROOT / "scripts" / "experimental" / "ingest_cn_nl_raw_text_stub.py"
PDF_INGEST_SCRIPT_PATH = REPO_ROOT / "scripts" / "experimental" / "ingest_cn_nl_pdf_stub.py"
SOURCE_INGEST_SCRIPT_PATH = REPO_ROOT / "scripts" / "run_source_ingest.py"
RAW_TEXT_PATH = REPO_ROOT / "data" / "raw_documents" / "cn-nl-article12.stub.txt"
RAW_MULTI_TEXT_PATH = REPO_ROOT / "data" / "raw_documents" / "cn-nl-multi-article.stub.txt"
RAW_SEMI_STRUCTURED_TEXT_PATH = (
    REPO_ROOT / "data" / "raw_documents" / "cn-nl-semi-structured.stub.txt"
)


def run_builder(
    output_path: Path, source_path: Path | None = None
) -> subprocess.CompletedProcess[str]:
    command = [sys.executable, str(SCRIPT_PATH)]
    if source_path is not None:
        command.extend(["--source", str(source_path)])
    command.extend(["--output", str(output_path)])
    return subprocess.run(
        command,
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
    )


def run_raw_parser(
    output_path: Path, input_path: Path | None = None
) -> subprocess.CompletedProcess[str]:
    command = [sys.executable, str(RAW_PARSE_SCRIPT_PATH)]
    if input_path is not None:
        command.extend(["--input", str(input_path)])
    command.extend(["--output", str(output_path)])
    return subprocess.run(
        command,
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
    )


def run_raw_ingest(
    parsed_output_path: Path,
    dataset_output_path: Path,
    input_path: Path | None = None,
    report_output_path: Path | None = None,
) -> subprocess.CompletedProcess[str]:
    command = [sys.executable, str(RAW_INGEST_SCRIPT_PATH)]
    if input_path is not None:
        command.extend(["--input", str(input_path)])
    command.extend(["--parsed-output", str(parsed_output_path)])
    command.extend(["--dataset-output", str(dataset_output_path)])
    if report_output_path is not None:
        command.extend(["--report-output", str(report_output_path)])
    return subprocess.run(
        command,
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
    )


def run_pdf_ingest(
    pdf_input_path: Path,
    extracted_text_output_path: Path,
    parsed_output_path: Path,
    dataset_output_path: Path,
    report_output_path: Path,
    manifest_path: Path | None = None,
    document_id: str | None = None,
    title: str | None = None,
    jurisdictions: str | None = None,
    document_type: str | None = None,
    source_id: str | None = None,
) -> subprocess.CompletedProcess[str]:
    command = [
        sys.executable,
        str(PDF_INGEST_SCRIPT_PATH),
        "--input",
        str(pdf_input_path),
        "--raw-text-output",
        str(extracted_text_output_path),
        "--parsed-output",
        str(parsed_output_path),
        "--dataset-output",
        str(dataset_output_path),
        "--report-output",
        str(report_output_path),
    ]
    if manifest_path is not None:
        command.extend(["--manifest", str(manifest_path)])
    if document_id is not None:
        command.extend(["--document-id", document_id])
    if title is not None:
        command.extend(["--title", title])
    if jurisdictions is not None:
        command.extend(["--jurisdictions", jurisdictions])
    if document_type is not None:
        command.extend(["--document-type", document_type])
    if source_id is not None:
        command.extend(["--source-id", source_id])
    return subprocess.run(
        command,
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
    )


def run_source_ingest(
    catalog_path: Path,
    summary_output_path: Path,
) -> subprocess.CompletedProcess[str]:
    command = [
        sys.executable,
        str(SOURCE_INGEST_SCRIPT_PATH),
        "--catalog",
        str(catalog_path),
        "--summary-output",
        str(summary_output_path),
    ]
    return subprocess.run(
        command,
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
    )


def write_invalid_source(tmp_path: Path, mutate) -> Path:
    payload = json.loads(SOURCE_PATH.read_text(encoding="utf-8"))
    mutate(payload)
    source_path = tmp_path / "invalid-source.json"
    source_path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return source_path


def build_parser_like_source_payload() -> dict:
    return {
        "document": {
            "document_id": "cn-nl-main-treaty",
            "title": "China-Netherlands Tax Treaty",
            "document_type": "treaty_text",
            "jurisdictions": ["CN", "NL"],
            "notes": [
                "Parser-like intermediate representation for the import pipeline."
            ],
        },
        "parsed_articles": [
            {
                "article_number": "12",
                "article_title": "Royalties",
                "article_label": "Article 12",
                "income_type": "royalties",
                "summary": "Defines treaty treatment for royalties between the two jurisdictions.",
                "article_notes": [
                    "Beneficial ownership and factual qualification may matter."
                ],
                "paragraphs": [
                    {
                        "paragraph_id": "art12-p1",
                        "paragraph_label": "Article 12(1)",
                        "source_reference": "Article 12(1)",
                        "source_language": "en",
                        "source_segments": [
                            {
                                "segment_id": "art12-p1-s1",
                                "segment_order": 1,
                                "page_hint": 6,
                                "source_kind": "article_paragraph",
                                "text_quality": "clean",
                                "normalization_status": "verbatim",
                                "text": "Royalty treatment is governed by Article 12(1).",
                            },
                            {
                                "segment_id": "art12-p1-s2",
                                "segment_order": 2,
                                "page_hint": 6,
                                "source_kind": "article_paragraph",
                                "text_quality": "clean",
                                "normalization_status": "normalized",
                                "text": "Treaty conditions and factual qualification still matter.",
                            },
                        ],
                        "extracted_rules": [
                            {
                                "rule_id": "cn-nl-art12-p1-base",
                                "rule_type": "withholding_tax_cap",
                                "rate": "10%",
                                "direction": "bidirectional",
                                "candidate_rank": 1,
                                "is_primary_candidate": True,
                                "extraction_confidence": 0.98,
                                "derived_from_segments": ["art12-p1-s1", "art12-p1-s2"],
                                "conditions": [
                                    "Treaty applicability depends on the facts of the payment."
                                ],
                                "human_review_required": True,
                                "review_reason": "Final eligibility depends on facts beyond v1 scope.",
                            },
                            {
                                "rule_id": "cn-nl-art12-p1-alt",
                                "rule_type": "withholding_tax_cap",
                                "rate": "15%",
                                "direction": "bidirectional",
                                "candidate_rank": 2,
                                "is_primary_candidate": False,
                                "extraction_confidence": 0.41,
                                "derived_from_segments": ["art12-p1-s1"],
                                "conditions": [
                                    "Lower-confidence alternate extraction candidate retained for pipeline review."
                                ],
                                "human_review_required": True,
                                "review_reason": "Alternate candidate retained for parser-review workflow only.",
                            },
                        ],
                    }
                ],
            }
        ],
    }


def write_source_payload(tmp_path: Path, payload: dict) -> Path:
    source_path = tmp_path / "source.json"
    source_path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return source_path


def build_simple_pdf(lines: list[str]) -> bytes:
    return build_multi_page_pdf([lines])


def build_multi_page_pdf(pages: list[list[str]]) -> bytes:
    objects: list[bytes] = []

    def add_object(content: bytes) -> int:
        objects.append(content)
        return len(objects)

    font_id = add_object(b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>")
    page_ids: list[int] = []

    for page_lines in pages:
        content_lines = [b"BT", b"/F1 12 Tf"]
        y_position = 760
        for line in page_lines:
            escaped = (
                line.replace("\\", "\\\\")
                .replace("(", "\\(")
                .replace(")", "\\)")
                .encode("latin-1")
            )
            content_lines.append(f"72 {y_position} Td".encode("ascii"))
            content_lines.append(b"(" + escaped + b") Tj")
            y_position -= 18
        content_lines.append(b"ET")
        stream = b"\n".join(content_lines)
        content_id = add_object(
            b"<< /Length "
            + str(len(stream)).encode("ascii")
            + b" >>\nstream\n"
            + stream
            + b"\nendstream"
        )
        page_ids.append(
            add_object(
                f"<< /Type /Page /Parent PLACEHOLDER_PAGES 0 R /MediaBox [0 0 612 792] /Contents {content_id} 0 R /Resources << /Font << /F1 {font_id} 0 R >> >> >>".encode(
                    "ascii"
                )
            )
        )

    kids = " ".join(f"{page_id} 0 R" for page_id in page_ids)
    pages_id = add_object(
        f"<< /Type /Pages /Kids [{kids}] /Count {len(page_ids)} >>".encode("ascii")
    )
    for page_id in page_ids:
        objects[page_id - 1] = objects[page_id - 1].replace(
            b"PLACEHOLDER_PAGES", str(pages_id).encode("ascii")
        )
    catalog_id = add_object(
        f"<< /Type /Catalog /Pages {pages_id} 0 R >>".encode("ascii")
    )

    header = b"%PDF-1.4\n%\xe2\xe3\xcf\xd3\n"
    body = bytearray(header)
    offsets = [0]
    for index, obj in enumerate(objects, start=1):
        offsets.append(len(body))
        body.extend(f"{index} 0 obj\n".encode("ascii"))
        body.extend(obj)
        body.extend(b"\nendobj\n")

    xref_start = len(body)
    body.extend(f"xref\n0 {len(objects) + 1}\n".encode("ascii"))
    body.extend(b"0000000000 65535 f \n")
    for offset in offsets[1:]:
        body.extend(f"{offset:010d} 00000 n \n".encode("ascii"))
    body.extend(
        f"trailer\n<< /Size {len(objects) + 1} /Root {catalog_id} 0 R >>\nstartxref\n{xref_start}\n%%EOF\n".encode(
            "ascii"
        )
    )
    return bytes(body)


def test_build_script_generates_v3_compatible_dataset(tmp_path: Path):
    output_path = tmp_path / "cn-nl.generated.json"

    result = run_builder(output_path)

    assert result.returncode == 0, result.stderr
    assert output_path.exists()

    payload = json.loads(output_path.read_text(encoding="utf-8"))
    assert payload["treaty"]["treaty_id"] == "cn-nl"
    assert payload["treaty"]["source_type"] == "import_stub_from_source_documents"
    assert payload["treaty"]["source_documents"][0]["document_id"] == "cn-nl-main-treaty"
    assert payload["articles"][0]["paragraphs"][0]["source_reference"].startswith("Article ")
    assert payload["articles"][0]["paragraphs"][0]["source_language"] == "en"
    assert payload["articles"][0]["paragraphs"][0]["rules"][0]["extraction_confidence"] == 0.98
    assert payload["articles"][0]["paragraphs"][0]["source_segments"][0]["page_hint"] == 8
    assert payload["articles"][0]["paragraphs"][0]["source_segments"][0]["source_kind"] == "article_paragraph"
    assert payload["articles"][0]["paragraphs"][0]["source_segments"][0]["text_quality"] == "clean"
    assert payload["articles"][0]["paragraphs"][0]["source_segments"][0]["normalization_status"] == "verbatim"
    assert payload["articles"][0]["paragraphs"][0]["provenance_summary"] == {
        "primary_rule_id": "cn-nl-art10-p2b-general",
        "paragraph_confidence": 0.98,
        "segment_count": 1,
        "covered_segment_count": 1,
        "segment_coverage": 1.0,
    }
    assert payload["articles"][0]["paragraphs"][0]["rules"][0]["derived_from_segments"]
    assert payload["articles"][2]["paragraphs"][0]["rules"][0]["is_primary_candidate"] is True


def test_raw_text_stub_generates_parser_like_fixture_and_full_import_chain(tmp_path: Path, monkeypatch):
    parser_output_path = tmp_path / "parser-output.json"
    dataset_output_path = tmp_path / "cn-nl.generated.json"

    parse_result = run_raw_parser(parser_output_path)

    assert parse_result.returncode == 0, parse_result.stderr
    parser_payload = json.loads(parser_output_path.read_text(encoding="utf-8"))
    assert parser_payload["document"]["document_id"] == "cn-nl-article12-raw-stub"
    assert parser_payload["parsed_articles"][0]["article_number"] == "12"
    assert parser_payload["parsed_articles"][0]["paragraphs"][0]["source_segments"][0]["text"].startswith(
        "Royalty treatment is governed"
    )
    assert (
        parser_payload["parsed_articles"][0]["paragraphs"][0]["source_segments"][0]["raw_line_number"]
        == 11
    )

    build_result = run_builder(dataset_output_path, source_path=parser_output_path)

    assert build_result.returncode == 0, build_result.stderr
    dataset_payload = json.loads(dataset_output_path.read_text(encoding="utf-8"))
    assert dataset_payload["articles"][0]["paragraphs"][0]["source_segments"][0]["raw_line_number"] == 11
    monkeypatch.setattr(service, "DATA_PATH", dataset_output_path)
    response = service.analyze_scenario("中国居民企业向荷兰支付特许权使用费")
    assert response["supported"] is True
    assert response["result"]["article_number"] == "12"
    assert response["result"]["rate"] == "10%"


def test_raw_text_stub_supports_multiple_articles_and_paragraphs(tmp_path: Path):
    parser_output_path = tmp_path / "parser-output.multi.json"
    dataset_output_path = tmp_path / "cn-nl.multi.generated.json"

    parse_result = run_raw_parser(parser_output_path, input_path=RAW_MULTI_TEXT_PATH)

    assert parse_result.returncode == 0, parse_result.stderr
    parser_payload = json.loads(parser_output_path.read_text(encoding="utf-8"))
    assert len(parser_payload["parsed_articles"]) == 2
    assert parser_payload["parsed_articles"][0]["article_number"] == "11"
    assert len(parser_payload["parsed_articles"][1]["paragraphs"]) == 2
    assert (
        parser_payload["parsed_articles"][1]["paragraphs"][1]["paragraph_label"]
        == "Article 12(2)"
    )

    build_result = run_builder(dataset_output_path, source_path=parser_output_path)

    assert build_result.returncode == 0, build_result.stderr
    dataset_payload = json.loads(dataset_output_path.read_text(encoding="utf-8"))
    assert len(dataset_payload["articles"]) == 2
    assert dataset_payload["articles"][0]["article_number"] == "11"
    assert len(dataset_payload["articles"][1]["paragraphs"]) == 2
    assert (
        dataset_payload["articles"][1]["paragraphs"][1]["provenance_summary"]["segment_count"]
        == 1
    )


def test_raw_text_stub_supports_semi_structured_treaty_text(tmp_path: Path):
    parser_output_path = tmp_path / "parser-output.semi.json"
    dataset_output_path = tmp_path / "cn-nl.semi.generated.json"
    ingest_parsed_output_path = tmp_path / "cn-nl.semi.ingest.parsed.json"
    ingest_dataset_output_path = tmp_path / "cn-nl.semi.ingest.generated.json"
    ingest_report_output_path = tmp_path / "cn-nl.semi.ingest.report.json"

    parse_result = run_raw_parser(parser_output_path, input_path=RAW_SEMI_STRUCTURED_TEXT_PATH)

    assert parse_result.returncode == 0, parse_result.stderr
    parser_payload = json.loads(parser_output_path.read_text(encoding="utf-8"))
    assert len(parser_payload["parsed_articles"]) == 2
    assert parser_payload["parsed_articles"][0]["article_number"] == "11"
    assert parser_payload["parsed_articles"][0]["income_type"] == "interest"
    assert parser_payload["parsed_articles"][0]["paragraphs"][1]["paragraph_label"] == "Article 11(2)"
    assert (
        parser_payload["parsed_articles"][0]["paragraphs"][1]["extracted_rules"][0]["rate"]
        == "10%"
    )
    assert (
        parser_payload["parsed_articles"][1]["paragraphs"][1]["source_segments"][0]["raw_line_number"]
        == 13
    )

    build_result = run_builder(dataset_output_path, source_path=parser_output_path)

    assert build_result.returncode == 0, build_result.stderr
    dataset_payload = json.loads(dataset_output_path.read_text(encoding="utf-8"))
    assert len(dataset_payload["articles"]) == 2
    assert dataset_payload["articles"][1]["article_number"] == "12"
    assert dataset_payload["articles"][1]["paragraphs"][1]["rules"][0]["rate"] == "10%"

    ingest_result = run_raw_ingest(
        parsed_output_path=ingest_parsed_output_path,
        dataset_output_path=ingest_dataset_output_path,
        input_path=RAW_SEMI_STRUCTURED_TEXT_PATH,
        report_output_path=ingest_report_output_path,
    )

    assert ingest_result.returncode == 0, ingest_result.stderr
    assert "Ingest status: ok (0 attention items)" in ingest_result.stdout
    ingest_report_payload = json.loads(ingest_report_output_path.read_text(encoding="utf-8"))
    assert ingest_report_payload["status"] == "ok"
    assert ingest_report_payload["attention_item_count"] == 0


def test_raw_ingest_script_runs_full_chain_from_raw_text(tmp_path: Path, monkeypatch):
    parsed_output_path = tmp_path / "raw-ingest.parsed.json"
    dataset_output_path = tmp_path / "raw-ingest.dataset.json"
    report_output_path = tmp_path / "raw-ingest.report.json"

    result = run_raw_ingest(
        parsed_output_path=parsed_output_path,
        dataset_output_path=dataset_output_path,
        input_path=RAW_MULTI_TEXT_PATH,
        report_output_path=report_output_path,
    )

    assert result.returncode == 0, result.stderr
    assert parsed_output_path.exists()
    assert dataset_output_path.exists()
    assert report_output_path.exists()

    parsed_payload = json.loads(parsed_output_path.read_text(encoding="utf-8"))
    dataset_payload = json.loads(dataset_output_path.read_text(encoding="utf-8"))
    report_payload = json.loads(report_output_path.read_text(encoding="utf-8"))
    assert len(parsed_payload["parsed_articles"]) == 2
    assert len(dataset_payload["articles"]) == 2
    assert report_payload == {
        "document_id": "cn-nl-multi-article-raw-stub",
        "status": "warning",
        "article_count": 2,
        "paragraph_count": 3,
        "rule_count": 4,
        "source_segment_count": 5,
        "normalized_segment_count": 3,
        "warning_segment_count": 1,
        "attention_item_count": 1,
        "attention_items": [
            {
                "paragraph_label": "Article 12(2)",
                "source_reference": "Article 12(2)",
                "reasons": [
                    "warning_segment_present",
                    "low_paragraph_confidence",
                ],
            }
        ],
    }
    assert "Ingest status: warning (1 attention item)" in result.stdout

    monkeypatch.setattr(service, "DATA_PATH", dataset_output_path)
    response = service.analyze_scenario("中国居民企业向荷兰支付特许权使用费")
    assert response["supported"] is True
    assert response["result"]["article_number"] == "12"


def test_pdf_ingest_script_runs_full_chain_from_text_pdf(tmp_path: Path):
    pdf_input_path = tmp_path / "cn-nl-semi-structured.pdf"
    raw_text_output_path = tmp_path / "cn-nl-extracted.txt"
    parsed_output_path = tmp_path / "cn-nl-from-pdf.parsed.json"
    dataset_output_path = tmp_path / "cn-nl-from-pdf.dataset.json"
    report_output_path = tmp_path / "cn-nl-from-pdf.report.json"
    pdf_input_path.write_bytes(
        build_simple_pdf(
            [
                "DOCUMENT_ID: cn-nl-pdf-raw-stub",
                "TITLE: China-Netherlands Tax Treaty PDF Stub",
                "DOCUMENT_TYPE: treaty_text",
                "JURISDICTIONS: CN,NL",
                "Article 12 Royalties",
                "1. Royalties arising in one of the States and paid to a resident of the other State may be taxed in that other State.",
                "2. However, such royalties may also be taxed in the first-mentioned State, but the tax so charged shall not exceed 10 per cent of the gross amount of the royalties.",
            ]
        )
    )

    result = run_pdf_ingest(
        pdf_input_path=pdf_input_path,
        extracted_text_output_path=raw_text_output_path,
        parsed_output_path=parsed_output_path,
        dataset_output_path=dataset_output_path,
        report_output_path=report_output_path,
    )

    assert result.returncode == 0, result.stderr
    assert raw_text_output_path.exists()
    assert parsed_output_path.exists()
    assert dataset_output_path.exists()
    assert report_output_path.exists()
    extracted_text = raw_text_output_path.read_text(encoding="utf-8")
    assert "Article 12 Royalties" in extracted_text
    dataset_payload = json.loads(dataset_output_path.read_text(encoding="utf-8"))
    assert dataset_payload["articles"][0]["article_number"] == "12"
    assert dataset_payload["articles"][0]["paragraphs"][1]["rules"][0]["rate"] == "10%"
    report_payload = json.loads(report_output_path.read_text(encoding="utf-8"))
    assert report_payload["document_id"] == "cn-nl-pdf-raw-stub"
    assert report_payload["status"] == "ok"


def test_pdf_ingest_script_accepts_external_document_metadata(tmp_path: Path):
    pdf_input_path = tmp_path / "cn-nl-no-metadata.pdf"
    raw_text_output_path = tmp_path / "cn-nl-no-metadata-extracted.txt"
    parsed_output_path = tmp_path / "cn-nl-no-metadata.parsed.json"
    dataset_output_path = tmp_path / "cn-nl-no-metadata.dataset.json"
    report_output_path = tmp_path / "cn-nl-no-metadata.report.json"
    pdf_input_path.write_bytes(
        build_simple_pdf(
            [
                "Article 12 Royalties",
                "1. Royalties arising in one of the States and paid to a resident of the other State may be taxed in that other State.",
                "2. However, such royalties may also be taxed in the first-mentioned State, but the tax so charged shall not exceed 10 per cent of the gross amount of the royalties.",
            ]
        )
    )

    result = run_pdf_ingest(
        pdf_input_path=pdf_input_path,
        extracted_text_output_path=raw_text_output_path,
        parsed_output_path=parsed_output_path,
        dataset_output_path=dataset_output_path,
        report_output_path=report_output_path,
        document_id="cn-nl-pdf-external-metadata-stub",
        title="China-Netherlands Tax Treaty PDF External Metadata Stub",
        jurisdictions="CN,NL",
        document_type="treaty_text",
    )

    assert result.returncode == 0, result.stderr
    extracted_text = raw_text_output_path.read_text(encoding="utf-8")
    assert extracted_text.startswith("DOCUMENT_ID: cn-nl-pdf-external-metadata-stub")
    parsed_payload = json.loads(parsed_output_path.read_text(encoding="utf-8"))
    assert parsed_payload["document"]["document_id"] == "cn-nl-pdf-external-metadata-stub"
    dataset_payload = json.loads(dataset_output_path.read_text(encoding="utf-8"))
    assert dataset_payload["treaty"]["source_documents"][0]["document_id"] == "cn-nl-pdf-external-metadata-stub"
    report_payload = json.loads(report_output_path.read_text(encoding="utf-8"))
    assert report_payload["document_id"] == "cn-nl-pdf-external-metadata-stub"


def test_pdf_ingest_script_accepts_manifest_metadata(tmp_path: Path):
    pdf_input_path = tmp_path / "cn-nl-manifest.pdf"
    manifest_path = tmp_path / "cn-nl-manifest.json"
    raw_text_output_path = tmp_path / "cn-nl-manifest-extracted.txt"
    parsed_output_path = tmp_path / "cn-nl-manifest.parsed.json"
    dataset_output_path = tmp_path / "cn-nl-manifest.dataset.json"
    report_output_path = tmp_path / "cn-nl-manifest.report.json"
    pdf_input_path.write_bytes(
        build_simple_pdf(
            [
                "Article 11 Interest",
                "1. Interest arising in one of the States and paid to a resident of the other State may be taxed in that other State.",
                "2. However, such interest may also be taxed in the first-mentioned State, but the tax shall not exceed 10 per cent of the gross amount of the interest.",
            ]
        )
    )
    manifest_path.write_text(
        json.dumps(
            {
                "document_id": "cn-nl-pdf-manifest-stub",
                "title": "China-Netherlands Tax Treaty PDF Manifest Stub",
                "document_type": "treaty_text",
                "jurisdictions": ["CN", "NL"],
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )

    result = run_pdf_ingest(
        pdf_input_path=pdf_input_path,
        manifest_path=manifest_path,
        extracted_text_output_path=raw_text_output_path,
        parsed_output_path=parsed_output_path,
        dataset_output_path=dataset_output_path,
        report_output_path=report_output_path,
    )

    assert result.returncode == 0, result.stderr
    extracted_text = raw_text_output_path.read_text(encoding="utf-8")
    assert extracted_text.startswith("DOCUMENT_ID: cn-nl-pdf-manifest-stub")
    parsed_payload = json.loads(parsed_output_path.read_text(encoding="utf-8"))
    assert parsed_payload["document"]["document_id"] == "cn-nl-pdf-manifest-stub"
    assert parsed_payload["document"]["jurisdictions"] == ["CN", "NL"]
    dataset_payload = json.loads(dataset_output_path.read_text(encoding="utf-8"))
    assert dataset_payload["articles"][0]["article_number"] == "11"
    report_payload = json.loads(report_output_path.read_text(encoding="utf-8"))
    assert report_payload["document_id"] == "cn-nl-pdf-manifest-stub"


def test_pdf_ingest_script_merges_wrapped_paragraph_lines(tmp_path: Path):
    pdf_input_path = tmp_path / "cn-nl-wrapped.pdf"
    raw_text_output_path = tmp_path / "cn-nl-wrapped-extracted.txt"
    parsed_output_path = tmp_path / "cn-nl-wrapped.parsed.json"
    dataset_output_path = tmp_path / "cn-nl-wrapped.dataset.json"
    report_output_path = tmp_path / "cn-nl-wrapped.report.json"
    pdf_input_path.write_bytes(
        build_simple_pdf(
            [
                "DOCUMENT_ID: cn-nl-pdf-wrapped-stub",
                "TITLE: China-Netherlands Tax Treaty PDF Wrapped Stub",
                "DOCUMENT_TYPE: treaty_text",
                "JURISDICTIONS: CN,NL",
                "Article 12 Royalties",
                "1. Royalties arising in one of the States and paid to a resident of the other State",
                "may be taxed in that other State.",
                "2. However, such royalties may also be taxed in the first-mentioned State,",
                "but the tax so charged shall not exceed 10 per cent of the gross amount of the royalties.",
            ]
        )
    )

    result = run_pdf_ingest(
        pdf_input_path=pdf_input_path,
        extracted_text_output_path=raw_text_output_path,
        parsed_output_path=parsed_output_path,
        dataset_output_path=dataset_output_path,
        report_output_path=report_output_path,
    )

    assert result.returncode == 0, result.stderr
    extracted_text = raw_text_output_path.read_text(encoding="utf-8")
    assert (
        "1. Royalties arising in one of the States and paid to a resident of the other State may be taxed in that other State."
        in extracted_text
    )
    assert (
        "2. However, such royalties may also be taxed in the first-mentioned State, but the tax so charged shall not exceed 10 per cent of the gross amount of the royalties."
        in extracted_text
    )
    dataset_payload = json.loads(dataset_output_path.read_text(encoding="utf-8"))
    assert dataset_payload["articles"][0]["paragraphs"][1]["rules"][0]["rate"] == "10%"


def test_pdf_ingest_script_ignores_repeated_headers_and_page_numbers(tmp_path: Path):
    pdf_input_path = tmp_path / "cn-nl-header-noise.pdf"
    raw_text_output_path = tmp_path / "cn-nl-header-noise-extracted.txt"
    parsed_output_path = tmp_path / "cn-nl-header-noise.parsed.json"
    dataset_output_path = tmp_path / "cn-nl-header-noise.dataset.json"
    report_output_path = tmp_path / "cn-nl-header-noise.report.json"
    pdf_input_path.write_bytes(
        build_multi_page_pdf(
            [
                [
                    "China-Netherlands Tax Treaty",
                    "DOCUMENT_ID: cn-nl-pdf-header-noise-stub",
                    "TITLE: China-Netherlands Tax Treaty PDF Header Noise Stub",
                    "DOCUMENT_TYPE: treaty_text",
                    "JURISDICTIONS: CN,NL",
                    "Article 12 Royalties",
                    "1. Royalties arising in one of the States and paid to a resident of the other State may be taxed in that other State.",
                    "Page 1",
                ],
                [
                    "China-Netherlands Tax Treaty",
                    "2. However, such royalties may also be taxed in the first-mentioned State, but the tax so charged shall not exceed 10 per cent of the gross amount of the royalties.",
                    "Page 2",
                ],
            ]
        )
    )

    result = run_pdf_ingest(
        pdf_input_path=pdf_input_path,
        extracted_text_output_path=raw_text_output_path,
        parsed_output_path=parsed_output_path,
        dataset_output_path=dataset_output_path,
        report_output_path=report_output_path,
    )

    assert result.returncode == 0, result.stderr
    extracted_text = raw_text_output_path.read_text(encoding="utf-8")
    extracted_lines = extracted_text.splitlines()
    assert "China-Netherlands Tax Treaty" not in extracted_lines
    assert "Page 1" not in extracted_lines
    assert "Page 2" not in extracted_lines
    dataset_payload = json.loads(dataset_output_path.read_text(encoding="utf-8"))
    assert dataset_payload["articles"][0]["paragraphs"][1]["rules"][0]["rate"] == "10%"


def test_source_catalog_ingest_runs_mixed_sources_and_writes_batch_summary(tmp_path: Path):
    raw_input_path = tmp_path / "catalog-interest.stub.txt"
    raw_parsed_output_path = tmp_path / "catalog-interest.parsed.json"
    raw_dataset_output_path = tmp_path / "catalog-interest.dataset.json"
    raw_report_output_path = tmp_path / "catalog-interest.report.json"
    pdf_input_path = tmp_path / "catalog-royalties.pdf"
    pdf_raw_text_output_path = tmp_path / "catalog-royalties.extracted.txt"
    pdf_parsed_output_path = tmp_path / "catalog-royalties.parsed.json"
    pdf_dataset_output_path = tmp_path / "catalog-royalties.dataset.json"
    pdf_report_output_path = tmp_path / "catalog-royalties.report.json"
    summary_output_path = tmp_path / "catalog.summary.json"
    catalog_path = tmp_path / "catalog.json"

    raw_input_path.write_text(
        "\n".join(
            [
                "DOCUMENT_ID: cn-nl-catalog-interest-raw-stub",
                "TITLE: China-Netherlands Tax Treaty Catalog Interest Stub",
                "DOCUMENT_TYPE: treaty_text",
                "JURISDICTIONS: CN,NL",
                "",
                "Article 11 Interest",
                "1. Interest arising in one of the States and paid to a resident of the other State may be taxed in that other State.",
                "2. However, such interest may also be taxed in the first-mentioned State, but the tax shall not exceed 10 per cent of the gross amount of the interest.",
                "",
            ]
        ),
        encoding="utf-8",
    )
    pdf_input_path.write_bytes(
        build_simple_pdf(
            [
                "Article 12 Royalties",
                "1. Royalties arising in one of the States and paid to a resident of the other State may be taxed in that other State.",
                "2. However, such royalties may also be taxed in the first-mentioned State, but the tax so charged shall not exceed 10 per cent of the gross amount of the royalties.",
            ]
        )
    )
    catalog_path.write_text(
        json.dumps(
            {
                "sources": [
                    {
                        "source_id": "sat-cn-nl-2013-en-pdf",
                        "source_type": "raw_text",
                        "input_path": str(raw_input_path),
                        "parsed_output_path": str(raw_parsed_output_path),
                        "dataset_output_path": str(raw_dataset_output_path),
                        "report_output_path": str(raw_report_output_path),
                    },
                    {
                        "source_id": "nl-2013-consolidated-text",
                        "source_type": "pdf_text",
                        "input_path": str(pdf_input_path),
                        "raw_text_output_path": str(pdf_raw_text_output_path),
                        "parsed_output_path": str(pdf_parsed_output_path),
                        "dataset_output_path": str(pdf_dataset_output_path),
                        "report_output_path": str(pdf_report_output_path),
                        "document_id": "cn-nl-catalog-pdf-stub",
                        "title": "China-Netherlands Tax Treaty Catalog PDF Stub",
                        "document_type": "treaty_text",
                        "jurisdictions": ["CN", "NL"],
                    },
                ]
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )

    result = run_source_ingest(catalog_path=catalog_path, summary_output_path=summary_output_path)

    assert result.returncode == 0, result.stderr
    assert raw_dataset_output_path.exists()
    assert pdf_dataset_output_path.exists()
    assert summary_output_path.exists()
    summary_payload = json.loads(summary_output_path.read_text(encoding="utf-8"))
    assert summary_payload == {
        "source_count": 2,
        "success_count": 2,
        "failure_count": 0,
        "results": [
            {
                "source_id": "sat-cn-nl-2013-en-pdf",
                "source_type": "raw_text",
                "status": "ok",
                "report_output_path": str(raw_report_output_path),
            },
            {
                "source_id": "nl-2013-consolidated-text",
                "source_type": "pdf_text",
                "status": "ok",
                "report_output_path": str(pdf_report_output_path),
            },
        ],
    }
    raw_report_payload = json.loads(raw_report_output_path.read_text(encoding="utf-8"))
    pdf_report_payload = json.loads(pdf_report_output_path.read_text(encoding="utf-8"))
    assert raw_report_payload["source_id"] == "sat-cn-nl-2013-en-pdf"
    assert pdf_report_payload["source_id"] == "nl-2013-consolidated-text"
    assert "Completed source catalog ingest: 2 ok, 0 failed" in result.stdout


def test_source_catalog_ingest_records_failures_without_stopping_batch(tmp_path: Path):
    raw_input_path = tmp_path / "catalog-ok.stub.txt"
    raw_parsed_output_path = tmp_path / "catalog-ok.parsed.json"
    raw_dataset_output_path = tmp_path / "catalog-ok.dataset.json"
    raw_report_output_path = tmp_path / "catalog-ok.report.json"
    bad_pdf_input_path = tmp_path / "catalog-bad.pdf"
    bad_pdf_raw_text_output_path = tmp_path / "catalog-bad.extracted.txt"
    bad_pdf_parsed_output_path = tmp_path / "catalog-bad.parsed.json"
    bad_pdf_dataset_output_path = tmp_path / "catalog-bad.dataset.json"
    bad_pdf_report_output_path = tmp_path / "catalog-bad.report.json"
    summary_output_path = tmp_path / "catalog-failure.summary.json"
    catalog_path = tmp_path / "catalog-failure.json"

    raw_input_path.write_text(
        "\n".join(
            [
                "DOCUMENT_ID: cn-nl-catalog-ok-raw-stub",
                "TITLE: China-Netherlands Tax Treaty Catalog OK Raw Stub",
                "DOCUMENT_TYPE: treaty_text",
                "JURISDICTIONS: CN,NL",
                "",
                "Article 11 Interest",
                "1. Interest arising in one of the States and paid to a resident of the other State may be taxed in that other State.",
                "2. However, such interest may also be taxed in the first-mentioned State, but the tax shall not exceed 10 per cent of the gross amount of the interest.",
                "",
            ]
        ),
        encoding="utf-8",
    )
    bad_pdf_input_path.write_bytes(
        build_simple_pdf(
            [
                "Article 12 Royalties",
                "1. Royalties arising in one of the States and paid to a resident of the other State may be taxed in that other State.",
            ]
        )
    )
    catalog_path.write_text(
        json.dumps(
            {
                "sources": [
                    {
                        "source_id": "sat-cn-nl-2013-en-pdf",
                        "source_type": "raw_text",
                        "input_path": str(raw_input_path),
                        "parsed_output_path": str(raw_parsed_output_path),
                        "dataset_output_path": str(raw_dataset_output_path),
                        "report_output_path": str(raw_report_output_path),
                    },
                    {
                        "source_id": "nl-2013-consolidated-text",
                        "source_type": "pdf_text",
                        "input_path": str(bad_pdf_input_path),
                        "raw_text_output_path": str(bad_pdf_raw_text_output_path),
                        "parsed_output_path": str(bad_pdf_parsed_output_path),
                        "dataset_output_path": str(bad_pdf_dataset_output_path),
                        "report_output_path": str(bad_pdf_report_output_path),
                    },
                ]
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )

    result = run_source_ingest(catalog_path=catalog_path, summary_output_path=summary_output_path)

    assert result.returncode == 1
    assert raw_dataset_output_path.exists()
    assert not bad_pdf_dataset_output_path.exists()
    summary_payload = json.loads(summary_output_path.read_text(encoding="utf-8"))
    assert summary_payload == {
        "source_count": 2,
        "success_count": 1,
        "failure_count": 1,
        "results": [
            {
                "source_id": "sat-cn-nl-2013-en-pdf",
                "source_type": "raw_text",
                "status": "ok",
                "report_output_path": str(raw_report_output_path),
            },
            {
                "source_id": "nl-2013-consolidated-text",
                "source_type": "pdf_text",
                "status": "error",
                "report_output_path": str(bad_pdf_report_output_path),
            },
        ],
    }
    assert "Completed source catalog ingest: 1 ok, 1 failed" in result.stdout
    bad_report_payload = json.loads(bad_pdf_report_output_path.read_text(encoding="utf-8"))
    assert bad_report_payload["status"] == "error"
    assert bad_report_payload["source_id"] == "nl-2013-consolidated-text"
    ok_report_payload = json.loads(raw_report_output_path.read_text(encoding="utf-8"))
    assert ok_report_payload["source_id"] == "sat-cn-nl-2013-en-pdf"


def test_pdf_ingest_parse_failure_report_preserves_source_id(tmp_path: Path):
    pdf_input_path = tmp_path / "bad-parse.pdf"
    extracted_text_output_path = tmp_path / "bad-parse.extracted.txt"
    parsed_output_path = tmp_path / "bad-parse.parsed.json"
    dataset_output_path = tmp_path / "bad-parse.dataset.json"
    report_output_path = tmp_path / "bad-parse.report.json"

    pdf_input_path.write_bytes(
        build_simple_pdf(
            [
                "This is not parseable treaty text.",
                "It has no article heading or parser tags.",
            ]
        )
    )

    result = run_pdf_ingest(
        pdf_input_path=pdf_input_path,
        extracted_text_output_path=extracted_text_output_path,
        parsed_output_path=parsed_output_path,
        dataset_output_path=dataset_output_path,
        report_output_path=report_output_path,
        document_id="cn-nl-bad-parse-pdf",
        title="China-Netherlands Bad Parse PDF",
        jurisdictions="CN,NL",
        document_type="treaty_text",
        source_id="nl-2013-consolidated-text",
    )

    assert result.returncode == 1
    report_payload = json.loads(report_output_path.read_text(encoding="utf-8"))
    assert report_payload["status"] == "error"
    assert report_payload["error_stage"] == "parse"
    assert report_payload["document_id"] == "cn-nl-bad-parse-pdf"
    assert report_payload["source_id"] == "nl-2013-consolidated-text"


def test_source_catalog_ingest_rejects_unknown_official_source_id(tmp_path: Path):
    raw_input_path = tmp_path / "catalog-interest.stub.txt"
    raw_parsed_output_path = tmp_path / "catalog-interest.parsed.json"
    raw_dataset_output_path = tmp_path / "catalog-interest.dataset.json"
    raw_report_output_path = tmp_path / "catalog-interest.report.json"
    summary_output_path = tmp_path / "catalog.summary.json"
    catalog_path = tmp_path / "catalog.json"

    raw_input_path.write_text(
        "\n".join(
            [
                "DOCUMENT_ID: cn-nl-catalog-interest-raw-stub",
                "TITLE: China-Netherlands Tax Treaty Catalog Interest Stub",
                "DOCUMENT_TYPE: treaty_text",
                "JURISDICTIONS: CN,NL",
                "",
                "Article 11 Interest",
                "1. Interest arising in one of the States and paid to a resident of the other State may be taxed in that other State.",
                "2. However, such interest may also be taxed in the first-mentioned State, but the tax shall not exceed 10 per cent of the gross amount of the interest.",
                "",
            ]
        ),
        encoding="utf-8",
    )
    catalog_path.write_text(
        json.dumps(
            {
                "sources": [
                    {
                        "source_id": "unknown-official-source",
                        "source_type": "raw_text",
                        "input_path": str(raw_input_path),
                        "parsed_output_path": str(raw_parsed_output_path),
                        "dataset_output_path": str(raw_dataset_output_path),
                        "report_output_path": str(raw_report_output_path),
                    }
                ]
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )

    result = run_source_ingest(catalog_path=catalog_path, summary_output_path=summary_output_path)

    assert result.returncode == 1
    assert not raw_dataset_output_path.exists()
    assert not summary_output_path.exists()
    assert "Unknown source_id in catalog: unknown-official-source" in result.stderr


def test_raw_text_stub_tolerates_blank_lines_and_missing_optional_notes(tmp_path: Path):
    raw_text = """DOCUMENT_ID: cn-nl-interest-raw-stub
TITLE: China-Netherlands Tax Treaty Interest Stub
DOCUMENT_TYPE: treaty_text
JURISDICTIONS: CN,NL

ARTICLE: 11|Interest|interest
SUMMARY: Defines treaty treatment for interest between the two jurisdictions.

PARAGRAPH: art11-p1|Article 11(1)|Article 11(1)|en
SEGMENT: art11-p1-s1|1|5|article_paragraph|clean|verbatim|Interest treatment is governed by Article 11(1).
RULE: cn-nl-art11-p1-base|withholding_tax_cap|10%|bidirectional|1|true|0.97|art11-p1-s1|Treaty applicability depends on the facts of the payment.|Final eligibility depends on facts beyond v1 scope.
"""
    raw_input_path = tmp_path / "interest.stub.txt"
    parser_output_path = tmp_path / "interest.parsed.json"
    raw_input_path.write_text(raw_text, encoding="utf-8")

    parse_result = run_raw_parser(parser_output_path, input_path=raw_input_path)

    assert parse_result.returncode == 0, parse_result.stderr
    parser_payload = json.loads(parser_output_path.read_text(encoding="utf-8"))
    assert parser_payload["document"]["document_id"] == "cn-nl-interest-raw-stub"
    assert parser_payload["parsed_articles"][0]["article_number"] == "11"
    assert parser_payload["parsed_articles"][0]["article_notes"] == []


def test_raw_text_stub_ignores_comment_lines(tmp_path: Path):
    raw_text = """# narrow parser comment
DOCUMENT_ID: cn-nl-interest-commented-stub
TITLE: China-Netherlands Tax Treaty Interest Stub
DOCUMENT_TYPE: treaty_text
JURISDICTIONS: CN,NL

# article block starts here
ARTICLE: 11|Interest|interest
SUMMARY: Defines treaty treatment for interest between the two jurisdictions.
PARAGRAPH: art11-p1|Article 11(1)|Article 11(1)|en
SEGMENT: art11-p1-s1|1|5|article_paragraph|clean|verbatim|Interest treatment is governed by Article 11(1).
RULE: cn-nl-art11-p1-base|withholding_tax_cap|10%|bidirectional|1|true|0.97|art11-p1-s1|Treaty applicability depends on the facts of the payment.|Final eligibility depends on facts beyond v1 scope.
"""
    raw_input_path = tmp_path / "interest-commented.stub.txt"
    parser_output_path = tmp_path / "interest-commented.parsed.json"
    raw_input_path.write_text(raw_text, encoding="utf-8")

    parse_result = run_raw_parser(parser_output_path, input_path=raw_input_path)

    assert parse_result.returncode == 0, parse_result.stderr
    parser_payload = json.loads(parser_output_path.read_text(encoding="utf-8"))
    assert parser_payload["document"]["document_id"] == "cn-nl-interest-commented-stub"
    assert parser_payload["parsed_articles"][0]["paragraphs"][0]["paragraph_id"] == "art11-p1"


def test_raw_ingest_script_writes_error_report_for_invalid_raw_input(tmp_path: Path):
    raw_text = """DOCUMENT_ID: cn-nl-invalid-normalization-stub
TITLE: China-Netherlands Tax Treaty Invalid Normalization Stub
DOCUMENT_TYPE: treaty_text
JURISDICTIONS: CN,NL

ARTICLE: 12|Royalties|royalties
SUMMARY: Defines treaty treatment for royalties between the two jurisdictions.
PARAGRAPH: art12-p1|Article 12(1)|Article 12(1)|en
SEGMENT: art12-p1-s1|1|6|article_paragraph|clean|machine_magic|Royalty treatment is governed by Article 12(1).
RULE: cn-nl-art12-p1-base|withholding_tax_cap|10%|bidirectional|1|true|0.98|art12-p1-s1|Treaty applicability depends on the facts of the payment.|Final eligibility depends on facts beyond the current review scope.
"""
    raw_input_path = tmp_path / "invalid-normalization.stub.txt"
    parsed_output_path = tmp_path / "invalid-normalization.parsed.json"
    dataset_output_path = tmp_path / "invalid-normalization.dataset.json"
    report_output_path = tmp_path / "invalid-normalization.report.json"
    raw_input_path.write_text(raw_text, encoding="utf-8")

    result = run_raw_ingest(
        parsed_output_path=parsed_output_path,
        dataset_output_path=dataset_output_path,
        input_path=raw_input_path,
        report_output_path=report_output_path,
    )

    assert result.returncode == 1
    assert not parsed_output_path.exists()
    assert not dataset_output_path.exists()
    assert report_output_path.exists()
    report_payload = json.loads(report_output_path.read_text(encoding="utf-8"))
    assert report_payload == {
        "status": "error",
        "document_id": "cn-nl-invalid-normalization-stub",
        "error_stage": "validation",
        "error_message": "Found invalid normalization_status for art12-p1-s1: machine_magic",
    }
    assert "Found invalid normalization_status for art12-p1-s1: machine_magic" in result.stderr


def test_generated_dataset_is_consumable_by_analysis_service(tmp_path: Path, monkeypatch):
    output_path = tmp_path / "cn-nl.generated.json"
    result = run_builder(output_path)

    assert result.returncode == 0, result.stderr

    monkeypatch.setattr(service, "DATA_PATH", output_path)

    response = service.analyze_scenario("中国居民企业向荷兰支付特许权使用费")

    assert response["supported"] is True
    assert response["result"]["article_number"] == "12"
    assert response["result"]["source_reference"] == "Article 12(2)"
    assert response["result"]["rate"] == "10%"
    assert response["result"]["extraction_confidence"] == 0.98
    assert "the tax so charged shall not exceed 10 per cent" in response["result"]["source_excerpt"]


def test_build_script_rejects_segment_without_source_reference(tmp_path: Path):
    def mutate(payload: dict) -> None:
        payload["parsed_articles"][0]["paragraphs"][0]["source_reference"] = ""

    source_path = write_invalid_source(tmp_path, mutate)
    output_path = tmp_path / "cn-nl.generated.json"

    result = run_builder(output_path, source_path=source_path)

    assert result.returncode == 1
    assert "missing source_reference" in result.stderr


def test_build_script_rejects_duplicate_rule_id(tmp_path: Path):
    def mutate(payload: dict) -> None:
        duplicate_rule_id = payload["parsed_articles"][0]["paragraphs"][0]["extracted_rules"][0]["rule_id"]
        payload["parsed_articles"][1]["paragraphs"][0]["extracted_rules"][0]["rule_id"] = duplicate_rule_id

    source_path = write_invalid_source(tmp_path, mutate)
    output_path = tmp_path / "cn-nl.generated.json"

    result = run_builder(output_path, source_path=source_path)

    assert result.returncode == 1
    assert "duplicate rule_id" in result.stderr


def test_build_script_accepts_parser_like_intermediate_format(tmp_path: Path):
    source_path = write_source_payload(tmp_path, build_parser_like_source_payload())
    output_path = tmp_path / "cn-nl.generated.json"

    result = run_builder(output_path, source_path=source_path)

    assert result.returncode == 0, result.stderr
    payload = json.loads(output_path.read_text(encoding="utf-8"))
    assert payload["articles"][0]["article_number"] == "12"
    assert payload["articles"][0]["paragraphs"][0]["rules"][0]["rule_id"] == "cn-nl-art12-p1-base"
    assert payload["articles"][0]["paragraphs"][0]["source_excerpt"] == (
        "Royalty treatment is governed by Article 12(1). Treaty conditions and factual qualification still matter."
    )
    assert payload["articles"][0]["paragraphs"][0]["provenance_summary"] == {
        "primary_rule_id": "cn-nl-art12-p1-base",
        "paragraph_confidence": 0.98,
        "segment_count": 2,
        "covered_segment_count": 2,
        "segment_coverage": 1.0,
    }
    assert payload["articles"][0]["paragraphs"][0]["rules"][0]["derived_from_segments"] == [
        "art12-p1-s1",
        "art12-p1-s2",
    ]
    assert len(payload["articles"][0]["paragraphs"][0]["rules"]) == 2
    assert payload["articles"][0]["paragraphs"][0]["rules"][0]["candidate_rank"] == 1
    assert payload["articles"][0]["paragraphs"][0]["rules"][1]["candidate_rank"] == 2


def test_build_script_rejects_unsupported_income_type_in_parser_output(tmp_path: Path):
    payload = build_parser_like_source_payload()
    payload["parsed_articles"][0]["income_type"] = "services"
    source_path = write_source_payload(tmp_path, payload)
    output_path = tmp_path / "cn-nl.generated.json"

    result = run_builder(output_path, source_path=source_path)

    assert result.returncode == 1
    assert "unsupported income_type" in result.stderr


def test_build_script_rejects_out_of_range_extraction_confidence(tmp_path: Path):
    payload = build_parser_like_source_payload()
    payload["parsed_articles"][0]["paragraphs"][0]["extracted_rules"][0][
        "extraction_confidence"
    ] = 1.5
    source_path = write_source_payload(tmp_path, payload)
    output_path = tmp_path / "cn-nl.generated.json"

    result = run_builder(output_path, source_path=source_path)

    assert result.returncode == 1
    assert "invalid extraction_confidence" in result.stderr


def test_build_script_rejects_rule_with_unknown_source_segment_reference(tmp_path: Path):
    payload = build_parser_like_source_payload()
    payload["parsed_articles"][0]["paragraphs"][0]["extracted_rules"][0][
        "derived_from_segments"
    ] = ["art12-p1-s9"]
    source_path = write_source_payload(tmp_path, payload)
    output_path = tmp_path / "cn-nl.generated.json"

    result = run_builder(output_path, source_path=source_path)

    assert result.returncode == 1
    assert "unknown source segment" in result.stderr


def test_build_script_rejects_duplicate_source_segment_id(tmp_path: Path):
    payload = build_parser_like_source_payload()
    payload["parsed_articles"][0]["paragraphs"][0]["source_segments"][1]["segment_id"] = "art12-p1-s1"
    source_path = write_source_payload(tmp_path, payload)
    output_path = tmp_path / "cn-nl.generated.json"

    result = run_builder(output_path, source_path=source_path)

    assert result.returncode == 1
    assert "duplicate source segment" in result.stderr


def test_build_script_rejects_multiple_primary_candidates_in_one_paragraph(tmp_path: Path):
    payload = build_parser_like_source_payload()
    payload["parsed_articles"][0]["paragraphs"][0]["extracted_rules"][1]["is_primary_candidate"] = True
    source_path = write_source_payload(tmp_path, payload)
    output_path = tmp_path / "cn-nl.generated.json"

    result = run_builder(output_path, source_path=source_path)

    assert result.returncode == 1
    assert "multiple primary candidates" in result.stderr


def test_build_script_aggregates_partial_segment_coverage_into_paragraph_provenance(tmp_path: Path):
    payload = build_parser_like_source_payload()
    payload["parsed_articles"][0]["paragraphs"][0]["extracted_rules"][0]["derived_from_segments"] = [
        "art12-p1-s1"
    ]
    source_path = write_source_payload(tmp_path, payload)
    output_path = tmp_path / "cn-nl.generated.json"

    result = run_builder(output_path, source_path=source_path)

    assert result.returncode == 0, result.stderr
    generated = json.loads(output_path.read_text(encoding="utf-8"))
    assert generated["articles"][0]["paragraphs"][0]["provenance_summary"] == {
        "primary_rule_id": "cn-nl-art12-p1-base",
        "paragraph_confidence": 0.98,
        "segment_count": 2,
        "covered_segment_count": 1,
        "segment_coverage": 0.5,
    }


def test_build_script_rejects_unknown_segment_normalization_status(tmp_path: Path):
    payload = build_parser_like_source_payload()
    payload["parsed_articles"][0]["paragraphs"][0]["source_segments"][0][
        "normalization_status"
    ] = "post_processed_magic"
    source_path = write_source_payload(tmp_path, payload)
    output_path = tmp_path / "cn-nl.generated.json"

    result = run_builder(output_path, source_path=source_path)

    assert result.returncode == 1
    assert "invalid normalization_status" in result.stderr
