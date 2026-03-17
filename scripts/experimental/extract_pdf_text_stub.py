from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

from pypdf import PdfReader


REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_INPUT_PATH = REPO_ROOT / "data" / "raw_documents" / "cn-nl-text.pdf"
DEFAULT_OUTPUT_PATH = REPO_ROOT / "data" / "raw_documents" / "cn-nl-extracted.txt"
ARTICLE_HEADING_PATTERN = re.compile(r"^Article\s+\d+\s+.+$")
PAGE_NUMBER_PATTERN = re.compile(r"^Page\s+\d+$", re.IGNORECASE)
DOCUMENT_FIELD_PREFIXES = (
    "DOCUMENT_ID: ",
    "TITLE: ",
    "DOCUMENT_TYPE: ",
    "JURISDICTIONS: ",
    "DOCUMENT_NOTE: ",
)
NUMBERED_PARAGRAPH_PATTERN = re.compile(r"^\d+\.\s+.+$")


class PdfExtractionError(ValueError):
    pass


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


def write_text(text: str, output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(text, encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Extract text from a narrow text-based PDF into raw treaty text."
    )
    parser.add_argument(
        "--input",
        type=Path,
        default=DEFAULT_INPUT_PATH,
        help="Input PDF path.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_OUTPUT_PATH,
        help="Output text path.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        text = extract_pdf_text(args.input)
    except (OSError, PdfExtractionError) as error:
        print(str(error), file=sys.stderr)
        return 1

    write_text(text, args.output)
    print(f"Wrote extracted text to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
