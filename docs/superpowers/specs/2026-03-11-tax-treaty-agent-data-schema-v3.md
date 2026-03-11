# Tax Treaty Agent Data Schema v3

Date: 2026-03-11
Status: Approved for implementation

## Goal

Upgrade the treaty dataset from article-centered seed data to an ingestion-ready structure that can later accept semi-automated extraction from official treaty text.

v3 keeps the frontend API readable while shifting the data model toward:

- traceable source anchors
- paragraph-level segmentation
- rule-level applicability logic
- future import-pipeline compatibility

## Why v3 Exists

v2 improved the project by moving from answer records to `treaty -> article -> rate_rules`.

That is already better than hand-written answers, but it is still too shallow for a reusable treaty knowledge layer because:

- source anchors live only as free-form excerpts
- paragraph boundaries are missing
- rule provenance is too implicit
- future extraction from official text would still require reshaping the data

v3 adds the missing middle layer:

- `treaty -> article -> paragraph -> rule`

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
- `source_documents`
- `notes`

Purpose:

- identify the treaty package
- keep provenance metadata close to the dataset
- prepare for future multi-document ingestion

## `articles[]`

Each article should contain:

- `article_number`
- `article_title`
- `article_label`
- `income_type`
- `summary`
- `notes`
- `paragraphs`

Purpose:

- keep the legal article as the stable top-level unit
- separate article identity from paragraph-level source anchors

## `paragraphs[]`

Each paragraph should contain:

- `paragraph_id`
- `paragraph_label`
- `source_reference`
- `source_excerpt`
- `rules`

Purpose:

- preserve paragraph boundaries from the source document
- provide a clean anchor for future citations and import tooling

## `rules[]`

Each rule should contain:

- `rule_id`
- `rule_type`
- `rate`
- `direction`
- `conditions`
- `human_review_required`
- `review_reason`

Purpose:

- keep decision logic independent from article and paragraph metadata
- allow multiple rules to coexist under one paragraph later

## Backend Mapping Rule

The backend should:

1. identify `income_type`
2. find the matching article
3. inspect its paragraphs
4. select the applicable rule
5. shape the frontend response using article identity plus paragraph-level source anchors

This keeps the UI contract understandable while moving the dataset closer to a general treaty knowledge pipeline.

## Why This Helps Future Ingestion

v3 is designed so that future pipeline steps can map naturally into the schema:

1. official text acquisition
2. article segmentation
3. paragraph segmentation
4. rule extraction
5. human review
6. dataset validation

That means v3 is not just a prettier JSON file. It is the intended target structure for later semi-automated import work.
