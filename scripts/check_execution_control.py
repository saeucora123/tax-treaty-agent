from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
CONTROL_PATH = ROOT / "docs" / "superpowers" / "execution" / "execution-control.json"
GATE_RESULT_RE = re.compile(r"^Gate result:\s*`?(PASS|FAIL|PENDING)`?\s*$", re.IGNORECASE)


def load_control() -> dict:
    return json.loads(CONTROL_PATH.read_text(encoding="utf-8"))


def read_gate_result(path: Path) -> str:
    if not path.exists():
        return "MISSING"
    for line in path.read_text(encoding="utf-8").splitlines():
        match = GATE_RESULT_RE.match(line.strip())
        if match:
            return match.group(1).upper()
    return "UNKNOWN"


def artifact_status(paths: list[str]) -> list[tuple[str, bool]]:
    statuses = []
    for rel in paths:
        statuses.append((rel, (ROOT / rel).exists()))
    return statuses


def print_summary(control: dict) -> int:
    print("Execution Control Summary")
    print(f"Authority memo: {control['authority_memo']}")
    print(f"Active workstreams: {', '.join(control['active_workstreams'])}")
    print(f"Next decision point: {control['next_decision_point']}")
    print("")

    for stage_id, info in control["stages"].items():
        gate_path = ROOT / info["gate_review"]
        gate_result = read_gate_result(gate_path)
        print(f"[{stage_id}] {info['label']}")
        print(f"  status: {info['status']}")
        print(f"  gate review: {info['gate_review']} -> {gate_result}")
        missing = [rel for rel, exists in artifact_status(info["required_artifacts"]) if not exists]
        if missing:
            print("  missing artifacts:")
            for rel in missing:
                print(f"    - {rel}")
        else:
            print("  required artifacts: OK")
        print("")
    return 0


def check_stage(control: dict, stage_id: str) -> int:
    info = control["stages"].get(stage_id)
    if not info:
        print(f"Unknown stage: {stage_id}", file=sys.stderr)
        return 2

    gate_result = read_gate_result(ROOT / info["gate_review"])
    active = stage_id in control["active_workstreams"]
    print(f"Stage: {stage_id}")
    print(f"Label: {info['label']}")
    print(f"Active now: {'yes' if active else 'no'}")
    print(f"Configured status: {info['status']}")
    print(f"Gate result: {gate_result}")

    missing = [rel for rel, exists in artifact_status(info["required_artifacts"]) if not exists]
    if missing:
        print("Missing artifacts:")
        for rel in missing:
            print(f"  - {rel}")
    else:
        print("Missing artifacts: none")

    if active:
        return 0
    return 1


def check_promotion(control: dict, target: str) -> int:
    rule = next((item for item in control["promotion_rules"] if item["to"] == target), None)
    if not rule:
        print(f"No promotion rule found for: {target}", file=sys.stderr)
        return 2

    missing_passes = []
    print(f"Promotion target: {target}")
    for stage_id in rule.get("requires_gate_pass", []):
        stage = control["stages"].get(stage_id)
        if not stage:
            missing_passes.append((stage_id, "UNKNOWN_STAGE"))
            continue
        result = read_gate_result(ROOT / stage["gate_review"])
        print(f"  requires {stage_id}: {result}")
        if result != "PASS":
            missing_passes.append((stage_id, result))

    extras = rule.get("extra_conditions", [])
    if extras:
        print("  extra conditions:")
        for item in extras:
            print(f"    - {item}")

    if missing_passes:
        print("")
        print("Promotion blocked.")
        for stage_id, result in missing_passes:
            print(f"  - {stage_id} is not PASS (current: {result})")
        return 1

    print("")
    print("Promotion gate check passed at the file/status level.")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Check execution-stage controls for Tax Treaty Agent.")
    parser.add_argument("--stage", help="Inspect a specific stage.")
    parser.add_argument("--promote-to", help="Check whether promotion to a target stage is currently allowed.")
    args = parser.parse_args()

    control = load_control()

    if args.stage:
        return check_stage(control, args.stage)
    if args.promote_to:
        return check_promotion(control, args.promote_to)
    return print_summary(control)


if __name__ == "__main__":
    raise SystemExit(main())
