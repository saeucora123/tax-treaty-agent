import json
import sys
from pathlib import Path

import pytest


REPO_ROOT = Path(__file__).resolve().parents[2]
BACKEND_PATH = REPO_ROOT / "backend"
if str(BACKEND_PATH) not in sys.path:
    sys.path.insert(0, str(BACKEND_PATH))

from app import treaty_onboarding  # noqa: E402


CN_SG_SOURCE_PATH = REPO_ROOT / "data" / "source_documents" / "cn-sg-main-treaty.json"
CN_SG_STABLE_DATASET_PATH = REPO_ROOT / "data" / "treaties" / "cn-sg.v3.json"
CN_NL_SOURCE_PATH = REPO_ROOT / "data" / "source_documents" / "cn-nl-main-treaty.json"
CN_NL_STABLE_DATASET_PATH = REPO_ROOT / "data" / "treaties" / "cn-nl.v3.json"
OECD_BASELINE_PATH = (
    REPO_ROOT
    / "data"
    / "onboarding"
    / "baselines"
    / "oecd-model-2017.articles10-12.reference.json"
)


def write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def pair_fixture_config(pair_id: str) -> dict:
    if pair_id == "cn-sg":
        return {
            "source_path": CN_SG_SOURCE_PATH,
            "stable_dataset_path": CN_SG_STABLE_DATASET_PATH,
            "jurisdictions": ["CN", "SG"],
        }
    if pair_id == "cn-nl":
        return {
            "source_path": CN_NL_SOURCE_PATH,
            "stable_dataset_path": CN_NL_STABLE_DATASET_PATH,
            "jurisdictions": ["CN", "NL"],
        }
    raise AssertionError(f"Unsupported pair fixture config: {pair_id}")


def build_manifest_payload(tmp_path: Path, pair_id: str = "cn-sg") -> dict:
    fixture = pair_fixture_config(pair_id)
    stable_dataset = load_json(fixture["stable_dataset_path"])
    work_dir = tmp_path / f"{pair_id}-shadow"
    return {
        "pair_id": pair_id,
        "mode": "shadow_rebuild",
        "jurisdictions": fixture["jurisdictions"],
        "target_articles": ["10", "11", "12"],
        "source_documents": [str(fixture["source_path"])],
        "stable_reference_dataset": str(tmp_path / f"{pair_id}.v3.reference.json"),
        "promotion_target_dataset": str(tmp_path / f"{pair_id}.v3.promoted.json"),
        "work_dir": str(work_dir),
        "treaty_metadata": {
            "version": stable_dataset["treaty"]["version"],
            "source_type": stable_dataset["treaty"]["source_type"],
            "notes": stable_dataset["treaty"]["notes"],
            "source_trace": stable_dataset["treaty"]["source_trace"],
            "mli_context": stable_dataset["treaty"]["mli_context"],
        },
    }


