from __future__ import annotations

import json
from pathlib import Path

from app.llm_input_parser import LLMInputParserError, parse_scenario_to_json


REPO_ROOT = Path(__file__).resolve().parents[2]
STABLE_TREATY_REGISTRY = {
    ("CN", "NL"): REPO_ROOT / "data" / "treaties" / "cn-nl.v3.json",
    ("CN", "SG"): REPO_ROOT / "data" / "treaties" / "cn-sg.v3.json",
}
LLM_GENERATED_TREATY_REGISTRY = {
    ("CN", "NL"): REPO_ROOT / "data" / "treaties" / "cn-nl.v3.generated.from-llm.json",
}
DATA_PATH = STABLE_TREATY_REGISTRY[("CN", "NL")]
LLM_GENERATED_DATA_PATH = LLM_GENERATED_TREATY_REGISTRY[("CN", "NL")]
NORMAL_CONFIDENCE_THRESHOLD = 0.95
AUTO_CONCLUSION_CONFIDENCE_THRESHOLD = 0.80
SUPPORTED_SCOPE_EXAMPLES_BY_PAIR = {
    ("CN", "NL"): [
        "中国居民企业向荷兰公司支付股息",
        "中国居民企业向荷兰银行支付利息",
        "中国居民企业向荷兰公司支付特许权使用费",
    ],
    ("CN", "SG"): [
        "中国居民企业向新加坡公司支付股息",
        "中国居民企业向新加坡银行支付利息",
        "中国居民企业向新加坡公司支付特许权使用费",
    ],
}
TREATY_DISPLAY_NAMES_ZH = {
    ("CN", "NL"): "中国-荷兰税收协定",
    ("CN", "SG"): "中国-新加坡税收协定",
}
PAIR_LABELS_EN = {
    ("CN", "NL"): "China-Netherlands",
    ("CN", "SG"): "China-Singapore",
}
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
COUNTRY_FOOTPRINTS = {
    "CN": [
        "中国",
        "中国居民企业",
        "中国公司",
        "China",
        "Chinese",
        "PRC",
        "People's Republic of China",
        "Peoples Republic of China",
        "北京",
        "Beijing",
    ],
    "NL": [
        "荷兰",
        "荷兰公司",
        "Netherlands",
        "The Netherlands",
        "Holland",
        "Dutch",
        "阿姆斯特丹",
        "Amsterdam",
    ],
    "SG": [
        "新加坡",
        "新加坡公司",
        "Singapore",
        "Singaporean",
        "新加坡银行",
        "Singapore bank",
        "Singapore company",
    ],
    "US": ["美国", "美国公司", "United States", "USA", "Washington", "华盛顿"],
}
BOUNDARY_NOTE = (
    "This is a first-pass treaty pre-review based on limited scenario facts. "
    "Final eligibility still depends on additional facts, documents, and analysis "
    "outside the current review scope."
)
STATE_LABELS_ZH = {
    "pre_review_complete": "预审完成",
    "can_be_completed": "可补全",
    "partial_review": "预审部分完成",
    "needs_human_intervention": "需要人工介入",
    "out_of_scope": "不在支持范围",
}
FACT_VALUE_LABELS = {
    "direct_holding_confirmed": "Direct holding confirmed",
    "direct_holding_threshold_met": "Direct holding is at least 25%",
    "pe_effectively_connected": "Dividend effectively connected with a China PE / fixed base",
    "beneficial_owner_confirmed": "Beneficial owner status separately confirmed",
}
HANDOFF_RECOMMENDED_ROUTE_BY_STATE = {
    "pre_review_complete": "standard_review",
    "can_be_completed": "complete_facts_then_rerun",
    "partial_review": "manual_review",
    "needs_human_intervention": "manual_review",
    "out_of_scope": "out_of_scope_rewrite",
}
HANDOFF_NOTE = "This is a bounded pre-review output, not a final tax opinion."


def canonical_country_pair(*countries: str) -> tuple[str, str]:
    return tuple(sorted(countries))


def get_supported_scope_examples() -> list[str]:
    examples: list[str] = []
    for pair in sorted(STABLE_TREATY_REGISTRY):
        examples.extend(SUPPORTED_SCOPE_EXAMPLES_BY_PAIR.get(pair, []))
    return examples


def is_supported_stable_pair(pair: tuple[str, str] | None) -> bool:
    return pair in STABLE_TREATY_REGISTRY


def is_pair_available_in_data_source(
    pair: tuple[str, str] | None,
    data_source: str,
) -> bool:
    if pair is None:
        return False
    return pair in get_treaty_registry(data_source)


def get_treaty_registry(data_source: str) -> dict[tuple[str, str], Path]:
    if data_source == "llm_generated":
        registry = dict(LLM_GENERATED_TREATY_REGISTRY)
        registry[("CN", "NL")] = LLM_GENERATED_DATA_PATH
        return registry
    registry = dict(STABLE_TREATY_REGISTRY)
    registry[("CN", "NL")] = DATA_PATH
    return registry


def get_supported_pair_labels_en() -> list[str]:
    return [PAIR_LABELS_EN[pair] for pair in sorted(STABLE_TREATY_REGISTRY)]


def build_supported_pair_list_text() -> str:
    return ", ".join(get_supported_pair_labels_en())


def build_treaty_display_name(payer_country: str, payee_country: str) -> str:
    return TREATY_DISPLAY_NAMES_ZH.get(
        canonical_country_pair(payer_country, payee_country),
        f"{payer_country}-{payee_country} tax treaty",
    )


def finalize_response(response: dict) -> dict:
    response["handoff_package"] = build_handoff_package(response)
    return response


def build_handoff_package(response: dict) -> dict:
    machine_handoff = build_machine_handoff(response)
    return {
        "machine_handoff": machine_handoff,
        "human_review_brief": build_human_review_brief(response, machine_handoff),
    }


