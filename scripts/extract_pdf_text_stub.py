from __future__ import annotations

import argparse
import sys
from pathlib import Path

from pypdf import PdfReader


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_INPUT_PATH = REPO_ROOT / "data" / "raw_documents" / "cn-nl-text.pdf"
DEFAULT_OUTPUT_PATH = REPO_ROOT / "data" / "raw_documents" / "cn-nl-extracted.txt"


class PdfExtractionError(ValueError):
    pass


def extract_pdf_text(input_path: Path) -> str:
    reader = PdfReader(str(input_path))
    page_texts: list[str] = []

    for page in reader.pages:
        text = page.extract_text() or ""
        normalized = normalize_text(text)
        if normalized:
            page_texts.append(normalized)

    if not page_texts:
        raise PdfExtractionError("No extractable text found in PDF.")

    return "\n".join(page_texts).strip() + "\n"


def normalize_text(text: str) -> str:
    lines = [line.strip() for line in text.splitlines()]
    kept_lines: list[str] = []
    previous_blank = False

    for line in lines:
        if not line:
            if not previous_blank:
                kept_lines.append("")
            previous_blank = True
            continue
        kept_lines.append(line)
        previous_blank = False

    while kept_lines and kept_lines[-1] == "":
        kept_lines.pop()

    return "\n".join(kept_lines)


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