def build_cn_kr_source_payload() -> dict:
    return {
        "document": {
            "document_id": "cn-kr-main-treaty",
            "title": "China-Korea Tax Treaty",
            "document_type": "treaty_text",
            "jurisdictions": ["CN", "KR"],
            "notes": ["Initial onboarding source fixture for CN-KR."],
            "source_trace": {
                "treaty_full_name": "Agreement between the Government of the People's Republic of China and the Government of the Republic of Korea for the Avoidance of Double Taxation and the Prevention of Fiscal Evasion with respect to Taxes on Income",
                "version_note": "Initial onboarding source fixture compiled from official English treaty text.",
                "source_document_title": "China-Korea Tax Treaty",
                "language_version": "en",
                "official_source_ids": ["nts-cn-kr-treaty-text", "unts-cn-kr-treaty-pdf"],
                "working_papers": {
                    "dividends": "docs/superpowers/research/stage-6-evidence/cn-kr-dividends.md",
                    "interest": "docs/superpowers/research/stage-6-evidence/cn-kr-interest.md",
                    "royalties": "docs/superpowers/research/stage-6-evidence/cn-kr-royalties.md",
                },
                "protocol_note": None,
            },
            "mli_context": {
                "covered_tax_agreement": False,
                "ppt_applies": False,
                "summary": "MLI review signal only.",
                "human_review_note": "Confirm anti-abuse and PPT issues during manual review.",
                "official_source_ids": ["oecd-mli-signatories-and-parties"],
            },
        },
        "parsed_articles": [
            {
                "article_number": "10",
                "article_title": "Dividends",
                "article_label": "Article 10",
                "income_type": "dividends",
                "summary": "Defines treaty treatment for dividends between China and Korea.",
                "article_notes": [],
                "paragraphs": [
                    {
                        "paragraph_id": "art10-p2",
                        "paragraph_label": "Article 10(2)",
                        "source_reference": "Article 10(2)",
                        "source_language": "en",
                        "source_segments": [
                            {
                                "segment_id": "art10-p2-s1",
                                "segment_order": 1,
                                "page_hint": 5,
                                "source_kind": "article_paragraph",
                                "text_quality": "clean",
                                "normalization_status": "verbatim",
                                "text": "The tax charged in the State of source shall not exceed 10 per cent of the gross amount of the dividends, and shall not exceed 5 per cent if the beneficial owner is a company directly holding at least 25 per cent of the capital of the company paying the dividends.",
                            }
                        ],
                        "extracted_rules": [
                            {
                                "rule_id": "cn-kr-art10-p2-r1",
                                "rule_type": "source_tax_limit",
                                "rate": "10%",
                                "direction": "bidirectional",
                                "candidate_rank": 1,
                                "is_primary_candidate": True,
                                "extraction_confidence": 0.98,
                                "derived_from_segments": ["art10-p2-s1"],
                                "conditions": ["General dividend branch."],
                                "human_review_required": True,
                                "review_reason": "General dividend branch.",
                            }
                        ],
                    }
                ],
            },
            {
                "article_number": "11",
                "article_title": "Interest",
                "article_label": "Article 11",
                "income_type": "interest",
                "summary": "Defines treaty treatment for interest between China and Korea.",
                "article_notes": [],
                "paragraphs": [
                    {
                        "paragraph_id": "art11-p2",
                        "paragraph_label": "Article 11(2)",
                        "source_reference": "Article 11(2)",
                        "source_language": "en",
                        "source_segments": [
                            {
                                "segment_id": "art11-p2-s1",
                                "segment_order": 1,
                                "page_hint": 6,
                                "source_kind": "article_paragraph",
                                "text_quality": "clean",
                                "normalization_status": "verbatim",
                                "text": "However, such interest may also be taxed in the first-mentioned State, but the tax shall not exceed 10 per cent of the gross amount of the interest.",
                            }
                        ],
                        "extracted_rules": [
                            {
                                "rule_id": "cn-kr-art11-p2-r1",
                                "rule_type": "source_tax_limit",
                                "rate": "10%",
                                "direction": "bidirectional",
                                "candidate_rank": 1,
                                "is_primary_candidate": True,
                                "extraction_confidence": 0.98,
                                "derived_from_segments": ["art11-p2-s1"],
                                "conditions": ["General interest branch."],
                                "human_review_required": True,
                                "review_reason": "General interest branch.",
                            }
                        ],
                    }
                ],
            },
            {
                "article_number": "12",
                "article_title": "Royalties",
                "article_label": "Article 12",
                "income_type": "royalties",
                "summary": "Defines treaty treatment for royalties between China and Korea.",
                "article_notes": [],
                "paragraphs": [
                    {
                        "paragraph_id": "art12-p2",
                        "paragraph_label": "Article 12(2)",
                        "source_reference": "Article 12(2)",
                        "source_language": "en",
                        "source_segments": [
                            {
                                "segment_id": "art12-p2-s1",
                                "segment_order": 1,
                                "page_hint": 7,
                                "source_kind": "article_paragraph",
                                "text_quality": "clean",
                                "normalization_status": "verbatim",
                                "text": "However, such royalties may also be taxed in the first-mentioned State, but the tax so charged shall not exceed 10 per cent of the gross amount of the royalties.",
                            }
                        ],
                        "extracted_rules": [
                            {
                                "rule_id": "cn-kr-art12-p2-r1",
                                "rule_type": "source_tax_limit",
                                "rate": "10%",
                                "direction": "bidirectional",
                                "candidate_rank": 1,
                                "is_primary_candidate": True,
                                "extraction_confidence": 0.98,
                                "derived_from_segments": ["art12-p2-s1"],
                                "conditions": ["General royalties branch."],
                                "human_review_required": True,
                                "review_reason": "General royalties branch.",
                            }
                        ],
                    }
                ],
            },
        ],
    }


def build_initial_manifest_payload(tmp_path: Path) -> dict:
    return {
        "pair_id": "cn-kr",
        "mode": "initial_onboarding",
        "jurisdictions": ["CN", "KR"],
        "target_articles": ["10", "11", "12"],
        "source_documents": [str(tmp_path / "cn-kr-main-treaty.json")],
        "promotion_target_dataset": str(tmp_path / "cn-kr.v3.json"),
        "work_dir": str(tmp_path / "cn-kr-initial-onboarding"),
        "baseline_reference": str(tmp_path / "baseline.reference.json"),
        "treaty_metadata": {
            "version": "v3",
            "source_type": "manual_structured_from_official_text",
            "notes": ["Initial onboarding candidate for CN-KR."],
            "source_trace": build_cn_kr_source_payload()["document"]["source_trace"],
            "mli_context": build_cn_kr_source_payload()["document"]["mli_context"],
        },
    }


