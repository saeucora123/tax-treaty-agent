# Project Status

Last updated: 2026-03-11

## Current State

The repo started as a folder containing exported chat transcripts.

The project direction is now clarified and documented:

- build a public-facing `Tax Treaty Agent`
- use a simple web frontend plus backend API
- optimize for GitHub presentation, resume strength, and later expansion

The repo now also has a live implementation base:

- git initialized
- backend MVP skeleton created
- seed treaty data added
- first tests passing
- frontend demo shell added
- local browser demo verified
- parser behavior tightened for incomplete vs unsupported scenarios
- China-Netherlands scenarios now support direction-aware parsing (`CN -> NL` and `NL -> CN`)
- backend now reads article-centered treaty data from `cn-nl.v2.json`
- backend and frontend now expose treaty `source_excerpt` for supported results
- backend now reads ingestion-ready `cn-nl.v3.json` with `article -> paragraph -> rule` structure and exposes `source_reference`
- first import stub now builds `cn-nl.v3.generated.json` from `data/source_documents/cn-nl-main-treaty.json`
- import builder now rejects missing `source_reference` values and duplicate `rule_id` values before dataset generation
- source fixture now uses a parser-like nested shape: `parsed_articles -> paragraphs -> extracted_rules`
- import builder now also rejects unsupported `income_type` values before dataset generation
- generated v3 data now preserves `source_language` and `extraction_confidence`
- import builder now rejects out-of-range `extraction_confidence` values before dataset generation
- API and frontend now expose source quality metadata for supported results
- low-confidence supported matches now escalate to `high` review priority in API and UI
- supported results now include fixed next-step verification checklists by income type
- unsupported and incomplete results now include fixed repair guidance, including missing fields and suggested rewrite examples
- supported results now open with a one-sentence preliminary summary before the detailed record
- ambiguous country detection now falls back to `incomplete_scenario` instead of guessing from the first keyword hit
- supported results now distinguish between concrete next steps and the key missing facts that still block higher confidence
- live demo reference inputs now advertise only live-reachable product states (`Supported`, `Unsupported`, `Incomplete`) so the UI does not imply confidence-sensitive results that the default dataset does not trigger by scenario text alone
- supported results now include an explicit boundary note explaining that the output is a first-pass pre-review rather than a final eligibility conclusion, and user-facing wording no longer mixes product state with old `v1 scope` phrasing
- supported results now also include a one-line immediate action recommendation that compresses `review / priority review / hold` into a clearer next handling step
- the parser now recognizes a few common royalty-like business labels (`软件许可费`, `软件授权费`, `技术授权费`, `品牌费`) and maps them into the supported royalties lane instead of rejecting them as unknown transaction types
- incomplete/unsupported repair guidance can now show a short bridge note when a business term is normalized into a formal treaty category, while the rewrite template itself stays in the more official treaty wording
- unsupported and incomplete cards now also open with a one-line immediate action, so users can see the handling path before reading the repair details
- source-document fixtures now preserve ordered `source_segments` with `page_hint` and `source_kind`, and generated rules now carry `derived_from_segments` lineage so the import stub looks more like official-text cut segments feeding a parser output
- one paragraph can now retain multiple candidate rules in the import stub, while the current matcher explicitly prefers the primary candidate so API behavior stays stable
- generated paragraphs now include a `provenance_summary` with paragraph confidence and segment coverage, giving the import boundary an early notion of extraction completeness
- source segments now also preserve `text_quality` and `normalization_status`, so the import stub can distinguish clean/verbatim text from normalized or riskier text before that complexity reaches the product layer
- the repo now also has a narrow raw-text parser stub that turns a treaty text sample into the parser-like source fixture shape before the builder generates v3 treaty data
- the raw-text parser stub now also has a multi-article / multi-paragraph sample path, so the text-entry chain is no longer limited to a single Article 12 example
- the raw-text parser stub now tolerates a small amount of realistic authoring noise (blank lines, missing optional notes, comment lines) without widening into a general parser
- the raw-text chain now also has a one-command ingestion script that writes both the parser-like fixture and the generated dataset from the same raw text input
- that one-command ingestion script now also writes a short ingest report with document/article/paragraph/rule counts plus normalization and warning segment counts
- the ingest report now also exposes an overall status plus paragraph-level attention items, so the pipeline can point to risky extracted paragraphs instead of only returning aggregate counts
- failed raw-text ingests now also emit structured error reports with stage and message, while still refusing to write partial parsed/dataset outputs
- raw-text parser outputs now also preserve per-segment `raw_line_number`, and the generated dataset keeps that provenance so later debugging can jump back to exact input lines
- the raw-text parser now also supports one semi-structured treaty-text shape with `Article` headings and numbered paragraphs, so the text-entry chain is no longer limited to heavily tagged parser-style input
- the repo now also has a first narrow PDF entry path: a text-based PDF can be converted into extracted raw text and then run through the existing parser-like ingest workflow
- that PDF entry path now also cleans two common text-extraction issues before parsing: wrapped paragraph lines and repeated header/page-number noise
- the PDF path now also supports externally supplied document metadata, so a more realistic official-text PDF can enter the system without being pre-edited to include internal header lines
- that external PDF metadata can now also come from a manifest JSON file, so the document-ingest path is starting to resemble a maintainable source catalog rather than a one-off command
- the repo now also has a source-catalog batch ingest entrypoint, which can run mixed raw-text and text-PDF sources in one batch and emit a summary even when one source fails
- public product identity has now been explicitly realigned around “bounded treaty pre-review tool,” distinct from the internal GitHub/resume goal
- Phase 1 runtime LLM parsing is now user-auditable: when the LLM parser is used, responses can include a small `input_interpretation` block showing how payer/payee/income-type were read before treaty lookup
- backend tests are now guarded against accidental paid live-model calls: under `pytest`, DeepSeek config stays off unless explicitly re-enabled for a deliberate live smoke run
- the runtime LLM lane now also has a dedicated live smoke command, and a real DeepSeek run has already succeeded for a natural-language royalties scenario instead of only mocked tests
- the runtime LLM lane now also has explicit conservative-boundary coverage for incomplete, out-of-scope, and non-tax inputs, so Phase 1 no longer depends only on a happy-path smoke demo
- Phase 2 has now started in code too: a constrained offline LLM document-extraction path can read clean treaty text, generate a parser-like source payload, and flow it into a generated v3 dataset
- the current Phase 2 path has already succeeded once with a real DeepSeek run on clean Article 11/12 treaty text, producing an extracted source fixture plus generated dataset/report artifacts
- that Phase 2 lane is now also materially more product-compatible: obvious `10 per cent` rate caps can be backfilled from paragraph text during extraction, and the runtime matcher can prefer rate-bearing rules over earlier narrative paragraphs when reading generated datasets
- the generated `from-llm` dataset has now been smoke-checked directly against the analysis service, and a royalties scenario can resolve to `Article 12(2)` with a `10%` rate using LLM-generated treaty data
- runtime analysis now supports a controlled data-source switch: default requests still use the stable curated dataset, while an explicit `llm_generated` path can drive the same analysis flow from LLM-generated treaty data and report `data_source_used` in the response
- the Phase 2 extractor now also normalizes rule-quality semantics more defensively: taxation-right paragraphs and rate-cap paragraphs can both receive actionable default `conditions` / `review_reason` text, and rate-bearing aliases like `source_tax_limit` are treated as the same family as `rate_limitation` instead of slipping through with empty guidance
- the conservative runtime now also treats multi-rate treaty branches as a real ambiguity signal: if one article carries multiple distinct rate-bearing rules, the result escalates to `no auto conclusion` and can expose `alternative_rate_candidates` instead of quietly choosing one branch
- that ambiguity handling is now broader: the runtime also catches same-paragraph multi-rate candidates, so future LLM extractions do not need perfectly separated paragraphs to keep the review engine conservative

