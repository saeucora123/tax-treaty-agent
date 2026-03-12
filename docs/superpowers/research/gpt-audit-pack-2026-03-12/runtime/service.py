from __future__ import annotations

import json
from pathlib import Path

from app.llm_input_parser import LLMInputParserError, parse_scenario_to_json


DATA_PATH = (
    Path(__file__).resolve().parents[2] / "data" / "treaties" / "cn-nl.v3.json"
)
LLM_GENERATED_DATA_PATH = (
    Path(__file__).resolve().parents[2]
    / "data"
    / "treaties"
    / "cn-nl.v3.generated.from-llm.json"
)
NORMAL_CONFIDENCE_THRESHOLD = 0.95
AUTO_CONCLUSION_CONFIDENCE_THRESHOLD = 0.80
SUPPORTED_SCOPE_EXAMPLES = [
    "中国居民企业向荷兰公司支付股息",
    "中国居民企业向荷兰银行支付利息",
    "中国居民企业向荷兰公司支付特许权使用费",
]
REVIEW_CHECKLISTS = {
    "royalties": [
        "Confirm the payment is actually for the use of, or right to use, qualifying intellectual property.",
        "Confirm the recipient is the beneficial owner of the royalty income.",
        "Check the underlying contract, invoice, and payment flow for factual consistency.",
    ],
    "dividends": [
        "Confirm the payment is legally characterized as a dividend rather than another return.",
        "Confirm the recipient is the beneficial owner of the dividend income.",
        "Check shareholding facts and supporting corporate records before relying on the treaty rate.",
    ],
    "interest": [
        "Confirm the payment is legally characterized as interest under the financing arrangement.",
        "Confirm the recipient is the beneficial owner of the interest income.",
        "Check the loan agreement, interest calculation, and payment records for consistency.",
    ],
}
KEY_MISSING_FACTS = {
    "royalties": [
        "Whether the payment is truly for qualifying intellectual property use.",
        "Whether the recipient is the beneficial owner of the royalty income.",
        "Whether the contract and payment flow support treaty characterization.",
    ],
    "dividends": [
        "Whether the payment is legally a dividend rather than another type of return.",
        "Whether the recipient is the beneficial owner of the dividend income.",
        "Whether shareholding facts support relying on the treaty position.",
    ],
    "interest": [
        "Whether the payment is legally characterized as interest under the financing arrangement.",
        "Whether the recipient is the beneficial owner of the interest income.",
        "Whether the lending documents and payment records support the treaty characterization.",
    ],
}
TRANSACTION_KEYWORDS = {
    "royalties": [
        "特许权使用费",
        "软件许可费",
        "软件授权费",
        "技术授权费",
        "品牌费",
    ],
    "dividends": ["股息"],
    "interest": ["利息"],
}
TRANSACTION_LABELS_ZH = {
    "dividends": "股息",
    "interest": "利息",
    "royalties": "特许权使用费",
}
BOUNDARY_NOTE = (
    "This is a first-pass treaty pre-review based on limited scenario facts. "
    "Final eligibility still depends on additional facts, documents, and analysis "
    "outside the current review scope."
)


