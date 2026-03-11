# Project Memory

Last updated: 2026-03-11

## Identity

- Project name: `Tax Treaty Agent`
- Repo path: `D:/AI_Projects/first agent`
- Project type: public-facing AI tool / GitHub portfolio project

## Primary Goal

Create a GitHub-worthy project that shows the ability to translate international tax business logic into a practical AI system.

Original project motivation:

- this project started as a way to build toward an `AI + international tax` direction that fits the user's long-term career interest
- the initial product idea was: a user inputs a cross-border transaction scenario, and the system identifies the likely treaty article, rate, and caution points
- the repo should keep serving that original intent: prove the user can turn a real international-tax problem into a credible AI system, not just produce a polished generic demo

## Positioning

Target signal:

- understands international tax context
- can use AI and vibe coding effectively
- can turn business logic into a usable system

This repo should not drift toward:

- generic chatbot experiments
- broad legal-tech platform ambitions
- engineering complexity that does not improve the demo

Public-facing product identity:

- a cross-border payment treaty pre-review tool
- bounded, source-aware, and conservative
- not a final tax opinion engine

Internal project-selection goal:

- optimize the repo to become a strong GitHub and resume project
- keep that internal criterion out of public-facing product copy

Important balancing rule:

- GitHub presentation matters, but it should not outrank making the product genuinely useful for a narrow real workflow
- expansion control matters: prefer staged completion over “keep adding forever,” and prefer small real pipeline advances over repeated local polish

## Recommended Product Shape

- frontend web shell
- backend API
- structured treaty data
- bounded output format

## Release Strategy

Recommended release style:

- semi-public open source

Public:

- code
- docs
- architecture explanation
- sample data
- screenshots or demo assets

Not required in v1:

- all raw source materials
- full production hardening
- heavy enterprise workflow complexity

## MVP Scope

Country pair:

- China-Netherlands only

Transaction types:

- dividends
- interest
- royalties

Interaction:

- single-turn scenario input

Required output sections:

- applicable treaty
- likely article
- tax rate
- conditions
- caution notes
- whether human review is recommended

## Architecture Direction

Preferred path:

- A version: small-data, real-architecture MVP
- B version: real-treaty-driven upgrade

Current B-stage direction:

- move from result-centered treaty entries to article-centered treaty data
- keep the frontend API stable while upgrading the data and matcher layers
- v3 should evolve toward ingestion-ready treaty data with paragraph-level anchors and rule-level source traceability
- the first import boundary is now `source_documents -> builder script -> generated v3 dataset`
- source fixtures should increasingly resemble parser output rather than flat hand-written segments
- parser metadata worth preserving in this layer includes source language and rule extraction confidence
- confidence tiering should be allowed to change product behavior, including withholding automatic conclusions when extraction confidence is very low
- for supported cases, the product should help users act by returning concrete next-step verification items, not only abstract review warnings
- for unsupported or incomplete cases, the product should return repair guidance with missing fields and example rewrites, not just a rejection message
- for supported cases, the UI should lead with a short conclusion-style summary before the detailed evidence rows
- when a single payer or payee segment mentions multiple countries, the parser should return `incomplete` rather than guessing from keyword order
- for supported cases, keep `key_missing_facts` separate from `review_checklist`: one explains why confidence is limited, the other tells the user what to verify next
- example prompts should be organized by product state so a first-time user can understand the system boundary without inventing their own test cases
- supported results should explicitly explain that they are first-pass pre-reviews, not final eligibility determinations, and old `v1 scope` wording should be normalized to clearer `current review scope` language
- supported results should also compress review state into a one-line immediate action recommendation so users do not have to infer next handling steps from longer review text
- within the narrow MVP, the parser can safely treat a few common business labels such as `软件许可费`, `软件授权费`, `技术授权费`, and `品牌费` as royalty-like inputs rather than rejecting them outright
- when repair guidance touches business wording aliases, the product should bridge from the user's label into the formal treaty category instead of fully mirroring casual phrasing; templates should stay more official than chatty
- unsupported and incomplete results should also carry a one-line immediate action so failure states remain operational rather than reading like a dead-end error page
- the import boundary has now moved one step closer to real parser output: paragraphs can carry ordered `source_segments` with page hints and source kinds, and rules can declare `derived_from_segments` lineage
- the import stub now supports multiple candidate rules under one paragraph, with `candidate_rank` and `is_primary_candidate` so the current matcher can stay stable while future parser outputs grow richer
- generated paragraphs now also carry a small provenance summary (`primary_rule_id`, paragraph confidence, segment coverage) so later document-ingestion work can reason about paragraph completeness without changing the current API surface
- source segments now also preserve `text_quality` and `normalization_status`, which gives the import boundary a place to hold OCR/cleanup risk signals before any frontend contract needs to change
- the repo now has its first live `raw text -> parser-like fixture -> generated dataset` path via a narrow raw-text stub parser, which is the first real step beyond hand-authored source JSON
- that raw-text entry path now also has a multi-article / multi-paragraph sample, so the parser stub is no longer only proving a single-paragraph Article 12 happy path
- the raw-text stub parser should stay narrow but not brittle: blank lines, missing optional notes, and comment lines are acceptable input noise
- the raw-text entry path now also has a one-command orchestration script, which is useful because future document ingestion should feel like a workflow step rather than two manual script hops
- that one-command orchestration script now also emits a short ingest report, so the narrow text-entry workflow exposes counts and warning/normalization signals instead of only writing files
- the ingest report is no longer only numeric: it now includes overall status and paragraph-level attention items, and failed ingests also emit structured error reports instead of disappearing into stderr only
- raw-text source segments now also preserve `raw_line_number`, so later debugging and provenance review can point back to exact input lines instead of only paragraph labels or page hints
- the raw-text parser is no longer limited to tagged pseudo-parser lines: it now also accepts one narrow semi-structured treaty-text style with `Article ...` headings and numbered paragraphs, which is a more realistic bridge toward future PDF/text ingestion
- the repo now also has its first narrow text-PDF ingestion path: extractable-text PDFs can be converted into raw treaty text and then fed through the same parser-like ingest chain; OCR is still intentionally out of scope

Important rule:

- A must not be a fake hardcoded toy
- A should already use real boundaries, real schema, and real refusal behavior

## Trust Guardrails

- The model may help parse and phrase answers, but not invent rates.
- Treaty facts should live in structured data.
- Unsupported cases should refuse or recommend review.
- This should feel like a professional tool, not a casual chatbot.

## Current Durable Working Surface

- `docs/superpowers/specs/2026-03-11-tax-treaty-agent-design.md`
- `docs/superpowers/specs/2026-03-11-tax-treaty-agent-alignment-roadmap-design.md`
- `docs/superpowers/specs/2026-03-11-tax-treaty-agent-import-stub-design.md`
- `docs/superpowers/plans/2026-03-11-tax-treaty-agent-implementation-plan.md`
- `docs/superpowers/plans/2026-03-11-tax-treaty-agent-phase-a-checklist.md`
- `AGENTS.md`
- `.codex/project-status.md`

## Likely Future Working Surface

- `frontend/`
- `backend/`
- `data/`
- `README.md`


