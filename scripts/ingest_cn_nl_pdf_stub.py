from __future__ import annotations

import argparse
import sys
from pathlib import Path

from extract_pdf_text_stub import extract_pdf_text, write_text
from ingest_cn_nl_raw_text_stub import (
    build_error_report,
    build_ingest_report,
    extract_document_id,
    write_report,
)
from build_cn_nl_dataset import (
    SourceValidationError,
    build_dataset,
    validate_source_payload,
    write_dataset,
)
from parse_cn_nl_raw_text_stub import RawParseError, parse_raw_text, write_payload


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_INPUT_PATH = REPO_ROOT / "data" / "raw_documents" / "cn-nl-text.pdf"
DEFAULT_RAW_TEXT_OUTPUT_PATH = REPO_ROOT / "data" / "raw_documents" / "cn-nl-extracted.txt"
DEFAULT_PARSED_OUTPUT_PATH = (
    REPO_ROOT / "data" / "source_documents" / "cn-nl-from-pdf.parsed.json"
)
DEFAULT_DATASET_OUTPUT_PATH = (
    REPO_ROOT / "data" / "treaties" / "cn-nl.v3.generated.from-pdf.json"
)
DEFAULT_REPORT_OUTPUT_PATH = (
    REPO_ROOT / "data" / "treaties" / "cn-nl.v3.generated.from-pdf.report.json"
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run the narrow text-PDF ingestion chain into parser-like JSON and generated treaty data."
    )
    parser.add_argument(
        "--input",
        type=Path,
        default=DEFAULT_INPUT_PATH,
        help="Input PDF path.",
    )
    parser.add_argument(
        "--raw-text-output",
        type=Path,
        default=DEFAULT_RAW_TEXT_OUTPUT_PATH,
        help="Output path for extracted raw text.",
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
    return parser.parse_args()


def main() -> int:
    args = parse_args()

    try:
        extracted_text = extract_pdf_text(args.input)
    except OSError as error:
        write_report(build_error_report(None, "io", str(error)), args.report_output)
        print(str(error), file=sys.stderr)
        return 1
    except ValueError as error:
        write_report(build_error_report(None, "pdf_extract", str(error)), args.report_output)
        print(str(error), file=sys.stderr)
        return 1

    write_text(extracted_text, args.raw_text_output)
    lines = extracted_text.splitlines()

    try:
        source_payload = parse_raw_text(lines)
    except RawParseError as error:
        write_report(
            build_error_report(
                extract_document_id(lines),
                "parse",
                str(error),
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
                source_payload.get("document", {}).get("document_id"),
                "validation",
                str(error),
            ),
            args.report_output,
        )
        print(str(error), file=sys.stderr)
        return 1

    dataset = build_dataset(source_payload)
    report = build_ingest_report(source_payload, dataset)
    write_payload(source_payload, args.parsed_output)
    write_dataset(dataset, args.dataset_output)
    write_report(report, args.report_output)
    print(f"Wrote extracted text to {args.raw_text_output}")
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