def analyze_scenario(scenario: str, data_source: str = "stable") -> dict:
    resolved_data_source = normalize_data_source(data_source)
    normalized = normalize_input(scenario)
    input_interpretation = build_input_interpretation(normalized)
    if normalized["reason"] == "incomplete_scenario":
        response = {
            "data_source_used": resolved_data_source,
            "supported": False,
            "reason": "incomplete_scenario",
            "message": "Please provide a clearer scenario with both payer and payee country context.",
            "immediate_action": build_unsupported_action("incomplete_scenario"),
            **build_input_guidance("incomplete_scenario", normalized),
        }
        if input_interpretation is not None:
            response["input_interpretation"] = input_interpretation
        return response

    if set(normalized["country_pair"]) != {"CN", "NL"}:
        response = {
            "data_source_used": resolved_data_source,
            "supported": False,
            "reason": "unsupported_country_pair",
            "message": "Current MVP supports only China-Netherlands treaty scenarios.",
            "immediate_action": build_unsupported_action("unsupported_country_pair"),
            **build_input_guidance("unsupported_country_pair", normalized),
        }
        if input_interpretation is not None:
            response["input_interpretation"] = input_interpretation
        return response

    match = find_treaty_entry(
        normalized["transaction_type"],
        data_source=resolved_data_source,
    )
    if match is None:
        response = {
            "data_source_used": resolved_data_source,
            "supported": False,
            "reason": "unsupported_transaction_type",
            "message": "Current MVP supports only dividends, interest, and royalties.",
            "immediate_action": build_unsupported_action("unsupported_transaction_type"),
            **build_input_guidance("unsupported_transaction_type", normalized),
        }
        if input_interpretation is not None:
            response["input_interpretation"] = input_interpretation
        return response

    response = {
        "data_source_used": resolved_data_source,
        "supported": True,
        "normalized_input": {
            "payer_country": normalized["payer_country"],
            "payee_country": normalized["payee_country"],
            "transaction_type": normalized["transaction_type"],
        },
        "result": shape_result(match),
    }
    if input_interpretation is not None:
        response["input_interpretation"] = input_interpretation
    return response


def normalize_data_source(data_source: str) -> str:
    if data_source == "llm_generated":
        return "llm_generated"
    return "stable"


def normalize_input(scenario: str) -> dict:
    llm_normalized = try_llm_normalize_input(scenario)
    if llm_normalized is not None:
        return {
            **llm_normalized,
            "parser_source": llm_normalized.get("parser_source", "llm"),
        }

    payer_country, payee_country = detect_flow_countries(scenario)

    if payer_country is None or payee_country is None:
        country_pair = None
        reason = "incomplete_scenario"
    else:
        country_pair = (payer_country, payee_country)
        reason = "ok"

    transaction_type, matched_transaction_label = detect_transaction_type(scenario)

    return {
        "country_pair": country_pair,
        "payer_country": payer_country,
        "payee_country": payee_country,
        "transaction_type": transaction_type,
        "matched_transaction_label": matched_transaction_label,
        "parser_source": "rules",
        "reason": reason,
    }


def try_llm_normalize_input(scenario: str) -> dict | None:
    try:
        payload = parse_scenario_to_json(scenario)
    except LLMInputParserError:
        return None

    if payload is None:
        return None

    payer_country = normalize_country_code(payload.get("payer_country"))
    payee_country = normalize_country_code(payload.get("payee_country"))
    transaction_type = normalize_transaction_type(payload.get("transaction_type"))
    matched_transaction_label = normalize_optional_label(payload.get("matched_transaction_label"))
    needs_clarification = bool(payload.get("needs_clarification"))

    if needs_clarification or payer_country is None or payee_country is None:
        country_pair = None
        reason = "incomplete_scenario"
    else:
        country_pair = (payer_country, payee_country)
        reason = "ok"

    return {
        "country_pair": country_pair,
        "payer_country": payer_country,
        "payee_country": payee_country,
        "transaction_type": transaction_type,
        "matched_transaction_label": matched_transaction_label,
        "parser_source": "llm",
        "reason": reason,
    }


def build_input_interpretation(normalized: dict) -> dict | None:
    if normalized.get("parser_source") != "llm":
        return None

    return {
        "parser_source": "llm",
        "payer_country": normalized["payer_country"],
        "payee_country": normalized["payee_country"],
        "transaction_type": normalized["transaction_type"],
        "matched_transaction_label": normalized["matched_transaction_label"],
    }


