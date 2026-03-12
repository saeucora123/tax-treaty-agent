# GPT Research Audit Brief

Last updated: 2026-03-12

## What This Project Is

`Tax Treaty Agent` is a bounded international-tax treaty pre-review tool.

It is **not**:

- a final legal or tax opinion engine
- a generic chatbot
- a free-form tax agent

It is designed to show a credible `AI + international tax` system shape:

- narrow scope
- structured treaty facts
- conservative runtime behavior
- explicit refusal states
- source-aware outputs

## Current Scope

- Country pair: `China <-> Netherlands`
- Income types: `dividends`, `interest`, `royalties`
- Interaction: single-turn input

## Core Trust Model

- treaty facts must come from structured treaty data
- runtime LLM is allowed to interpret the user input, but not invent rates or treaty facts
- unsupported, incomplete, low-confidence, and branch-ambiguous cases must fail conservatively
- runtime default path stays on a stable curated dataset
- `llm_generated` is a controlled validation lane, not the default public-demo path

## Current Architecture

### Layer 1: Offline Data Grounding

Goal:

- turn treaty text into structured treaty data

Current path:

- clean treaty text
- constrained LLM extraction
- parser-like source payload
- generated dataset

Current characteristics:

- generated data keeps article / paragraph / rule structure
- source references and provenance survive generation
- rate-bearing paragraphs receive deterministic local repair in a few narrow cases when the LLM partially collapses obvious textual structure

### Layer 2: Conservative Runtime Engine

Goal:

- accept a natural-language cross-border payment scenario
- route it into structured treaty lookup
- return bounded pre-review output

Current path:

- user scenario
- constrained LLM input understanding
- normalized payer / payee / income type
- structured treaty lookup
- review / hold / incomplete / unsupported behavior

## What Is Already Real

### Phase 1 runtime

- real DeepSeek runtime input parser is connected
- user inputs can be mapped into:
  - `payer_country`
  - `payee_country`
  - `transaction_type`
- bad inputs refuse conservatively instead of being guessed
- API/UI can show `input_interpretation`, so model reading is user-auditable

### Phase 2 offline pipeline

- real constrained DeepSeek extraction is already wired into the repo
- clean treaty text can become:
  - parsed source JSON
  - generated treaty dataset
  - ingest report
- generated dataset can already drive the runtime engine through an explicit `llm_generated` data-source switch

## Strongest Concrete Proofs So Far

### Royalties proof

- clean Article 11 / 12 treaty text has been extracted with DeepSeek
- generated dataset has been consumed by runtime
- royalties scenario can resolve through the `llm_generated` lane to:
  - `Article 12(2)`
  - `10%`

### Dividend branch proof

The repo now also has a harder `Article 10` sample with dividend branches:

- one branch at `5%`
- one branch at `10%`

This is important because it proves more than “the model can find one rate”.

Current behavior:

- offline LLM extraction can generate branch candidates
- if the model partially collapses the enumerated branch text, a very narrow deterministic repair can restore the explicit `(a) 5% / (b) 10%` structure from the paragraph text
- runtime does **not** try to infer whether the ownership threshold is satisfied
- runtime does **not** silently choose one branch
- runtime instead returns:
  - `auto_conclusion_allowed = false`
  - `review_priority = high`
  - `alternative_rate_candidates`

This is currently one of the project’s strongest “credible AI system” proof points.

## What The Reviewer Should Look For

Please evaluate:

1. whether this is now a genuinely strong prototype or still too much “demo shell”
2. whether the offline-to-online loop is already convincing enough
3. which parts are real long-term system value vs transitional scaffolding
4. whether the project is now close to a high-value stop line for GitHub / resume use

## Recommended Files To Attach

### Context

- `README.md`
- `.codex/project-status.md`

### Runtime

- `backend/app/service.py`
- `backend/app/llm_input_parser.py`
- `backend/tests/test_analyze.py`

### Phase 2 extraction

- `backend/app/llm_document_extractor.py`
- `scripts/ingest_cn_nl_llm_text.py`
- `scripts/build_cn_nl_dataset.py`
- `backend/tests/test_llm_document_extractor.py`
- `backend/tests/test_llm_document_ingest.py`

### Real generated artifacts

- `data/raw_documents/cn-nl-article10-dividends-branch.clean.txt`
- `data/source_documents/cn-nl.article10.dividends-branch.llm.parsed.json`
- `data/treaties/cn-nl.v3.generated.article10-branch.from-llm.json`
- `data/treaties/cn-nl.v3.generated.article10-branch.from-llm.report.json`

## Current Review Question

The key question is no longer “is there any AI here?”

The key question is:

> Is this now a sufficiently strong, bounded, defensible AI system prototype that it should start shifting from core implementation into project-level consolidation and presentation?
