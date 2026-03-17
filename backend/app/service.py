from __future__ import annotations

import json
import warnings
from pathlib import Path

from app.constants import (
    AUTO_CONCLUSION_CONFIDENCE_THRESHOLD,
    BOUNDARY_NOTE,
    COUNTRY_FOOTPRINTS,
    FACT_VALUE_LABELS,
    HANDOFF_NOTE,
    HANDOFF_RECOMMENDED_ROUTE_BY_STATE,
    KEY_MISSING_FACTS,
    NORMAL_CONFIDENCE_THRESHOLD,
    PAIR_LABELS_EN,
    REVIEW_CHECKLISTS,
    SCHEMA_VERSION,
    STATE_LABELS_ZH,
    SUPPORTED_SCOPE_EXAMPLES_BY_PAIR,
    TREATY_DISPLAY_NAMES_ZH,
    TRANSACTION_KEYWORDS,
    TRANSACTION_LABELS_ZH,
)
from app.guided_facts import (
    BACKEND_GUIDED_FACT_CONFIG,
    DIVIDEND_DEPRECATED_BRIDGE_FACT_KEYS,
    DIVIDEND_FACT_KEYS,
    DIVIDEND_RAW_FACT_KEYS,
)
from app.llm_input_parser import LLMInputParserError, parse_scenario_to_json
from app.providers import (
    DATA_PATH,
    LLM_GENERATED_DATA_PATH,
    LLM_GENERATED_TREATY_REGISTRY,
    STABLE_TREATY_REGISTRY,
    build_supported_pair_list_text,
    build_treaty_display_name,
    canonical_country_pair,
    get_supported_scope_examples,
    get_treaty_registry,
    is_pair_available_in_data_source,
    is_supported_stable_pair,
    normalize_data_source,
    resolve_data_path,
)


def _normalize_guided_fact_value(value: object) -> str | None:
    if not isinstance(value, str):
        return None
    normalized = value.strip()
    return normalized or None


def calculate_threshold_met(percentage_str: str) -> bool | None:
    if percentage_str == "unknown":
        return None
    try:
        return float(percentage_str) >= 25.0
    except (TypeError, ValueError):
        return None


def calculate_holding_period_signal(months_str: str | None) -> bool:
    if months_str in {None, "", "unknown"}:
        return True
    try:
        return int(months_str) < 12
    except (TypeError, ValueError):
        return True


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
    response["schema_version"] = SCHEMA_VERSION
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
    bo_precheck = response.get("bo_precheck")
    guided_conflict = response.get("guided_conflict")

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

    machine_handoff = {
        "schema_version": SCHEMA_VERSION,
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
        "bo_precheck": bo_precheck,
        "guided_conflict": guided_conflict,
    }
    if supported and is_cn_nl_dividend_response(response):
        machine_handoff["determining_condition_priority"] = determine_dividend_condition_priority(response)
        machine_handoff["mli_ppt_review_required"] = build_dividend_mli_ppt_review_required(
            response.get("user_declared_facts") or {}
        )
        machine_handoff["short_holding_period_review_required"] = (
            build_dividend_short_holding_period_review_required(response)
        )
        machine_handoff["payment_date_unconfirmed"] = build_dividend_payment_date_unconfirmed(
            response
        )
        machine_handoff["calculated_threshold_met"] = build_dividend_calculated_threshold_met(
            response
        )
        source_reference = build_dividend_handoff_source_reference(
            response,
            machine_handoff["determining_condition_priority"],
        )
        if source_reference is not None:
            machine_handoff["source_reference"] = source_reference
    return machine_handoff


def is_cn_nl_dividend_response(response: dict) -> bool:
    normalized_input = response.get("normalized_input") or {}
    return (
        response.get("supported") is True
        and normalized_input.get("payer_country") == "CN"
        and normalized_input.get("payee_country") == "NL"
        and normalized_input.get("transaction_type") == "dividends"
    )


def build_dividend_handoff_source_reference(
    response: dict,
    determining_condition_priority: int | None,
) -> str | None:
    if determining_condition_priority == 1:
        return "Art. 10(4)"
    if determining_condition_priority in {4, 6, 8, 10}:
        return "Art. 10(2)(b)"
    if determining_condition_priority == 12:
        return "Art. 10(2)(a)"
    return (response.get("result") or {}).get("source_reference")