## Recent Decisions

- The project should be a bounded tool, not a free-form chatbot.
- The repo should aim for semi-public open source presentation.
- The first version should use `API + simple web shell`.
- The first version should be `A version`: small-data, real-architecture MVP.
- The `A -> B` evolution path is intentional:
  - A uses manually curated structured treaty data
  - B upgrades toward more complete real-treaty-driven retrieval
- MVP scope is intentionally narrow:
  - China-Netherlands only
  - dividends / interest / royalties only
- The parser should not default missing country context to `CN -> NL`.
- Incomplete scenarios and unsupported country pairs should be distinguished explicitly.
- Direction matters: payer/payee should be inferred from the text flow around `向`, not from keyword presence alone.
- B1 data direction is now article-centered:
  - treaty -> articles -> rate_rules
  - frontend contract stays stable while the data layer grows more realistic
- next data-layer direction is ingestion-ready:
  - treaty -> articles -> paragraphs -> rules
  - paragraph-level source anchors prepare the repo for future semi-automated import
- the first import boundary is intentionally narrow:
  - structured source segments stand in for future parser output
  - builder script proves the backend can consume generated v3 data
  - builder validation now blocks two high-risk data mistakes early: missing anchors and duplicate rule ids
  - fixture shape is now one step closer to a real parser handoff
  - parser metadata now survives generation instead of being discarded immediately
