import json
import sys
from pathlib import Path

import pytest

from app import llm_document_extractor


REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPTS_PATH = REPO_ROOT / "scripts"
if str(SCRIPTS_PATH) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_PATH))

import build_cn_nl_dataset as dataset_builder  # noqa: E402


class FakeHTTPResponse:
    def __init__(self, payload: dict):
        self._payload = json.dumps(payload).encode("utf-8")

    def read(self) -> bytes:
        return self._payload

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False


def test_build_request_payload_for_document_extraction_is_explicit_about_schema():
    payload = llm_document_extractor.build_request_payload(
        raw_text=(
            "Article 12 Royalties\n"
            "1. Royalties arising in one of the States and paid to a resident of the other State may be taxed in that other State.\n"
            "2. However, such royalties may also be taxed in the first-mentioned State, but the tax so charged shall not exceed 10 per cent of the gross amount of the royalties."
        ),
        model="deepseek-chat",
        source_language="en",
    )

    system_prompt = payload["messages"][0]["content"]

    assert "Return only JSON with a top-level key parsed_articles." in system_prompt
    assert '"income_type"' in system_prompt
    assert '"paragraph_number"' in system_prompt
    assert '"extraction_confidence"' in system_prompt
    assert "Use income_type only from: dividends, interest, royalties, unknown." in system_prompt


def test_extract_source_payload_from_text_reads_deepseek_response(monkeypatch):
    config = llm_document_extractor.LLMInputParserConfig(
        api_key="test-key",
        base_url="https://example.com",
        model="deepseek-chat",
        timeout_seconds=5,
    )
    monkeypatch.setattr(
        llm_document_extractor.request,
        "urlopen",
        lambda req, timeout: FakeHTTPResponse(
            {
                "choices": [
                    {
                        "message": {
                            "content": json.dumps(
                                {
                                    "parsed_articles": [
                                        {
                                            "article_number": "12",
                                            "article_title": "Royalties",
                                            "income_type": "royalties",
                                            "summary": "Treaty treatment for royalties between the two jurisdictions.",
                                            "article_notes": [
                                                "Beneficial ownership may matter."
                                            ],
                                            "paragraphs": [
                                                {
                                                    "paragraph_number": "1",
                                                    "source_reference": "Article 12(1)",
                                                    "text": "Royalties arising in one of the States and paid to a resident of the other State may be taxed in that other State.",
                                                    "rules": [
                                                        {
                                                            "rule_type": "withholding_tax_cap",
                                                            "rate": "10%",
                                                            "direction": "bidirectional",
                                                            "conditions": [
                                                                "Treaty applicability depends on the facts of the payment."
                                                            ],
                                                            "review_reason": "Final eligibility depends on facts outside the current review scope.",
                                                            "extraction_confidence": 0.93,
                                                        }
                                                    ],
                                                }
                                            ],
                                        }
                                    ]
                                }
                            )
                        }
                    }
                ]
            }
        ),
    )

    payload = llm_document_extractor.extract_source_payload_from_text(
        raw_text=(
            "Article 12 Royalties\n"
            "1. Royalties arising in one of the States and paid to a resident of the other State may be taxed in that other State."
        ),
        document_id="cn-nl-article12-llm",
        title="China-Netherlands Tax Treaty Article 12",
        document_type="treaty_text",
        jurisdictions=["CN", "NL"],
        source_language="en",
        config=config,
    )

    assert payload == {
        "document": {
            "document_id": "cn-nl-article12-llm",
            "title": "China-Netherlands Tax Treaty Article 12",
            "document_type": "treaty_text",
            "jurisdictions": ["CN", "NL"],
            "notes": [
                "Generated by constrained LLM document extraction."
            ],
        },
        "parsed_articles": [
            {
                "article_number": "12",
                "article_title": "Royalties",
                "article_label": "Article 12",
                "income_type": "royalties",
                "summary": "Treaty treatment for royalties between the two jurisdictions.",
                "article_notes": ["Beneficial ownership may matter."],
                "paragraphs": [
                    {
                        "paragraph_id": "art12-p1",
                        "paragraph_label": "Article 12(1)",
                        "source_reference": "Article 12(1)",
                        "source_language": "en",
                        "source_segments": [
                            {
                                "segment_id": "art12-p1-s1",
                                "segment_order": 1,
                                "page_hint": None,
                                "source_kind": "article_paragraph",
                                "text_quality": "clean",
                                "normalization_status": "verbatim",
                                "text": "Royalties arising in one of the States and paid to a resident of the other State may be taxed in that other State.",
                            }
                        ],
                        "extracted_rules": [
                            {
                                "rule_id": "cn-nl-art12-p1-r1",
                                "rule_type": "withholding_tax_cap",
                                "rate": "10%",
                                "direction": "bidirectional",
                                "candidate_rank": 1,
                                "is_primary_candidate": True,
                                "extraction_confidence": 0.93,
                                "derived_from_segments": ["art12-p1-s1"],
                                "conditions": [
                                    "Treaty applicability depends on the facts of the payment."
                                ],
                                "human_review_required": True,
                                "review_reason": "Final eligibility depends on facts outside the current review scope.",
                            }
                        ],
                    }
                ],
            }
        ],
    }


