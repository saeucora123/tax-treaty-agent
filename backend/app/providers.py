from __future__ import annotations

from pathlib import Path

from app.constants import (
    PAIR_LABELS_EN,
    REPO_ROOT,
    SUPPORTED_SCOPE_EXAMPLES_BY_PAIR,
    TREATY_DISPLAY_NAMES_ZH,
)


STABLE_TREATY_REGISTRY = {
    ("CN", "NL"): REPO_ROOT / "data" / "treaties" / "cn-nl.v3.json",
    ("CN", "SG"): REPO_ROOT / "data" / "treaties" / "cn-sg.v3.json",
}
LLM_GENERATED_TREATY_REGISTRY = {
    ("CN", "NL"): REPO_ROOT / "data" / "treaties" / "cn-nl.v3.generated.from-llm.json",
}
DATA_PATH = STABLE_TREATY_REGISTRY[("CN", "NL")]
LLM_GENERATED_DATA_PATH = LLM_GENERATED_TREATY_REGISTRY[("CN", "NL")]


def normalize_data_source(data_source: str) -> str:
    if data_source == "llm_generated":
        return "llm_generated"
    return "stable"


def canonical_country_pair(*countries: str) -> tuple[str, str]:
    return tuple(sorted(countries))


def get_supported_scope_examples() -> list[str]:
    examples: list[str] = []
    for pair in sorted(STABLE_TREATY_REGISTRY):
        examples.extend(SUPPORTED_SCOPE_EXAMPLES_BY_PAIR.get(pair, []))
    return examples


def is_supported_stable_pair(pair: tuple[str, str] | None) -> bool:
    return pair in STABLE_TREATY_REGISTRY


def get_treaty_registry(data_source: str) -> dict[tuple[str, str], Path]:
    if data_source == "llm_generated":
        registry = dict(LLM_GENERATED_TREATY_REGISTRY)
        registry[("CN", "NL")] = LLM_GENERATED_DATA_PATH
        return registry
    registry = dict(STABLE_TREATY_REGISTRY)
    registry[("CN", "NL")] = DATA_PATH
    return registry


def is_pair_available_in_data_source(
    pair: tuple[str, str] | None,
    data_source: str,
) -> bool:
    if pair is None:
        return False
    return pair in get_treaty_registry(data_source)


def get_supported_pair_labels_en() -> list[str]:
    return [PAIR_LABELS_EN[pair] for pair in sorted(STABLE_TREATY_REGISTRY)]


def build_supported_pair_list_text() -> str:
    return ", ".join(get_supported_pair_labels_en())


def build_treaty_display_name(payer_country: str, payee_country: str) -> str:
    return TREATY_DISPLAY_NAMES_ZH.get(
        canonical_country_pair(payer_country, payee_country),
        f"{payer_country}-{payee_country} tax treaty",
    )


def resolve_data_path(data_source: str, country_pair: tuple[str, str]) -> Path:
    registry = get_treaty_registry(data_source)
    if country_pair not in registry:
        raise FileNotFoundError(country_pair)
    return registry[country_pair]