def build_dividend_mli_ppt_review_required(user_declared_facts: dict) -> bool:
    for fact in user_declared_facts.get("facts", []):
        if fact.get("fact_key") == "mli_ppt_risk_flag":
            return fact.get("value") != "yes"
    return True


def build_dividend_short_holding_period_review_required(response: dict) -> bool:
    facts = extract_user_declared_facts_map(response)
    return calculate_holding_period_signal(facts.get("holding_period_months"))


def build_dividend_payment_date_unconfirmed(response: dict) -> bool:
    facts = extract_user_declared_facts_map(response)
    percentage = facts.get("direct_holding_percentage")
    if calculate_threshold_met(percentage) is None and percentage != "unknown":
        return False
    if percentage in {None, "unknown"}:
        return False
    return facts.get("payment_date") in {None, "", "unknown"}


def build_dividend_calculated_threshold_met(response: dict) -> bool | None:
    facts = extract_user_declared_facts_map(response)
    percentage = facts.get("direct_holding_percentage")
    if percentage in {None, ""}:
        return None
    return calculate_threshold_met(percentage)


def determine_dividend_condition_priority(response: dict) -> int | None:
    fact_completion_status = (response.get("fact_completion_status") or {}).get("status_code")
    facts = extract_user_declared_facts_map(response)
    calculated_threshold_met = calculate_threshold_met(facts.get("direct_holding_percentage"))
    percentage_present = "direct_holding_percentage" in facts
    percentage_unknown = facts.get("direct_holding_percentage") == "unknown"

    if response.get("guided_conflict") is not None or fact_completion_status == "terminated_conflicting_user_facts":
        return 13
    if fact_completion_status == "terminated_pe_exclusion":
        return 1
    if fact_completion_status == "terminated_beneficial_owner_unconfirmed":
        return 2
    if fact_completion_status == "terminated_unknown_facts":
        if facts.get("beneficial_owner_confirmed") == "unknown":
            return 3
        if percentage_unknown:
            return 5
        if not percentage_present and facts.get("direct_holding_confirmed") == "unknown":
            return 7
        if not percentage_present and facts.get("direct_holding_threshold_met") == "unknown":
            return 9
        if facts.get("holding_structure_is_direct") == "unknown":
            return 11
        return None
    if fact_completion_status != "completed_narrowed":
        return None
    if (response.get("result") or {}).get("rate") == "5%":
        if calculated_threshold_met is True:
            return 12
        return 12 if _resolve_deprecated_bridge_dividend_branch(facts, emit_warning=False) == "5%" else None
    if calculated_threshold_met is False:
        return 4
    if not percentage_present and facts.get("direct_holding_confirmed") == "no":
        return 6
    if not percentage_present and facts.get("direct_holding_threshold_met") == "no":
        return 8
    if facts.get("holding_structure_is_direct") == "no":
        return 10
    return None


def extract_user_declared_facts_map(response: dict) -> dict[str, str]:
    facts: dict[str, str] = {}
    for fact in (response.get("user_declared_facts") or {}).get("facts", []):
        fact_key = fact.get("fact_key")
        value = fact.get("value")
        if fact_key and isinstance(value, str):
            facts[fact_key] = value
    return facts


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
    if machine_handoff.get("bo_precheck"):
        lines.append(machine_handoff["bo_precheck"]["reason_summary"])
    if machine_handoff.get("guided_conflict"):
        lines.append(machine_handoff["guided_conflict"]["reason_summary"])
    return lines


def build_handoff_facts_to_verify(response: dict, machine_handoff: dict) -> list[str]:
    facts_to_verify = list(machine_handoff["blocking_facts"])
    if machine_handoff["user_declared_facts"]:
        facts_to_verify.insert(
            0,
            "Verify the user-declared facts before relying on the narrowed treaty result.",
        )
    if machine_handoff.get("bo_precheck"):
        facts_to_verify.append(machine_handoff["bo_precheck"]["review_note"])
    if machine_handoff.get("guided_conflict"):
        facts_to_verify.extend(machine_handoff["guided_conflict"]["conflicting_claims"])
    if not facts_to_verify and response.get("supported"):
        facts_to_verify.extend(response.get("result", {}).get("review_checklist", []))
    return facts_to_verify