def test_extract_source_payload_from_text_is_builder_compatible(monkeypatch):
    config = llm_document_extractor.LLMInputParserConfig(
        api_key="test-key",
        base_url="https://example.com",
        model="deepseek-chat",
        timeout_seconds=5,
    )
    monkeypatch.setattr(
        llm_document_extractor.request,
        "urlopen",
        lambda req, timeout: FakeHTTPResponse(
            {
                "choices": [
                    {
                        "message": {
                            "content": """```json
{
  "parsed_articles": [
    {
      "article_number": "11",
      "article_title": "Interest",
      "income_type": "interest",
      "summary": "Treaty treatment for interest between the two jurisdictions.",
      "article_notes": ["Beneficial ownership may matter."],
      "paragraphs": [
        {
          "paragraph_number": "2",
          "source_reference": "Article 11(2)",
          "text": "However, such interest may also be taxed in the first-mentioned State, but the tax shall not exceed 10 per cent of the gross amount of the interest.",
          "rules": [
            {
              "rule_type": "withholding_tax_cap",
              "rate": "10%",
              "direction": "bidirectional",
              "conditions": ["Treaty applicability depends on the facts of the payment."],
              "review_reason": "Final eligibility depends on facts outside the current review scope.",
              "extraction_confidence": 0.91
            }
          ]
        }
      ]
    }
  ]
}
```"""
                        }
                    }
                ]
            }
        ),
    )

    payload = llm_document_extractor.extract_source_payload_from_text(
        raw_text=(
            "Article 11 Interest\n"
            "2. However, such interest may also be taxed in the first-mentioned State, but the tax shall not exceed 10 per cent of the gross amount of the interest."
        ),
        document_id="cn-nl-interest-llm",
        title="China-Netherlands Tax Treaty Article 11",
        document_type="treaty_text",
        jurisdictions=["CN", "NL"],
        source_language="en",
        config=config,
    )

    dataset_builder.validate_source_payload(payload)
    dataset = dataset_builder.build_dataset(payload)

    assert dataset["articles"][0]["article_number"] == "11"
    assert dataset["articles"][0]["paragraphs"][0]["rules"][0]["rate"] == "10%"
    assert dataset["articles"][0]["paragraphs"][0]["source_reference"] == "Article 11(2)"


def test_extract_source_payload_backfills_rate_from_paragraph_text_when_model_leaves_na(monkeypatch):
    config = llm_document_extractor.LLMInputParserConfig(
        api_key="test-key",
        base_url="https://example.com",
        model="deepseek-chat",
        timeout_seconds=5,
    )
    monkeypatch.setattr(
        llm_document_extractor.request,
        "urlopen",
        lambda req, timeout: FakeHTTPResponse(
            {
                "choices": [
                    {
                        "message": {
                            "content": json.dumps(
                                {
                                    "parsed_articles": [
                                        {
                                            "article_number": "12",
                                            "article_title": "Royalties",
                                            "income_type": "royalties",
                                            "summary": "Treaty treatment for royalties between the two jurisdictions.",
                                            "article_notes": [],
                                            "paragraphs": [
                                                {
                                                    "paragraph_number": "2",
                                                    "source_reference": "Article 12(2)",
                                                    "text": "However, such royalties may also be taxed in the first-mentioned State, but the tax so charged shall not exceed 10 per cent of the gross amount of the royalties.",
                                                    "rules": [
                                                        {
                                                            "rule_type": "rate_limitation",
                                                            "rate": "N/A",
                                                            "direction": "payer_to_payee",
                                                            "conditions": [],
                                                            "review_reason": "Specific rate cap on source State taxation of royalties",
                                                            "extraction_confidence": 0.98,
                                                        }
                                                    ],
                                                }
                                            ],
                                        }
                                    ]
                                }
                            )
                        }
                    }
                ]
            }
        ),
    )

    payload = llm_document_extractor.extract_source_payload_from_text(
        raw_text=(
            "Article 12 Royalties\n"
            "2. However, such royalties may also be taxed in the first-mentioned State, but the tax so charged shall not exceed 10 per cent of the gross amount of the royalties."
        ),
        document_id="cn-nl-royalties-llm",
        title="China-Netherlands Tax Treaty Article 12",
        document_type="treaty_text",
        jurisdictions=["CN", "NL"],
        source_language="en",
        config=config,
    )

    assert (
        payload["parsed_articles"][0]["paragraphs"][0]["extracted_rules"][0]["rate"] == "10%"
    )
    assert payload["parsed_articles"][0]["paragraphs"][0]["extracted_rules"][0][
        "conditions"
    ] == [
        "The treaty rate cap applies only if the payment qualifies for treaty treatment.",
        "The stated cap applies to the gross amount of the payment.",
    ]


