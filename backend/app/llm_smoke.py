from __future__ import annotations

from app.service import analyze_scenario


def build_input_smoke_report(scenario: str, response: dict) -> dict:
    input_interpretation = response.get("input_interpretation")
    parser_source = "llm" if input_interpretation else "rules"
    status = "llm_used" if parser_source == "llm" else "fallback_to_rules"

    report = {
        "status": status,
        "scenario": scenario,
        "supported": response["supported"],
        "parser_source": parser_source,
        "input_interpretation": input_interpretation,
    }

    if "normalized_input" in response:
        report["normalized_input"] = response["normalized_input"]

    if response["supported"]:
        report["result_summary"] = response["result"]["summary"]
        report["immediate_action"] = response["result"]["immediate_action"]
    else:
        report["reason"] = response["reason"]
        report["immediate_action"] = response["immediate_action"]

    return report


def run_input_smoke(scenario: str) -> dict:
    response = analyze_scenario(scenario)
    return build_input_smoke_report(scenario, response)
