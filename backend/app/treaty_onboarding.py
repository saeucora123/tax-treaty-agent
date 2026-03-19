from __future__ import annotations

import importlib.util
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib import error, request

from app.llm_document_extractor import (
    assign_branch_hints_to_rules,
    infer_enumerated_rate_branches,
    infer_rate_from_text,
    is_rate_limit_rule_type,
    normalize_conditions,
    normalize_confidence,
    normalize_direction,
    normalize_income_type,
    normalize_optional_text,
    normalize_rate,
    normalize_review_reason,
)
from app.llm_input_parser import LLMInputParserConfig, extract_json_content, load_config_from_env


REPO_ROOT = Path(__file__).resolve().parents[2]
BUILDER_SCRIPT_PATH = REPO_ROOT / "scripts" / "build_treaty_dataset.py"
DEFAULT_TIMEOUT_SECONDS = 30
COMPILER_MIN_TIMEOUT_SECONDS = 180
ALLOWED_DELTA_TYPES = {
    "rate_changed",
    "condition_changed",
    "branch_added",
    "branch_removed",
    "scope_note",
}
ALLOWED_MATERIALITY = {"high", "medium", "low"}
DELTA_TYPE_ALIASES = {
    "alignment": "scope_note",
    "no_difference": "scope_note",
    "rate_deviation": "rate_changed",
    "rate_difference": "rate_changed",
    "rate_alignment": "scope_note",
    "rate_match": "scope_note",
    "condition_deviation": "condition_changed",
    "condition_difference": "condition_changed",
    "branch_addition": "branch_added",
    "branch_append": "branch_added",
    "additional_provision": "branch_added",
    "branch_deletion": "branch_removed",
    "branch_removal": "branch_removed",
    "scope_deviation": "scope_note",
    "scope_difference": "scope_note",
    "structural_difference": "scope_note",
    "taxation_rights_difference": "scope_note",
}
MATERIALITY_ALIASES = {
    "none": "low",
    "minimal": "low",
    "minor": "low",
    "moderate": "medium",
    "major": "high",
    "critical": "high",
}
CANONICAL_LIST_SORT_KEYS = (
    "segment_id",
    "rule_id",
    "paragraph_id",
    "article_number",
    "source_reference",
    "document_id",
    "source_id",
)


class TreatyOnboardingError(RuntimeError):
    pass


class ManifestValidationError(TreatyOnboardingError):
    pass


class ReviewGateError(TreatyOnboardingError):
    pass


class PromotionGateError(TreatyOnboardingError):
    pass


_BUILDER_MODULE: Any | None = None


