from __future__ import annotations

import argparse
import json
from datetime import date
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
CONTROL_PATH = ROOT / "docs" / "superpowers" / "execution" / "execution-control.json"


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def dump_json(path: Path, payload: dict) -> None:
    path.write_text(json.dumps(payload, ensure_ascii=True, indent=2) + "\n", encoding="utf-8")


def dedupe_append(items: list[str], values: list[str]) -> list[str]:
    existing = list(items)
    for value in values:
        if value not in existing:
            existing.append(value)
    return existing


def remove_values(items: list[str], values: list[str]) -> list[str]:
    removals = set(values)
    return [item for item in items if item not in removals]


def main() -> int:
    parser = argparse.ArgumentParser(description="Record structured execution progress for Tax Treaty Agent.")
    parser.add_argument("--stage", required=True, help="Stage id, for example stage_1 or stage_3.")
    parser.add_argument("--summary", help="Replace the status summary for this stage.")
    parser.add_argument("--checkpoint", help="Replace the current checkpoint text for this stage.")
    parser.add_argument("--global-note", help="Replace the global execution note.")
    parser.add_argument("--add-completed", action="append", default=[], help="Append a completed item.")
    parser.add_argument("--add-in-progress", action="append", default=[], help="Append an in-progress item.")
    parser.add_argument("--add-next", action="append", default=[], help="Append a next item.")
    parser.add_argument("--add-blocker", action="append", default=[], help="Append a blocker.")
    parser.add_argument("--remove-in-progress", action="append", default=[], help="Remove an in-progress item.")
    parser.add_argument("--remove-next", action="append", default=[], help="Remove a next item.")
    parser.add_argument("--remove-blocker", action="append", default=[], help="Remove a blocker.")
    parser.add_argument("--sync", action="store_true", help="Run sync_execution_progress.py after update.")
    args = parser.parse_args()

    control = load_json(CONTROL_PATH)
    progress_path = ROOT / control["progress_file"]
    progress = load_json(progress_path)

    if args.stage not in progress["stages"]:
        raise SystemExit(f"Unknown stage in progress file: {args.stage}")

    stage = progress["stages"][args.stage]

    if args.summary:
        stage["status_summary"] = args.summary
    if args.checkpoint:
        stage["current_checkpoint"] = args.checkpoint
    if args.global_note:
        progress["global_note"] = args.global_note

    stage["completed_items"] = dedupe_append(stage.get("completed_items", []), args.add_completed)
    stage["in_progress_items"] = dedupe_append(stage.get("in_progress_items", []), args.add_in_progress)
    stage["next_items"] = dedupe_append(stage.get("next_items", []), args.add_next)
    stage["blocking_items"] = dedupe_append(stage.get("blocking_items", []), args.add_blocker)

    stage["in_progress_items"] = remove_values(stage.get("in_progress_items", []), args.remove_in_progress)
    stage["next_items"] = remove_values(stage.get("next_items", []), args.remove_next)
    stage["blocking_items"] = remove_values(stage.get("blocking_items", []), args.remove_blocker)

    progress["last_updated"] = date.today().isoformat()
    dump_json(progress_path, progress)

    print(f"Recorded progress for {args.stage}.")
    print(f"Progress file: {progress_path}")

    if args.sync:
        sync_script = ROOT / "scripts" / "sync_execution_progress.py"
        code = __import__("subprocess").run(["python", str(sync_script)], cwd=ROOT, check=False).returncode
        return code

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