def build_baseline_reference_payload() -> dict:
    return {
        "baseline_id": "oecd-model-2017-articles10-12",
        "title": "OECD Model Tax Convention 2017 baseline reference for Articles 10 to 12",
        "model_version": "2017",
        "articles": [
            {
                "article_number": "10",
                "article_title": "Dividends",
                "income_type": "dividends",
                "paragraphs": [
                    {
                        "paragraph_number": "2(a)",
                        "source_reference": "OECD Model 2017 Article 10(2)(a)",
                        "text": "Reduced dividend branch for direct 25 per cent corporate holdings maintained throughout a 365-day period.",
                        "reference_rules": [
                            {
                                "rule_label": "direct_corporate_reduced_rate",
                                "rate": "5%",
                                "conditions": [
                                    "The beneficial owner is a company that holds directly at least 25 per cent of the capital of the paying company throughout a 365-day period that includes the payment date."
                                ],
                            }
                        ],
                    },
                    {
                        "paragraph_number": "2(b)",
                        "source_reference": "OECD Model 2017 Article 10(2)(b)",
                        "text": "General dividend withholding cap for other cases.",
                        "reference_rules": [
                            {
                                "rule_label": "general_dividend_rate",
                                "rate": "15%",
                                "conditions": [
                                    "Applies in all other dividend cases not covered by the reduced-rate branch."
                                ],
                            }
                        ],
                    },
                ],
            },
            {
                "article_number": "11",
                "article_title": "Interest",
                "income_type": "interest",
                "paragraphs": [
                    {
                        "paragraph_number": "2",
                        "source_reference": "OECD Model 2017 Article 11(2)",
                        "text": "General interest withholding cap when the beneficial owner is resident in the other state.",
                        "reference_rules": [
                            {
                                "rule_label": "general_interest_rate",
                                "rate": "10%",
                                "conditions": [
                                    "The beneficial owner of the interest is a resident of the other Contracting State."
                                ],
                            }
                        ],
                    }
                ],
            },
            {
                "article_number": "12",
                "article_title": "Royalties",
                "income_type": "royalties",
                "paragraphs": [
                    {
                        "paragraph_number": "1",
                        "source_reference": "OECD Model 2017 Article 12(1)",
                        "text": "Royalties are taxable only in the residence state of the beneficial owner.",
                        "reference_rules": [
                            {
                                "rule_label": "exclusive_residence_royalty_rule",
                                "rate": "0%",
                                "conditions": [
                                    "Royalties arise in one state and are beneficially owned by a resident of the other Contracting State."
                                ],
                            }
                        ],
                    },
                    {
                        "paragraph_number": "2",
                        "source_reference": "OECD Model 2017 Article 12(2)",
                        "text": "Definition paragraph for royalties; no source-state withholding cap is created here.",
                        "reference_rules": [
                            {
                                "rule_label": "royalty_definition_scope",
                                "rate": "N/A",
                                "conditions": [
                                    "Payments are for the use of, or right to use, qualifying intellectual property or industrial, commercial, or scientific experience."
                                ],
                            }
                        ],
                    },
                ],
            },
        ],
    }


def build_raw_candidate_response_from_source(source_payload: dict) -> dict:
    parsed_articles: list[dict] = []
    for article in source_payload["parsed_articles"]:
        paragraphs: list[dict] = []
        for paragraph in article["paragraphs"]:
            paragraph_number = paragraph["paragraph_id"].split("-p", 1)[1]
            paragraph_text = " ".join(
                segment["text"].strip()
                for segment in paragraph.get("source_segments", [])
                if segment["text"].strip()
            )
            paragraphs.append(
                {
                    "paragraph_number": paragraph_number,
                    "source_reference": paragraph["source_reference"],
                    "text": paragraph_text,
                    "rules": [
                        {
                            "rule_type": rule["rule_type"],
                            "rate": rule["rate"],
                            "direction": rule["direction"],
                            "conditions": rule["conditions"],
                            "review_reason": rule["review_reason"],
                            "extraction_confidence": rule["extraction_confidence"],
                        }
                        for rule in paragraph["extracted_rules"]
                    ],
                }
            )
        parsed_articles.append(
            {
                "article_number": article["article_number"],
                "article_title": article["article_title"],
                "income_type": article["income_type"],
                "paragraphs": paragraphs,
            }
        )
    return {"parsed_articles": parsed_articles}


