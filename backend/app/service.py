from __future__ import annotations

import json
from pathlib import Path


DATA_PATH = (
    Path(__file__).resolve().parents[2] / "data" / "treaties" / "cn-nl.v1.json"
)


def analyze_scenario(scenario: str) -> dict:
    normalized = normalize_input(scenario)
    if normalized["reason"] == "incomplete_scenario":
        return {
            "supported": False,
            "reason": "incomplete_scenario",
            "message": "Please provide a clearer scenario with both payer and payee country context.",
        }

    if normalized["country_pair"] != ("CN", "NL"):
        return {
            "supported": False,
            "reason": "unsupported_country_pair",
            "message": "Current MVP supports only China-Netherlands treaty scenarios.",
        }

    match = find_treaty_entry(normalized["transaction_type"])
    if match is None:
        return {
            "supported": False,
            "reason": "unsupported_transaction_type",
            "message": "Current MVP supports only dividends, interest, and royalties.",
        }

    return {
        "supported": True,
        "normalized_input": {
            "payer_country": normalized["country_pair"][0],
            "payee_country": normalized["country_pair"][1],
            "transaction_type": normalized["transaction_type"],
        },
        "result": shape_result(match),
    }


def normalize_input(scenario: str) -> dict:
    payer_country = detect_country(scenario, country_codes=["CN"])
    payee_country = detect_country(scenario, country_codes=["NL", "US"])

    if payer_country is None or payee_country is None:
        country_pair = None
        reason = "incomplete_scenario"
    else:
        country_pair = (payer_country, payee_country)
        reason = "ok"

    if "特许权使用费" in scenario:
        transaction_type = "royalties"
    elif "股息" in scenario:
        transaction_type = "dividends"
    elif "利息" in scenario:
        transaction_type = "interest"
    else:
        transaction_type = "unknown"

    return {
        "country_pair": country_pair,
        "transaction_type": transaction_type,
        "reason": reason,
    }


def detect_country(scenario: str, country_codes: list[str]) -> str | None:
    keyword_map = {
        "CN": ["中国", "中国居民企业", "中国公司"],
        "NL": ["荷兰", "荷兰公司"],
        "US": ["美国", "美国公司"],
    }

    for country_code in country_codes:
        for keyword in keyword_map[country_code]:
            if keyword in scenario:
                return country_code

    return None


def find_treaty_entry(transaction_type: str) -> dict | None:
    with DATA_PATH.open("r", encoding="utf-8") as file:
        entries = json.load(file)

    for entry in entries:
        if entry["transaction_type"] == transaction_type:
            return entry

    return None


def shape_result(entry: dict) -> dict:
    return {
        "article_number": entry["article_number"],
        "article_title": entry["article_title"],
        "rate": entry["rate"],
        "conditions": entry["conditions"],
        "notes": entry["notes"],
        "human_review_required": entry["human_review_required"],
        "review_reason": entry["review_reason"],
    }
