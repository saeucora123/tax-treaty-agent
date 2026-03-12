from __future__ import annotations

import json
from pathlib import Path

from app import stage2_eval


ROOT = Path(__file__).resolve().parents[2]
CASE_FILE = ROOT / "data" / "evals" / "stage2" / "stage-2-cn-sg-cases.json"


def test_stage2_report_includes_gate_metric_summary(tmp_path: Path):
    output_path = tmp_path / "stage2-report.json"

    report = stage2_eval.run_stage2_evaluation(CASE_FILE, output_path=output_path)

    assert output_path.exists()
    payload = json.loads(output_path.read_text(encoding="utf-8"))
    assert payload["metrics"]["g2_1_threshold"] == {
        "threshold": 0.9,
        "actual": report["pass_rate"],
        "met": True,
    }
    assert payload["metrics"]["overall_pass_rate"]["value"] == report["pass_rate"]