def build_delta_analysis_payload() -> list[dict]:
    return [
        {
            "article_number": "10",
            "income_type": "dividends",
            "baseline_reference": "OECD Model 2017 Article 10(2)(b)",
            "bilateral_reference": "CN-SG Article 10(2)(b)",
            "delta_type": "rate_changed",
            "summary": "The general dividend withholding cap is reduced from 15 per cent in the OECD baseline to 10 per cent in the bilateral treaty.",
            "materiality": "high",
            "reviewer_attention": "Confirm that the bilateral general branch is preserved as the fallback dividend lane.",
        },
        {
            "article_number": "11",
            "income_type": "interest",
            "baseline_reference": "OECD Model 2017 Article 11(2)",
            "bilateral_reference": "CN-SG Article 11(2)(a)",
            "delta_type": "branch_added",
            "summary": "The bilateral treaty adds a preferential branch for interest received by a bank or financial institution.",
            "materiality": "high",
            "reviewer_attention": "Verify that the bank-specific branch is represented separately from the general 10 per cent lane.",
        },
        {
            "article_number": "12",
            "income_type": "royalties",
            "baseline_reference": "OECD Model 2017 Article 12(1)",
            "bilateral_reference": "CN-SG Article 12(2)",
            "delta_type": "rate_changed",
            "summary": "The bilateral treaty allows source-state royalty withholding up to 10 per cent instead of exclusive residence taxation.",
            "materiality": "high",
            "reviewer_attention": "Confirm that the bilateral royalty cap replaces the OECD residence-only baseline in the runtime dataset.",
        },
    ]


def test_load_manifest_rejects_missing_treaty_metadata(tmp_path: Path):
    manifest_path = tmp_path / "manifest.json"
    payload = build_manifest_payload(tmp_path)
    payload.pop("treaty_metadata")
    write_json(manifest_path, payload)

    with pytest.raises(treaty_onboarding.ManifestValidationError):
        treaty_onboarding.load_manifest(manifest_path)


def test_load_manifest_resolves_optional_baseline_reference_path(tmp_path: Path):
    manifest_path = write_manifest(tmp_path, include_baseline=True)

    manifest = treaty_onboarding.load_manifest(manifest_path)

    assert manifest["baseline_reference"] == str((tmp_path / "baseline.reference.json").resolve())


def test_extract_compilation_units_filters_target_articles_and_ignores_existing_rules():
    source_payload = load_json(CN_SG_SOURCE_PATH)

    units = treaty_onboarding.extract_compilation_units(source_payload, ["10", "12"])

    assert [article["article_number"] for article in units] == ["10", "12"]
    assert "rules" not in units[0]["paragraphs"][0]
    assert units[0]["paragraphs"][0]["text"].startswith("10 per cent")
    assert units[1]["paragraphs"][0]["source_reference"] == "CN-SG Article 12(2)"


def test_build_compiler_request_payload_includes_baseline_reference_units_when_present():
    source_payload = load_json(CN_SG_SOURCE_PATH)
    baseline_reference = build_baseline_reference_payload()
    units = treaty_onboarding.extract_compilation_units(source_payload, ["10", "11", "12"])

    payload = treaty_onboarding.build_compiler_request_payload(
        units,
        model="deepseek-chat",
        baseline_reference=baseline_reference,
    )

    content = json.loads(payload["messages"][1]["content"])
    assert "parsed_articles" in content
    assert content["baseline_reference"]["baseline_id"] == baseline_reference["baseline_id"]
    assert content["baseline_reference"]["articles"][0]["article_number"] == "10"


def test_load_manifest_supports_cn_nl_shadow_shape(tmp_path: Path):
    manifest_path = write_manifest(tmp_path, pair_id="cn-nl")

    manifest = treaty_onboarding.load_manifest(manifest_path)

    assert manifest["pair_id"] == "cn-nl"
    assert manifest["jurisdictions"] == ["CN", "NL"]
    assert manifest["source_documents"] == [str(CN_NL_SOURCE_PATH.resolve())]


def test_extract_compilation_units_for_cn_nl_uses_structured_article_branches():
    source_payload = load_json(CN_NL_SOURCE_PATH)

    units = treaty_onboarding.extract_compilation_units(source_payload, ["10"])

    assert [article["article_number"] for article in units] == ["10"]
    assert units[0]["paragraphs"][0]["source_reference"] == "Article 10(2)(b)"
    assert units[0]["paragraphs"][1]["text"].startswith("However, such dividends may also be taxed")