def build_machine_handoff(response: dict) -> dict:
    supported = bool(response.get("supported"))
    review_state_code = response.get("review_state", {}).get("state_code")
    normalized_input = response.get("normalized_input") or {}
    confirmed_scope = response.get("confirmed_scope") or {}
    result = response.get("result") or {}
    user_declared_facts = response.get("user_declared_facts") or {}
    source_trace = result.get("source_trace") or {}
    mli_context = result.get("mli_context") or {}

    if supported:
        record_kind = "supported"
        applicable_treaty = confirmed_scope.get("applicable_treaty")
        payment_direction = confirmed_scope.get("payment_direction")
        income_type = confirmed_scope.get("income_type")
        article_number = result.get("article_number")
        article_title = result.get("article_title")
        rate_display = result.get("rate")
        auto_conclusion_allowed = result.get("auto_conclusion_allowed", False)
        human_review_required = result.get("human_review_required", True)
        source_reference = result.get("source_reference")
        source_excerpt = result.get("source_excerpt")
        treaty_version = source_trace.get("version_note")
        mli_summary = mli_context.get("summary")
        review_priority = result.get("review_priority", "normal")
        blocking_facts = list(result.get("key_missing_facts", []))
    else:
        record_kind = "incomplete" if response.get("reason") == "incomplete_scenario" else "unsupported"
        applicable_treaty = None
        payment_direction = build_payment_direction(normalized_input)
        income_type = normalized_input.get("transaction_type")
        article_number = None
        article_title = None
        rate_display = None
        auto_conclusion_allowed = False
        human_review_required = True
        source_reference = None
        source_excerpt = None
        treaty_version = None
        mli_summary = None
        review_priority = "high" if review_state_code in {"needs_human_intervention", "out_of_scope"} else "normal"
        blocking_facts = list(response.get("missing_fields", []))

    return {
        "schema_version": "stage5.v1",
        "record_kind": record_kind,
        "review_state_code": review_state_code,
        "recommended_route": HANDOFF_RECOMMENDED_ROUTE_BY_STATE[review_state_code],
        "applicable_treaty": applicable_treaty,
        "payment_direction": payment_direction,
        "income_type": income_type,
        "article_number": article_number,
        "article_title": article_title,
        "rate_display": rate_display,
        "auto_conclusion_allowed": auto_conclusion_allowed,
        "human_review_required": human_review_required,
        "data_source_used": response.get("data_source_used"),
        "source_reference": source_reference,
        "source_excerpt": source_excerpt,
        "treaty_version": treaty_version,
        "mli_summary": mli_summary,
        "review_priority": review_priority,
        "blocking_facts": blocking_facts,
        "next_actions": list(response.get("next_actions", [])),
        "user_declared_facts": list(user_declared_facts.get("facts", [])),
    }


def build_payment_direction(normalized_input: dict) -> str | None:
    payer_country = normalized_input.get("payer_country")
    payee_country = normalized_input.get("payee_country")
    if not payer_country or not payee_country:
        return None
    return f"{payer_country} -> {payee_country}"


def build_human_review_brief(response: dict, machine_handoff: dict) -> dict:
    return {
        "brief_title": "Treaty Pre-Review Brief",
        "headline": build_handoff_headline(response, machine_handoff),
        "disposition": build_handoff_disposition(machine_handoff["review_state_code"]),
        "summary_lines": build_handoff_summary_lines(response, machine_handoff),
        "facts_to_verify": build_handoff_facts_to_verify(response, machine_handoff),
        "handoff_note": HANDOFF_NOTE,
    }


def build_handoff_headline(response: dict, machine_handoff: dict) -> str:
    if response.get("supported"):
        direction = machine_handoff.get("payment_direction") or "Current scenario"
        income_type = machine_handoff.get("income_type") or "payment"
        return f"{direction} {income_type} falls inside current treaty scope."

    if response.get("reason") == "incomplete_scenario":
        return "Current scenario needs additional facts before treaty pre-review can continue."
    if response.get("reason") == "unavailable_data_source":
        return "Current scenario cannot continue because the requested dataset is unavailable."
    return "Current scenario is outside the supported pilot treaty scope."


def build_handoff_disposition(review_state_code: str) -> str:
    dispositions = {
        "pre_review_complete": "Proceed with standard human review.",
        "can_be_completed": "Complete the missing facts and rerun the pre-review.",
        "partial_review": "Escalate this scenario for manual review.",
        "needs_human_intervention": "Escalate this scenario for manual review.",
        "out_of_scope": "Rewrite the scenario inside the supported pilot scope.",
    }
    return dispositions[review_state_code]


def build_handoff_summary_lines(response: dict, machine_handoff: dict) -> list[str]:
    lines: list[str] = []
    if response.get("supported"):
        article_number = machine_handoff.get("article_number")
        article_title = machine_handoff.get("article_title")
        rate_display = machine_handoff.get("rate_display")
        if article_number and article_title:
            lines.append(f"Article {article_number} {article_title} is the current treaty lane.")
        if rate_display is not None:
            lines.append(f"Current rate display: {rate_display}.")
        if machine_handoff.get("treaty_version"):
            lines.append(machine_handoff["treaty_version"])
        if machine_handoff.get("mli_summary"):
            lines.append(machine_handoff["mli_summary"])
    else:
        message = response.get("message")
        if message:
            lines.append(message)

    immediate_action = response.get("immediate_action")
    if immediate_action:
        lines.append(immediate_action)

    if machine_handoff["user_declared_facts"]:
        lines.append("User-declared facts remain unverified and should be checked during review.")
    return lines


def build_handoff_facts_to_verify(response: dict, machine_handoff: dict) -> list[str]:
    facts_to_verify = list(machine_handoff["blocking_facts"])
    if machine_handoff["user_declared_facts"]:
        facts_to_verify.insert(
            0,
            "Verify the user-declared facts before relying on the narrowed treaty result.",
        )
    if not facts_to_verify and response.get("supported"):
        facts_to_verify.extend(response.get("result", {}).get("review_checklist", []))
    return facts_to_verify


