from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPTS_PATH = REPO_ROOT / "scripts"
if str(SCRIPTS_PATH) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_PATH))

from build_treaty_dataset import (
    SourceValidationError,
    build_dataset,
    validate_source_payload,
    write_dataset,
)
from parse_cn_nl_raw_text_stub import (
    DEFAULT_INPUT_PATH,
    RawParseError,
    parse_raw_text,
    load_lines,
    write_payload,
)

DEFAULT_PARSED_OUTPUT_PATH = (
    REPO_ROOT / "data" / "source_documents" / "cn-nl-ingested.parsed.json"
)
DEFAULT_DATASET_OUTPUT_PATH = (
    REPO_ROOT / "data" / "treaties" / "cn-nl.v3.generated.from-ingest.json"
)
DEFAULT_REPORT_OUTPUT_PATH = (
    REPO_ROOT / "data" / "treaties" / "cn-nl.v3.generated.from-ingest.report.json"
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run the narrow raw-text ingestion chain into parser-like JSON and generated treaty data."
    )
    parser.add_argument(
        "--input",
        type=Path,
        default=DEFAULT_INPUT_PATH,
        help="Input path for the raw text stub.",
    )
    parser.add_argument(
        "--parsed-output",
        type=Path,
        default=DEFAULT_PARSED_OUTPUT_PATH,
        help="Output path for the parser-like source fixture JSON.",
    )
    parser.add_argument(
        "--dataset-output",
        type=Path,
        default=DEFAULT_DATASET_OUTPUT_PATH,
        help="Output path for the generated dataset JSON.",
    )
    parser.add_argument(
        "--report-output",
        type=Path,
        default=DEFAULT_REPORT_OUTPUT_PATH,
        help="Output path for the ingest report JSON.",
    )
    parser.add_argument(
        "--source-id",
        type=str,
        help="Optional official source id for governance traceability.",
    )
    return parser.parse_args()


def build_attention_items(dataset: dict) -> list[dict]:
    attention_items: list[dict] = []

    for article in dataset["articles"]:
        for paragraph in article["paragraphs"]:
            reasons: list[str] = []
            provenance_summary = paragraph.get("provenance_summary", {})
            if any(
                segment.get("text_quality") == "warning"
                for segment in paragraph.get("source_segments", [])
            ):
                reasons.append("warning_segment_present")
            paragraph_confidence = provenance_summary.get("paragraph_confidence")
            if paragraph_confidence is not None and paragraph_confidence < 0.8:
                reasons.append("low_paragraph_confidence")
            if provenance_summary.get("segment_coverage", 1.0) < 1.0:
                reasons.append("partial_segment_coverage")

            if reasons:
                attention_items.append(
                    {
                        "paragraph_label": paragraph["paragraph_label"],
                        "source_reference": paragraph["source_reference"],
                        "reasons": reasons,
                    }
                )

    return attention_items


def build_ingest_report(source_payload: dict, dataset: dict, source_id: str | None = None) -> dict:
    article_count = len(source_payload["parsed_articles"])
    paragraph_count = 0
    rule_count = 0
    source_segment_count = 0
    normalized_segment_count = 0
    warning_segment_count = 0
    attention_items = build_attention_items(dataset)

    for article in source_payload["parsed_articles"]:
        paragraphs = article["paragraphs"]
        paragraph_count += len(paragraphs)
        for paragraph in paragraphs:
            source_segments = paragraph.get("source_segments", [])
            extracted_rules = paragraph.get("extracted_rules", [])
            rule_count += len(extracted_rules)
            source_segment_count += len(source_segments)
            normalized_segment_count += sum(
                1
                for segment in source_segments
                if segment.get("normalization_status") == "normalized"
            )
            warning_segment_count += sum(
                1 for segment in source_segments if segment.get("text_quality") == "warning"
            )

    report = {
        "document_id": source_payload["document"]["document_id"],
        "status": "warning" if attention_items else "ok",
        "article_count": article_count,
        "paragraph_count": paragraph_count,
        "rule_count": rule_count,
        "source_segment_count": source_segment_count,
        "normalized_segment_count": normalized_segment_count,
        "warning_segment_count": warning_segment_count,
        "attention_item_count": len(attention_items),
        "attention_items": attention_items,
    }
    if source_id is not None:
        report["source_id"] = source_id
    return report


def write_report(report: dict, output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def extract_document_id(lines: list[str]) -> str | None:
    for raw_line in lines:
        line = raw_line.strip()
        if line.startswith("DOCUMENT_ID: "):
            return line.removeprefix("DOCUMENT_ID: ").strip()
    return None


def build_error_report(
    document_id: str | None,
    error_stage: str,
    error_message: str,
    source_id: str | None = None,
) -> dict:
    report = {
        "status": "error",
        "document_id": document_id,
        "error_stage": error_stage,
        "error_message": error_message,
    }
    if source_id is not None:
        report["source_id"] = source_id
    return report


def main() -> int:
    args = parse_args()
    lines: list[str] = []

    try:
        lines = load_lines(args.input)
        source_payload = parse_raw_text(lines)
    except OSError as error:
        write_report(
            build_error_report(
                document_id=None,
                error_stage="io",
                error_message=str(error),
                source_id=args.source_id,
            ),
            args.report_output,
        )
        print(str(error), file=sys.stderr)
        return 1
    except RawParseError as error:
        write_report(
            build_error_report(
                document_id=extract_document_id(lines),
                error_stage="parse",
                error_message=str(error),
                source_id=args.source_id,
            ),
            args.report_output,
        )
        print(str(error), file=sys.stderr)
        return 1

    try:
        validate_source_payload(source_payload)
    except (ValueError, SourceValidationError) as error:
        write_report(
            build_error_report(
                document_id=source_payload.get("document", {}).get("document_id"),
                error_stage="validation",
                error_message=str(error),
                source_id=args.source_id,
            ),
            args.report_output,
        )
        print(str(error), file=sys.stderr)
        return 1

    dataset = build_dataset(source_payload)
    report = build_ingest_report(source_payload, dataset, source_id=args.source_id)
    write_payload(source_payload, args.parsed_output)
    write_dataset(dataset, args.dataset_output)
    write_report(report, args.report_output)
    print(f"Wrote parser-like fixture to {args.parsed_output}")
    print(f"Wrote dataset to {args.dataset_output}")
    print(f"Wrote ingest report to {args.report_output}")
    attention_label = (
        "attention item" if report["attention_item_count"] == 1 else "attention items"
    )
    print(
        "Ingest status: "
        f"{report['status']} ({report['attention_item_count']} {attention_label})"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
