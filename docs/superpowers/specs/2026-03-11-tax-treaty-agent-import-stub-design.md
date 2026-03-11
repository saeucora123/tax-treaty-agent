# Tax Treaty Agent Import Stub Design

Date: 2026-03-11
Status: Implemented

## Goal

Add the first minimal bridge from source documents into the v3 treaty schema.

This slice is intentionally narrow:

- no PDF parsing yet
- no OCR yet
- no generic ingestion framework yet
- just enough structure to prove that source-aligned content can be transformed into a v3-compatible dataset

The import boundary now has two narrow entry forms:

- parser-like source JSON fixtures
- one raw-text stub that can be parsed into the same parser-like fixture shape
- one text-based PDF path that first extracts text, then reuses the same raw-text ingestion chain

The repo now also has a narrow orchestration script for the raw-text path:

- `raw text -> parser-like fixture -> generated dataset`
- kept as one command so the text-entry chain can be demonstrated as a workflow, not only as separate scripts
- the same command now also emits a short ingest report so the workflow is reviewable instead of silent

There is now also a narrow orchestration script for the PDF path:

- `text PDF -> extracted raw text -> parser-like fixture -> generated dataset`
- this path is intentionally limited to PDFs that already contain extractable text
- it is not OCR and does not claim to support scanned documents yet
- when the PDF text does not carry repo-specific metadata headers, the ingest command can inject document metadata at the CLI boundary instead of requiring the official text itself to be rewritten
- the same metadata can also be supplied via a small JSON manifest, which is closer to how a maintained source-document catalog would work

There is now also a narrow source-catalog batch script:

- it reads a small JSON catalog of source entries
- it can mix `raw_text` and `pdf_text` sources in one batch
- it writes a batch summary with per-source status instead of requiring each source to be ingested by hand
- failed sources do not prevent later sources from being attempted in the same batch

Phase 2 has now started with a separate constrained LLM document-extraction lane:

- clean treaty text can be sent to a real model for offline extraction
- the model is only responsible for article / paragraph / rule extraction
- document metadata and final parser-like fixture structure are still controlled locally
- the extracted source payload can then flow through the existing builder into a generated v3 dataset
- this is intentionally an offline data-production path, not a runtime fact-generation path

## Scope

Add:

- a `data/source_documents/` fixture for the China-Netherlands treaty
- a builder script that converts source segments into treaty `articles -> paragraphs -> rules`
- regression tests proving the generated dataset can be consumed by the current backend service

## Design Choice

Use a parser-like structured source-document fixture rather than raw treaty text.

Reason:

- keeps this step small and reliable
- establishes the handoff shape that a future parser should emit
- proves the data pipeline boundary before harder text-extraction work
- reduces one future migration step by aligning the fixture with `parsed_articles -> paragraphs -> extracted_rules`

## Output

The builder emits `cn-nl.v3.generated.json` with:

- `source_type: import_stub_from_source_documents`
- source-document metadata
- article-grouped treaty data
- paragraph-level anchors
- rule payloads compatible with the current matcher

The current fixture shape is:

- `document`
- `parsed_articles[]`
- `paragraphs[]`
- `source_segments[]`
- `extracted_rules[]`

The current preserved parser metadata is:

- `source_language` on each paragraph
- `provenance_summary` on each paragraph
- `extraction_confidence` on each extracted rule
- `segment_order`, `raw_line_number`, `page_hint`, and `source_kind` on each source segment
- `text_quality` and `normalization_status` on each source segment
- `derived_from_segments` on each extracted rule
- `candidate_rank` and `is_primary_candidate` on each extracted rule

The current paragraph provenance summary includes:

- `primary_rule_id`
- `paragraph_confidence`
- `segment_count`
- `covered_segment_count`
- `segment_coverage`

The builder validates that:

- `extraction_confidence` stays within `0..1`
- `derived_from_segments` only references known source segments
- duplicate source segment ids are rejected early
- one paragraph cannot declare multiple primary candidates
- segment-level provenance states stay within supported enums for `text_quality` and `normalization_status`

The current raw-text parser stub is intentionally narrow:

- it supports only one highly structured raw text format
- it is not a PDF parser
- it exists to prove `raw text -> parser-like fixture -> generated dataset` as a live chain
- it now tolerates blank lines, missing optional notes, and `#` comment lines so the stub format is not unnecessarily brittle
- it now also supports one semi-structured treaty-text style:
  - `Article <number> <title>` headings
  - numbered paragraph lines like `1. ...`
  - narrow rule derivation from paragraph text when an explicit rate phrase such as `10 per cent` appears

The current PDF extractor stub is also intentionally narrow:

- it only targets text-based PDFs
- it normalizes extracted text into the same raw-text entry lane
- it can now merge wrapped paragraph lines from extracted PDF text
- it can now drop repeated header lines and simple page-number noise such as `Page 1`
- if no extractable text is found, the PDF path fails conservatively instead of pretending OCR exists

The current LLM document-ingest path is intentionally narrow too:

- it targets clean treaty-text slices, not arbitrary long messy documents yet
- it is designed to prove `clean text -> LLM extracted source payload -> generated dataset`
- it keeps the model inside a bounded extraction role instead of letting the model define document metadata or runtime treaty facts
- the next quality focus in this lane should be extraction fidelity for rate-bearing paragraphs and rule prioritization, not more orchestration layers

The raw-text entry path now has two sample scales:

- a single-article Article 12 stub
- a multi-article / multi-paragraph stub proving the parser is no longer hard-wired to one paragraph shape
- a semi-structured treaty-text stub that is closer to official-looking article / paragraph prose than tagged parser input

The current ingestion report includes:

- `status`
- `document_id`
- `article_count`
- `paragraph_count`
- `rule_count`
- `source_segment_count`
- `normalized_segment_count`
- `warning_segment_count`
- `attention_item_count`
- `attention_items[]`

The ingestion script now also writes a structured error report on parse / validation / IO failure:

- failed runs still emit a small JSON artifact
- the report records `error_stage` and `error_message`
- failed runs do not write partial parsed or dataset outputs

## Next Likely Step

Add a richer parser-output layer next, such as segment-level OCR confidence, article-language metadata, or paragraph summaries derived from multiple evidence types.