def test_extract_source_payload_backfills_more_actionable_defaults_for_taxation_right_rules(
    monkeypatch,
):
    config = llm_document_extractor.LLMInputParserConfig(
        api_key="test-key",
        base_url="https://example.com",
        model="deepseek-chat",
        timeout_seconds=5,
    )
    monkeypatch.setattr(
        llm_document_extractor.request,
        "urlopen",
        lambda req, timeout: FakeHTTPResponse(
            {
                "choices": [
                    {
                        "message": {
                            "content": json.dumps(
                                {
                                    "parsed_articles": [
                                        {
                                            "article_number": "12",
                                            "article_title": "Royalties",
                                            "income_type": "royalties",
                                            "summary": "Treaty treatment for royalties between the two jurisdictions.",
                                            "article_notes": [],
                                            "paragraphs": [
                                                {
                                                    "paragraph_number": "1",
                                                    "source_reference": "Article 12(1)",
                                                    "text": "Royalties arising in one of the States and paid to a resident of the other State may be taxed in that other State.",
                                                    "rules": [
                                                        {
                                                            "rule_type": "taxation_right",
                                                            "rate": "N/A",
                                                            "direction": "bidirectional",
                                                            "conditions": [],
                                                            "review_reason": "",
                                                            "extraction_confidence": 0.95,
                                                        }
                                                    ],
                                                }
                                            ],
                                        }
                                    ]
                                }
                            )
                        }
                    }
                ]
            }
        ),
    )

    payload = llm_document_extractor.extract_source_payload_from_text(
        raw_text=(
            "Article 12 Royalties\n"
            "1. Royalties arising in one of the States and paid to a resident of the other State may be taxed in that other State."
        ),
        document_id="cn-nl-royalties-llm",
        title="China-Netherlands Tax Treaty Article 12",
        document_type="treaty_text",
        jurisdictions=["CN", "NL"],
        source_language="en",
        config=config,
    )

    rule = payload["parsed_articles"][0]["paragraphs"][0]["extracted_rules"][0]
    assert rule["conditions"] == [
        "This paragraph allocates taxing rights between the treaty jurisdictions.",
        "This paragraph does not by itself state a reduced withholding cap.",
    ]
    assert rule["review_reason"] == (
        "Taxing-right paragraph extracted for context; a separate rate-bearing paragraph may still control the treaty cap."
    )