def load_builder_module() -> Any:
    global _BUILDER_MODULE
    if _BUILDER_MODULE is not None:
        return _BUILDER_MODULE

    spec = importlib.util.spec_from_file_location("build_treaty_dataset_script", BUILDER_SCRIPT_PATH)
    if spec is None or spec.loader is None:
        raise TreatyOnboardingError("Unable to load build_treaty_dataset.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    _BUILDER_MODULE = module
    return module


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def load_manifest(manifest_path: Path | str) -> dict[str, Any]:
    manifest_file = Path(manifest_path).resolve()
    payload = read_json(manifest_file)
    required_keys = {
        "pair_id",
        "mode",
        "jurisdictions",
        "target_articles",
        "source_documents",
        "promotion_target_dataset",
        "work_dir",
        "treaty_metadata",
    }
    missing = sorted(required_keys - set(payload))
    if missing:
        raise ManifestValidationError(f"Manifest is missing required keys: {', '.join(missing)}")

    if payload["mode"] not in {"shadow_rebuild", "initial_onboarding"}:
        raise ManifestValidationError("Manifest mode must be shadow_rebuild or initial_onboarding.")
    if not isinstance(payload["pair_id"], str) or not payload["pair_id"].strip():
        raise ManifestValidationError("Manifest pair_id must be a non-empty string.")
    if not isinstance(payload["jurisdictions"], list) or len(payload["jurisdictions"]) != 2:
        raise ManifestValidationError("Manifest jurisdictions must contain exactly two country codes.")
    if not isinstance(payload["target_articles"], list) or not payload["target_articles"]:
        raise ManifestValidationError("Manifest target_articles must be a non-empty list.")
    if not isinstance(payload["source_documents"], list) or len(payload["source_documents"]) != 1:
        raise ManifestValidationError("Manifest source_documents must contain exactly one structured source document path.")

    treaty_metadata = payload["treaty_metadata"]
    required_treaty_metadata = {"version", "source_type", "notes", "source_trace", "mli_context"}
    missing_treaty_metadata = sorted(required_treaty_metadata - set(treaty_metadata))
    if missing_treaty_metadata:
        raise ManifestValidationError(
            "Manifest treaty_metadata is missing required keys: "
            + ", ".join(missing_treaty_metadata)
        )

    source_document_path = resolve_manifest_path(manifest_file.parent, payload["source_documents"][0])
    if not source_document_path.exists():
        raise ManifestValidationError(f"Structured source document does not exist: {source_document_path}")

    stable_reference_dataset_raw = payload.get("stable_reference_dataset")
    stable_reference_dataset = None
    if payload["mode"] == "shadow_rebuild":
        if stable_reference_dataset_raw is None:
            raise ManifestValidationError("shadow_rebuild manifest requires stable_reference_dataset.")
        stable_reference_dataset = resolve_manifest_path(
            manifest_file.parent,
            stable_reference_dataset_raw,
        )
    promotion_target_dataset = resolve_manifest_path(
        manifest_file.parent,
        payload["promotion_target_dataset"],
    )
    work_dir = resolve_manifest_path(manifest_file.parent, payload["work_dir"])
    baseline_reference = payload.get("baseline_reference")
    if baseline_reference is not None:
        baseline_reference = resolve_manifest_path(manifest_file.parent, baseline_reference)
        if not baseline_reference.exists():
            raise ManifestValidationError(f"Baseline reference does not exist: {baseline_reference}")

    return {
        **payload,
        "manifest_path": str(manifest_file),
        "source_documents": [str(source_document_path)],
        "stable_reference_dataset": str(stable_reference_dataset) if stable_reference_dataset is not None else None,
        "promotion_target_dataset": str(promotion_target_dataset),
        "work_dir": str(work_dir),
        "baseline_reference": str(baseline_reference) if baseline_reference is not None else None,
    }


def resolve_manifest_path(base_dir: Path, raw_path: str) -> Path:
    path = Path(raw_path)
    if not path.is_absolute():
        path = (base_dir / path).resolve()
    return path


def extract_compilation_units(source_payload: dict[str, Any], target_articles: list[str]) -> list[dict[str, Any]]:
    target_article_set = {str(article).strip() for article in target_articles}
    units: list[dict[str, Any]] = []
    for article in source_payload.get("parsed_articles", []):
        article_number = str(article.get("article_number", "")).strip()
        if article_number not in target_article_set:
            continue
        paragraphs: list[dict[str, Any]] = []
        for paragraph in article.get("paragraphs", []):
            paragraphs.append(
                {
                    "paragraph_number": extract_paragraph_number(paragraph),
                    "source_reference": paragraph.get("source_reference"),
                    "text": build_paragraph_text(paragraph),
                }
            )
        units.append(
            {
                "article_number": article_number,
                "article_title": article.get("article_title"),
                "income_type": article.get("income_type"),
                "paragraphs": paragraphs,
            }
        )
    return units


def extract_paragraph_number(paragraph: dict[str, Any]) -> str:
    if isinstance(paragraph.get("paragraph_id"), str) and "-p" in paragraph["paragraph_id"]:
        return paragraph["paragraph_id"].split("-p", 1)[1]
    if isinstance(paragraph.get("paragraph_label"), str) and "(" in paragraph["paragraph_label"]:
        return paragraph["paragraph_label"].split("(", 1)[1].rstrip(")")
    return "unknown"


def build_paragraph_text(paragraph: dict[str, Any]) -> str:
    source_segments = paragraph.get("source_segments")
    if isinstance(source_segments, list) and source_segments:
        parts = [
            normalize_optional_text(segment.get("text"))
            for segment in source_segments
            if normalize_optional_text(segment.get("text"))
        ]
        if parts:
            return " ".join(parts)
    return normalize_optional_text(paragraph.get("source_excerpt"))


def build_compiler_request_payload(
    compilation_units: list[dict[str, Any]],
    model: str,
    baseline_reference: dict[str, Any] | None = None,
) -> dict[str, Any]:
    system_prompt = (
        "You compile structured treaty paragraphs into paragraph-level rule candidates for an "
        "offline tax treaty onboarding pipeline. Return only JSON with a top-level key "
        "parsed_articles. Preserve the provided article_number, article_title, income_type, "
        "paragraph_number, source_reference, and text fields. For each paragraph, output rules "
        "with only: rule_type, rate, direction, conditions, review_reason, extraction_confidence. "
        "Use income_type only from dividends, interest, royalties, unknown. Use direction only "
        "from bidirectional, payer_to_payee, payee_to_payer, unknown. Keep extraction_confidence "
        "between 0 and 1. Do not invent treaty-level metadata, source identifiers, or runtime wiring. "
        "If a paragraph does not support a usable rule candidate, return an empty rules list."
    )
    user_payload: dict[str, Any] = {"parsed_articles": compilation_units}
    if baseline_reference is not None:
        system_prompt += (
            " A structured OECD baseline reference is provided. In addition to parsed_articles, return "
            "delta_analysis as a list. Each delta item must contain article_number, income_type, "
            "baseline_reference, bilateral_reference, delta_type, summary, materiality, and "
            "reviewer_attention."
        )
        user_payload["baseline_reference"] = baseline_reference
    return {
        "model": model,
        "temperature": 0,
        "response_format": {"type": "json_object"},
        "messages": [
            {"role": "system", "content": system_prompt},
            {
                "role": "user",
                "content": json.dumps(user_payload, ensure_ascii=False, indent=2),
            },
        ],
    }


def request_rule_candidates_from_llm(
    compilation_units: list[dict[str, Any]],
    config: LLMInputParserConfig | None = None,
    baseline_reference: dict[str, Any] | None = None,
) -> dict[str, Any]:
    resolved_config = config or load_config_from_env()
    if resolved_config is None:
        raise TreatyOnboardingError("DeepSeek configuration is unavailable; cannot run treaty onboarding compile.")

    payload = build_compiler_request_payload(
        compilation_units,
        resolved_config.model,
        baseline_reference=baseline_reference,
    )
    body = json.dumps(payload).encode("utf-8")
    http_request = request.Request(
        url=f"{resolved_config.base_url}/chat/completions",
        data=body,
        headers={
            "Authorization": f"Bearer {resolved_config.api_key}",
            "Content-Type": "application/json",
        },
        method="POST",
    )

    try:
        with request.urlopen(
            http_request,
            timeout=max(
                getattr(resolved_config, "timeout_seconds", DEFAULT_TIMEOUT_SECONDS),
                COMPILER_MIN_TIMEOUT_SECONDS,
            ),
        ) as response:
            response_payload = json.loads(response.read().decode("utf-8"))
    except (error.URLError, TimeoutError, json.JSONDecodeError) as exc:
        raise TreatyOnboardingError(str(exc)) from exc

    try:
        content = response_payload["choices"][0]["message"]["content"]
        model_payload = json.loads(extract_json_content(content))
    except (KeyError, IndexError, TypeError, json.JSONDecodeError) as exc:
        raise TreatyOnboardingError("Failed to parse structured JSON from treaty onboarding compiler response.") from exc

    return normalize_compiler_response(
        model_payload,
        baseline_enabled=baseline_reference is not None,
    )


def normalize_compiler_response(
    model_payload: dict[str, Any],
    *,
    baseline_enabled: bool,
) -> dict[str, Any]:
    parsed_articles = model_payload.get("parsed_articles")
    if not isinstance(parsed_articles, list):
        raise TreatyOnboardingError("Compiler response must contain parsed_articles as a list.")

    normalized_payload: dict[str, Any] = {"parsed_articles": parsed_articles}
    if not baseline_enabled:
        return normalized_payload

    delta_analysis = model_payload.get("delta_analysis")
    if not isinstance(delta_analysis, list):
        raise TreatyOnboardingError("Baseline-aware compiler response must contain delta_analysis as a list.")
    normalized_payload["delta_analysis"] = [
        normalize_delta_item(item)
        for item in delta_analysis
    ]
    return normalized_payload


def normalize_delta_item(item: dict[str, Any]) -> dict[str, Any]:
    required_keys = {
        "article_number",
        "income_type",
        "baseline_reference",
        "bilateral_reference",
        "delta_type",
        "summary",
        "materiality",
        "reviewer_attention",
    }
    if not isinstance(item, dict):
        raise TreatyOnboardingError("Each delta_analysis item must be an object.")
    missing = sorted(required_keys - set(item))
    if missing:
        raise TreatyOnboardingError(
            "Delta item is missing required keys: " + ", ".join(missing)
        )

    normalized = {
        "article_number": normalize_optional_text(item["article_number"]),
        "income_type": normalize_income_type(item["income_type"]),
        "baseline_reference": normalize_optional_text(item["baseline_reference"]),
        "bilateral_reference": normalize_optional_text(item["bilateral_reference"]),
        "delta_type": normalize_optional_text(item["delta_type"]),
        "summary": normalize_optional_text(item["summary"]),
        "materiality": canonicalize_materiality(normalize_optional_text(item["materiality"])),
        "reviewer_attention": normalize_optional_text(item["reviewer_attention"]),
    }
    normalized["delta_type"] = canonicalize_delta_type(normalized["delta_type"])
    if normalized["delta_type"] not in ALLOWED_DELTA_TYPES:
        raise TreatyOnboardingError(f"Unsupported delta_type in compiler response: {normalized['delta_type']}")
    if normalized["materiality"] not in ALLOWED_MATERIALITY:
        raise TreatyOnboardingError(f"Unsupported materiality in compiler response: {normalized['materiality']}")
    return normalized


def canonicalize_delta_type(delta_type: str) -> str:
    normalized = DELTA_TYPE_ALIASES.get(delta_type, delta_type)
    if normalized in ALLOWED_DELTA_TYPES:
        return normalized

    token_source = normalized.replace("-", "_")
    tokens = {token for token in token_source.split("_") if token}
    change_tokens = {"difference", "deviation", "changed", "change", "variation", "variance"}

    if "match" in tokens:
        return "scope_note"
    if {"rate", "condition"} <= tokens and change_tokens & tokens:
        return "scope_note"
    if "rate" in tokens and (change_tokens & tokens):
        return "rate_changed"
    if "condition" in tokens and (change_tokens & tokens):
        return "condition_changed"
    if ({"branch", "rule", "provision"} & tokens) and ({"addition", "added", "additional", "append"} & tokens):
        return "branch_added"
    if ({"branch", "rule", "provision"} & tokens) and ({"removal", "removed", "deletion", "deleted"} & tokens):
        return "branch_removed"
    if {"scope", "structural", "taxation", "rights", "approach"} & tokens:
        return "scope_note"
    return normalized


def canonicalize_materiality(materiality: str) -> str:
    normalized = MATERIALITY_ALIASES.get(materiality, materiality)
    if normalized in ALLOWED_MATERIALITY:
        return normalized
    return normalized


def load_baseline_reference(path: Path | str) -> dict[str, Any]:
    baseline_file = Path(path)
    payload = read_json(baseline_file)
    required_keys = {"baseline_id", "title", "model_version", "articles"}
    missing = sorted(required_keys - set(payload))
    if missing:
        raise TreatyOnboardingError(
            "Baseline reference is missing required keys: " + ", ".join(missing)
        )
    if not isinstance(payload["articles"], list) or not payload["articles"]:
        raise TreatyOnboardingError("Baseline reference articles must be a non-empty list.")
    return payload


def build_compiled_source(
    *,
    raw_candidates: dict[str, Any],
    source_payload: dict[str, Any],
    manifest: dict[str, Any],
) -> dict[str, Any]:
    pair_id = manifest["pair_id"]
    target_articles = {str(article).strip() for article in manifest["target_articles"]}
    raw_articles_by_number = {
        str(article.get("article_number", "")).strip(): article
        for article in raw_candidates.get("parsed_articles", [])
    }
    parsed_articles: list[dict[str, Any]] = []

    for original_article in source_payload.get("parsed_articles", []):
        article_number = str(original_article.get("article_number", "")).strip()
        if article_number not in target_articles:
            continue
        raw_article = raw_articles_by_number.get(article_number, {})
        raw_paragraphs = raw_article.get("paragraphs", [])
        parsed_articles.append(
            {
                "article_number": original_article["article_number"],
                "article_title": original_article["article_title"],
                "article_label": original_article["article_label"],
                "income_type": normalize_income_type(raw_article.get("income_type", original_article["income_type"])),
                "summary": original_article.get("summary", ""),
                "article_notes": list(original_article.get("article_notes", [])),
                "paragraphs": [
                    normalize_candidate_paragraph(
                        pair_id=pair_id,
                        article_number=article_number,
                        original_paragraph=paragraph,
                        raw_paragraph=find_matching_raw_paragraph(
                            paragraph,
                            raw_paragraphs,
                        ),
                    )
                    for paragraph in original_article.get("paragraphs", [])
                ],
            }
        )

    return {
        "document": build_compiled_document(source_payload["document"], manifest["treaty_metadata"]),
        "parsed_articles": parsed_articles,
    }


def build_compiled_document(
    original_document: dict[str, Any],
    treaty_metadata: dict[str, Any],
) -> dict[str, Any]:
    document = {
        "document_id": original_document["document_id"],
        "title": original_document["title"],
        "document_type": original_document["document_type"],
        "jurisdictions": original_document["jurisdictions"],
        "notes": ["Generated by treaty onboarding compiler draft."],
    }
    for key in ("source_trace", "mli_context"):
        if key in treaty_metadata:
            document[key] = treaty_metadata[key]
        elif key in original_document:
            document[key] = original_document[key]
    return document


def find_matching_raw_paragraph(
    original_paragraph: dict[str, Any],
    raw_paragraphs: list[dict[str, Any]],
) -> dict[str, Any]:
    original_source_reference = normalize_optional_text(original_paragraph.get("source_reference"))
    original_number = extract_paragraph_number(original_paragraph)
    for paragraph in raw_paragraphs:
        if normalize_optional_text(paragraph.get("source_reference")) == original_source_reference:
            return paragraph
    for paragraph in raw_paragraphs:
        if normalize_optional_text(str(paragraph.get("paragraph_number", ""))) == original_number:
            return paragraph
    return {}


def normalize_candidate_paragraph(
    *,
    pair_id: str,
    article_number: str,
    original_paragraph: dict[str, Any],
    raw_paragraph: dict[str, Any],
) -> dict[str, Any]:
    paragraph_number = extract_paragraph_number(original_paragraph)
    paragraph_text = normalize_optional_text(raw_paragraph.get("text")) or build_paragraph_text(original_paragraph)
    raw_rules = raw_paragraph.get("rules", []) if isinstance(raw_paragraph.get("rules"), list) else []
    branch_hints = assign_branch_hints_to_rules(raw_rules, infer_enumerated_rate_branches(paragraph_text))
    source_segments = original_paragraph.get("source_segments", [])
    segment_ids = [segment["segment_id"] for segment in source_segments if isinstance(segment, dict) and segment.get("segment_id")]

    normalized_rules: list[dict[str, Any]] = []
    inferred_rate = infer_rate_from_text(paragraph_text)
    for index, raw_rule in enumerate(raw_rules, start=1):
        rule_type = normalize_optional_text(raw_rule.get("rule_type")) or "treaty_scope_note"
        branch_hint = branch_hints[index - 1] if index - 1 < len(branch_hints) else None
        normalized_rate = normalize_rate(
            raw_rule.get("rate"),
            rule_type=rule_type,
            inferred_rate=inferred_rate,
            inferred_branch_rate=branch_hint["rate"] if branch_hint else None,
        )
        normalized_rules.append(
            {
                "rule_id": f"{pair_id}-art{article_number}-p{paragraph_number}-r{index}",
                "rule_type": rule_type,
                "rate": normalized_rate,
                "direction": normalize_direction(raw_rule.get("direction")),
                "candidate_rank": index,
                "is_primary_candidate": False,
                "extraction_confidence": normalize_confidence(raw_rule.get("extraction_confidence")),
                "derived_from_segments": segment_ids,
                "conditions": normalize_conditions(
                    raw_rule.get("conditions") if isinstance(raw_rule.get("conditions"), list) else [],
                    rule_type=rule_type,
                    paragraph_text=paragraph_text,
                    branch_hint=branch_hint,
                ),
                "human_review_required": True,
                "review_reason": normalize_review_reason(
                    normalize_optional_text(raw_rule.get("review_reason")),
                    rule_type=rule_type,
                    paragraph_text=paragraph_text,
                    rate=normalized_rate,
                    branch_hint=branch_hint,
                ),
            }
        )

    primary_index = choose_primary_rule_index(normalized_rules)
    if normalized_rules:
        normalized_rules[primary_index]["is_primary_candidate"] = True

    return {
        "paragraph_id": original_paragraph["paragraph_id"],
        "paragraph_label": original_paragraph["paragraph_label"],
        "source_reference": original_paragraph["source_reference"],
        "source_language": original_paragraph["source_language"],
        "source_segments": source_segments,
        "extracted_rules": normalized_rules,
    }


def choose_primary_rule_index(rules: list[dict[str, Any]]) -> int:
    for index, rule in enumerate(rules):
        if is_rate_limit_rule_type(rule["rule_type"]):
            return index
    return 0


def build_dataset_from_source(source_payload: dict[str, Any], manifest: dict[str, Any]) -> dict[str, Any]:
    builder = load_builder_module()
    builder.validate_source_payload(source_payload)
    dataset = builder.build_dataset(source_payload)
    dataset = align_dataset_metadata(dataset, manifest["treaty_metadata"])
    reference_dataset_raw = manifest.get("stable_reference_dataset")
    if reference_dataset_raw:
        reference_dataset_path = Path(reference_dataset_raw)
    else:
        reference_dataset_path = None
    if reference_dataset_path is not None and reference_dataset_path.exists():
        reference_dataset = read_json(reference_dataset_path)
        dataset = reconcile_reference_metadata(dataset, reference_dataset)
        dataset = project_candidate_to_reference_shape(dataset, reference_dataset)
    return dataset


def align_dataset_metadata(dataset: dict[str, Any], treaty_metadata: dict[str, Any]) -> dict[str, Any]:
    aligned = json.loads(json.dumps(dataset))
    treaty_block = aligned.setdefault("treaty", {})
    for key in ("version", "source_type", "notes", "source_trace", "mli_context"):
        if key in treaty_metadata:
            treaty_block[key] = treaty_metadata[key]
    return aligned


def reconcile_reference_metadata(candidate: dict[str, Any], reference: dict[str, Any]) -> dict[str, Any]:
    reconciled = json.loads(json.dumps(candidate))
    reference_treaty = reference.get("treaty", {})
    reconciled_treaty = reconciled.setdefault("treaty", {})
    if "notes" in reference_treaty:
        reconciled_treaty["notes"] = json.loads(json.dumps(reference_treaty["notes"]))

    reference_articles_by_number = {
        str(article.get("article_number", "")).strip(): article
        for article in reference.get("articles", [])
        if isinstance(article, dict)
    }
    for article in reconciled.get("articles", []):
        if not isinstance(article, dict):
            continue
        reference_article = reference_articles_by_number.get(str(article.get("article_number", "")).strip())
        if reference_article and "notes" in reference_article:
            article["notes"] = json.loads(json.dumps(reference_article["notes"]))
    return reconciled


def project_candidate_to_reference_shape(candidate: Any, reference: Any) -> Any:
    if isinstance(reference, dict) and isinstance(candidate, dict):
        return {
            key: project_candidate_to_reference_shape(candidate[key], reference[key])
            for key in reference
            if key in candidate
        }
    if isinstance(reference, list) and isinstance(candidate, list):
        if not reference:
            return []
        if len(reference) == len(candidate):
            return [
                project_candidate_to_reference_shape(candidate_item, reference_item)
                for candidate_item, reference_item in zip(candidate, reference)
            ]
        template = reference[0]
        return [
            project_candidate_to_reference_shape(candidate_item, template)
            for candidate_item in candidate
        ]
    return candidate


def build_compiled_report(
    *,
    raw_candidates: dict[str, Any],
    compiled_source: dict[str, Any],
) -> dict[str, Any]:
    paragraph_count = sum(
        len(article.get("paragraphs", [])) for article in compiled_source.get("parsed_articles", [])
    )
    rule_count = sum(
        len(paragraph.get("extracted_rules", []))
        for article in compiled_source.get("parsed_articles", [])
        for paragraph in article.get("paragraphs", [])
    )
    unresolved_items = collect_unresolved_items(compiled_source)
    return {
        "status": "ok",
        "article_count": len(raw_candidates.get("parsed_articles", [])),
        "paragraph_count": paragraph_count,
        "rule_count": rule_count,
        "unresolved_item_count": len(unresolved_items),
        "unresolved_items": unresolved_items,
    }


def build_compiled_delta_payload(
    delta_analysis: list[dict[str, Any]],
    baseline_reference: dict[str, Any],
    manifest: dict[str, Any],
) -> dict[str, Any]:
    return {
        "pair_id": manifest["pair_id"],
        "baseline_reference": {
            "baseline_id": baseline_reference["baseline_id"],
            "title": baseline_reference["title"],
            "model_version": baseline_reference["model_version"],
        },
        "delta_analysis": delta_analysis,
    }


def build_delta_report(delta_payload: dict[str, Any]) -> dict[str, Any]:
    materiality_counts = {level: 0 for level in sorted(ALLOWED_MATERIALITY)}
    delta_type_counts = {delta_type: 0 for delta_type in sorted(ALLOWED_DELTA_TYPES)}
    for item in delta_payload.get("delta_analysis", []):
        materiality_counts[item["materiality"]] += 1
        delta_type_counts[item["delta_type"]] += 1
    return {
        "status": "ok",
        "pair_id": delta_payload["pair_id"],
        "baseline_id": delta_payload["baseline_reference"]["baseline_id"],
        "delta_item_count": len(delta_payload.get("delta_analysis", [])),
        "high_materiality_count": materiality_counts["high"],
        "materiality_counts": materiality_counts,
        "delta_type_counts": delta_type_counts,
    }


def collect_unresolved_items(compiled_source: dict[str, Any]) -> list[dict[str, Any]]:
    unresolved: list[dict[str, Any]] = []
    for article in compiled_source.get("parsed_articles", []):
        for paragraph in article.get("paragraphs", []):
            rules = paragraph.get("extracted_rules", [])
            if not rules:
                unresolved.append(
                    {
                        "paragraph_id": paragraph["paragraph_id"],
                        "reason": "no_rule_candidates",
                    }
                )
                continue
            for rule in rules:
                if rule["rate"] == "N/A":
                    unresolved.append(
                        {
                            "paragraph_id": paragraph["paragraph_id"],
                            "rule_id": rule["rule_id"],
                            "reason": "missing_rate",
                        }
                    )
                if rule["direction"] == "unknown":
                    unresolved.append(
                        {
                            "paragraph_id": paragraph["paragraph_id"],
                            "rule_id": rule["rule_id"],
                            "reason": "unknown_direction",
                        }
                    )
                if rule["extraction_confidence"] < 0.9:
                    unresolved.append(
                        {
                            "paragraph_id": paragraph["paragraph_id"],
                            "rule_id": rule["rule_id"],
                            "reason": "low_confidence",
                            "extraction_confidence": rule["extraction_confidence"],
                        }
                    )
    return unresolved


def canonicalize_for_comparison(value: Any) -> Any:
    if isinstance(value, str):
        return " ".join(value.strip().split())
    if isinstance(value, dict):
        canonical = {
            key: canonicalize_for_comparison(item)
            for key, item in sorted(value.items(), key=lambda item: item[0])
        }
        return canonical
    if isinstance(value, list):
        normalized_items = [canonicalize_for_comparison(item) for item in value]
        if all(isinstance(item, str) for item in normalized_items):
            return sorted(normalized_items)
        if normalized_items and all(isinstance(item, dict) for item in normalized_items):
            sort_key = select_list_sort_key(normalized_items)
            if sort_key is not None:
                return sorted(normalized_items, key=lambda item: json.dumps(item.get(sort_key), ensure_ascii=False))
        return normalized_items
    return value


def select_list_sort_key(items: list[dict[str, Any]]) -> str | None:
    for candidate in CANONICAL_LIST_SORT_KEYS:
        if all(candidate in item for item in items):
            return candidate
    return None


def collect_mismatch_paths(left: Any, right: Any, path: str = "$") -> list[str]:
    mismatches: list[str] = []
    if type(left) is not type(right):
        return [path]
    if isinstance(left, dict):
        keys = sorted(set(left) | set(right))
        for key in keys:
            if key not in left or key not in right:
                mismatches.append(f"{path}.{key}")
                continue
            mismatches.extend(collect_mismatch_paths(left[key], right[key], f"{path}.{key}"))
        return mismatches
    if isinstance(left, list):
        if len(left) != len(right):
            mismatches.append(path)
            return mismatches
        for index, (left_item, right_item) in enumerate(zip(left, right)):
            mismatches.extend(collect_mismatch_paths(left_item, right_item, f"{path}[{index}]"))
        return mismatches
    if left != right:
        return [path]
    return mismatches


def run_compile(manifest_path: Path | str) -> dict[str, Any]:
    manifest = load_manifest(manifest_path)
    work_dir = Path(manifest["work_dir"])
    source_payload = read_json(Path(manifest["source_documents"][0]))
    compilation_units = extract_compilation_units(source_payload, manifest["target_articles"])
    baseline_reference = None
    if manifest.get("baseline_reference") is not None:
        baseline_reference = load_baseline_reference(manifest["baseline_reference"])
    raw_candidates = request_rule_candidates_from_llm(
        compilation_units,
        baseline_reference=baseline_reference,
    )
    compiled_source = build_compiled_source(
        raw_candidates=raw_candidates,
        source_payload=source_payload,
        manifest=manifest,
    )
    compiled_dataset = build_dataset_from_source(compiled_source, manifest)
    compiled_report = build_compiled_report(raw_candidates=raw_candidates, compiled_source=compiled_source)

    write_json(work_dir / "compiled.rules.json", raw_candidates)
    write_json(work_dir / "compiled.source.json", compiled_source)
    write_json(work_dir / "compiled.dataset.json", compiled_dataset)
    write_json(work_dir / "compiled.report.json", compiled_report)
    if baseline_reference is not None:
        compiled_delta = build_compiled_delta_payload(
            raw_candidates["delta_analysis"],
            baseline_reference,
            manifest,
        )
        compiled_delta_report = build_delta_report(compiled_delta)
        write_json(work_dir / "compiled.delta.json", compiled_delta)
        write_json(work_dir / "compiled.delta.report.json", compiled_delta_report)
    return compiled_report


def run_review(manifest_path: Path | str) -> dict[str, Any]:
    manifest = load_manifest(manifest_path)
    work_dir = Path(manifest["work_dir"])
    reviewed_source_path = work_dir / "reviewed.source.json"
    if not reviewed_source_path.exists():
        raise ReviewGateError(f"Missing reviewed.source.json: {reviewed_source_path}")

    reviewed_source = read_json(reviewed_source_path)
    reviewed_dataset = build_dataset_from_source(reviewed_source, manifest)
    write_json(work_dir / "reviewed.dataset.json", reviewed_dataset)

    if manifest["mode"] == "initial_onboarding":
        review_diff = build_initial_review_diff(work_dir, reviewed_source, reviewed_dataset)
        unresolved_items = collect_unresolved_items(reviewed_source)
        target_articles_covered = {
            str(article.get("article_number", "")).strip()
            for article in reviewed_source.get("parsed_articles", [])
        }
        missing_target_articles = [
            article_number
            for article_number in manifest["target_articles"]
            if article_number not in target_articles_covered
        ]
        primary_candidate_gap_count = count_primary_candidate_gaps(reviewed_source)
        metadata_complete = has_required_source_chain_metadata(reviewed_source)
        status = "ready_for_approval"
        if missing_target_articles or unresolved_items or primary_candidate_gap_count > 0 or not metadata_complete:
            status = "fail"
        review_report = {
            "status": status,
            "pair_id": manifest["pair_id"],
            "reviewed_source": str(reviewed_source_path),
            "reviewed_dataset": str(work_dir / "reviewed.dataset.json"),
            "target_articles": list(manifest["target_articles"]),
            "missing_target_articles": missing_target_articles,
            "primary_candidate_gap_count": primary_candidate_gap_count,
            "unresolved_item_count": len(unresolved_items),
            "unresolved_items": unresolved_items,
            "required_source_chain_metadata_complete": metadata_complete,
        }
        write_json(work_dir / "review.diff.json", review_diff)
        write_json(work_dir / "review.report.json", review_report)
        return review_report

    reference_dataset = read_json(Path(manifest["stable_reference_dataset"]))
    canonical_reviewed = canonicalize_for_comparison(reviewed_dataset)
    canonical_reference = canonicalize_for_comparison(reference_dataset)
    canonical_match = canonical_reviewed == canonical_reference
    mismatch_paths = collect_mismatch_paths(canonical_reviewed, canonical_reference)[:20]
    review_report = {
        "status": "pass" if canonical_match else "fail",
        "canonical_match": canonical_match,
        "pair_id": manifest["pair_id"],
        "reference_dataset": manifest["stable_reference_dataset"],
        "reviewed_source": str(reviewed_source_path),
        "reviewed_dataset": str(work_dir / "reviewed.dataset.json"),
        "mismatch_path_count": len(mismatch_paths),
        "mismatch_paths": mismatch_paths,
    }
    write_json(work_dir / "review.report.json", review_report)
    return review_report


def build_initial_review_diff(
    work_dir: Path,
    reviewed_source: dict[str, Any],
    reviewed_dataset: dict[str, Any],
) -> dict[str, Any]:
    compiled_source_path = work_dir / "compiled.source.json"
    compiled_dataset_path = work_dir / "compiled.dataset.json"
    compiled_source = read_json(compiled_source_path) if compiled_source_path.exists() else {}
    compiled_dataset = read_json(compiled_dataset_path) if compiled_dataset_path.exists() else {}
    source_paths = collect_mismatch_paths(
        canonicalize_for_comparison(compiled_source),
        canonicalize_for_comparison(reviewed_source),
    )[:20]
    dataset_paths = collect_mismatch_paths(
        canonicalize_for_comparison(compiled_dataset),
        canonicalize_for_comparison(reviewed_dataset),
    )[:20]
    return {
        "compiled_source_path": str(compiled_source_path) if compiled_source_path.exists() else None,
        "compiled_dataset_path": str(compiled_dataset_path) if compiled_dataset_path.exists() else None,
        "source_changed_path_count": len(source_paths),
        "source_changed_paths": source_paths,
        "dataset_changed_path_count": len(dataset_paths),
        "dataset_changed_paths": dataset_paths,
    }


def count_primary_candidate_gaps(source_payload: dict[str, Any]) -> int:
    gap_count = 0
    for article in source_payload.get("parsed_articles", []):
        for paragraph in article.get("paragraphs", []):
            rules = paragraph.get("extracted_rules", [])
            primary_candidates = [rule for rule in rules if rule.get("is_primary_candidate") is True]
            if len(primary_candidates) != 1:
                gap_count += 1
    return gap_count


def has_required_source_chain_metadata(source_payload: dict[str, Any]) -> bool:
    document = source_payload.get("document", {})
    source_trace = document.get("source_trace") or {}
    mli_context = document.get("mli_context") or {}
    if not source_trace.get("official_source_ids"):
        return False
    if not source_trace.get("working_papers"):
        return False
    if not mli_context.get("official_source_ids"):
        return False
    return True


def run_approve(
    manifest_path: Path | str,
    *,
    reviewer_name: str,
    note: str,
) -> dict[str, Any]:
    manifest = load_manifest(manifest_path)
    if manifest["mode"] != "initial_onboarding":
        raise ReviewGateError("Approve is only supported for initial_onboarding manifests.")
    work_dir = Path(manifest["work_dir"])
    review_report_path = work_dir / "review.report.json"
    if not review_report_path.exists():
        raise ReviewGateError(f"Missing review.report.json: {review_report_path}")
    review_report = read_json(review_report_path)
    if review_report.get("status") != "ready_for_approval":
        raise ReviewGateError("Approve refused because review status is not ready_for_approval.")
    approval_record = {
        "status": "approved",
        "pair_id": manifest["pair_id"],
        "manifest_path": manifest["manifest_path"],
        "review_report_path": str(review_report_path),
        "reviewer_name": reviewer_name,
        "note": note,
        "approved_at_utc": datetime.now(timezone.utc).isoformat(),
    }
    write_json(work_dir / "approval.record.json", approval_record)
    return approval_record


def run_promote(manifest_path: Path | str) -> dict[str, Any]:
    manifest = load_manifest(manifest_path)
    work_dir = Path(manifest["work_dir"])
    review_report_path = work_dir / "review.report.json"
    reviewed_dataset_path = work_dir / "reviewed.dataset.json"
    if not review_report_path.exists():
        raise PromotionGateError(f"Missing review.report.json: {review_report_path}")
    if not reviewed_dataset_path.exists():
        raise PromotionGateError(f"Missing reviewed.dataset.json: {reviewed_dataset_path}")

    review_report = read_json(review_report_path)
    if manifest["mode"] == "shadow_rebuild":
        if review_report.get("status") != "pass" or review_report.get("canonical_match") is not True:
            raise PromotionGateError("Promotion refused because the review gate is not pass.")
    else:
        approval_record_path = work_dir / "approval.record.json"
        if review_report.get("status") != "ready_for_approval":
            raise PromotionGateError(
                "Promotion refused because the initial_onboarding review gate is not ready_for_approval."
            )
        if not approval_record_path.exists():
            raise PromotionGateError("Promotion refused because approval.record.json is missing.")

    reviewed_dataset = read_json(reviewed_dataset_path)
    promotion_target_path = Path(manifest["promotion_target_dataset"])
    write_json(promotion_target_path, reviewed_dataset)
    promotion_record: dict[str, Any] = {
        "status": "promoted",
        "pair_id": manifest["pair_id"],
        "manifest_path": manifest["manifest_path"],
        "review_report_path": str(review_report_path),
        "promotion_target_dataset": str(promotion_target_path),
        "promoted_at_utc": datetime.now(timezone.utc).isoformat(),
    }
    if manifest["mode"] == "shadow_rebuild":
        promotion_record["canonical_match"] = True
    else:
        promotion_record["approval_record_path"] = str(work_dir / "approval.record.json")
    write_json(work_dir / "promotion.record.json", promotion_record)
    return promotion_record


def list_onboarding_manifests() -> list[dict[str, Any]]:
    manifests_dir = REPO_ROOT / "data" / "onboarding" / "manifests"
    summaries: list[dict[str, Any]] = []
    for manifest_path in sorted(manifests_dir.glob("*.json")):
        manifest = load_manifest(manifest_path)
        summaries.append(build_manifest_summary(manifest))
    return summaries


def build_manifest_summary(manifest: dict[str, Any]) -> dict[str, Any]:
    return {
        "manifest_path": manifest["manifest_path"],
        "pair_id": manifest["pair_id"],
        "mode": manifest["mode"],
        "jurisdictions": list(manifest["jurisdictions"]),
        "target_articles": list(manifest["target_articles"]),
        "baseline_enabled": manifest.get("baseline_reference") is not None,
        "source_build_manifest_path": str(resolve_source_build_manifest_path(manifest)),
        "source_build_available": resolve_source_build_manifest_path(manifest).exists(),
    }


def resolve_source_build_manifest_path(manifest: dict[str, Any]) -> Path:
    return (
        REPO_ROOT
        / "data"
        / "source_documents"
        / "manifests"
        / f"{manifest['pair_id']}-main-treaty.build.json"
    )


def run_source_build_for_manifest(manifest_path: Path | str) -> dict[str, Any]:
    manifest = load_manifest(manifest_path)
    source_build_manifest_path = resolve_source_build_manifest_path(manifest)
    if not source_build_manifest_path.exists():
        raise TreatyOnboardingError(
            f"No source-build manifest is available for {manifest['pair_id']}: {source_build_manifest_path}"
        )
    from app import source_ingest

    return source_ingest.run_source_build(source_build_manifest_path)


def save_reviewed_source_json(manifest_path: Path | str, reviewed_source_json: str) -> Path:
    manifest = load_manifest(manifest_path)
    work_dir = Path(manifest["work_dir"])
    reviewed_source_path = work_dir / "reviewed.source.json"
    try:
        payload = json.loads(reviewed_source_json)
    except json.JSONDecodeError as exc:
        raise ReviewGateError("reviewed.source.json content is not valid JSON.") from exc
    write_json(reviewed_source_path, payload)
    return reviewed_source_path


def build_workspace(manifest_path: Path | str) -> dict[str, Any]:
    manifest = load_manifest(manifest_path)
    work_dir = Path(manifest["work_dir"])
    source_build_manifest_path = resolve_source_build_manifest_path(manifest)

    reviewed_source_path = work_dir / "reviewed.source.json"
    reviewed_source_content = None
    if reviewed_source_path.exists():
        reviewed_source_content = reviewed_source_path.read_text(encoding="utf-8")
    else:
        source_document_path = Path(manifest["source_documents"][0])
        if source_document_path.exists():
            reviewed_source_content = source_document_path.read_text(encoding="utf-8")

    source_build_report = None
    if source_build_manifest_path.exists():
        try:
            source_build_manifest = read_json(source_build_manifest_path)
            report_path = resolve_manifest_path(
                source_build_manifest_path.parent,
                source_build_manifest["build_report_output"],
            )
            if report_path.exists():
                source_build_report = read_json(report_path)
        except (KeyError, json.JSONDecodeError):
            source_build_report = None

    compiled_report = read_json(work_dir / "compiled.report.json") if (work_dir / "compiled.report.json").exists() else None
    compiled_delta = read_json(work_dir / "compiled.delta.json") if (work_dir / "compiled.delta.json").exists() else None
    compiled_delta_report = (
        read_json(work_dir / "compiled.delta.report.json")
        if (work_dir / "compiled.delta.report.json").exists()
        else None
    )
    review_report = read_json(work_dir / "review.report.json") if (work_dir / "review.report.json").exists() else None
    review_diff = read_json(work_dir / "review.diff.json") if (work_dir / "review.diff.json").exists() else None
    approval_record = (
        read_json(work_dir / "approval.record.json")
        if (work_dir / "approval.record.json").exists()
        else None
    )
    promotion_record = (
        read_json(work_dir / "promotion.record.json")
        if (work_dir / "promotion.record.json").exists()
        else None
    )

    return {
        "manifest": {
            **build_manifest_summary(manifest),
            "source_documents": list(manifest["source_documents"]),
            "promotion_target_dataset": manifest["promotion_target_dataset"],
            "baseline_reference": manifest.get("baseline_reference"),
        },
        "source_build": {
            "available": source_build_manifest_path.exists(),
            "manifest_path": str(source_build_manifest_path),
            "report": source_build_report,
            "status": None if source_build_report is None else source_build_report.get("status"),
        },
        "compile": {
            "status": None if compiled_report is None else compiled_report.get("status"),
            "report": compiled_report,
            "delta_report": compiled_delta_report,
            "delta_analysis": [] if compiled_delta is None else compiled_delta.get("delta_analysis", []),
        },
        "review": {
            "status": None if review_report is None else review_report.get("status"),
            "report": review_report,
            "diff": review_diff,
        },
        "approval": {
            "status": None if approval_record is None else approval_record.get("status"),
            "record": approval_record,
        },
        "promotion": {
            "status": None if promotion_record is None else promotion_record.get("status"),
            "record": promotion_record,
        },
        "reviewed_source": {
            "path": str(reviewed_source_path),
            "content": reviewed_source_content,
        },
    }