def test_build_compiled_source_assigns_pair_specific_deterministic_ids(tmp_path: Path):
    source_payload = load_json(CN_SG_SOURCE_PATH)
    manifest = treaty_onboarding.load_manifest(write_manifest(tmp_path))
    raw_candidates = build_raw_candidate_response_from_source(
        {
            "parsed_articles": [source_payload["parsed_articles"][0]],
        }
    )

    compiled_source = treaty_onboarding.build_compiled_source(
        raw_candidates=raw_candidates,
        source_payload=source_payload,
        manifest=manifest,
    )

    first_paragraph = compiled_source["parsed_articles"][0]["paragraphs"][0]
    first_rule = first_paragraph["extracted_rules"][0]
    assert first_paragraph["paragraph_id"] == "art10-p2b"
    assert first_rule["rule_id"] == "cn-sg-art10-p2b-r1"
    assert first_rule["candidate_rank"] == 1
    assert first_rule["is_primary_candidate"] is True
    assert first_rule["derived_from_segments"] == ["art10-p2b-s1"]


def test_build_dataset_from_source_reconciles_cn_nl_governed_notes_against_reference(tmp_path: Path):
    manifest_path = write_manifest(tmp_path, pair_id="cn-nl")
    manifest = treaty_onboarding.load_manifest(manifest_path)
    source_payload = load_json(CN_NL_SOURCE_PATH)
    stable_dataset = load_json(CN_NL_STABLE_DATASET_PATH)

    reviewed_dataset = treaty_onboarding.build_dataset_from_source(source_payload, manifest)

    assert reviewed_dataset["articles"][0]["notes"] == stable_dataset["articles"][0]["notes"]
    assert reviewed_dataset["articles"][1]["notes"] == stable_dataset["articles"][1]["notes"]


def test_normalize_compiler_response_requires_delta_analysis_when_baseline_enabled():
    with pytest.raises(treaty_onboarding.TreatyOnboardingError):
        treaty_onboarding.normalize_compiler_response(
            {"parsed_articles": []},
            baseline_enabled=True,
        )


def test_normalize_compiler_response_maps_common_delta_type_synonyms():
    normalized = treaty_onboarding.normalize_compiler_response(
        {
            "parsed_articles": [],
            "delta_analysis": [
                {
                    "article_number": "10",
                    "income_type": "dividends",
                    "baseline_reference": "OECD Model 2017 Article 10(2)(b)",
                    "bilateral_reference": "CN-SG Article 10(2)(b)",
                    "delta_type": "rate_deviation",
                    "summary": "General dividend rate differs from the OECD baseline.",
                    "materiality": "high",
                    "reviewer_attention": "yes",
                },
                {
                    "article_number": "10",
                    "income_type": "dividends",
                    "baseline_reference": "OECD Model 2017 Article 10(2)(a)",
                    "bilateral_reference": "CN-SG Article 10(2)(a)",
                    "delta_type": "condition_deviation",
                    "summary": "Holding-period condition differs from the OECD baseline.",
                    "materiality": "medium",
                    "reviewer_attention": "yes",
                },
                {
                    "article_number": "11",
                    "income_type": "interest",
                    "baseline_reference": "OECD Model 2017 Article 11(2)",
                    "bilateral_reference": "CN-SG Article 11(2)(a)",
                    "delta_type": "additional_provision",
                    "summary": "The bilateral treaty adds a bank-specific interest branch.",
                    "materiality": "medium",
                    "reviewer_attention": "recommended",
                },
                {
                    "article_number": "11",
                    "income_type": "interest",
                    "baseline_reference": "OECD Model 2017 Article 11(2)",
                    "bilateral_reference": "CN-SG Article 11(2)(b)",
                    "delta_type": "rate_match",
                    "summary": "The general interest branch matches the baseline rate.",
                    "materiality": "low",
                    "reviewer_attention": "optional",
                },
                {
                    "article_number": "11",
                    "income_type": "interest",
                    "baseline_reference": "OECD Model 2017 Article 11(2)",
                    "bilateral_reference": "CN-SG Article 11(2)(b)",
                    "delta_type": "rate_alignment",
                    "summary": "The general interest branch aligns with the baseline rate.",
                    "materiality": "none",
                    "reviewer_attention": "optional",
                },
                {
                    "article_number": "12",
                    "income_type": "royalties",
                    "baseline_reference": "OECD Model 2017 Article 12(1)",
                    "bilateral_reference": "CN-SG Article 12(2)",
                    "delta_type": "structural_difference",
                    "summary": "The bilateral treaty creates a source-state royalty taxation branch.",
                    "materiality": "high",
                    "reviewer_attention": "required",
                },
                {
                    "article_number": "11",
                    "income_type": "interest",
                    "baseline_reference": "OECD Model 2017 Article 11(2)",
                    "bilateral_reference": "CN-SG Article 11(2)(a)",
                    "delta_type": "rule_addition",
                    "summary": "The bilateral treaty introduces an extra interest branch for banks.",
                    "materiality": "medium",
                    "reviewer_attention": "recommended",
                },
                {
                    "article_number": "12",
                    "income_type": "royalties",
                    "baseline_reference": "OECD Model 2017 Article 12(1)",
                    "bilateral_reference": "CN-SG Article 12(2)",
                    "delta_type": "taxation_approach_difference",
                    "summary": "The bilateral treaty uses a different royalty taxation approach from the baseline.",
                    "materiality": "high",
                    "reviewer_attention": "required",
                },
                {
                    "article_number": "10",
                    "income_type": "dividends",
                    "baseline_reference": "OECD Model 2017 Article 10(2)",
                    "bilateral_reference": "CN-SG Article 10(2)",
                    "delta_type": "rate_and_condition_variation",
                    "summary": "The bilateral treaty differs on both the fallback rate and the reduced-rate conditions.",
                    "materiality": "high",
                    "reviewer_attention": "required",
                },
            ],
        },
        baseline_enabled=True,
    )

    assert normalized["delta_analysis"][0]["delta_type"] == "rate_changed"
    assert normalized["delta_analysis"][1]["delta_type"] == "condition_changed"
    assert normalized["delta_analysis"][2]["delta_type"] == "branch_added"
    assert normalized["delta_analysis"][3]["delta_type"] == "scope_note"
    assert normalized["delta_analysis"][4]["delta_type"] == "scope_note"
    assert normalized["delta_analysis"][4]["materiality"] == "low"
    assert normalized["delta_analysis"][5]["delta_type"] == "scope_note"
    assert normalized["delta_analysis"][6]["delta_type"] == "branch_added"
    assert normalized["delta_analysis"][7]["delta_type"] == "scope_note"
    assert normalized["delta_analysis"][8]["delta_type"] == "scope_note"