def normalize_country_code(raw_value: object) -> str | None:
    if not isinstance(raw_value, str):
        return None
    normalized = raw_value.strip().upper()
    if not normalized:
        return None
    alias_map = {
        "CHINA": "CN",
        "PRC": "CN",
        "PEOPLE'S REPUBLIC OF CHINA": "CN",
        "PEOPLES REPUBLIC OF CHINA": "CN",
        "CN": "CN",
        "NETHERLANDS": "NL",
        "THE NETHERLANDS": "NL",
        "HOLLAND": "NL",
        "DUTCH": "NL",
        "NL": "NL",
        "UNITED STATES": "US",
        "UNITED STATES OF AMERICA": "US",
        "USA": "US",
        "U.S.": "US",
        "U.S.A.": "US",
        "US": "US",
    }
    if normalized in alias_map:
        return alias_map[normalized]
    return normalized


def normalize_transaction_type(raw_value: object) -> str:
    if not isinstance(raw_value, str):
        return "unknown"
    normalized = raw_value.strip().lower()
    if normalized in TRANSACTION_KEYWORDS:
        return normalized
    return "unknown"


def normalize_optional_label(raw_value: object) -> str | None:
    if not isinstance(raw_value, str):
        return None
    normalized = raw_value.strip()
    if not normalized:
        return None
    return normalized


def detect_flow_countries(scenario: str) -> tuple[str | None, str | None]:
    if "向" in scenario:
        payer_segment, payee_segment = scenario.split("向", 1)
        payer_country = detect_country(payer_segment, country_codes=["CN", "NL", "US"])
        payee_country = detect_country(payee_segment, country_codes=["CN", "NL", "US"])
        return payer_country, payee_country

    return None, None


def detect_country(scenario: str, country_codes: list[str]) -> str | None:
    keyword_map = {
        "CN": ["中国", "中国居民企业", "中国公司"],
        "NL": ["荷兰", "荷兰公司"],
        "US": ["美国", "美国公司"],
    }

    matches: list[str] = []
    for country_code in country_codes:
        for keyword in keyword_map[country_code]:
            if keyword in scenario:
                matches.append(country_code)
                break

    unique_matches = list(dict.fromkeys(matches))
    if len(unique_matches) == 1:
        return unique_matches[0]

    return None


def detect_transaction_type(scenario: str) -> tuple[str, str | None]:
    for transaction_type, keywords in TRANSACTION_KEYWORDS.items():
        for keyword in keywords:
            if keyword in scenario:
                return transaction_type, keyword

    return "unknown", None


def find_treaty_entry(transaction_type: str, data_source: str = "stable") -> dict | None:
    with resolve_data_path(data_source).open("r", encoding="utf-8") as file:
        payload = json.load(file)

    for article in payload["articles"]:
        if article["income_type"] == transaction_type:
            selected_paragraph = None
            selected_rule = None
            for paragraph in article["paragraphs"]:
                base_rule = select_rate_rule(paragraph["rules"])
                if base_rule is None:
                    continue
                if selected_rule is None or rule_preference_key(base_rule) > rule_preference_key(selected_rule):
                    selected_paragraph = paragraph
                    selected_rule = base_rule

            if selected_paragraph is None or selected_rule is None:
                continue

            review_priority, review_reason, auto_conclusion_allowed = build_review_guidance(
                selected_rule
            )
            alternative_rate_candidates = collect_alternative_rate_candidates(
                article["paragraphs"],
                selected_rule=selected_rule,
                selected_source_reference=selected_paragraph["source_reference"],
            )
            if alternative_rate_candidates:
                review_priority = "high"
                auto_conclusion_allowed = False
                review_reason = (
                    f"{review_reason} Multiple treaty rate branches were found in this article, "
                    "and the current scenario does not provide enough facts to choose one automatically."
                )
            result = {
                "summary": build_summary(
                    article_number=article["article_number"],
                    article_title=article["article_title"],
                    rate=selected_rule["rate"],
                    review_priority=review_priority,
                    auto_conclusion_allowed=auto_conclusion_allowed,
                ),
                "boundary_note": BOUNDARY_NOTE,
                "immediate_action": build_immediate_action(
                    review_priority=review_priority,
                    auto_conclusion_allowed=auto_conclusion_allowed,
                ),
                "article_number": article["article_number"],
                "article_title": article["article_title"],
                "source_reference": selected_paragraph["source_reference"],
                "source_language": selected_paragraph["source_language"],
                "source_excerpt": selected_paragraph["source_excerpt"],
                "rate": selected_rule["rate"],
                "extraction_confidence": selected_rule["extraction_confidence"],
                "auto_conclusion_allowed": auto_conclusion_allowed,
                "key_missing_facts": KEY_MISSING_FACTS[article["income_type"]],
                "review_checklist": REVIEW_CHECKLISTS[article["income_type"]],
                "conditions": selected_rule["conditions"],
                "notes": article["notes"],
                "human_review_required": selected_rule["human_review_required"],
                "review_priority": review_priority,
                "review_reason": review_reason,
            }
            if alternative_rate_candidates:
                result["alternative_rate_candidates"] = alternative_rate_candidates
            return result

    return None


