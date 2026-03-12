# China-Netherlands Source Governance Design

Date: 2026-03-12  
Status: Implemented

## Goal

Close the biggest credibility gap around the current China-Netherlands MVP:

- where the treaty text actually comes from
- which source is the current runtime basis
- which sources are historical or MLI context only
- which repo artifacts are curated subsets versus LLM-generated demo outputs

This slice is intentionally narrow. It does **not** attempt to build a crawler, downloader, or OCR pipeline.

## Why This Slice Matters

The repo has already proven two valuable things:

- a constrained runtime LLM lane can route natural-language inputs into treaty lookup
- an offline constrained LLM lane can turn clean treaty text into generated datasets

What was still too fuzzy was the source layer. Without a clear source-governance package, a fair reviewer could still ask:

- are these treaty texts official?
- which version is the project really using?
- where does MLI fit?
- are the clean text samples just hand-made excerpts with no durable provenance?

This slice answers those questions directly.

## Scope

Add:

- a machine-readable official source registry for the China-Netherlands treaty line
- a machine-readable artifact usage map tying repo assets back to official source ids
- a small validation test so the registry cannot silently drift into broken references

Do not add:

- automatic downloading
- automatic source discovery
- OCR
- multi-country source governance
- legal-opinion logic about which text prevails in every edge case

## Output Files

### 1. Official Source Registry

`data/source_registry/cn-nl-official-sources.json`

This registry records the current source universe for the China-Netherlands line, including:

- China-side official tax pages
- China-side official treaty PDFs
- China-side MLI synthesized texts
- Dutch treaty-database metadata pages
- Dutch consolidated treaty text
- Dutch official gazette references for signature / entry-into-force history

### 2. Source Usage Map

`data/source_registry/cn-nl-source-usage-map.json`

This file answers a different question:

- which repo artifacts currently derive from which official sources?

That matters because the repo mixes several kinds of assets:

- clean text samples
- parsed source payloads
- generated datasets
- stable curated runtime data

These should not all be described the same way.

### 3. Validation Test

`backend/tests/test_source_registry.py`

The test locks two useful invariants:

- the registry must keep both primary treaty-text anchors and MLI context anchors
- the usage map must only point at known source ids and existing repo artifacts

### 4. Catalog-Level Source Validation

`scripts/ingest_source_catalog_stub.py`

The catalog ingest path now also validates that every ingest entry declares a `source_id` that exists in the official registry.

That matters because this repo now wants to say more than:

- "this file was ingested"

It now also wants to say:

- "this file was ingested as a derivative of a specific official source record"

The current validation is intentionally narrow:

- every catalog entry must declare `source_id`
- that `source_id` must exist in `cn-nl-official-sources.json`
- the batch fails fast if a catalog source id is unknown

This is enough to connect source governance to ingestion without turning the repo into a source-management platform.

The ingest reports themselves now also preserve that `source_id`.

That matters because review artifacts should remain meaningful even when a developer opens one report file in isolation. A single report can now answer both:

- which ingest job ran
- which governed official source record it claims to derive from

## Registry Semantics

Each source entry records:

- `source_id`
- `title`
- `issuing_authority`
- `jurisdictions`
- `source_type`
- `official_url`
- `language`
- `status`
- `preferred_use`
- `notes`

The `preferred_use` field is intentionally practical rather than legalistic. It helps future sessions answer:

- should this source anchor the current runtime dataset?
- is this mainly governance/reference context?
- is this mainly MLI context?

It does **not** claim to replace a full treaty-law hierarchy analysis.

## Usage-Map Semantics

The usage map separates three artifact states:

- `verified_excerpt`
- `llm_generated_demo_artifact`
- `curated_subset`

This is important for honest project claims.

For example:

- clean text files are still curated excerpts
- generated Phase 2 datasets are still demo artifacts, even when they come from real model runs
- the stable runtime dataset is still a curated subset, not a complete source-governed treaty mirror

## Current Governance Position

After this slice, the repo can now say something much more precise:

- the current China-Netherlands runtime logic is grounded in a known set of official sources
- the repo distinguishes between treaty-text anchors and MLI context sources
- the current stable dataset is still curated
- the current LLM-generated datasets are still bounded proof artifacts, not the default production truth

That is the correct honesty level for the project at this stage.

## Next Likely Step

If source governance needs one more narrow advance later, the best next move is:

- connect the existing source-catalog ingest layer to `source_id` metadata

That would let raw text / PDF ingest entries explicitly declare which official source they came from, without yet forcing the repo into automated downloading or a larger source-management platform.