def test_build_delta_report_counts_materiality_levels():
    delta_payload = treaty_onboarding.build_compiled_delta_payload(
        build_delta_analysis_payload(),
        build_baseline_reference_payload(),
        {"pair_id": "cn-sg"},
    )

    report = treaty_onboarding.build_delta_report(delta_payload)

    assert report["delta_item_count"] == 3
    assert report["high_materiality_count"] == 3
    assert report["materiality_counts"]["high"] == 3
    assert report["delta_type_counts"]["rate_changed"] == 2
    assert report["delta_type_counts"]["branch_added"] == 1


def test_canonicalize_for_comparison_ignores_whitespace_and_id_list_order():
    left = {
        "notes": ["  alpha  ", "beta"],
        "official_source_ids": ["b-source", "a-source"],
        "paragraphs": [
            {
                "paragraph_id": "art10-p2b",
                "conditions": ["Applies   in all other cases."],
            },
            {
                "paragraph_id": "art10-p2a",
                "conditions": [" Reduced rate branch. "],
            },
        ],
    }
    right = {
        "paragraphs": [
            {
                "paragraph_id": "art10-p2a",
                "conditions": ["Reduced rate branch."],
            },
            {
                "paragraph_id": "art10-p2b",
                "conditions": ["Applies in all other cases."],
            },
        ],
        "official_source_ids": ["a-source", "b-source"],
        "notes": ["alpha", "beta"],
    }

    assert treaty_onboarding.canonicalize_for_comparison(left) == treaty_onboarding.canonicalize_for_comparison(right)


def test_run_promote_refuses_when_review_gate_is_not_pass(tmp_path: Path):
    manifest_path = write_manifest(tmp_path)
    manifest = treaty_onboarding.load_manifest(manifest_path)
    work_dir = Path(manifest["work_dir"])
    write_json(
        work_dir / "review.report.json",
        {
            "status": "fail",
            "canonical_match": False,
        },
    )

    with pytest.raises(treaty_onboarding.PromotionGateError):
        treaty_onboarding.run_promote(manifest_path)


