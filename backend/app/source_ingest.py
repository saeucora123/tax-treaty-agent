from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path
import sys

from pypdf import PdfReader

from app.llm_document_extractor import extract_source_payload_from_text


SCRIPTS_PATH = Path(__file__).resolve().parents[2] / "scripts"
if str(SCRIPTS_PATH) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_PATH))

from build_treaty_dataset import validate_source_payload


REPO_ROOT = Path(__file__).resolve().parents[2]
ARTICLE_HEADING_PATTERN = re.compile(r"^Article\s+\d+\s+.+$")
NUMBERED_PARAGRAPH_PATTERN = re.compile(r"^\d+\.\s+.+$")
PAGE_NUMBER_PATTERN = re.compile(r"^Page\s+\d+$", re.IGNORECASE)
DOCUMENT_FIELD_PREFIXES = (
    "DOCUMENT_ID: ",
    "TITLE: ",
    "DOCUMENT_TYPE: ",
    "JURISDICTIONS: ",
    "DOCUMENT_NOTE: ",
)


class SourceBuildError(ValueError):
    pass


class PdfExtractionError(ValueError):
    pass


def load_json(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as file:
        return json.load(file)


def write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def resolve_relative_path(value: str | Path, *, base_dir: Path) -> Path:
    path = Path(value)
    if path.is_absolute():
        return path
    return (base_dir / path).resolve()


def load_known_source_ids(pair_id: str) -> set[str]:
    registry_path = REPO_ROOT / "data" / "source_registry" / f"{pair_id}-official-sources.json"
    registry = load_json(registry_path)
    return {source["source_id"] for source in registry["sources"]}


def validate_manifest(manifest: dict) -> None:
    required_top_level = [
        "pair_id",
        "jurisdictions",
        "target_articles",
        "document",
        "sources",
        "output_source_document",
        "build_report_output",
    ]
    for field in required_top_level:
        if field not in manifest:
            raise SourceBuildError(f"Source-build manifest is missing required field: {field}")

    document = manifest["document"]
    required_document_fields = [
        "document_id",
        "title",
        "document_type",
        "source_trace",
        "mli_context",
    ]
    for field in required_document_fields:
        if field not in document:
            raise SourceBuildError(f"Source-build document block is missing required field: {field}")

    source_trace = document["source_trace"]
    if not source_trace.get("official_source_ids"):
        raise SourceBuildError("Source-build manifest document.source_trace.official_source_ids cannot be empty")
    if not source_trace.get("working_papers"):
        raise SourceBuildError("Source-build manifest document.source_trace.working_papers cannot be empty")

    mli_context = document["mli_context"]
    if not mli_context.get("official_source_ids"):
        raise SourceBuildError("Source-build manifest document.mli_context.official_source_ids cannot be empty")

    if not manifest["sources"]:
        raise SourceBuildError("Source-build manifest must include at least one source entry")


def normalize_text(text: str) -> str:
    lines = [line.strip() for line in text.splitlines()]
    lines = drop_repeated_header_lines(lines)
    kept_lines: list[str] = []
    for line in lines:
        if not line:
            if kept_lines and kept_lines[-1] != "":
                kept_lines.append("")
            continue
        if PAGE_NUMBER_PATTERN.match(line):
            continue
        if should_attach_to_previous_line(line, kept_lines):
            kept_lines[-1] = f"{kept_lines[-1]} {line}"
            continue
        kept_lines.append(line)
    while kept_lines and kept_lines[-1] == "":
        kept_lines.pop()
    return "\n".join(kept_lines)


def should_attach_to_previous_line(line: str, kept_lines: list[str]) -> bool:
    if not kept_lines:
        return False
    previous_line = kept_lines[-1]
    if previous_line == "":
        return False
    if line.startswith("#"):
        return False
    if line.startswith(DOCUMENT_FIELD_PREFIXES):
        return False
    if PAGE_NUMBER_PATTERN.match(line):
        return False
    if ARTICLE_HEADING_PATTERN.match(line):
        return False
    if NUMBERED_PARAGRAPH_PATTERN.match(line):
        return False
    return True


def drop_repeated_header_lines(lines: list[str]) -> list[str]:
    candidates = [
        line
        for line in lines
        if line
        and not line.startswith(DOCUMENT_FIELD_PREFIXES)
        and not ARTICLE_HEADING_PATTERN.match(line)
        and not NUMBERED_PARAGRAPH_PATTERN.match(line)
        and not PAGE_NUMBER_PATTERN.match(line)
    ]
    repeated_headers = {line for line in set(candidates) if candidates.count(line) > 1}
    return [line for line in lines if line not in repeated_headers]


def extract_pdf_text(input_path: Path) -> str:
    reader = PdfReader(str(input_path))
    page_texts: list[str] = []
    for page in reader.pages:
        text = page.extract_text() or ""
        if text.strip():
            page_texts.append(text)
    if not page_texts:
        raise PdfExtractionError("No extractable text found in PDF.")
    normalized = normalize_text("\n".join(page_texts))
    if not normalized:
        raise PdfExtractionError("No extractable text found in PDF.")
    return normalized.strip() + "\n"


def build_document_payload(manifest: dict) -> dict:
    document = dict(manifest["document"])
    document["jurisdictions"] = list(manifest["jurisdictions"])
    document.setdefault("notes", [])
    return document


def sort_articles(parsed_articles: list[dict]) -> list[dict]:
    def sort_key(article: dict) -> tuple[int, str]:
        article_number = str(article["article_number"])
        try:
            return (int(article_number), article_number)
        except ValueError:
            return (999, article_number)

    return sorted(parsed_articles, key=sort_key)


def merge_source_payloads(manifest: dict, source_payloads: list[dict]) -> dict:
    parsed_articles: list[dict] = []
    for payload in source_payloads:
        parsed_articles.extend(payload.get("parsed_articles", []))
    merged = {
        "document": build_document_payload(manifest),
        "parsed_articles": sort_articles(parsed_articles),
    }
    validate_source_payload(merged)
    return merged


def build_report(
    manifest: dict,
    merged_payload: dict,
    *,
    results: list[dict],
    missing_target_articles: list[str],
    started_at_utc: str,
    completed_at_utc: str,
    duration_seconds: int,
) -> dict:
    paragraph_count = 0
    rule_count = 0
    for article in merged_payload["parsed_articles"]:
        paragraph_count += len(article["paragraphs"])
        for paragraph in article["paragraphs"]:
            rule_count += len(paragraph["extracted_rules"])

    return {
        "status": "ok" if not missing_target_articles else "error",
        "pair_id": manifest["pair_id"],
        "started_at_utc": started_at_utc,
        "completed_at_utc": completed_at_utc,
        "duration_seconds": duration_seconds,
        "source_count": len(results),
        "article_count": len(merged_payload["parsed_articles"]),
        "paragraph_count": paragraph_count,
        "rule_count": rule_count,
        "target_articles": list(manifest["target_articles"]),
        "missing_target_articles": missing_target_articles,
        "results": results,
    }


def build_source_entry_payload(entry: dict, *, jurisdictions: list[str]) -> tuple[dict, str | None]:
    source_type = entry["source_type"]
    input_path = Path(entry["input_path"])
    language = entry.get("language", "en")
    if source_type == "raw_text":
        raw_text = input_path.read_text(encoding="utf-8")
        payload = extract_source_payload_from_text(
            raw_text,
            document_id=entry["document_id"],
            title=entry["title"],
            document_type=entry["document_type"],
            jurisdictions=jurisdictions,
            source_language=language,
        )
        if payload is None:
            raise SourceBuildError(
                f"LLM extractor is unavailable for raw_text source: {entry['source_id']}"
            )
        return payload, None

    if source_type == "pdf_text":
        raw_text = extract_pdf_text(input_path)
        payload = extract_source_payload_from_text(
            raw_text,
            document_id=entry["document_id"],
            title=entry["title"],
            document_type=entry["document_type"],
            jurisdictions=jurisdictions,
            source_language=language,
        )
        if payload is None:
            raise SourceBuildError(
                f"LLM extractor is unavailable for pdf_text source: {entry['source_id']}"
            )
        return payload, raw_text

    raise SourceBuildError(f"Unsupported source_type in source-build manifest: {source_type}")


def run_source_build(manifest_path: Path) -> dict:
    started_at = datetime.now(timezone.utc)
    manifest_path = manifest_path.resolve()
    manifest = load_json(manifest_path)
    validate_manifest(manifest)
    manifest_dir = manifest_path.parent
    known_source_ids = load_known_source_ids(manifest["pair_id"])
    source_payloads: list[dict] = []
    results: list[dict] = []

    for entry in manifest["sources"]:
        if entry["source_id"] not in known_source_ids:
            raise SourceBuildError(f"Unknown source_id in source-build manifest: {entry['source_id']}")
        payload, raw_text = build_source_entry_payload(
            {
                **entry,
                "input_path": str(resolve_relative_path(entry["input_path"], base_dir=manifest_dir)),
            },
            jurisdictions=list(manifest["jurisdictions"]),
        )
        parsed_output_path = resolve_relative_path(entry["parsed_output_path"], base_dir=manifest_dir)
        write_json(parsed_output_path, payload)
        if entry["source_type"] == "pdf_text":
            raw_text_output_value = entry.get("raw_text_output_path")
            if not raw_text_output_value:
                raise SourceBuildError(
                    f"pdf_text source is missing raw_text_output_path: {entry['source_id']}"
                )
            write_text(
                resolve_relative_path(raw_text_output_value, base_dir=manifest_dir),
                raw_text or "",
            )
        source_payloads.append(payload)
        results.append(
            {
                "source_id": entry["source_id"],
                "source_type": entry["source_type"],
                "parsed_output_path": str(parsed_output_path),
            }
        )

    merged_payload = merge_source_payloads(manifest, source_payloads)
    found_articles = {article["article_number"] for article in merged_payload["parsed_articles"]}
    missing_target_articles = [
        article_number
        for article_number in manifest["target_articles"]
        if article_number not in found_articles
    ]
    if missing_target_articles:
        raise SourceBuildError(
            "Missing target articles in merged source document: "
            + ", ".join(missing_target_articles)
        )

    output_source_document = resolve_relative_path(
        manifest["output_source_document"],
        base_dir=manifest_dir,
    )
    build_report_output = resolve_relative_path(
        manifest["build_report_output"],
        base_dir=manifest_dir,
    )
    write_json(output_source_document, merged_payload)
    completed_at = datetime.now(timezone.utc)
    report = build_report(
        manifest,
        merged_payload,
        results=results,
        missing_target_articles=missing_target_articles,
        started_at_utc=started_at.isoformat(),
        completed_at_utc=completed_at.isoformat(),
        duration_seconds=max(0, int((completed_at - started_at).total_seconds())),
    )
    write_json(build_report_output, report)
    return report
