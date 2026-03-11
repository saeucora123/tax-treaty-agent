from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_INPUT_PATH = REPO_ROOT / "data" / "raw_documents" / "cn-nl-article12.stub.txt"
DEFAULT_OUTPUT_PATH = REPO_ROOT / "data" / "source_documents" / "cn-nl-article12.parsed.json"
ARTICLE_HEADING_PATTERN = re.compile(r"^Article\s+(\d+)\s+(.+)$")
PARAGRAPH_TEXT_PATTERN = re.compile(r"^(\d+)\.\s+(.+)$")
PERCENT_RATE_PATTERN = re.compile(r"(\d+)\s+per\s+cent", re.IGNORECASE)


class RawParseError(ValueError):
    pass


def load_lines(input_path: Path) -> list[str]:
    return input_path.read_text(encoding="utf-8").splitlines()


def parse_raw_text(lines: list[str]) -> dict:
    document: dict = {"notes": []}
    parsed_articles: list[dict] = []
    current_article: dict | None = None
    current_paragraph: dict | None = None

    for line_number, raw_line in enumerate(lines, start=1):
        line = raw_line.strip()
        if not line:
            continue
        if line.startswith("#"):
            continue

        if line.startswith("DOCUMENT_ID: "):
            document["document_id"] = line.removeprefix("DOCUMENT_ID: ").strip()
            continue
        if line.startswith("TITLE: "):
            document["title"] = line.removeprefix("TITLE: ").strip()
            continue
        if line.startswith("DOCUMENT_TYPE: "):
            document["document_type"] = line.removeprefix("DOCUMENT_TYPE: ").strip()
            continue
        if line.startswith("JURISDICTIONS: "):
            document["jurisdictions"] = [
                item.strip() for item in line.removeprefix("JURISDICTIONS: ").split(",")
            ]
            continue
        if line.startswith("DOCUMENT_NOTE: "):
            document["notes"].append(line.removeprefix("DOCUMENT_NOTE: ").strip())
            continue

        if line.startswith("ARTICLE: "):
            article_number, article_title, income_type = split_exact(
                line.removeprefix("ARTICLE: "), 3, "ARTICLE"
            )
            current_article = build_article_block(
                article_number=article_number,
                article_title=article_title,
                income_type=income_type,
                summary="",
            )
            parsed_articles.append(current_article)
            current_paragraph = None
            continue

        if line.startswith("SUMMARY: "):
            require_context(current_article, "SUMMARY")
            current_article["summary"] = line.removeprefix("SUMMARY: ").strip()
            continue

        if line.startswith("ARTICLE_NOTE: "):
            require_context(current_article, "ARTICLE_NOTE")
            current_article["article_notes"].append(line.removeprefix("ARTICLE_NOTE: ").strip())
            continue

        if line.startswith("PARAGRAPH: "):
            require_context(current_article, "PARAGRAPH")
            paragraph_id, paragraph_label, source_reference, source_language = split_exact(
                line.removeprefix("PARAGRAPH: "), 4, "PARAGRAPH"
            )
            current_paragraph = build_paragraph_block(
                paragraph_id=paragraph_id,
                paragraph_label=paragraph_label,
                source_reference=source_reference,
                source_language=source_language,
            )
            current_article["paragraphs"].append(current_paragraph)
            continue

        if line.startswith("SEGMENT: "):
            require_context(current_paragraph, "SEGMENT")
            (
                segment_id,
                segment_order,
                page_hint,
                source_kind,
                text_quality,
                normalization_status,
                text,
            ) = split_exact(line.removeprefix("SEGMENT: "), 7, "SEGMENT")
            current_paragraph["source_segments"].append(
                {
                    "segment_id": segment_id,
                    "segment_order": int(segment_order),
                    "raw_line_number": line_number,
                    "page_hint": int(page_hint),
                    "source_kind": source_kind,
                    "text_quality": text_quality,
                    "normalization_status": normalization_status,
                    "text": text,
                }
            )
            continue

        if line.startswith("RULE: "):
            require_context(current_paragraph, "RULE")
            (
                rule_id,
                rule_type,
                rate,
                direction,
                candidate_rank,
                is_primary_candidate,
                extraction_confidence,
                derived_from_segments,
                condition,
                review_reason,
            ) = split_exact(line.removeprefix("RULE: "), 10, "RULE")
            current_paragraph["extracted_rules"].append(
                {
                    "rule_id": rule_id,
                    "rule_type": rule_type,
                    "rate": rate,
                    "direction": direction,
                    "candidate_rank": int(candidate_rank),
                    "is_primary_candidate": parse_bool(is_primary_candidate),
                    "extraction_confidence": float(extraction_confidence),
                    "derived_from_segments": [item.strip() for item in derived_from_segments.split(",") if item.strip()],
                    "conditions": [condition],
                    "human_review_required": True,
                    "review_reason": review_reason,
                }
            )
            continue

        article_heading_match = ARTICLE_HEADING_PATTERN.match(line)
        if article_heading_match:
            article_number, article_title = article_heading_match.groups()
            current_article = build_article_block(
                article_number=article_number,
                article_title=article_title,
                income_type=infer_income_type(article_title),
                summary=f"Auto-derived from semi-structured raw text for {article_title.lower()}.",
            )
            parsed_articles.append(current_article)
            current_paragraph = None
            continue

        paragraph_text_match = PARAGRAPH_TEXT_PATTERN.match(line)
        if paragraph_text_match:
            require_context(current_article, "numbered paragraph")
            paragraph_number, paragraph_text = paragraph_text_match.groups()
            current_paragraph = build_paragraph_block(
                paragraph_id=build_paragraph_id(current_article["article_number"], paragraph_number),
                paragraph_label=build_paragraph_label(current_article["article_number"], paragraph_number),
                source_reference=build_paragraph_label(current_article["article_number"], paragraph_number),
                source_language="en",
            )
            current_paragraph["source_segments"].append(
                {
                    "segment_id": f"{current_paragraph['paragraph_id']}-s1",
                    "segment_order": 1,
                    "raw_line_number": line_number,
                    "page_hint": None,
                    "source_kind": "article_paragraph",
                    "text_quality": "clean",
                    "normalization_status": "verbatim",
                    "text": paragraph_text,
                }
            )
            current_paragraph["extracted_rules"].append(
                build_semistructured_rule(
                    article_number=current_article["article_number"],
                    paragraph_number=paragraph_number,
                    income_type=current_article["income_type"],
                    segment_id=f"{current_paragraph['paragraph_id']}-s1",
                    paragraph_text=paragraph_text,
                )
            )
            current_article["paragraphs"].append(current_paragraph)
            continue

        raise RawParseError(f"Unsupported raw text line: {line}")

    validate_parsed_payload(document, parsed_articles)
    return {"document": document, "parsed_articles": parsed_articles}