def test_shadow_rebuild_compile_review_promote_round_trip(tmp_path: Path, monkeypatch):
    source_payload = load_json(CN_SG_SOURCE_PATH)
    stable_dataset = load_json(CN_SG_STABLE_DATASET_PATH)
    manifest_path = write_manifest(tmp_path)
    manifest = treaty_onboarding.load_manifest(manifest_path)
    write_json(Path(manifest["stable_reference_dataset"]), stable_dataset)
    write_json(Path(manifest["work_dir"]) / "reviewed.source.json", source_payload)

    monkeypatch.setattr(
        treaty_onboarding,
        "request_rule_candidates_from_llm",
        lambda *args, **kwargs: build_raw_candidate_response_from_source(source_payload),
    )

    compile_report = treaty_onboarding.run_compile(manifest_path)
    assert compile_report["status"] == "ok"
    assert (Path(manifest["work_dir"]) / "compiled.rules.json").exists()
    assert (Path(manifest["work_dir"]) / "compiled.source.json").exists()
    assert (Path(manifest["work_dir"]) / "compiled.dataset.json").exists()
    assert (Path(manifest["work_dir"]) / "compiled.report.json").exists()

    review_report = treaty_onboarding.run_review(manifest_path)
    assert review_report["status"] == "pass"
    assert review_report["canonical_match"] is True
    assert (Path(manifest["work_dir"]) / "reviewed.dataset.json").exists()
    assert (Path(manifest["work_dir"]) / "review.report.json").exists()

    promotion_record = treaty_onboarding.run_promote(manifest_path)
    assert promotion_record["status"] == "promoted"
    assert promotion_record["canonical_match"] is True
    promoted_dataset = load_json(Path(manifest["promotion_target_dataset"]))
    assert treaty_onboarding.canonicalize_for_comparison(promoted_dataset) == treaty_onboarding.canonicalize_for_comparison(stable_dataset)
    assert (Path(manifest["work_dir"]) / "promotion.record.json").exists()


def test_v1_shadow_rebuild_compile_path_keeps_delta_artifacts_absent(tmp_path: Path, monkeypatch):
    source_payload = load_json(CN_SG_SOURCE_PATH)
    stable_dataset = load_json(CN_SG_STABLE_DATASET_PATH)
    manifest_path = write_manifest(tmp_path)
    manifest = treaty_onboarding.load_manifest(manifest_path)
    write_json(Path(manifest["stable_reference_dataset"]), stable_dataset)

    monkeypatch.setattr(
        treaty_onboarding,
        "request_rule_candidates_from_llm",
        lambda *args, **kwargs: build_raw_candidate_response_from_source(source_payload),
    )

    treaty_onboarding.run_compile(manifest_path)

    assert not (Path(manifest["work_dir"]) / "compiled.delta.json").exists()
    assert not (Path(manifest["work_dir"]) / "compiled.delta.report.json").exists()


def test_cn_nl_shadow_rebuild_compile_review_promote_round_trip(tmp_path: Path, monkeypatch):
    source_payload = load_json(CN_NL_SOURCE_PATH)
    stable_dataset = load_json(CN_NL_STABLE_DATASET_PATH)
    manifest_path = write_manifest(tmp_path, pair_id="cn-nl")
    manifest = treaty_onboarding.load_manifest(manifest_path)
    write_json(Path(manifest["stable_reference_dataset"]), stable_dataset)
    write_json(Path(manifest["work_dir"]) / "reviewed.source.json", source_payload)

    monkeypatch.setattr(
        treaty_onboarding,
        "request_rule_candidates_from_llm",
        lambda *args, **kwargs: build_raw_candidate_response_from_source(source_payload),
    )

    compile_report = treaty_onboarding.run_compile(manifest_path)
    assert compile_report["status"] == "ok"
    review_report = treaty_onboarding.run_review(manifest_path)
    assert review_report["status"] == "pass"
    assert review_report["canonical_match"] is True

    promotion_record = treaty_onboarding.run_promote(manifest_path)
    assert promotion_record["status"] == "promoted"
    promoted_dataset = load_json(Path(manifest["promotion_target_dataset"]))
    assert treaty_onboarding.canonicalize_for_comparison(promoted_dataset) == treaty_onboarding.canonicalize_for_comparison(stable_dataset)