def resolve_input_mode(
    input_mode: str | None,
    *,
    scenario: str | None,
    guided_input: dict | None,
) -> str:
    if input_mode == "guided":
        return "guided"
    if input_mode == "free_text":
        return "free_text"
    if guided_input:
        return "guided"
    if scenario:
        return "free_text"
    return "free_text"


def build_guided_payload(guided_input: dict | None) -> dict:
    payload = dict(guided_input or {})
    facts = {}
    for key, value in dict(payload.get("facts") or {}).items():
        normalized = _normalize_guided_fact_value(value)
        if normalized is not None:
            facts[key] = normalized
    payload["facts"] = facts
    return payload


def normalize_guided_input(guided_input: dict) -> dict:
    payer_country = guided_input.get("payer_country")
    payee_country = guided_input.get("payee_country")
    transaction_type = guided_input.get("income_type") or "unknown"
    country_pair = None
    reason = "ok"
    if payer_country and payee_country:
        country_pair = (payer_country, payee_country)
    else:
        reason = "incomplete_scenario"
    if transaction_type == "unknown":
        reason = "incomplete_scenario"
    return {
        "country_pair": country_pair,
        "payer_country": payer_country,
        "payee_country": payee_country,
        "transaction_type": transaction_type,
        "matched_transaction_label": None,
        "parser_source": "guided",
        "reason": reason,
    }


def filter_guided_facts_for_income_type(facts: dict, income_type: str) -> dict:
    allowed = BACKEND_GUIDED_FACT_CONFIG.get(income_type, [])
    filtered: dict[str, str] = {}
    for key, value in facts.items():
        if key not in allowed:
            continue
        if income_type != "dividends":
            if value in {"yes", "no", "unknown"}:
                filtered[key] = value
            continue
        if key in DIVIDEND_RAW_FACT_KEYS:
            filtered[key] = value
            continue
        if value in {"yes", "no", "unknown"}:
            filtered[key] = value
    return filtered


def build_bo_precheck(input_mode_used: str, normalized: dict, guided_facts: dict) -> dict | None:
    income_type = normalized.get("transaction_type")
    if income_type not in {"dividends", "interest", "royalties"}:
        return None

    bo_fact_key = "beneficial_owner_confirmed" if income_type == "dividends" else "beneficial_owner_status"
    is_cn_nl_dividend = (
        income_type == "dividends"
        and normalized.get("payer_country") == "CN"
        and normalized.get("payee_country") == "NL"
    )

    def build_facts_considered() -> list[dict]:
        if is_cn_nl_dividend:
            return [
                {
                    "fact_key": "beneficial_owner_confirmed",
                    "value": guided_facts.get("beneficial_owner_confirmed", "unknown"),
                },
                {
                    "fact_key": "holding_structure_is_direct",
                    "value": guided_facts.get("holding_structure_is_direct", "unknown"),
                },
            ]
        if bo_fact_key not in guided_facts:
            return []
        return [{"fact_key": bo_fact_key, "value": guided_facts[bo_fact_key]}]

    facts_considered = build_facts_considered()
    if bo_fact_key not in guided_facts:
        return {
            "status": "insufficient_facts",
            "reason_code": "legacy_free_text_missing_bo_fact"
            if input_mode_used == "free_text"
            else "beneficial_owner_unknown",
            "reason_summary": (
                "The current free-text path does not provide a structured BO fact, so the system cannot emit a stronger BO workflow signal."
                if input_mode_used == "free_text"
                else "The guided BO fact is still unknown."
            ),
            "facts_considered": facts_considered,
            "review_note": "Confirm BO evidence before relying on treaty benefits.",
        }

    value = guided_facts[bo_fact_key]
    if (
        is_cn_nl_dividend
        and value == "yes"
        and guided_facts.get("holding_structure_is_direct") == "no"
        and (
            guided_facts.get("direct_holding_threshold_met") == "yes"
            or calculate_threshold_met(guided_facts.get("direct_holding_percentage")) is True
        )
    ):
        return {
            "status": "flagged_for_review",
            "reason_code": "indirect_structure_requires_bo_review",
            "reason_summary": "The dividend facts indicate an intermediate holding structure despite a claimed threshold path, so BO-focused manual review is required.",
            "facts_considered": facts_considered,
            "review_note": "Review the intermediate holding structure and BO support before relying on treaty benefits.",
        }
    if value == "yes":
        return {
            "status": "no_initial_flag",
            "reason_code": "beneficial_owner_confirmed",
            "reason_summary": "The guided beneficial-owner fact is marked confirmed, so the system does not raise an initial BO workflow flag.",
            "facts_considered": facts_considered,
            "review_note": "Beneficial-owner status still requires human verification outside this tool.",
        }
    if value == "no":
        return {
            "status": "flagged_for_review",
            "reason_code": "beneficial_owner_not_confirmed",
            "reason_summary": "The guided beneficial-owner fact is marked unconfirmed, so the case should be escalated for BO-focused manual review.",
            "facts_considered": facts_considered,
            "review_note": "Do not rely on treaty benefits until BO support has been reviewed manually.",
        }
    return {
        "status": "insufficient_facts",
        "reason_code": "beneficial_owner_unknown",
        "reason_summary": "The guided BO fact is still unknown.",
        "facts_considered": facts_considered,
        "review_note": "Confirm BO evidence before relying on treaty benefits.",
    }