def resolve_data_path(data_source: str) -> Path:
    if data_source == "llm_generated":
        return LLM_GENERATED_DATA_PATH
    return DATA_PATH


def select_rate_rule(rules: list[dict]) -> dict | None:
    for rule in rules:
        if rule.get("is_primary_candidate") is True:
            return rule

    for rule in rules:
        if rule["direction"] == "bidirectional":
            return rule

    return None


def rule_preference_key(rule: dict) -> tuple[int, float]:
    has_numeric_rate = 0 if rule.get("rate") in {"", "N/A", None} else 1
    return (has_numeric_rate, float(rule.get("extraction_confidence", 0)))


def collect_alternative_rate_candidates(
    paragraphs: list[dict],
    *,
    selected_rule: dict,
    selected_source_reference: str,
) -> list[dict]:
    candidates: list[dict] = []
    seen: set[tuple[str, str, str]] = set()
    selected_rate = selected_rule.get("rate")
    selected_rule_id = selected_rule.get("rule_id")

    for paragraph in paragraphs:
        for rule in paragraph["rules"]:
            candidate_rate = rule.get("rate")
            if candidate_rate in {"", "N/A", None}:
                continue
            if rule.get("rule_id") == selected_rule_id:
                continue
            if (
                paragraph["source_reference"] == selected_source_reference
                and candidate_rate == selected_rate
            ):
                continue
            key = (
                paragraph["source_reference"],
                candidate_rate,
                rule.get("rule_id", ""),
            )
            if key in seen:
                continue
            seen.add(key)
            candidates.append(
                {
                    "source_reference": paragraph["source_reference"],
                    "rate": candidate_rate,
                    "conditions": rule.get("conditions", []),
                }
            )

    return candidates


def build_review_guidance(rule: dict) -> tuple[str, str, bool]:
    base_reason = normalize_review_reason(rule["review_reason"])
    confidence = rule["extraction_confidence"]

    if confidence < AUTO_CONCLUSION_CONFIDENCE_THRESHOLD:
        return (
            "high",
            f"{base_reason} Source extraction confidence is too low, so this version is not suitable for an automatic treaty conclusion.",
            False,
        )

    if confidence < NORMAL_CONFIDENCE_THRESHOLD:
        return (
            "high",
            f"{base_reason} Source extraction confidence is not high enough for routine reliance, so prioritize manual verification.",
            True,
        )

    if rule["human_review_required"]:
        return ("normal", base_reason, True)

    return ("none", base_reason, True)


def normalize_review_reason(reason: str) -> str:
    return reason.replace("facts beyond v1 scope", "facts outside the current review scope")


def shape_result(entry: dict) -> dict:
    return entry