def split_exact(payload: str, expected_parts: int, label: str) -> list[str]:
    parts = [part.strip() for part in payload.split("|")]
    if len(parts) != expected_parts:
        raise RawParseError(f"{label} line expected {expected_parts} fields, got {len(parts)}")
    return parts


def build_article_block(
    article_number: str,
    article_title: str,
    income_type: str,
    summary: str,
) -> dict:
    return {
        "article_number": article_number,
        "article_title": article_title,
        "article_label": f"Article {article_number}",
        "income_type": income_type,
        "summary": summary,
        "article_notes": [],
        "paragraphs": [],
    }


def build_paragraph_block(
    paragraph_id: str,
    paragraph_label: str,
    source_reference: str,
    source_language: str,
) -> dict:
    return {
        "paragraph_id": paragraph_id,
        "paragraph_label": paragraph_label,
        "source_reference": source_reference,
        "source_language": source_language,
        "source_segments": [],
        "extracted_rules": [],
    }


def build_paragraph_id(article_number: str, paragraph_number: str) -> str:
    return f"art{article_number}-p{paragraph_number}"


def build_paragraph_label(article_number: str, paragraph_number: str) -> str:
    return f"Article {article_number}({paragraph_number})"


def infer_income_type(article_title: str) -> str:
    normalized = article_title.strip().lower()
    if normalized.startswith("dividend"):
        return "dividends"
    if normalized.startswith("interest"):
        return "interest"
    if normalized.startswith("royalt"):
        return "royalties"
    raise RawParseError(f"Unsupported semi-structured article title: {article_title}")


