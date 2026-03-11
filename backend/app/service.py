from __future__ import annotations

import json
from pathlib import Path


DATA_PATH = (
    Path(__file__).resolve().parents[2] / "data" / "treaties" / "cn-nl.v3.json"
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


def analyze_scenario(scenario: str) -> dict:
    normalized = normalize_input(scenario)
    if normalized["reason"] == "incomplete_scenario":
        return {
            "supported": False,
            "reason": "incomplete_scenario",
            "message": "Please provide a clearer scenario with both payer and payee country context.",
            "immediate_action": build_unsupported_action("incomplete_scenario"),
            **build_input_guidance("incomplete_scenario", normalized),
        }

    if set(normalized["country_pair"]) != {"CN", "NL"}:
        return {
            "supported": False,
            "reason": "unsupported_country_pair",
            "message": "Current MVP supports only China-Netherlands treaty scenarios.",
            "immediate_action": build_unsupported_action("unsupported_country_pair"),
            **build_input_guidance("unsupported_country_pair", normalized),
        }

    match = find_treaty_entry(normalized["transaction_type"])
    if match is None:
        return {
            "supported": False,
            "reason": "unsupported_transaction_type",
            "message": "Current MVP supports only dividends, interest, and royalties.",
            "immediate_action": build_unsupported_action("unsupported_transaction_type"),
            **build_input_guidance("unsupported_transaction_type", normalized),
        }

    return {
        "supported": True,
        "normalized_input": {
            "payer_country": normalized["payer_country"],
            "payee_country": normalized["payee_country"],
            "transaction_type": normalized["transaction_type"],
        },
        "result": shape_result(match),
    }


def normalize_input(scenario: str) -> dict:
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
        "reason": reason,
    }


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


def find_treaty_entry(transaction_type: str) -> dict | None:
    with DATA_PATH.open("r", encoding="utf-8") as file:
        payload = json.load(file)

    for article in payload["articles"]:
        if article["income_type"] == transaction_type:
            for paragraph in article["paragraphs"]:
                base_rule = select_rate_rule(paragraph["rules"])
                if base_rule is None:
                    continue
                review_priority, review_reason, auto_conclusion_allowed = build_review_guidance(
                    base_rule
                )
                return {
                    "summary": build_summary(
                        article_number=article["article_number"],
                        article_title=article["article_title"],
                        rate=base_rule["rate"],
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
                    "source_reference": paragraph["source_reference"],
                    "source_language": paragraph["source_language"],
                    "source_excerpt": paragraph["source_excerpt"],
                    "rate": base_rule["rate"],
                    "extraction_confidence": base_rule["extraction_confidence"],
                    "auto_conclusion_allowed": auto_conclusion_allowed,
                    "key_missing_facts": KEY_MISSING_FACTS[article["income_type"]],
                    "review_checklist": REVIEW_CHECKLISTS[article["income_type"]],
                    "conditions": base_rule["conditions"],
                    "notes": article["notes"],
                    "human_review_required": base_rule["human_review_required"],
                    "review_priority": review_priority,
                    "review_reason": review_reason,
                }

    return None


def select_rate_rule(rules: list[dict]) -> dict | None:
    for rule in rules:
        if rule.get("is_primary_candidate") is True:
            return rule

    for rule in rules:
        if rule["direction"] == "bidirectional":
            return rule

    return None


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