def test_baseline_aware_cn_sg_compile_review_promote_round_trip(tmp_path: Path, monkeypatch):
    source_payload = load_json(CN_SG_SOURCE_PATH)
    stable_dataset = load_json(CN_SG_STABLE_DATASET_PATH)
    baseline_reference = build_baseline_reference_payload()
    manifest_path = write_manifest(tmp_path, include_baseline=True)
    manifest = treaty_onboarding.load_manifest(manifest_path)
    write_json(Path(manifest["stable_reference_dataset"]), stable_dataset)
    write_json(Path(manifest["work_dir"]) / "reviewed.source.json", source_payload)

    monkeypatch.setattr(
        treaty_onboarding,
        "request_rule_candidates_from_llm",
        lambda *args, **kwargs: {
            "parsed_articles": build_raw_candidate_response_from_source(source_payload)["parsed_articles"],
            "delta_analysis": build_delta_analysis_payload(),
        },
    )

    compile_report = treaty_onboarding.run_compile(manifest_path)
    assert compile_report["status"] == "ok"
    assert (Path(manifest["work_dir"]) / "compiled.delta.json").exists()
    assert (Path(manifest["work_dir"]) / "compiled.delta.report.json").exists()

    compiled_delta = load_json(Path(manifest["work_dir"]) / "compiled.delta.json")
    compiled_delta_report = load_json(Path(manifest["work_dir"]) / "compiled.delta.report.json")
    assert compiled_delta["baseline_reference"]["baseline_id"] == baseline_reference["baseline_id"]
    assert compiled_delta_report["delta_item_count"] == 3
    assert compiled_delta_report["high_materiality_count"] == 3

    review_report = treaty_onboarding.run_review(manifest_path)
    assert review_report["status"] == "pass"
    assert review_report["canonical_match"] is True

    promotion_record = treaty_onboarding.run_promote(manifest_path)
    assert promotion_record["status"] == "promoted"


def test_baseline_aware_cn_nl_compile_review_round_trip(tmp_path: Path, monkeypatch):
    source_payload = load_json(CN_NL_SOURCE_PATH)
    stable_dataset = load_json(CN_NL_STABLE_DATASET_PATH)
    manifest_path = write_manifest(tmp_path, pair_id="cn-nl", include_baseline=True)
    manifest = treaty_onboarding.load_manifest(manifest_path)
    write_json(Path(manifest["stable_reference_dataset"]), stable_dataset)
    write_json(Path(manifest["work_dir"]) / "reviewed.source.json", source_payload)

    monkeypatch.setattr(
        treaty_onboarding,
        "request_rule_candidates_from_llm",
        lambda *args, **kwargs: {
            "parsed_articles": build_raw_candidate_response_from_source(source_payload)["parsed_articles"],
            "delta_analysis": build_delta_analysis_payload(),
        },
    )

    compile_report = treaty_onboarding.run_compile(manifest_path)
    assert compile_report["status"] == "ok"
    review_report = treaty_onboarding.run_review(manifest_path)
    assert review_report["status"] == "pass"
    assert review_report["canonical_match"] is True


def test_initial_onboarding_review_approve_promote_round_trip(tmp_path: Path, monkeypatch):
    source_payload = build_cn_kr_source_payload()
    source_path = tmp_path / "cn-kr-main-treaty.json"
    baseline_path = tmp_path / "baseline.reference.json"
    manifest_path = tmp_path / "cn-kr.initial-oecd.json"
    write_json(source_path, source_payload)
    write_json(baseline_path, build_baseline_reference_payload())
    write_json(manifest_path, build_initial_manifest_payload(tmp_path))

    manifest = treaty_onboarding.load_manifest(manifest_path)
    write_json(Path(manifest["work_dir"]) / "reviewed.source.json", source_payload)

    monkeypatch.setattr(
        treaty_onboarding,
        "request_rule_candidates_from_llm",
        lambda *args, **kwargs: {
            "parsed_articles": build_raw_candidate_response_from_source(source_payload)["parsed_articles"],
            "delta_analysis": build_delta_analysis_payload(),
        },
    )

    compile_report = treaty_onboarding.run_compile(manifest_path)
    assert compile_report["status"] == "ok"
    review_report = treaty_onboarding.run_review(manifest_path)
    assert review_report["status"] == "ready_for_approval"
    assert review_report["unresolved_item_count"] == 0
    assert (Path(manifest["work_dir"]) / "review.diff.json").exists()

    approval_record = treaty_onboarding.run_approve(
        manifest_path,
        reviewer_name="Codex Reviewer",
        note="Approved for initial runtime promotion.",
    )
    assert approval_record["status"] == "approved"

    promotion_record = treaty_onboarding.run_promote(manifest_path)
    assert promotion_record["status"] == "promoted"
    assert Path(manifest["promotion_target_dataset"]).exists()


def write_manifest(tmp_path: Path, pair_id: str = "cn-sg", include_baseline: bool = False) -> Path:
    manifest_path = tmp_path / f"{pair_id}.shadow.json"
    manifest_payload = build_manifest_payload(tmp_path, pair_id=pair_id)
    stable_dataset = load_json(pair_fixture_config(pair_id)["stable_dataset_path"])
    if include_baseline:
        baseline_path = tmp_path / "baseline.reference.json"
        write_json(baseline_path, build_baseline_reference_payload())
        manifest_payload["baseline_reference"] = str(baseline_path)
    write_json(Path(manifest_payload["stable_reference_dataset"]), stable_dataset)
    write_json(manifest_path, manifest_payload)
    return manifest_path
