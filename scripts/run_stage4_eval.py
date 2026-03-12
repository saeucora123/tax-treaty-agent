from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent
BACKEND_ROOT = REPO_ROOT / "backend"
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from app.stage4_eval import run_stage4_evaluation


DEFAULT_CASE_PATH = REPO_ROOT / "data" / "evals" / "stage4" / "stage-4-precision-pack.json"
DEFAULT_OUTPUT_PATH = (
    REPO_ROOT
    / "docs"
    / "superpowers"
    / "research"
    / "stage-4-evidence"
    / "2026-03-12-stage-4-precision-report.json"
)


def main() -> int:
    parser = argparse.ArgumentParser(description="Run the Tax Treaty Agent Stage 4 precision pack.")
    parser.add_argument("--cases", type=Path, default=DEFAULT_CASE_PATH)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT_PATH)
    args = parser.parse_args()

    report = run_stage4_evaluation(args.cases, output_path=args.output)
    summary = {
        "case_file": str(args.cases),
        "output_file": str(args.output),
        "total_cases": report["total_cases"],
        "passed_cases": report["passed_cases"],
        "failed_cases": report["failed_cases"],
        "category_summary": report["category_summary"],
        "termination_summary": report["termination_summary"],
        "metrics": report["metrics"],
    }
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