def analyze_scenario(
    scenario: str,
    data_source: str = "stable",
    fact_inputs: dict | None = None,
) -> dict:
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
        response.update(
            build_stage3_narrowing_contract(
                reason="incomplete_scenario",
                normalized=normalized,
            )
        )
        if input_interpretation is not None:
            response["input_interpretation"] = input_interpretation
        return finalize_response(response)

    pair = canonical_country_pair(*normalized["country_pair"])

    if not is_supported_stable_pair(pair):
        response = {
            "data_source_used": resolved_data_source,
            "supported": False,
            "reason": "unsupported_country_pair",
            "message": (
                "Current pilot scope supports only "
                f"{build_supported_pair_list_text()} treaty scenarios."
            ),
            "immediate_action": build_unsupported_action("unsupported_country_pair"),
            **build_input_guidance("unsupported_country_pair", normalized),
        }
        response.update(
            build_stage3_narrowing_contract(
                reason="unsupported_country_pair",
                normalized=normalized,
            )
        )
        if input_interpretation is not None:
            response["input_interpretation"] = input_interpretation
        return finalize_response(response)

    if not is_pair_available_in_data_source(pair, resolved_data_source):
        response = build_data_source_unavailable_response(resolved_data_source)
        if input_interpretation is not None:
            response["input_interpretation"] = input_interpretation
        return finalize_response(response)

    try:
        match = find_treaty_entry(
            normalized["transaction_type"],
            payer_country=normalized["payer_country"],
            payee_country=normalized["payee_country"],
            country_pair=pair,
            data_source=resolved_data_source,
        )
    except FileNotFoundError:
        response = build_data_source_unavailable_response(resolved_data_source)
        if input_interpretation is not None:
            response["input_interpretation"] = input_interpretation
        return finalize_response(response)

    if match is None:
        response = {
            "data_source_used": resolved_data_source,
            "supported": False,
            "reason": "unsupported_transaction_type",
            "message": "Current MVP supports only dividends, interest, and royalties.",
            "immediate_action": build_unsupported_action("unsupported_transaction_type"),
            **build_input_guidance("unsupported_transaction_type", normalized),
        }
        response.update(
            build_stage3_narrowing_contract(
                reason="unsupported_transaction_type",
                normalized=normalized,
            )
        )
        if input_interpretation is not None:
            response["input_interpretation"] = input_interpretation
        return finalize_response(response)

    stage4_payload = build_empty_stage4_payload()
    match, stage4_payload = apply_stage4_fact_completion(
        match,
        normalized=normalized,
        fact_inputs=fact_inputs or {},
    )
    shaped_result = shape_result(match)
    response = {
        "data_source_used": resolved_data_source,
        "supported": True,
        "normalized_input": {
            "payer_country": normalized["payer_country"],
            "payee_country": normalized["payee_country"],
            "transaction_type": normalized["transaction_type"],
        },
        "result": shaped_result,
    }
    response.update(
        build_stage3_supported_contract(
            result=shaped_result,
            normalized=normalized,
        )
    )
    if stage4_payload["stage4_active"]:
        response["fact_completion"] = stage4_payload["fact_completion"]
        response["user_declared_facts"] = stage4_payload["user_declared_facts"]
        response["fact_completion_status"] = stage4_payload["fact_completion_status"]
        response["change_summary"] = stage4_payload["change_summary"]
        if stage4_payload["review_state_override"] is not None:
            response["review_state"] = stage4_payload["review_state_override"]
        if stage4_payload["next_actions_override"] is not None:
            response["next_actions"] = stage4_payload["next_actions_override"]
    if input_interpretation is not None:
        response["input_interpretation"] = input_interpretation
    return finalize_response(response)


def normalize_data_source(data_source: str) -> str:
    if data_source == "llm_generated":
        return "llm_generated"
    return "stable"


def normalize_input(scenario: str) -> dict:
    llm_normalized = try_llm_normalize_input(scenario)
    if llm_normalized is not None:
        return apply_llm_guardrails(
            scenario,
            {
                **llm_normalized,
                "parser_source": llm_normalized.get("parser_source", "llm"),
            },
        )

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


def apply_llm_guardrails(scenario: str, normalized: dict) -> dict:
    if normalized.get("reason") != "ok":
        return normalized

    deterministic_payer, deterministic_payee = detect_flow_countries(scenario)
    deterministic_transaction_type, _ = detect_transaction_type(scenario)

    if (
        deterministic_payer is not None
        and deterministic_payee is not None
        and (
            normalized["payer_country"] != deterministic_payer
            or normalized["payee_country"] != deterministic_payee
        )
    ):
        return build_llm_rejection_payload(
            normalized,
            payer_country=None,
            payee_country=None,
            transaction_type="unknown",
        )

    if (
        deterministic_transaction_type != "unknown"
        and normalized["transaction_type"] != deterministic_transaction_type
    ):
        return build_llm_rejection_payload(
            normalized,
            transaction_type="unknown",
        )

    if not has_minimum_llm_evidence(scenario, normalized):
        return build_llm_rejection_payload(
            normalized,
            payer_country=None,
            payee_country=None,
            transaction_type="unknown",
        )

    return normalized


def build_llm_rejection_payload(
    normalized: dict,
    *,
    payer_country: str | None | object = ...,
    payee_country: str | None | object = ...,
    transaction_type: str | object = ...,
) -> dict:
    adjusted = dict(normalized)
    if payer_country is not ...:
        adjusted["payer_country"] = payer_country
    if payee_country is not ...:
        adjusted["payee_country"] = payee_country
    if transaction_type is not ...:
        adjusted["transaction_type"] = transaction_type

    if adjusted["payer_country"] is None or adjusted["payee_country"] is None:
        adjusted["country_pair"] = None
    else:
        adjusted["country_pair"] = (
            adjusted["payer_country"],
            adjusted["payee_country"],
        )
    adjusted["reason"] = "incomplete_scenario"
    return adjusted


def has_minimum_llm_evidence(scenario: str, normalized: dict) -> bool:
    if not scenario_has_country_footprint(scenario, normalized.get("payer_country")):
        return False
    if not scenario_has_country_footprint(scenario, normalized.get("payee_country")):
        return False

    transaction_type = normalized.get("transaction_type")
    matched_label = normalized.get("matched_transaction_label")
    return scenario_has_tax_signal(scenario, transaction_type, matched_label)


def scenario_has_country_footprint(scenario: str, country_code: str | None) -> bool:
    if country_code is None:
        return False
    for keyword in COUNTRY_FOOTPRINTS.get(country_code, []):
        if keyword in scenario:
            return True
    return False


