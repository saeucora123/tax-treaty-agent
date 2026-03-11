from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
RAW_INGEST_SCRIPT_PATH = REPO_ROOT / "scripts" / "ingest_cn_nl_raw_text_stub.py"
PDF_INGEST_SCRIPT_PATH = REPO_ROOT / "scripts" / "ingest_cn_nl_pdf_stub.py"
DEFAULT_CATALOG_PATH = REPO_ROOT / "data" / "source_documents" / "source-catalog.stub.json"
DEFAULT_SUMMARY_OUTPUT_PATH = REPO_ROOT / "data" / "treaties" / "source-catalog.summary.json"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run a narrow source catalog through the existing raw-text and PDF ingest paths."
    )
    parser.add_argument(
        "--catalog",
        type=Path,
        default=DEFAULT_CATALOG_PATH,
        help="Input JSON catalog path.",
    )
    parser.add_argument(
        "--summary-output",
        type=Path,
        default=DEFAULT_SUMMARY_OUTPUT_PATH,
        help="Output path for the batch summary JSON.",
    )
    return parser.parse_args()


def load_catalog(catalog_path: Path) -> dict:
    with catalog_path.open("r", encoding="utf-8") as file:
        return json.load(file)


def run_source_entry(entry: dict) -> subprocess.CompletedProcess[str]:
    source_type = entry["source_type"]
    if source_type == "raw_text":
        command = [
            sys.executable,
            str(RAW_INGEST_SCRIPT_PATH),
            "--input",
            entry["input_path"],
            "--parsed-output",
            entry["parsed_output_path"],
            "--dataset-output",
            entry["dataset_output_path"],
            "--report-output",
            entry["report_output_path"],
        ]
    elif source_type == "pdf_text":
        command = [
            sys.executable,
            str(PDF_INGEST_SCRIPT_PATH),
            "--input",
            entry["input_path"],
            "--raw-text-output",
            entry["raw_text_output_path"],
            "--parsed-output",
            entry["parsed_output_path"],
            "--dataset-output",
            entry["dataset_output_path"],
            "--report-output",
            entry["report_output_path"],
        ]
        if "document_id" in entry:
            command.extend(["--document-id", entry["document_id"]])
        if "title" in entry:
            command.extend(["--title", entry["title"]])
        if "document_type" in entry:
            command.extend(["--document-type", entry["document_type"]])
        if "jurisdictions" in entry:
            jurisdictions = entry["jurisdictions"]
            if isinstance(jurisdictions, list):
                jurisdictions = ",".join(jurisdictions)
            command.extend(["--jurisdictions", jurisdictions])
        if "manifest_path" in entry:
            command.extend(["--manifest", entry["manifest_path"]])
    else:
        raise ValueError(f"Unsupported source_type in catalog: {source_type}")

    return subprocess.run(
        command,
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
    )


def build_summary(results: list[dict]) -> dict:
    success_count = sum(1 for result in results if result["status"] == "ok")
    failure_count = len(results) - success_count
    return {
        "source_count": len(results),
        "success_count": success_count,
        "failure_count": failure_count,
        "results": results,
    }


def write_summary(summary: dict, output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def main() -> int:
    args = parse_args()
    try:
        catalog = load_catalog(args.catalog)
        source_entries = catalog["sources"]
    except (OSError, ValueError, KeyError, json.JSONDecodeError) as error:
        print(str(error), file=sys.stderr)
        return 1

    results: list[dict] = []
    had_failure = False

    for entry in source_entries:
        result = run_source_entry(entry)
        status = "ok" if result.returncode == 0 else "error"
        if result.returncode != 0:
            had_failure = True
        results.append(
            {
                "source_id": entry["source_id"],
                "source_type": entry["source_type"],
                "status": status,
                "report_output_path": entry["report_output_path"],
            }
        )

    summary = build_summary(results)
    write_summary(summary, args.summary_output)
    print(
        "Completed source catalog ingest: "
        f"{summary['success_count']} ok, {summary['failure_count']} failed"
    )
    return 1 if had_failure else 0


if __name__ == "__main__":
    raise SystemExit(main())
