from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent
BACKEND_ROOT = REPO_ROOT / "backend"
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from app.stage1_eval import render_markdown_summary


DEFAULT_CASE_PATH = REPO_ROOT / "data" / "evals" / "stage1" / "stage-1-initial-cases.json"
DEFAULT_JSON_REPORT = (
    REPO_ROOT
    / "docs"
    / "superpowers"
    / "research"
    / "stage-1-evidence"
    / "2026-03-12-stage-1-initial-report.json"
)
DEFAULT_MD_REPORT = (
    REPO_ROOT
    / "docs"
    / "superpowers"
    / "research"
    / "stage-1-evidence"
    / "2026-03-12-stage-1-initial-summary.md"
)


def main() -> int:
    parser = argparse.ArgumentParser(description="Render a markdown summary for the Stage 1 evaluation report.")
    parser.add_argument("--cases", type=Path, default=DEFAULT_CASE_PATH)
    parser.add_argument("--report", type=Path, default=DEFAULT_JSON_REPORT)
    parser.add_argument("--output", type=Path, default=DEFAULT_MD_REPORT)
    args = parser.parse_args()

    report = json.loads(args.report.read_text(encoding="utf-8"))
    markdown = render_markdown_summary(report, case_path=args.cases, report_path=args.report)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(markdown, encoding="utf-8")
    print(args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