def build_summary(
    article_number: str,
    article_title: str,
    rate: str,
    review_priority: str,
    auto_conclusion_allowed: bool,
) -> str:
    base = f"Preliminary view: Article {article_number} {article_title} appears relevant"

    if not auto_conclusion_allowed:
        return (
            f"{base}, but this version should not issue an automatic conclusion. "
            f"The current indicative treaty rate is {rate}."
        )

    if review_priority == "high":
        return (
            f"{base}, with a treaty rate ceiling of {rate}. "
            "Prioritize manual review before relying on this result."
        )

    return (
        f"{base}, with a treaty rate ceiling of {rate}. "
        "Manual review is still recommended."
    )


def build_immediate_action(review_priority: str, auto_conclusion_allowed: bool) -> str:
    if not auto_conclusion_allowed:
        return (
            "Do not rely on this result yet. Resolve the missing facts and supporting "
            "documents before any treaty conclusion."
        )

    if review_priority == "high":
        return "Escalate this case for priority manual review before using the treaty result."

    return "Proceed with standard manual review before relying on the treaty position."


def build_unsupported_action(reason: str) -> str:
    if reason == "unsupported_country_pair":
        return "Rewrite the scenario into the supported China-Netherlands scope before running another review."

    if reason == "unsupported_transaction_type":
        return "Restate the payment using a supported income type before relying on treaty review output."

    return "Add the missing scenario facts before running the treaty review again."


def build_input_guidance(reason: str, normalized: dict) -> dict:
    classification_note = build_classification_note(normalized)

    if reason == "unsupported_country_pair":
        payload = {
            "missing_fields": [],
            "suggested_format": "Try a sentence like: 中国居民企业向荷兰公司支付特许权使用费",
            "suggested_examples": SUPPORTED_SCOPE_EXAMPLES,
        }
        if classification_note:
            payload["classification_note"] = classification_note
        return payload

    if reason == "unsupported_transaction_type":
        payload = {
            "missing_fields": ["transaction_type"],
            "suggested_format": "Try a sentence like: 中国居民企业向荷兰公司支付特许权使用费",
            "suggested_examples": SUPPORTED_SCOPE_EXAMPLES,
        }
        if classification_note:
            payload["classification_note"] = classification_note
        return payload

    missing_fields = []
    if normalized["payer_country"] is None:
        missing_fields.append("payer_country")
    if normalized["payee_country"] is None:
        missing_fields.append("payee_country")
    if normalized["transaction_type"] == "unknown":
        missing_fields.append("transaction_type")

    payload = {
        "missing_fields": missing_fields,
        "suggested_format": f"Try a sentence like: {build_supported_sentence(normalized)}",
        "suggested_examples": [
            "中国居民企业向荷兰公司支付股息",
            "荷兰公司向中国公司支付利息",
        ],
    }
    if classification_note:
        payload["classification_note"] = classification_note
    return payload


def build_supported_sentence(normalized: dict) -> str:
    payer_country = normalized["payer_country"] or "CN"
    payee_country = normalized["payee_country"] or "NL"
    transaction_type = normalized["transaction_type"]
    if transaction_type == "unknown":
        transaction_type = "royalties"

    payer_label = "中国居民企业" if payer_country == "CN" else "荷兰公司"
    if payee_country == "NL":
        payee_label = "荷兰银行" if transaction_type == "interest" else "荷兰公司"
    else:
        payee_label = "中国公司"

    return f"{payer_label}向{payee_label}支付{TRANSACTION_LABELS_ZH[transaction_type]}"


def build_classification_note(normalized: dict) -> str:
    matched_label = normalized["matched_transaction_label"]
    transaction_type = normalized["transaction_type"]

    if matched_label is None or transaction_type == "unknown":
        return ""

    canonical_label = TRANSACTION_LABELS_ZH[transaction_type]
    if matched_label == canonical_label:
        return ""

    return (
        f"Current review maps `{matched_label}` into the {transaction_type} lane for first-pass treaty review. "
        f"Use a fuller scenario so the tool can test the treaty position under the standard treaty {transaction_type} framework."
    )