def test_extract_source_payload_treats_source_tax_limit_as_rate_bearing_limit_rule(
    monkeypatch,
):
    config = llm_document_extractor.LLMInputParserConfig(
        api_key="test-key",
        base_url="https://example.com",
        model="deepseek-chat",
        timeout_seconds=5,
    )
    monkeypatch.setattr(
        llm_document_extractor.request,
        "urlopen",
        lambda req, timeout: FakeHTTPResponse(
            {
                "choices": [
                    {
                        "message": {
                            "content": json.dumps(
                                {
                                    "parsed_articles": [
                                        {
                                            "article_number": "12",
                                            "article_title": "Royalties",
                                            "income_type": "royalties",
                                            "summary": "Treaty treatment for royalties between the two jurisdictions.",
                                            "article_notes": [],
                                            "paragraphs": [
                                                {
                                                    "paragraph_number": "2",
                                                    "source_reference": "Article 12(2)",
                                                    "text": "However, such royalties may also be taxed in the first-mentioned State, but the tax so charged shall not exceed 10 per cent of the gross amount of the royalties.",
                                                    "rules": [
                                                        {
                                                            "rule_type": "source_tax_limit",
                                                            "rate": "10%",
                                                            "direction": "payer_to_payee",
                                                            "conditions": [],
                                                            "review_reason": "",
                                                            "extraction_confidence": 0.98,
                                                        }
                                                    ],
                                                }
                                            ],
                                        }
                                    ]
                                }
                            )
                        }
                    }
                ]
            }
        ),
    )

    payload = llm_document_extractor.extract_source_payload_from_text(
        raw_text=(
            "Article 12 Royalties\n"
            "2. However, such royalties may also be taxed in the first-mentioned State, but the tax so charged shall not exceed 10 per cent of the gross amount of the royalties."
        ),
        document_id="cn-nl-royalties-llm",
        title="China-Netherlands Tax Treaty Article 12",
        document_type="treaty_text",
        jurisdictions=["CN", "NL"],
        source_language="en",
        config=config,
    )

    rule = payload["parsed_articles"][0]["paragraphs"][0]["extracted_rules"][0]
    assert rule["conditions"] == [
        "The treaty rate cap applies only if the payment qualifies for treaty treatment.",
        "The stated cap applies to the gross amount of the payment.",
    ]
    assert rule["review_reason"] == (
        "Rate cap extracted from the paragraph text at 10%; treaty eligibility still requires fact review."
    )


def test_extract_source_payload_preserves_multiple_dividend_rate_branches(monkeypatch):
    config = llm_document_extractor.LLMInputParserConfig(
        api_key="test-key",
        base_url="https://example.com",
        model="deepseek-chat",
        timeout_seconds=5,
    )
    monkeypatch.setattr(
        llm_document_extractor.request,
        "urlopen",
        lambda req, timeout: FakeHTTPResponse(
            {
                "choices": [
                    {
                        "message": {
                            "content": json.dumps(
                                {
                                    "parsed_articles": [
                                        {
                                            "article_number": "10",
                                            "article_title": "Dividends",
                                            "income_type": "dividends",
                                            "summary": "Treaty treatment for dividends between the two jurisdictions.",
                                            "article_notes": [],
                                            "paragraphs": [
                                                {
                                                    "paragraph_number": "2",
                                                    "source_reference": "Article 10(2)",
                                                    "text": (
                                                        "However, such dividends may also be taxed in the State "
                                                        "of source, but the tax so charged shall not exceed 10 per cent "
                                                        "of the gross amount of the dividends. Such tax shall not exceed "
                                                        "5 per cent if the beneficial owner is a company that directly "
                                                        "holds at least 25 per cent of the capital of the company paying "
                                                        "the dividends."
                                                    ),
                                                    "rules": [
                                                        {
                                                            "rule_type": "source_tax_limit",
                                                            "rate": "10%",
                                                            "direction": "payer_to_payee",
                                                            "conditions": [
                                                                "General dividend branch when no reduced-rate ownership condition is established."
                                                            ],
                                                            "review_reason": "General dividend branch.",
                                                            "extraction_confidence": 0.97,
                                                        },
                                                        {
                                                            "rule_type": "source_tax_limit",
                                                            "rate": "5%",
                                                            "direction": "payer_to_payee",
                                                            "conditions": [
                                                                "Reduced dividend branch if the beneficial owner is a company directly holding at least 25 per cent of the capital of the payer."
                                                            ],
                                                            "review_reason": "Reduced-rate dividend branch tied to the ownership threshold.",
                                                            "extraction_confidence": 0.95,
                                                        },
                                                    ],
                                                }
                                            ],
                                        }
                                    ]
                                }
                            )
                        }
                    }
                ]
            }
        ),
    )

    payload = llm_document_extractor.extract_source_payload_from_text(
        raw_text=(
            "Article 10 Dividends\n"
            "2. However, such dividends may also be taxed in the State of source, but the tax so charged "
            "shall not exceed 10 per cent of the gross amount of the dividends. Such tax shall not exceed "
            "5 per cent if the beneficial owner is a company that directly holds at least 25 per cent of the capital "
            "of the company paying the dividends."
        ),
        document_id="cn-nl-dividends-llm",
        title="China-Netherlands Tax Treaty Article 10",
        document_type="treaty_text",
        jurisdictions=["CN", "NL"],
        source_language="en",
        config=config,
    )

    rules = payload["parsed_articles"][0]["paragraphs"][0]["extracted_rules"]
    assert len(rules) == 2
    assert [rule["rate"] for rule in rules] == ["10%", "5%"]
    assert rules[0]["is_primary_candidate"] is True
    assert rules[1]["is_primary_candidate"] is False
    assert rules[0]["conditions"] == [
        "General dividend branch when no reduced-rate ownership condition is established."
    ]
    assert rules[1]["conditions"] == [
        "Reduced dividend branch if the beneficial owner is a company directly holding at least 25 per cent of the capital of the payer."
    ]


