from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys


REPO_ROOT = Path(__file__).resolve().parents[1]
BACKEND_PATH = REPO_ROOT / "backend"
if str(BACKEND_PATH) not in sys.path:
    sys.path.insert(0, str(BACKEND_PATH))

from app.llm_smoke import run_input_smoke  # noqa: E402


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run a real LLM input-understanding smoke check for Tax Treaty Agent."
    )
    parser.add_argument(
        "--scenario",
        required=True,
        help="Natural-language cross-border scenario to send through the runtime parser.",
    )
    parser.add_argument(
        "--output",
        help="Optional path to write the smoke report as JSON.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    report = run_input_smoke(args.scenario)
    rendered = json.dumps(report, ensure_ascii=False, indent=2)
    print(rendered)

    if args.output:
        output_path = Path(args.output)
        output_path.write_text(rendered + "\n", encoding="utf-8")

    return 0 if report["status"] == "llm_used" else 2


if __name__ == "__main__":
    raise SystemExit(main())
