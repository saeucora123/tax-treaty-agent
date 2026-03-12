from __future__ import annotations

import json
from pathlib import Path

from app import stage6_eval


def test_evaluate_case_checks_source_trace_and_mli_fields():
    case = {
        "id": "stage6-supported-001",
        "category": "source_trace_supported",
        "scenario": "中国居民企业向新加坡公司支付特许权使用费",
        "expected": {
            "supported": True,
            "review_state_code": "pre_review_complete",
            "article_number": "12",
            "rate": "10%",
            "source_reference": "CN-SG Article 12(2)",
            "placeholder_excerpt_allowed": False,
            "working_paper_suffix": "cn-sg-royalties-working-paper.md",
            "mli_ppt_expected": True,
        },
    }

    actual = {
        "supported": True,
        "review_state": {"state_code": "pre_review_complete"},
        "result": {
            "article_number": "12",
            "rate": "10%",
            "source_reference": "CN-SG Article 12(2)",
            "source_excerpt": "However, such royalties may also be taxed in the Contracting State in which they arise ...",
            "source_trace": {
                "working_paper_ref": "docs/superpowers/research/stage-6-evidence/2026-03-13-cn-sg-royalties-working-paper.md",
            },
            "mli_context": {
                "ppt_applies": True,
                "summary": "MLI Article 7 (PPT) applies and requires manual confirmation.",
            },
        },
    }

    report = stage6_eval.evaluate_case(case, analyzer=lambda payload: actual)

    assert report["passed"] is True
    assert report["checks"]["source_reference"] is True
    assert report["checks"]["real_excerpt"] is True
    assert report["checks"]["working_paper"] is True
    assert report["checks"]["mli_ppt"] is True


def test_run_stage6_evaluation_writes_report_file(tmp_path: Path):
    case_file = tmp_path / "stage6-cases.json"
    report_file = tmp_path / "stage6-report.json"
    case_file.write_text(
        json.dumps(
            [
                {
                    "id": "stage6-cn-sg-dividends",
                    "category": "source_trace_supported",
                    "scenario": "中国公司向新加坡公司支付股息",
                    "expected": {
                        "supported": True,
                        "review_state_code": "can_be_completed",
                        "article_number": "10",
                        "rate": "5% / 10%",
                        "source_reference": "CN-SG Article 10(2)(b)",
                        "placeholder_excerpt_allowed": False,
                        "working_paper_suffix": "cn-sg-dividends-working-paper.md",
                        "mli_ppt_expected": True,
                    },
                }
            ],
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )

    def fake_analyzer(case: dict) -> dict:
        return {
            "supported": True,
            "review_state": {"state_code": "can_be_completed"},
            "result": {
                "article_number": "10",
                "rate": "5% / 10%",
                "source_reference": "CN-SG Article 10(2)(b)",
                "source_excerpt": "10 per cent of the gross amount of the dividends in all other cases.",
                "source_trace": {
                    "working_paper_ref": "docs/superpowers/research/stage-6-evidence/2026-03-13-cn-sg-dividends-working-paper.md",
                },
                "mli_context": {
                    "ppt_applies": True,
                    "summary": "MLI Article 7 (PPT) applies and requires manual confirmation.",
                },
            },
        }

    report = stage6_eval.run_stage6_evaluation(
        case_file,
        output_path=report_file,
        analyzer=fake_analyzer,
    )

    assert report["total_cases"] == 1
    assert report["passed_cases"] == 1
    assert report["metrics"]["real_excerpt_rate"]["numerator"] == 1
    assert report["metrics"]["mli_fact_rate"]["numerator"] == 1
    assert report_file.exists() is True