def test_extract_source_payload_repairs_enumerated_dividend_branches_from_paragraph_text(
    monkeypatch,
):
    config = llm_document_extractor.LLMInputParserConfig(
        api_key="test-key",
        base_url="https://example.com",
        model="deepseek-chat",
        timeout_seconds=5,
    )
    monkeypatch.setattr(
        llm_document_extractor.request,
        "urlopen",
        lambda req, timeout: FakeHTTPResponse(
            {
                "choices": [
                    {
                        "message": {
                            "content": json.dumps(
                                {
                                    "parsed_articles": [
                                        {
                                            "article_number": "10",
                                            "article_title": "Dividends",
                                            "income_type": "dividends",
                                            "summary": "Treaty treatment for dividends between the two jurisdictions.",
                                            "article_notes": [],
                                            "paragraphs": [
                                                {
                                                    "paragraph_number": "2",
                                                    "source_reference": "Article 10(2)",
                                                    "text": (
                                                        "However, such dividends may also be taxed in the State of source, "
                                                        "but the tax so charged shall not exceed: (a) 5 per cent of the gross "
                                                        "amount of the dividends if the beneficial owner is a company which "
                                                        "holds directly at least 25 per cent of the capital of the company paying "
                                                        "the dividends; (b) 10 per cent of the gross amount of the dividends in all other cases."
                                                    ),
                                                    "rules": [
                                                        {
                                                            "rule_type": "withholding_tax_limit",
                                                            "rate": "5%",
                                                            "direction": "payer_to_payee",
                                                            "conditions": [],
                                                            "review_reason": "",
                                                            "extraction_confidence": 0.9,
                                                        },
                                                        {
                                                            "rule_type": "withholding_tax_limit",
                                                            "rate": "5%",
                                                            "direction": "payer_to_payee",
                                                            "conditions": [],
                                                            "review_reason": "",
                                                            "extraction_confidence": 0.9,
                                                        },
                                                    ],
                                                }
                                            ],
                                        }
                                    ]
                                }
                            )
                        }
                    }
                ]
            }
        ),
    )

    payload = llm_document_extractor.extract_source_payload_from_text(
        raw_text=(
            "Article 10 Dividends\n"
            "2. However, such dividends may also be taxed in the State of source, but the tax so charged "
            "shall not exceed: (a) 5 per cent of the gross amount of the dividends if the beneficial owner "
            "is a company which holds directly at least 25 per cent of the capital of the company paying "
            "the dividends; (b) 10 per cent of the gross amount of the dividends in all other cases."
        ),
        document_id="cn-nl-dividends-llm",
        title="China-Netherlands Tax Treaty Article 10",
        document_type="treaty_text",
        jurisdictions=["CN", "NL"],
        source_language="en",
        config=config,
    )

    rules = payload["parsed_articles"][0]["paragraphs"][0]["extracted_rules"]
    assert [rule["rate"] for rule in rules] == ["5%", "10%"]
    assert rules[0]["conditions"] == [
        "If the beneficial owner is a company which holds directly at least 25 per cent of the capital of the company paying the dividends."
    ]
    assert rules[1]["conditions"] == [
        "In all other cases."
    ]


def test_extract_source_payload_from_text_raises_on_invalid_response_shape(monkeypatch):
    config = llm_document_extractor.LLMInputParserConfig(
        api_key="test-key",
        base_url="https://example.com",
        model="deepseek-chat",
        timeout_seconds=5,
    )
    monkeypatch.setattr(
        llm_document_extractor.request,
        "urlopen",
        lambda req, timeout: FakeHTTPResponse({"choices": []}),
    )

    with pytest.raises(llm_document_extractor.LLMDocumentExtractionError):
        llm_document_extractor.extract_source_payload_from_text(
            raw_text="Article 12 Royalties\n1. Royalties ...",
            document_id="cn-nl-article12-llm",
            title="China-Netherlands Tax Treaty Article 12",
            document_type="treaty_text",
            jurisdictions=["CN", "NL"],
            source_language="en",
            config=config,
        )
