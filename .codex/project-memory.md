# Project Memory

Last updated: 2026-03-12

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

Gemini-aligned staged path to preserve:

- Phase 1: constrained LLM input understanding
- Phase 2: real document-to-structured-data generation
- Phase 3: dynamic review guidance only after phases 1-2 are real
- Phase 4: multi-country expansion last
- the best stop line for project value is around the end of Phase 2, not “keep building forever”

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
- the narrow text-PDF path now also handles two realistic cleanup cases before parsing: wrapped paragraph lines and simple repeated header/page-number noise
- the PDF ingest path no longer depends on the PDF body containing repo-specific metadata headers; maintainers can inject document metadata at the CLI boundary, which is closer to how real official source files will behave
- the PDF path can now also read that metadata from a small JSON manifest, which is a better long-lived maintenance shape than repeating CLI fields for every document
- the repo now also has a narrow source-catalog batch ingest path that can mix raw-text and text-PDF sources, write a batch summary, and keep going after individual source failures
- Phase 1 has now started in code: runtime input normalization can first attempt a constrained LLM structured-output path and falls back to the existing rule parser if unavailable or uncertain
- the constrained runtime LLM parser is now slightly hardened for real model behavior: it accepts fenced JSON content and the service layer normalizes common country-name outputs like `China` and `Netherlands` back into ISO-style routing codes before treaty lookup
- when the constrained runtime LLM parser is used, the API/UI should expose a small user-auditable `input_interpretation` block so the model's reading of payer/payee/income-type can be checked without exposing raw prompts or letting the model touch treaty facts
- automated test runs should not silently spend money or block on live model calls; runtime LLM config should stay off by default under `pytest` unless explicitly re-enabled for a deliberate live-parser test
- the repo now also has a dedicated live input-parser smoke path (`scripts/run_llm_input_smoke.py`) that reports whether the scenario truly flowed through the LLM parser or silently fell back to rules
- Phase 1 should be treated as “complete enough to stop” once the runtime LLM lane proves three things at once: supported natural-language routing works, clearly incomplete/out-of-scope cases refuse conservatively, and the model's reading can be audited without exposing raw prompt internals
- Phase 2 has now genuinely started: the repo has a constrained offline LLM document-extraction lane that can turn clean treaty text into a builder-compatible parser-like source payload and then into a generated v3 dataset
- in that Phase 2 lane, the model should stay responsible only for article/paragraph/rule extraction; document metadata injection, schema shaping, validation, and final dataset generation should remain deterministic local code
- Phase 2 extraction quality now has a concrete guiding rule: rate-bearing paragraphs matter more than narrative treaty paragraphs, so the pipeline should backfill obvious rate caps from paragraph text and the runtime matcher should prefer rules that actually carry usable rates
- runtime consumption of LLM-generated treaty data should stay feature-flagged: the stable curated dataset remains the default path, while `llm_generated` is an explicit opt-in lane used to prove the offline extraction pipeline can feed the conservative runtime engine without making the public demo brittle
- Phase 2 quality normalization should not rely on one exact model label: rate-bearing rule families such as `rate_limitation`, `source_tax_limit`, and `withholding_tax_cap` should be treated as the same semantic lane so conditions and review reasons remain usable when the model varies its taxonomy
- when one treaty article contains multiple distinct rate-bearing branches, the conservative runtime should not silently pick one and sound certain; it should surface alternative rate candidates and escalate to a no-auto-conclusion state until additional facts disambiguate the branch
- that branch-ambiguity rule should apply even when the model puts multiple rate candidates inside the same paragraph/rule cluster, not only when different paragraphs carry different rates
- a real Article 10 dividend branch sample is now part of the repo’s strongest Phase 2 proof: constrained DeepSeek extraction can produce a generated dataset with `5% / 10%` candidates, local repair logic can preserve distinct enumerated branch rates/conditions when the model partially collapses them, and the runtime can then refuse automatic conclusion and surface `alternative_rate_candidates` through the `llm_generated` lane without evaluating the ownership threshold itself
- branch-ambiguity UX should avoid anchoring the user on one selected rate: when multiple credible treaty rates remain, prefer a combined possible-rate display and filter out clearly low-confidence alternative candidates before escalating the runtime result
- runtime rule selection should not ignore direction once direction-specific treaty branches exist; when rules are marked with directional semantics, selection and alternative-rate collection should respect the current payer -> payee flow instead of only transaction type
- constrained runtime LLM parsing now also needs a deterministic second gate: if the scenario lacks minimal country/tax evidence or conflicts with simple rule-based evidence, the system should downgrade to `incomplete` instead of trusting a merely well-formed model parse
- explicit `llm_generated` runtime switching is now part of the API contract, so missing generated datasets should fail conservatively with a controlled unavailable-data-source response rather than throwing file errors
- UI wording should stay conservative even when the backend is already conservative: high-priority manual-review cases should not be framed as plain `SUPPORTED`, and branch-driven HOLD states should describe branch ambiguity instead of pretending the problem is always low confidence
- the current repo is no longer source-opaque: China-Netherlands now has a dedicated official-source registry plus artifact usage map, so future sessions should distinguish among official treaty anchors, MLI context texts, curated runtime subsets, and LLM-generated demo artifacts instead of speaking about “the treaty text” as one undifferentiated blob
- source governance is now lightly wired into the ingest layer itself: source-catalog entries must declare an official `source_id` that exists in the China-Netherlands source registry, which is the current narrow way to tie ingest jobs back to governed treaty sources without building a downloader platform
- per-source ingest reports should also retain `source_id`, not only the batch summary; otherwise source identity disappears once someone opens a single report file outside the catalog context
- within one extracted paragraph, primary-candidate selection should be semantic rather than positional: rate-bearing rules outrank leading narrative `taxation_right` rules, and narrative rules should not inherit paragraph-level rate backfills intended for cap-bearing branches
- runtime LLM guardrails should not be narrower than the repo's own accepted country aliases; if normalization accepts labels like `PRC`, `Holland`, or `Dutch`, the minimum-evidence footprint check should recognize them too instead of downgrading otherwise supported scenarios

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