def text_claims_reduced_dividend_branch(text: str) -> bool:
    lowered = text.lower()
    markers = ["25%", "直接持股", "协定优惠", "优惠税率", "5%", "reduced rate", "treaty benefit"]
    return any(marker in text or marker in lowered for marker in markers)


def detect_guided_conflict(guided_payload: dict, normalized: dict) -> dict | None:
    scenario_text = (guided_payload.get("scenario_text") or "").strip()
    if not scenario_text:
        return None

    conflicting_claims: list[str] = []
    supplemental_normalized = normalize_input(scenario_text)
    for field in ("payer_country", "payee_country", "transaction_type"):
        guided_value = normalized.get(field)
        supplemental_value = supplemental_normalized.get(field)
        if guided_value and supplemental_value and guided_value != supplemental_value:
            conflicting_claims.append(
                f"scenario_text maps {field} to {supplemental_value}, but the structured facts fix it as {guided_value}"
            )

    guided_facts = guided_payload.get("facts") or {}
    if normalized.get("transaction_type") == "dividends":
        reduced_branch_supported = (
            guided_facts.get("direct_holding_confirmed") == "yes"
            and guided_facts.get("direct_holding_threshold_met") == "yes"
            and guided_facts.get("holding_structure_is_direct") == "yes"
        )
        if text_claims_reduced_dividend_branch(scenario_text) and not reduced_branch_supported:
            conflicting_claims.append(
                "scenario_text claims the reduced dividend branch can be used, but the structured facts do not support that branch"
            )

    if not conflicting_claims:
        return None

    return {
        "status": "conflict_detected",
        "reason_code": "supplemental_text_conflicts_with_structured_facts",
        "reason_summary": "Supplemental scenario text conflicts with the structured guided facts, so the system preserved the structured facts and escalated for manual review.",
        "structured_facts_win": True,
        "conflicting_claims": conflicting_claims,
    }


def apply_guided_conflict_override(response: dict) -> None:
    if not response.get("supported") or not response.get("guided_conflict"):
        return
    response["review_state"] = {
        "state_code": "needs_human_intervention",
        "state_label_zh": STATE_LABELS_ZH["needs_human_intervention"],
        "state_summary": build_supported_state_summary("needs_human_intervention"),
    }
    conflict_action = {
        "priority": "high",
        "action": "停止依赖当前补充文本的自动推进，并以结构化事实为准转入人工复核。",
        "reason": "补充文本与结构化 guided facts 存在冲突；系统已保留结构化事实并拒绝自动调和两者。",
    }
    existing_actions = list(response.get("next_actions", []))
    if conflict_action not in existing_actions:
        response["next_actions"] = [conflict_action, *existing_actions]