def build_semistructured_rule(
    article_number: str,
    paragraph_number: str,
    income_type: str,
    segment_id: str,
    paragraph_text: str,
) -> dict:
    rate_match = PERCENT_RATE_PATTERN.search(paragraph_text)
    if rate_match:
        return {
            "rule_id": f"cn-nl-art{article_number}-p{paragraph_number}-base",
            "rule_type": "withholding_tax_cap",
            "rate": f"{rate_match.group(1)}%",
            "direction": "bidirectional",
            "candidate_rank": 1,
            "is_primary_candidate": True,
            "extraction_confidence": 0.9,
            "derived_from_segments": [segment_id],
            "conditions": [
                "Auto-derived from semi-structured treaty text and should still be manually reviewed."
            ],
            "human_review_required": True,
            "review_reason": "Semi-structured parser output still requires manual treaty review.",
        }

    return {
        "rule_id": f"cn-nl-art{article_number}-p{paragraph_number}-note",
        "rule_type": "treaty_scope_note",
        "rate": "N/A",
        "direction": "bidirectional",
        "candidate_rank": 1,
        "is_primary_candidate": True,
        "extraction_confidence": 0.86,
        "derived_from_segments": [segment_id],
        "conditions": [
            f"Auto-derived narrative paragraph for {income_type} review."
        ],
        "human_review_required": True,
        "review_reason": "Narrative treaty paragraph retained for context, not direct rate determination.",
    }


def parse_bool(raw_value: str) -> bool:
    lowered = raw_value.strip().lower()
    if lowered == "true":
        return True
    if lowered == "false":
        return False
    raise RawParseError(f"Invalid boolean value: {raw_value}")


def require_context(current: dict | None, label: str) -> None:
    if current is None:
        raise RawParseError(f"{label} line appeared before its required parent block")


def validate_parsed_payload(document: dict, parsed_articles: list[dict]) -> None:
    required_document_fields = ["document_id", "title", "document_type", "jurisdictions"]
    for field in required_document_fields:
        if field not in document or not document[field]:
            raise RawParseError(f"Missing required document field: {field}")

    if not parsed_articles:
        raise RawParseError("No ARTICLE blocks found in raw text stub")

    for article in parsed_articles:
        if not article["paragraphs"]:
            raise RawParseError(f"Article {article['article_number']} is missing paragraph blocks")
        for paragraph in article["paragraphs"]:
            if not paragraph["source_segments"]:
                raise RawParseError(f"Paragraph {paragraph['paragraph_id']} is missing SEGMENT lines")
            if not paragraph["extracted_rules"]:
                raise RawParseError(f"Paragraph {paragraph['paragraph_id']} is missing RULE lines")


def write_payload(payload: dict, output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Parse a narrow raw treaty text stub into the parser-like fixture format."
    )
    parser.add_argument(
        "--input",
        type=Path,
        default=DEFAULT_INPUT_PATH,
        help="Input path for the raw text stub.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_OUTPUT_PATH,
        help="Output path for the parser-like fixture JSON.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        payload = parse_raw_text(load_lines(args.input))
    except (OSError, RawParseError) as error:
        print(str(error), file=sys.stderr)
        return 1

    write_payload(payload, args.output)
    print(f"Wrote parser-like fixture to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
