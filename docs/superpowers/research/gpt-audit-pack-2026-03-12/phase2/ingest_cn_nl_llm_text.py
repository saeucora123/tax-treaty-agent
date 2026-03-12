from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys


REPO_ROOT = Path(__file__).resolve().parents[1]
BACKEND_PATH = REPO_ROOT / "backend"
if str(BACKEND_PATH) not in sys.path:
    sys.path.insert(0, str(BACKEND_PATH))

from app.llm_document_extractor import (  # noqa: E402
    LLMDocumentExtractionError,
    extract_source_payload_from_text,
    load_config_from_env,
)
from build_cn_nl_dataset import (  # noqa: E402
    SourceValidationError,
    build_dataset,
    validate_source_payload,
    write_dataset,
)


DEFAULT_INPUT_PATH = REPO_ROOT / "data" / "raw_documents" / "cn-nl-article11-12.clean.txt"
DEFAULT_PARSED_OUTPUT_PATH = (
    REPO_ROOT / "data" / "source_documents" / "cn-nl.llm-extracted.parsed.json"
)
DEFAULT_DATASET_OUTPUT_PATH = (
    REPO_ROOT / "data" / "treaties" / "cn-nl.v3.generated.from-llm.json"
)
DEFAULT_REPORT_OUTPUT_PATH = (
    REPO_ROOT / "data" / "treaties" / "cn-nl.v3.generated.from-llm.report.json"
)


def write_json(payload: dict, output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def count_rules(source_payload: dict) -> int:
    return sum(
        len(paragraph["extracted_rules"])
        for article in source_payload["parsed_articles"]
        for paragraph in article["paragraphs"]
    )


def count_paragraphs(source_payload: dict) -> int:
    return sum(len(article["paragraphs"]) for article in source_payload["parsed_articles"])


def build_success_report(source_payload: dict) -> dict:
    config = load_config_from_env()
    return {
        "status": "ok",
        "document_id": source_payload["document"]["document_id"],
        "article_count": len(source_payload["parsed_articles"]),
        "paragraph_count": count_paragraphs(source_payload),
        "rule_count": count_rules(source_payload),
        "llm_provider": "deepseek",
        "llm_model": config.model if config else None,
    }


def build_error_report(document_id: str, stage: str, message: str) -> dict:
    return {
        "status": "error",
        "document_id": document_id,
        "error_stage": stage,
        "error_message": message,
    }


def run_ingest(
    *,
    input_path: Path,
    parsed_output_path: Path,
    dataset_output_path: Path,
    report_output_path: Path,
    document_id: str,
    title: str,
    document_type: str,
    jurisdictions: list[str],
    source_language: str = "en",
) -> tuple[int, dict]:
    try:
        raw_text = input_path.read_text(encoding="utf-8")
        source_payload = extract_source_payload_from_text(
            raw_text,
            document_id=document_id,
            title=title,
            document_type=document_type,
            jurisdictions=jurisdictions,
            source_language=source_language,
        )
        if source_payload is None:
            raise LLMDocumentExtractionError(
                "DeepSeek configuration is unavailable; cannot run LLM document extraction."
            )
        write_json(source_payload, parsed_output_path)
        validate_source_payload(source_payload)
        dataset = build_dataset(source_payload)
        write_dataset(dataset, dataset_output_path)
        report = build_success_report(source_payload)
        write_json(report, report_output_path)
        return 0, report
    except OSError as error:
        report = build_error_report(document_id, "io", str(error))
    except LLMDocumentExtractionError as error:
        report = build_error_report(document_id, "llm_extraction", str(error))
    except SourceValidationError as error:
        report = build_error_report(document_id, "validation", str(error))

    write_json(report, report_output_path)
    return 1, report


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run a constrained LLM extraction from clean treaty text into parser-like source JSON and a generated dataset."
    )
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT_PATH)
    parser.add_argument("--parsed-output", type=Path, default=DEFAULT_PARSED_OUTPUT_PATH)
    parser.add_argument("--dataset-output", type=Path, default=DEFAULT_DATASET_OUTPUT_PATH)
    parser.add_argument("--report-output", type=Path, default=DEFAULT_REPORT_OUTPUT_PATH)
    parser.add_argument("--document-id", default="cn-nl-article11-12-llm")
    parser.add_argument("--title", default="China-Netherlands Tax Treaty Articles 11-12")
    parser.add_argument("--document-type", default="treaty_text")
    parser.add_argument("--jurisdictions", default="CN,NL")
    parser.add_argument("--source-language", default="en")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    exit_code, report = run_ingest(
        input_path=args.input,
        parsed_output_path=args.parsed_output,
        dataset_output_path=args.dataset_output,
        report_output_path=args.report_output,
        document_id=args.document_id,
        title=args.title,
        document_type=args.document_type,
        jurisdictions=[item.strip() for item in args.jurisdictions.split(",") if item.strip()],
        source_language=args.source_language,
    )
    if exit_code == 0:
        print(
            f"LLM ingest status: ok ({report['article_count']} articles, "
            f"{report['paragraph_count']} paragraphs, {report['rule_count']} rules)"
        )
    else:
        print(
            f"LLM ingest status: error at {report['error_stage']}: {report['error_message']}",
            file=sys.stderr,
        )
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