def scenario_has_tax_signal(
    scenario: str,
    transaction_type: str | None,
    matched_label: str | None,
) -> bool:
    if matched_label and matched_label in scenario:
        return True
    if transaction_type in TRANSACTION_KEYWORDS:
        for keyword in TRANSACTION_KEYWORDS[transaction_type]:
            if keyword in scenario:
                return True
    return False


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
        "SINGAPORE": "SG",
        "SINGAPOREAN": "SG",
        "SG": "SG",
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
        payer_country = detect_country(payer_segment, country_codes=["CN", "NL", "SG", "US"])
        payee_country = detect_country(payee_segment, country_codes=["CN", "NL", "SG", "US"])
        return payer_country, payee_country

    return None, None


def detect_country(scenario: str, country_codes: list[str]) -> str | None:
    matches: list[str] = []
    for country_code in country_codes:
        for keyword in COUNTRY_FOOTPRINTS.get(country_code, []):
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


def find_treaty_entry(
    transaction_type: str,
    *,
    payer_country: str,
    payee_country: str,
    country_pair: tuple[str, str],
    data_source: str = "stable",
) -> dict | None:
    with resolve_data_path(data_source, country_pair).open("r", encoding="utf-8") as file:
        payload = json.load(file)
    treaty_jurisdictions = payload["treaty"].get("jurisdictions", [])

    for article in payload["articles"]:
        if article["income_type"] == transaction_type:
            selected_paragraph = None
            selected_rule = None
            for paragraph in article["paragraphs"]:
                base_rule = select_rate_rule(
                    paragraph["rules"],
                    payer_country=payer_country,
                    payee_country=payee_country,
                    treaty_jurisdictions=treaty_jurisdictions,
                )
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
                payer_country=payer_country,
                payee_country=payee_country,
                treaty_jurisdictions=treaty_jurisdictions,
            )
            branch_candidates_full = build_branch_candidates_full(
                article["paragraphs"],
                selected_rule=selected_rule,
                selected_paragraph=selected_paragraph,
                alternative_rate_candidates=alternative_rate_candidates,
                payer_country=payer_country,
                payee_country=payee_country,
                treaty_jurisdictions=treaty_jurisdictions,
            )
            display_rate = selected_rule["rate"]
            if alternative_rate_candidates:
                review_priority = "high"
                auto_conclusion_allowed = False
                display_rate = format_possible_rates(
                    selected_rule["rate"], alternative_rate_candidates
                )
                review_reason = (
                    f"{review_reason} Multiple treaty rate branches were found in this article, "
                    "and the current scenario does not provide enough facts to choose one automatically."
                )
            result = {
                "treaty_id": payload["treaty"].get("treaty_id"),
                "treaty_title": payload["treaty"].get("title"),
                "summary": build_summary(
                    article_number=article["article_number"],
                    article_title=article["article_title"],
                    rate=display_rate,
                    review_priority=review_priority,
                    auto_conclusion_allowed=auto_conclusion_allowed,
                    has_rate_ambiguity=bool(alternative_rate_candidates),
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
                "rate": display_rate,
                "extraction_confidence": selected_rule["extraction_confidence"],
                "auto_conclusion_allowed": auto_conclusion_allowed,
                "key_missing_facts": KEY_MISSING_FACTS[article["income_type"]],
                "review_checklist": REVIEW_CHECKLISTS[article["income_type"]],
                "conditions": selected_rule["conditions"],
                "notes": article["notes"],
                "source_trace": build_source_trace(payload, article["income_type"]),
                "mli_context": build_mli_context(payload),
                "human_review_required": selected_rule["human_review_required"],
                "review_priority": review_priority,
                "review_reason": review_reason,
                "_branch_candidates_full": branch_candidates_full,
            }
            if alternative_rate_candidates:
                result["alternative_rate_candidates"] = alternative_rate_candidates
            return result

    return None


def resolve_data_path(data_source: str, country_pair: tuple[str, str]) -> Path:
    registry = get_treaty_registry(data_source)
    if country_pair not in registry:
        raise FileNotFoundError(country_pair)
    return registry[country_pair]


def select_rate_rule(
    rules: list[dict],
    *,
    payer_country: str,
    payee_country: str,
    treaty_jurisdictions: list[str],
) -> dict | None:
    for rule in rules:
        if (
            rule.get("is_primary_candidate") is True
            and rule_matches_direction(
                rule,
                payer_country=payer_country,
                payee_country=payee_country,
                treaty_jurisdictions=treaty_jurisdictions,
            )
        ):
            return rule

    for rule in rules:
        if rule_matches_direction(
            rule,
            payer_country=payer_country,
            payee_country=payee_country,
            treaty_jurisdictions=treaty_jurisdictions,
        ):
            return rule

    return None


def rule_matches_direction(
    rule: dict,
    *,
    payer_country: str,
    payee_country: str,
    treaty_jurisdictions: list[str],
) -> bool:
    direction = rule.get("direction", "bidirectional")
    if direction == "bidirectional":
        return True

    if len(treaty_jurisdictions) >= 2:
        first_jurisdiction, second_jurisdiction = treaty_jurisdictions[:2]
        if direction == "payer_to_payee":
            return (
                payer_country == first_jurisdiction
                and payee_country == second_jurisdiction
            )
        if direction == "payee_to_payer":
            return (
                payer_country == second_jurisdiction
                and payee_country == first_jurisdiction
            )

    if "_to_" in str(direction):
        from_code, to_code = str(direction).split("_to_", 1)
        return (
            payer_country == from_code.upper()
            and payee_country == to_code.upper()
        )

    return False


def rule_preference_key(rule: dict) -> tuple[int, float]:
    has_numeric_rate = 0 if rule.get("rate") in {"", "N/A", None} else 1
    return (has_numeric_rate, float(rule.get("extraction_confidence", 0)))


def collect_alternative_rate_candidates(
    paragraphs: list[dict],
    *,
    selected_rule: dict,
    selected_source_reference: str,
    payer_country: str,
    payee_country: str,
    treaty_jurisdictions: list[str],
) -> list[dict]:
    candidates: list[dict] = []
    seen: set[tuple[str, str, str]] = set()
    selected_rate = selected_rule.get("rate")
    selected_rule_id = selected_rule.get("rule_id")

    for paragraph in paragraphs:
        for rule in paragraph["rules"]:
            if not rule_matches_direction(
                rule,
                payer_country=payer_country,
                payee_country=payee_country,
                treaty_jurisdictions=treaty_jurisdictions,
            ):
                continue
            candidate_rate = rule.get("rate")
            if candidate_rate in {"", "N/A", None}:
                continue
            if float(rule.get("extraction_confidence", 0)) < AUTO_CONCLUSION_CONFIDENCE_THRESHOLD:
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
    return {key: value for key, value in entry.items() if not key.startswith("_")}


def build_source_trace(payload: dict, income_type: str) -> dict:
    treaty = payload.get("treaty", {})
    source_trace = treaty.get("source_trace") or {}
    working_papers = source_trace.get("working_papers") or {}
    return {
        "treaty_full_name": source_trace.get("treaty_full_name"),
        "version_note": source_trace.get("version_note"),
        "source_document_title": source_trace.get("source_document_title"),
        "language_version": source_trace.get("language_version"),
        "official_source_ids": list(source_trace.get("official_source_ids", [])),
        "protocol_note": source_trace.get("protocol_note"),
        "working_paper_ref": working_papers.get(income_type),
    }


def build_mli_context(payload: dict) -> dict:
    treaty = payload.get("treaty", {})
    mli_context = treaty.get("mli_context") or {}
    return {
        "covered_tax_agreement": bool(mli_context.get("covered_tax_agreement")),
        "ppt_applies": bool(mli_context.get("ppt_applies")),
        "summary": mli_context.get("summary"),
        "human_review_note": mli_context.get("human_review_note"),
        "official_source_ids": list(mli_context.get("official_source_ids", [])),
    }


def build_summary(
    article_number: str,
    article_title: str,
    rate: str,
    review_priority: str,
    auto_conclusion_allowed: bool,
    has_rate_ambiguity: bool = False,
) -> str:
    base = f"Preliminary view: Article {article_number} {article_title} appears relevant"

    if has_rate_ambiguity:
        return (
            f"{base}, but multiple treaty rate branches ({rate}) are possible and this version "
            "should not issue an automatic conclusion."
        )

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


def format_possible_rates(selected_rate: str, alternative_rate_candidates: list[dict]) -> str:
    rates = [selected_rate] + [candidate["rate"] for candidate in alternative_rate_candidates]
    unique_rates = list(dict.fromkeys(rate for rate in rates if rate))
    sortable_rates: list[tuple[int, str]] = []
    unsortable_rates: list[str] = []

    for rate in unique_rates:
        if rate.endswith("%"):
            try:
                sortable_rates.append((int(rate.rstrip("%")), rate))
                continue
            except ValueError:
                pass
        unsortable_rates.append(rate)

    ordered = [rate for _, rate in sorted(sortable_rates)] + unsortable_rates
    return " / ".join(ordered)


def build_unsupported_action(reason: str) -> str:
    if reason == "unavailable_data_source":
        return (
            "Retry with the stable curated dataset or regenerate the requested "
            "treaty dataset before reviewing this scenario."
        )

    if reason == "unsupported_country_pair":
        return (
            "Rewrite the scenario into the supported pilot treaty pair list "
            "before running another review."
        )

    if reason == "unsupported_transaction_type":
        return "Restate the payment using a supported income type before relying on treaty review output."

    return "Add the missing scenario facts before running the treaty review again."


def build_data_source_unavailable_response(data_source: str) -> dict:
    response = {
        "data_source_used": data_source,
        "supported": False,
        "reason": "unavailable_data_source",
        "message": "The requested treaty dataset is not currently available.",
        "immediate_action": build_unsupported_action("unavailable_data_source"),
        "missing_fields": [],
        "suggested_format": (
            "Try again with the stable dataset or regenerate the LLM-generated "
            "treaty dataset before reviewing this scenario."
        ),
        "suggested_examples": [
            "Use the default stable dataset for a normal review run.",
            "Regenerate the LLM-derived treaty dataset, then retry the same scenario.",
        ],
    }
    response.update(
        build_stage3_narrowing_contract(
            reason="unavailable_data_source",
            normalized={
                "payer_country": None,
                "payee_country": None,
                "transaction_type": "unknown",
            },
        )
    )
    return response


def build_input_guidance(reason: str, normalized: dict) -> dict:
    classification_note = build_classification_note(normalized)
    supported_examples = get_supported_scope_examples()

    if reason == "unsupported_country_pair":
        payload = {
            "missing_fields": [],
            "suggested_format": f"Try a sentence like: {supported_examples[-1]}",
            "suggested_examples": supported_examples,
        }
        if classification_note:
            payload["classification_note"] = classification_note
        return payload

    if reason == "unsupported_transaction_type":
        payload = {
            "missing_fields": ["transaction_type"],
            "suggested_format": f"Try a sentence like: {supported_examples[-1]}",
            "suggested_examples": supported_examples,
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
        "suggested_examples": supported_examples[:2],
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

    payer_labels = {
        "CN": "中国居民企业",
        "NL": "荷兰公司",
        "SG": "新加坡公司",
    }
    payee_labels = {
        ("NL", "interest"): "荷兰银行",
        ("SG", "interest"): "新加坡银行",
    }
    payer_label = payer_labels.get(payer_country, "中国居民企业")
    payee_label = payee_labels.get(
        (payee_country, transaction_type),
        payer_labels.get(payee_country, "荷兰公司"),
    )

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


def build_stage3_supported_contract(*, result: dict, normalized: dict) -> dict:
    state_code = classify_supported_state(result)
    payload = {
        "review_state": {
            "state_code": state_code,
            "state_label_zh": STATE_LABELS_ZH[state_code],
            "state_summary": build_supported_state_summary(state_code),
        },
        "confirmed_scope": {
            "applicable_treaty": build_treaty_display_name(
                normalized["payer_country"],
                normalized["payee_country"],
            ),
            "applicable_article": f"Article {result['article_number']} - {result['article_title']}",
            "payment_direction": f"{normalized['payer_country']} -> {normalized['payee_country']}",
            "income_type": normalized["transaction_type"],
        },
        "next_actions": build_supported_next_actions(state_code, result, normalized),
    }
    return payload


def build_stage3_narrowing_contract(*, reason: str, normalized: dict) -> dict:
    state_code = classify_unsupported_state(reason)
    payload = {
        "review_state": {
            "state_code": state_code,
            "state_label_zh": STATE_LABELS_ZH[state_code],
            "state_summary": build_unsupported_state_summary(state_code),
        },
        "next_actions": build_unsupported_next_actions(reason, normalized),
    }
    return payload


def classify_supported_state(result: dict) -> str:
    if not result["auto_conclusion_allowed"]:
        if result.get("alternative_rate_candidates"):
            return "can_be_completed"
        return "needs_human_intervention"
    if result["review_priority"] == "high":
        return "partial_review"
    return "pre_review_complete"


def classify_unsupported_state(reason: str) -> str:
    if reason == "incomplete_scenario":
        return "can_be_completed"
    if reason == "unavailable_data_source":
        return "needs_human_intervention"
    return "out_of_scope"


def build_supported_state_summary(state_code: str) -> str:
    summaries = {
        "pre_review_complete": "系统已完成第一轮预审，请按标准复核流程继续。",
        "can_be_completed": "系统已缩小范围；补充少量关键事实后，可进一步明确结果。",
        "partial_review": "系统已完成结构化缩减，但当前结果仍需优先人工复核。",
        "needs_human_intervention": "当前结果已触发保守停止，应转入人工处理而不是继续自动推进。",
    }
    return summaries[state_code]


def build_unsupported_state_summary(state_code: str) -> str:
    summaries = {
        "can_be_completed": "系统仍在当前预审范围内，但需要补充缺失事实后才能继续缩小结果。",
        "needs_human_intervention": "当前结果无法在现有自动化边界内继续推进，应转入人工处理。",
        "out_of_scope": "当前查询超出本产品的国家对或收入类型支持范围。",
    }
    return summaries[state_code]


def build_supported_next_actions(state_code: str, result: dict, normalized: dict) -> list[dict]:
    if state_code == "pre_review_complete":
        return [
            {
                "priority": "medium",
                "action": "按标准人工复核流程确认条款适用条件与受益所有人事实。",
                "reason": "当前结果属于第一轮预审完成，不等于最终税务结论。",
            }
        ]
    if state_code == "partial_review":
        return [
            {
                "priority": "high",
                "action": "优先核验条款适用条件、来源质量和关键事实后再引用该结果。",
                "reason": "当前来源置信度不足以支持常规依赖，但已完成条款缩减。",
            }
        ]
    if state_code == "can_be_completed":
        transaction_label = TRANSACTION_LABELS_ZH.get(
            normalized["transaction_type"],
            "当前协定",
        )
        return [
            {
                "priority": "high",
                "action": f"先核实{transaction_label}分支所需的关键事实，再判断候选税率分支。",
                "reason": "当前存在多个可信税率分支，系统不会自动替你选择其一。",
            }
        ]
    return [
        {
            "priority": "high",
            "action": "停止自动结论流程，并将当前条款、来源和待核事实交给人工复核。",
            "reason": "当前来源置信度过低，系统不应继续自动推进。",
        }
    ]


def build_unsupported_next_actions(reason: str, normalized: dict) -> list[dict]:
    if reason == "incomplete_scenario":
        payer_missing = normalized.get("payer_country") is None
        payee_missing = normalized.get("payee_country") is None
        transaction_missing = normalized.get("transaction_type") == "unknown"
        missing_fields = []
        if payer_missing:
            missing_fields.append("付款方国家或付款方主体信息")
        if payee_missing:
            missing_fields.append("收款方国家或收款方主体信息")
        if transaction_missing:
            missing_fields.append("收入类型")
        missing_text = "、".join(missing_fields) or "关键交易事实"
        if payer_missing and not payee_missing and not transaction_missing:
            reason_text = "当前缺少足够的付款方事实，系统无法确认交易方向。"
        elif payee_missing and not payer_missing and not transaction_missing:
            reason_text = "当前缺少足够的收款方事实，系统无法确认交易方向。"
        else:
            reason_text = "当前缺少足够事实，系统无法继续确认预审方向。"
        return [
            {
                "priority": "high",
                "action": f"补充{missing_text}后重新提交查询。",
                "reason": reason_text,
            }
        ]
    if reason == "unavailable_data_source":
        return [
            {
                "priority": "high",
                "action": "切回稳定数据源，或在人工确认数据已生成后再重试。",
                "reason": "当前请求的数据集不可用，系统不会伪造协定结论。",
            }
        ]
    return [
        {
            "priority": "high",
            "action": "改写为当前试点国家对列表内、且属于股息、利息或特许权使用费的查询后再重试。",
            "reason": (
                "当前场景属于产品边界之外；目前稳定数据源只支持 "
                f"{build_supported_pair_list_text()} 两个试点国家对。"
            ),
        }
    ]


def build_branch_candidates_full(
    paragraphs: list[dict],
    *,
    selected_rule: dict,
    selected_paragraph: dict,
    alternative_rate_candidates: list[dict],
    payer_country: str,
    payee_country: str,
    treaty_jurisdictions: list[str],
) -> list[dict]:
    candidates = [
        {
            "rule_id": selected_rule.get("rule_id"),
            "source_reference": selected_paragraph["source_reference"],
            "source_language": selected_paragraph["source_language"],
            "source_excerpt": selected_paragraph["source_excerpt"],
            "rate": selected_rule.get("rate"),
            "conditions": selected_rule.get("conditions", []),
            "extraction_confidence": selected_rule.get("extraction_confidence"),
            "review_reason": selected_rule.get("review_reason", ""),
            "human_review_required": selected_rule.get("human_review_required", True),
        }
    ]

    for paragraph in paragraphs:
        for rule in paragraph["rules"]:
            if not rule_matches_direction(
                rule,
                payer_country=payer_country,
                payee_country=payee_country,
                treaty_jurisdictions=treaty_jurisdictions,
            ):
                continue
            if rule.get("rule_id") == selected_rule.get("rule_id"):
                continue
            if rule.get("rate") in {"", "N/A", None}:
                continue
            public_key = (
                paragraph["source_reference"],
                rule.get("rate"),
                tuple(rule.get("conditions", [])),
            )
            if not any(
                (
                    candidate["source_reference"],
                    candidate["rate"],
                    tuple(candidate["conditions"]),
                )
                == public_key
                for candidate in alternative_rate_candidates
            ):
                continue
            candidates.append(
                {
                    "rule_id": rule.get("rule_id"),
                    "source_reference": paragraph["source_reference"],
                    "source_language": paragraph["source_language"],
                    "source_excerpt": paragraph["source_excerpt"],
                    "rate": rule.get("rate"),
                    "conditions": rule.get("conditions", []),
                    "extraction_confidence": rule.get("extraction_confidence"),
                    "review_reason": rule.get("review_reason", ""),
                    "human_review_required": rule.get("human_review_required", True),
                }
            )

    return candidates


def build_empty_stage4_payload() -> dict:
    return {
        "stage4_active": False,
        "fact_completion": None,
        "user_declared_facts": None,
        "fact_completion_status": None,
        "change_summary": None,
        "review_state_override": None,
        "next_actions_override": None,
    }


def apply_stage4_fact_completion(
    entry: dict,
    *,
    normalized: dict,
    fact_inputs: dict,
) -> tuple[dict, dict]:
    payload = build_empty_stage4_payload()
    if not is_stage4_dividend_target(entry, normalized):
        return entry, payload

    payload["stage4_active"] = True
    declared_facts = normalize_stage4_fact_inputs(fact_inputs)
    if declared_facts:
        payload["user_declared_facts"] = build_user_declared_facts(declared_facts)

    branch_resolution = resolve_dividend_branch_from_facts(declared_facts)
    if not declared_facts:
        payload["fact_completion"] = build_dividend_fact_completion()
        payload["fact_completion_status"] = {
            "status_code": "awaiting_user_facts",
            "status_label_zh": "待补事实",
            "status_summary": "请先补充关键持股事实，系统才能继续缩小股息税率分支。",
        }
        return entry, payload

    if declared_facts.get("pe_effectively_connected") == "yes":
        payload["fact_completion"] = None
        payload["fact_completion_status"] = {
            "status_code": "terminated_pe_exclusion",
            "status_label_zh": "转入排除情形复核",
            "status_summary": "当前场景触发了与中国常设机构或固定基地实际联系的排除提醒，系统结束 Article 10 分支自动缩减。",
        }
        payload["change_summary"] = build_stage4_change_summary(
            from_state_label=STATE_LABELS_ZH["can_be_completed"],
            to_state_label=STATE_LABELS_ZH["needs_human_intervention"],
            from_rate="5% / 10%",
            to_rate="Article 10 branch excluded",
            fact_inputs=declared_facts,
        )
        payload["review_state_override"] = {
            "state_code": "needs_human_intervention",
            "state_label_zh": STATE_LABELS_ZH["needs_human_intervention"],
            "state_summary": build_supported_state_summary("needs_human_intervention"),
        }
        payload["next_actions_override"] = [
            {
                "priority": "high",
                "action": "停止依赖当前股息分支自动缩减，并确认荷兰收款方是否在中国存在与该股息实际联系的常设机构或固定基地。",
                "reason": "如果该排除情形成立，当前场景可能需要转入其他条款并进行人工复核，而不是继续沿用 Article 10 分支结果。",
            }
        ]
        return entry, payload

    if has_conflicting_dividend_facts(declared_facts):
        payload["fact_completion"] = None
        payload["fact_completion_status"] = {
            "status_code": "terminated_conflicting_user_facts",
            "status_label_zh": "用户声明事实冲突",
            "status_summary": "已提交的补事实答案彼此冲突，系统结束当前股息分支自动缩减。",
        }
        payload["change_summary"] = build_stage4_change_summary(
            from_state_label=STATE_LABELS_ZH["can_be_completed"],
            to_state_label=STATE_LABELS_ZH["needs_human_intervention"],
            from_rate="5% / 10%",
            to_rate="treaty rate cannot be narrowed due to conflicting facts",
            fact_inputs=declared_facts,
        )
        payload["review_state_override"] = {
            "state_code": "needs_human_intervention",
            "state_label_zh": STATE_LABELS_ZH["needs_human_intervention"],
            "state_summary": build_supported_state_summary("needs_human_intervention"),
        }
        payload["next_actions_override"] = [
            {
                "priority": "high",
                "action": "先核对直接持股方式和持股比例的真实情况；当前答案彼此冲突，系统不会继续自动缩减股息税率分支。",
                "reason": "例如，在未直接持股的情况下不能同时把直接持股门槛判断为已满足；请先在线下核实后再重新预审。",
            }
        ]
        return entry, payload

    if declared_facts.get("beneficial_owner_confirmed") == "no":
        payload["fact_completion"] = None
        payload["fact_completion_status"] = {
            "status_code": "terminated_beneficial_owner_unconfirmed",
            "status_label_zh": "受益所有人前提未确认",
            "status_summary": "协定优惠前提中的受益所有人身份尚未被单独确认，系统结束当前股息分支自动缩减。",
        }
        payload["change_summary"] = build_stage4_change_summary(
            from_state_label=STATE_LABELS_ZH["can_be_completed"],
            to_state_label=STATE_LABELS_ZH["needs_human_intervention"],
            from_rate=branch_resolution or "5% / 10%",
            to_rate="treaty rate cannot be relied on yet",
            fact_inputs=declared_facts,
        )
        payload["review_state_override"] = {
            "state_code": "needs_human_intervention",
            "state_label_zh": STATE_LABELS_ZH["needs_human_intervention"],
            "state_summary": build_supported_state_summary("needs_human_intervention"),
        }
        payload["next_actions_override"] = [
            {
                "priority": "high",
                "action": "先单独确认受益所有人身份及其支持材料，在未确认前不要依赖当前协定优惠税率分支。",
                "reason": "受益所有人是协定优惠适用的前提条件；系统不会仅凭当前输入替你判断这一点是否成立。",
            }
        ]
        return entry, payload

    if branch_resolution is None:
        payload["fact_completion"] = None
        payload["fact_completion_status"] = {
            "status_code": "terminated_unknown_facts",
            "status_label_zh": "停止自动缩减",
            "status_summary": "关键事实仍未确认，系统结束当前补事实流程并建议先在线下核实。",
        }
        payload["change_summary"] = build_stage4_change_summary(
            from_state_label=STATE_LABELS_ZH["can_be_completed"],
            to_state_label=STATE_LABELS_ZH["needs_human_intervention"],
            from_rate="5% / 10%",
            to_rate="5% / 10%",
            fact_inputs=declared_facts,
        )
        payload["review_state_override"] = {
            "state_code": "needs_human_intervention",
            "state_label_zh": STATE_LABELS_ZH["needs_human_intervention"],
            "state_summary": build_supported_state_summary("needs_human_intervention"),
        }
        payload["next_actions_override"] = [
            {
                "priority": "high",
                "action": "先在线下确认直接持股比例和持股方式，再重新发起预审或转交人工复核。",
                "reason": "当前关键分支事实仍未确认，系统不会继续自动缩减股息税率分支。",
            }
        ]
        return entry, payload

    selected_branch = select_branch_candidate_by_rate(
        entry.get("_branch_candidates_full", []),
        branch_resolution,
    )
    if selected_branch is None:
        payload["fact_completion"] = build_dividend_fact_completion()
        return entry, payload

    narrowed_entry = dict(entry)
    narrowed_entry["rate"] = selected_branch["rate"]
    narrowed_entry["source_reference"] = selected_branch["source_reference"]
    narrowed_entry["source_language"] = selected_branch["source_language"]
    narrowed_entry["source_excerpt"] = selected_branch["source_excerpt"]
    narrowed_entry["extraction_confidence"] = selected_branch["extraction_confidence"]
    narrowed_entry["conditions"] = selected_branch["conditions"]
    narrowed_entry["review_priority"] = "normal"
    narrowed_entry["auto_conclusion_allowed"] = True
    narrowed_entry["human_review_required"] = True
    narrowed_entry["review_reason"] = (
        "Final eligibility depends on facts outside the current review scope. "
        "The current branch view reflects unverified user-declared direct holding facts."
    )
    narrowed_entry["summary"] = build_summary(
        article_number=narrowed_entry["article_number"],
        article_title=narrowed_entry["article_title"],
        rate=narrowed_entry["rate"],
        review_priority=narrowed_entry["review_priority"],
        auto_conclusion_allowed=True,
    )
    narrowed_entry["immediate_action"] = build_immediate_action(
        review_priority=narrowed_entry["review_priority"],
        auto_conclusion_allowed=True,
    )
    narrowed_entry.pop("alternative_rate_candidates", None)
    payload["fact_completion_status"] = {
        "status_code": "completed_narrowed",
        "status_label_zh": "已缩减",
        "status_summary": "系统已根据用户声明事实将股息分支缩减为单一候选税率。",
    }
    payload["change_summary"] = build_stage4_change_summary(
        from_state_label=STATE_LABELS_ZH["can_be_completed"],
        to_state_label=STATE_LABELS_ZH["pre_review_complete"],
        from_rate="5% / 10%",
        to_rate=branch_resolution,
        fact_inputs=declared_facts,
    )
    return narrowed_entry, payload


def is_stage4_dividend_target(entry: dict, normalized: dict) -> bool:
    if normalized.get("transaction_type") != "dividends":
        return False
    if normalized.get("payer_country") != "CN" or normalized.get("payee_country") != "NL":
        return False
    if not entry.get("alternative_rate_candidates"):
        return False
    candidate_rates = {
        candidate.get("rate") for candidate in entry.get("_branch_candidates_full", [])
    }
    return {"5%", "10%"}.issubset(candidate_rates)


def normalize_stage4_fact_inputs(fact_inputs: dict) -> dict:
    normalized = {}
    for key in FACT_VALUE_LABELS:
        value = fact_inputs.get(key)
        if value in {"yes", "no", "unknown"}:
            normalized[key] = value
    return normalized


def build_user_declared_facts(fact_inputs: dict) -> dict:
    facts = []
    for key, value in fact_inputs.items():
        facts.append(
            {
                "fact_key": key,
                "value": value,
                "label": FACT_VALUE_LABELS[key],
            }
        )
    return {
        "declaration_label": "User-declared facts (unverified)",
        "facts": facts,
    }


def resolve_dividend_branch_from_facts(fact_inputs: dict) -> str | None:
    direct_holding = fact_inputs.get("direct_holding_confirmed")
    threshold_met = fact_inputs.get("direct_holding_threshold_met")

    if direct_holding == "no":
        return "10%"
    if direct_holding != "yes":
        return None
    if threshold_met == "yes":
        return "5%"
    if threshold_met == "no":
        return "10%"
    return None


def has_conflicting_dividend_facts(fact_inputs: dict) -> bool:
    direct_holding = fact_inputs.get("direct_holding_confirmed")
    threshold_met = fact_inputs.get("direct_holding_threshold_met")
    return threshold_met == "yes" and direct_holding != "yes"


def select_branch_candidate_by_rate(
    branch_candidates: list[dict], rate: str
) -> dict | None:
    for candidate in branch_candidates:
        if candidate.get("rate") == rate:
            return candidate
    return None


def build_dividend_fact_completion() -> dict:
    return {
        "flow_type": "bounded_form",
        "session_type": "pseudo_multiturn",
        "user_declaration_note": "Facts entered here are user-declared and not independently verified.",
        "facts": [
            {
                "fact_key": "direct_holding_confirmed",
                "prompt": "Does the Dutch recipient directly hold capital in the Chinese payer?",
                "input_type": "single_select",
                "options": ["yes", "no", "unknown"],
            },
            {
                "fact_key": "direct_holding_threshold_met",
                "prompt": "If the holding is direct, is the direct holding at least 25%?",
                "input_type": "single_select",
                "options": ["yes", "no", "unknown"],
            },
            {
                "fact_key": "pe_effectively_connected",
                "prompt": "Is the dividend effectively connected with a permanent establishment or fixed base of the Dutch recipient in China?",
                "input_type": "single_select",
                "options": ["yes", "no", "unknown"],
            },
            {
                "fact_key": "beneficial_owner_confirmed",
                "prompt": "Has beneficial-owner status been separately confirmed outside this tool?",
                "input_type": "single_select",
                "options": ["yes", "no", "unknown"],
            },
        ],
    }


def build_stage4_change_summary(
    *,
    from_state_label: str,
    to_state_label: str,
    from_rate: str,
    to_rate: str,
    fact_inputs: dict,
) -> dict:
    return {
        "summary_label": "Result Change Summary",
        "state_change": f"{from_state_label} -> {to_state_label}",
        "rate_change": f"{from_rate} -> {to_rate}",
        "trigger_facts": [
            f"{FACT_VALUE_LABELS[key]}: {value}"
            for key, value in fact_inputs.items()
        ],
    }

