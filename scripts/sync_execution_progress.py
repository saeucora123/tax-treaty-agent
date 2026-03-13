from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
CONTROL_PATH = ROOT / "docs" / "superpowers" / "execution" / "execution-control.json"


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def render_stage_snapshot(stage_id: str, stage: dict, updated: str) -> str:
    lines = [
        f"Last synced: `{updated}`",
        f"Status summary: {stage['status_summary']}",
        f"Current checkpoint: {stage['current_checkpoint']}",
        "",
        "Completed so far:",
    ]
    for item in stage.get("completed_items", []):
        lines.append(f"- {item}")

    lines.extend(["", "In progress:"])
    for item in stage.get("in_progress_items", []):
        lines.append(f"- {item}")

    lines.extend(["", "Next up:"])
    for item in stage.get("next_items", []):
        lines.append(f"- {item}")

    lines.extend(["", "Current blockers:"])
    for item in stage.get("blocking_items", []):
        lines.append(f"- {item}")

    return "\n".join(lines).strip()


def replace_section(text: str, marker: str, new_content: str) -> str:
    start = f"<!-- {marker}:START -->"
    end = f"<!-- {marker}:END -->"
    if start not in text or end not in text:
        raise ValueError(f"Missing marker pair for {marker}")
    before, remainder = text.split(start, 1)
    _, after = remainder.split(end, 1)
    middle = f"{start}\n{new_content}\n{end}"
    return before + middle + after


def sync_targets(control: dict, progress: dict) -> None:
    updated = progress["last_updated"]
    for stage_id, stage in progress["stages"].items():
        snapshot = render_stage_snapshot(stage_id, stage, updated)
        for rel in stage.get("targets", []):
            path = ROOT / rel
            text = path.read_text(encoding="utf-8")
            new_text = replace_section(text, f"{stage_id.upper()}_PROGRESS", snapshot)
            path.write_text(new_text, encoding="utf-8")


def main() -> int:
    control = load_json(CONTROL_PATH)
    progress = load_json(ROOT / control["progress_file"])
    sync_targets(control, progress)
    print("Execution progress synced.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
