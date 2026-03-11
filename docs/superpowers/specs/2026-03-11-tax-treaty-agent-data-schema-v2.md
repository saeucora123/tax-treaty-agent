# Tax Treaty Agent Data Schema v2

Date: 2026-03-11
Status: Approved for implementation

## Goal

Move the project from result-centered seed data toward treaty-centered structured data without changing the frontend API contract.

This version is intended to be:

- closer to real treaty structure
- easier to extend later
- compatible with future source excerpts and richer rule logic

## Why v2 Exists

The original `cn-nl.v1.json` is useful for a fast MVP, but each record is already a summarized answer.

That makes it weak for:

- richer conditions
- multiple rules under one article
- source anchoring
- future PDF or RAG expansion

v2 shifts the data model from:

- `transaction_type -> answer`

to:

- `treaty -> article -> rate_rules`

## High-Level Shape

```json
{
  "treaty": {},
  "articles": []
}
```

## Top-Level `treaty`

Recommended fields:

- `treaty_id`
- `jurisdictions`
- `title`
- `version`
- `source_type`
- `notes`

Purpose:

- identify the treaty package
- describe where the structured data came from
- support future versioning and provenance notes

## `articles[]`

Each supported article should contain:

- `article_number`
- `article_title`
- `income_type`
- `summary`
- `source_excerpt`
- `notes`
- `rate_rules`

Purpose:

- treat the article as the main legal unit
- keep article-level knowledge separate from rule-level applicability logic

## `rate_rules[]`

Each rule should contain:

- `rule_id`
- `rate`
- `direction`
- `conditions`
- `human_review_required`
- `review_reason`

Purpose:

- allow multiple rate rules under a single article later
- separate rule matching from article identification

## Direction

For the current MVP, use:

- `bidirectional`

Later versions may support:

- `CN_to_NL`
- `NL_to_CN`
- other direction-specific variants

## Source Excerpts

`source_excerpt` should be short, readable, and treated as a structured anchor rather than a full-source dump.

Purpose:

- prepare the system for source-grounded UI later
- support future explainability features

## Example Shape

```json
{
  "treaty": {
    "treaty_id": "cn-nl",
    "jurisdictions": ["CN", "NL"],
    "title": "China-Netherlands Tax Treaty",
    "version": "v2",
    "source_type": "manual_structured_from_official_text",
    "notes": [
      "v2 is article-centered rather than result-centered"
    ]
  },
  "articles": [
    {
      "article_number": "12",
      "article_title": "Royalties",
      "income_type": "royalties",
      "summary": "Defines treaty treatment for royalties between the two jurisdictions.",
      "source_excerpt": "...",
      "notes": [
        "Beneficial ownership and factual qualification may matter"
      ],
      "rate_rules": [
        {
          "rule_id": "cn-nl-art12-base",
          "rate": "10%",
          "direction": "bidirectional",
          "conditions": [
            "Treaty applicability depends on transaction facts"
          ],
          "human_review_required": true,
          "review_reason": "Final eligibility depends on facts beyond MVP scope"
        }
      ]
    }
  ]
}
```

## Backend Mapping Rule

The backend should:

1. identify `income_type`
2. find the matching article
3. select the applicable `rate_rule`
4. shape the frontend response from that rule

This keeps the frontend contract stable while upgrading the data layer underneath.

## B1 Scope

For the first v2 file, include only:

- Article 10 Dividends
- Article 11 Interest
- Article 12 Royalties

Each article should include:

- article metadata
- one bidirectional rate rule
- one short source excerpt
- article notes

## Not Yet Included

v2 does not yet require:

- full treaty text
- PDF chunking
- vector search
- article cross-references
- multi-country standardization

Those belong in later B-stage upgrades.