def analyze_scenario(
    scenario: str | None,
    data_source: str = "stable",
    input_mode: str | None = None,
    guided_input: dict | None = None,
) -> dict:
    resolved_data_source = normalize_data_source(data_source)
    input_mode_used = resolve_input_mode(
        input_mode,
        scenario=scenario,
        guided_input=guided_input,
    )
    guided_payload = build_guided_payload(guided_input)
    if input_mode_used == "guided":
        normalized = normalize_guided_input(guided_payload)
        input_interpretation = None
    else:
        normalized = normalize_input(scenario or "")
        input_interpretation = build_input_interpretation(normalized)
    structured_guided_facts = filter_guided_facts_for_income_type(
        guided_payload.get("facts") or {},
        normalized.get("transaction_type", "unknown"),
    )
    if normalized["reason"] == "incomplete_scenario":
        response = {
            "input_mode_used": input_mode_used,
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
            "input_mode_used": input_mode_used,
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
        response["input_mode_used"] = input_mode_used
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
        response["input_mode_used"] = input_mode_used
        if input_interpretation is not None:
            response["input_interpretation"] = input_interpretation
        return finalize_response(response)

    if match is None:
        response = {
            "input_mode_used": input_mode_used,
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
        guided_facts=structured_guided_facts,
    )
    shaped_result = shape_result(match)
    response = {
        "input_mode_used": input_mode_used,
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
    if "user_declared_facts" not in response and structured_guided_facts:
        response["user_declared_facts"] = build_user_declared_facts(structured_guided_facts)
    response["bo_precheck"] = build_bo_precheck(
        input_mode_used,
        normalized,
        structured_guided_facts,
    )
    if input_mode_used == "guided":
        guided_conflict = detect_guided_conflict(guided_payload, normalized)
        if guided_conflict is not None:
            response["guided_conflict"] = guided_conflict
            apply_guided_conflict_override(response)
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
    guided_facts: dict,
) -> tuple[dict, dict]:
    payload = build_empty_stage4_payload()
    if not is_stage4_dividend_target(entry, normalized):
        return entry, payload

    payload["stage4_active"] = True
    declared_facts = normalize_stage4_guided_facts(guided_facts)
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
            declared_facts=declared_facts,
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
            from_rate=resolve_dividend_branch_without_bo_gate(declared_facts) or "5% / 10%",
            to_rate="treaty rate cannot be relied on yet",
            declared_facts=declared_facts,
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

    if declared_facts.get("beneficial_owner_confirmed") == "unknown":
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
            declared_facts=declared_facts,
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
            declared_facts=declared_facts,
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
            declared_facts=declared_facts,
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
        declared_facts=declared_facts,
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


def normalize_stage4_guided_facts(guided_facts: dict) -> dict:
    normalized = {}
    for key in DIVIDEND_FACT_KEYS:
        value = guided_facts.get(key)
        if key in DIVIDEND_RAW_FACT_KEYS:
            normalized_value = _normalize_guided_fact_value(value)
            if normalized_value is not None:
                normalized[key] = normalized_value
            continue
        if value in {"yes", "no", "unknown"}:
            normalized[key] = value
    return normalized


def build_user_declared_facts(declared_facts: dict) -> dict:
    facts = []
    for key, value in declared_facts.items():
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


def resolve_dividend_branch_from_facts(declared_facts: dict) -> str | None:
    percentage = declared_facts.get("direct_holding_percentage")
    calculated_threshold_met = calculate_threshold_met(percentage)
    holding_structure_is_direct = declared_facts.get("holding_structure_is_direct")
    if calculated_threshold_met is False:
        return "10%"
    if percentage == "unknown":
        return None
    if percentage is None and any(
        key in declared_facts for key in DIVIDEND_DEPRECATED_BRIDGE_FACT_KEYS
    ):
        bridge_branch = resolve_deprecated_bridge_dividend_branch(declared_facts)
        if bridge_branch is not None:
            return bridge_branch
    if holding_structure_is_direct == "no":
        return "10%"
    if holding_structure_is_direct == "unknown":
        return None
    if (
        calculated_threshold_met is True
        and holding_structure_is_direct == "yes"
        and declared_facts.get("beneficial_owner_confirmed") == "yes"
    ):
        return "5%"
    return None


def _resolve_deprecated_bridge_dividend_branch(
    declared_facts: dict,
    *,
    emit_warning: bool,
) -> str | None:
    if emit_warning:
        warnings.warn(
            "Deprecated dividend bridge facts were used without direct_holding_percentage.",
            DeprecationWarning,
            stacklevel=2,
        )
    direct_holding = declared_facts.get("direct_holding_confirmed")
    threshold_met = declared_facts.get("direct_holding_threshold_met")
    if direct_holding == "no":
        return "10%"
    if direct_holding == "unknown":
        return None
    if threshold_met == "no":
        return "10%"
    if threshold_met == "unknown":
        return None
    if (
        direct_holding == "yes"
        and threshold_met == "yes"
        and declared_facts.get("holding_structure_is_direct") == "yes"
        and declared_facts.get("beneficial_owner_confirmed") == "yes"
    ):
        return "5%"
    return None


def resolve_deprecated_bridge_dividend_branch(declared_facts: dict) -> str | None:
    """Use @deprecated threshold-level dividend fields when raw facts are absent."""
    return _resolve_deprecated_bridge_dividend_branch(
        declared_facts,
        emit_warning=True,
    )


def resolve_dividend_branch_without_bo_gate(declared_facts: dict) -> str | None:
    percentage = declared_facts.get("direct_holding_percentage")
    calculated_threshold_met = calculate_threshold_met(percentage)
    holding_structure_is_direct = declared_facts.get("holding_structure_is_direct")
    if calculated_threshold_met is False:
        return "10%"
    if percentage == "unknown":
        return None
    if percentage is None and any(
        key in declared_facts for key in DIVIDEND_DEPRECATED_BRIDGE_FACT_KEYS
    ):
        direct_holding = declared_facts.get("direct_holding_confirmed")
        threshold_met = declared_facts.get("direct_holding_threshold_met")
        if direct_holding == "no":
            return "10%"
        if direct_holding != "yes":
            return None
        if threshold_met == "no":
            return "10%"
        if threshold_met != "yes":
            return None
    if holding_structure_is_direct == "no":
        return "10%"
    if holding_structure_is_direct != "yes":
        return None
    return "5%"


def has_conflicting_dividend_facts(declared_facts: dict) -> bool:
    if "direct_holding_percentage" in declared_facts:
        return False
    direct_holding = declared_facts.get("direct_holding_confirmed")
    threshold_met = declared_facts.get("direct_holding_threshold_met")
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
                "fact_key": "direct_holding_percentage",
                "prompt": "What is the recipient's direct shareholding percentage in the paying company as of the payment date?",
                "input_type": "text",
            },
            {
                "fact_key": "payment_date",
                "prompt": "What is the dividend payment date (or declared payment date)?",
                "input_type": "text",
            },
            {
                "fact_key": "holding_period_months",
                "prompt": "How many months has the recipient continuously held the shares as of the payment date?",
                "input_type": "text",
            },
            {
                "fact_key": "beneficial_owner_confirmed",
                "prompt": "Has beneficial-owner status been separately confirmed outside this tool?",
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
                "fact_key": "holding_structure_is_direct",
                "prompt": "Is the holding structure confirmed to be direct with no intermediate holding entity between the recipient and the paying company?",
                "input_type": "single_select",
                "options": ["yes", "no", "unknown"],
            },
            {
                "fact_key": "mli_ppt_risk_flag",
                "prompt": "Has a principal purpose test (PPT) risk assessment been performed for this dividend payment under the MLI?",
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
    declared_facts: dict,
) -> dict:
    return {
        "summary_label": "Result Change Summary",
        "state_change": f"{from_state_label} -> {to_state_label}",
        "rate_change": f"{from_rate} -> {to_rate}",
        "trigger_facts": [
            f"{FACT_VALUE_LABELS[key]}: {value}"
            for key, value in declared_facts.items()
        ],
    }