- some of that parser metadata is now user-visible instead of staying buried in the data layer
- low-confidence extracted data now changes product behavior instead of only changing display text
- confidence-tiered review now distinguishes routine review, priority review, and hold-from-auto-conclusion states
- first-step user guidance should prefer concrete verification items over abstract warnings
- unsupported flows should help the user repair the input instead of only refusing
- supported flows should start with a short conclusion-style summary before detailed evidence
- ambiguous input handling should prefer refusal and repair guidance over best-guess inference
- the product should explain not only what to check next, but also which missing facts prevent a stronger conclusion
- the demo surface should teach the product boundary quickly instead of relying on trial-and-error input exploration
- the product should say out loud that it provides a bounded preliminary review, not a final tax conclusion
- the result card should keep getting more operational: short action guidance should be easier to scan than narrative review text
- narrow input robustness improvements are worthwhile when they preserve the same treaty bucket and reduce avoidable user rejection without broadening scope
- “helpful” wording should still feel like a professional tool: acknowledge business phrasing, then steer it back into the official review lane
- failure states should feel like guided workflow steps, not dead ends
- the next document-ingestion upgrades should build on source-segment lineage rather than replacing it
- richer parser output should keep accumulating under the import boundary instead of leaking directly into frontend-facing contracts
- paragraph-level provenance is now part of that boundary, so later parser upgrades can stay under the data layer instead of forcing frontend rewrites
- segment-level provenance is starting to look like a real document pipeline instead of a hand-written JSON shortcut
- the project has now crossed from “hand-shaped import boundary” into “text can enter the system through a live parsing step,” even though that step is still a very narrow stub
- that live parsing step is still narrow, but it now demonstrates more than one article/paragraph shape instead of a one-off special case
- the parser-entry layer should now evolve by adding realistic narrow cases, not by turning into an unbounded text parser too early
- the text-entry workflow is now starting to look like a real bounded ingestion path instead of a bag of disconnected scripts
- the bounded ingestion path is now also auditable at a glance because it emits a lightweight report rather than only silent file outputs
- the ingestion path is now auditable in both success and failure cases, which makes it feel much closer to a real document-import workflow
- a semi-structured ingest sample now runs end-to-end with `status: ok`, which is the first live step toward “more official-looking text can enter the system” without jumping straight to PDF parsing
- a synthetic text-based PDF now also runs end-to-end through the new PDF ingest path, which is the first live proof that “PDF can enter the system” has started, even though OCR/scanned PDFs remain out of scope
- the PDF path is now slightly less toy-like because it no longer assumes perfectly clean extracted text on every page
- the PDF path is also less toy-like because it no longer assumes the official document body will already contain Codex-friendly metadata fields
- the ingest layer is also less toy-like because sources no longer need to be run one by one by hand to approximate a maintained document pipeline

## Active Direction

Use a staged roadmap:

- Phase 1: constrained LLM input understanding
- Phase 2: real document-driven data generation
- Phase 3: dynamic review guidance
- Phase 4: multi-country expansion

Current priority correction:

- do not let Phase A packaging work outrun product usefulness
- before more GitHub-polish work, re-evaluate how this tool can help in a narrow real workflow rather than only looking impressive as a portfolio piece
- future sessions should anchor decisions to the original motivation: this repo exists to help the user build toward an `AI + international tax` direction through a real bounded product, not just a polished showcase
- control expansion actively: after a meaningful checkpoint, prefer the next real pipeline advance over adjacent nice-to-have refinements
- the current active slice is Phase 1: connect a real but tightly constrained LLM input parser without letting the model touch treaty facts or rates

The concrete execution checklist for the current stage now lives in:

- `docs/superpowers/plans/2026-03-11-tax-treaty-agent-phase-a-checklist.md`

## Next Likely Work

1. Phase 1 is now effectively locked: supported natural-language routing works, the runtime path is auditable, and clearly bad inputs refuse conservatively without widening model authority.
2. Current mainline is now Phase 2: improve document-to-structured-data fidelity, especially extraction quality for rule typing, conditions, review reasons, and more complex rule branches.
3. The controlled `stable` vs `llm_generated` runtime switch now gives the repo a safe way to prove the full offline-to-online loop without handing the default demo path to uncertain AI data.
4. Avoid turning Phase 2 into orchestration sprawl; the next valuable gains are extraction quality and builder/runtime compatibility, not more wrappers.
5. Treat the end of Phase 2 as the likely best stop line for a high-value GitHub/resume project.

## Risks To Watch

- letting v1 sprawl beyond the narrow MVP
- using LLM output as fact instead of structured treaty data
- building a flashy demo that cannot later evolve into the B version
- over-optimizing code complexity before the first clean demo exists


