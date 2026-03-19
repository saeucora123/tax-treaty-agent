from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
BACKEND_PATH = REPO_ROOT / "backend"
if str(BACKEND_PATH) not in sys.path:
    sys.path.insert(0, str(BACKEND_PATH))

from app import source_ingest as formal_source_ingest
from experimental import ingest_source_catalog_stub as experimental

DEFAULT_CATALOG_PATH = REPO_ROOT / "data" / "source_documents" / "source-catalog.stub.json"
DEFAULT_SUMMARY_OUTPUT_PATH = REPO_ROOT / "data" / "treaties" / "source-catalog.summary.json"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run the supported source-ingest pipeline against a catalog or manifest."
    )
    parser.add_argument(
        "--manifest",
        type=Path,
        help="Input pair-level source-build manifest path.",
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


def main() -> int:
    args = parse_args()
    if args.manifest is not None:
        try:
            report = formal_source_ingest.run_source_build(args.manifest)
        except (
            OSError,
            ValueError,
            KeyError,
            json.JSONDecodeError,
            formal_source_ingest.SourceBuildError,
        ) as error:
            print(str(error), file=sys.stderr)
            return 1
        print(
            "Completed source-build manifest: "
            f"{report['article_count']} articles, "
            f"missing_target_articles={len(report['missing_target_articles'])}"
        )
        return 0 if report["status"] == "ok" else 1

    try:
        catalog = experimental.load_catalog(args.catalog)
        source_entries = catalog["sources"]
        known_source_ids = experimental.load_known_source_ids()
        experimental.validate_source_entries(source_entries, known_source_ids)
    except (OSError, ValueError, KeyError, json.JSONDecodeError) as error:
        print(str(error), file=sys.stderr)
        return 1

    results: list[dict] = []
    had_failure = False

    for entry in source_entries:
        result = experimental.run_source_entry(entry)
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

    summary = experimental.build_summary(results)
    experimental.write_summary(summary, args.summary_output)
    print(
        "Completed source catalog ingest: "
        f"{summary['success_count']} ok, {summary['failure_count']} failed"
    )
    return 1 if had_failure else 0


if __name__ == "__main__":
    raise SystemExit(main())
