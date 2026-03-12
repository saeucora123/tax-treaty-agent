# Project Status

Last updated: 2026-03-13

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
- Phase 2 now has a real dividend-branch proof point too: a clean Article 10 sample with `5% / 10%` dividend branches can go through constrained DeepSeek extraction, be repaired into distinct branch rates/conditions when the model collapses them, and then drive the existing `no auto conclusion` runtime guard through the explicit `llm_generated` data-source path
- the multi-branch guard is now also less misleading and less noisy: runtime ignores low-confidence alternative-rate noise, and when a real branch ambiguity remains it no longer shows a single anchored rate but a combined possible-rate display instead
- the repo now also has a first formal China-Netherlands source-governance package: `data/source_registry/cn-nl-official-sources.json` records official China-side and Netherlands-side treaty/MLI/meta sources, while `data/source_registry/cn-nl-source-usage-map.json` ties current clean-text samples, generated datasets, and the stable runtime dataset back to those source ids
- that source-governance layer now also touches the ingest path: `ingest_source_catalog_stub.py` rejects catalog entries whose `source_id` is missing from the official China-Netherlands registry, so source catalog runs can no longer float free from governed source identity
- source-governed identity now also survives per-source report inspection: raw-text and PDF ingest reports can carry `source_id`, and source-catalog runs pass it through so a single report file still knows which official source record it claims to derive from
- README now leads with the two-layer architecture (`Offline Data Grounding` -> `Conservative Runtime Engine`), explicitly frames the strongest current proof point as the Article 10 dividend branch case, and surfaces source governance as a first-class part of the product story instead of burying it in implementation details
- the repo now also has a first detailed whitepaper draft (`2026-03-12-tax-treaty-agent-whitepaper.md`) that explains the project as a bounded professional AI system rather than a chatbot demo, with explicit sections on architecture, trust boundaries, source governance, proof case, and current limits
- the whitepaper layer is now bilingual at the repo level: alongside the English whitepaper, a standardized Chinese product whitepaper (`2026-03-12-tax-treaty-agent-whitepaper-zh.md`) now exists for external explanation, rehearsal, and future interview/storytelling use
- the repo now also has an execution-control layer beyond prose planning: a machine-readable stage file, gate-review stubs, an evidence-pack checklist, a progress ledger, and sync/check scripts now anchor stage discipline outside the chat context
- Stage 1 has now formally passed gate review: the repo has a replayable 70-case evidence pack, generated Stage 1 report/summary artifacts, explicit Hard Commitment mappings, and whitepaper-backed metrics plus commitments text
- analyze responses now also carry a deterministic `handoff_package`, pairing `machine_handoff` with a templated `human_review_brief` so downstream review can continue without changing the request contract
- the frontend now renders a `Workflow Handoff` block for supported, unsupported, incomplete, and Stage 4 cases without replacing the existing bounded fact-completion lane
- Stage 5 now also has a replayable 6-case handoff evidence pack plus an integration note, so the workflow-handoff contract is no longer only implied by scattered tests
- Stage 6 source-chain closure is now complete: both supported treaty pairs and all three supported income types expose treaty-version notes, paragraph-level references, real excerpts, working-paper lineage, and fact-based MLI / PPT prompts
- the earlier CN-SG dividend branch assumption has now been corrected from `7% / 12%` to the treaty-verified `5% / 10%` operative branch
- CN-NL interest and royalties now point to `Article 11(2)` and `Article 12(2)` directly, bringing the older pair up to the same source-chain standard as CN-SG
- the repo now also has a Stage 6 evidence pack, including working papers, comparison outputs, a source-chain replay report, and a documented 15-minute human review exercise

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
- the post-Article-10 audit pass has now also tightened two runtime guardrails: direction-specific rule branches must match the actual payer -> payee flow, and LLM input parses must survive a minimal deterministic evidence cross-check before they are allowed to drive a supported treaty result
- the post-Article-10 audit pass also tightened outward-facing behavior: missing `llm_generated` datasets now degrade into a controlled unavailable-data-source response, and the UI no longer frames branch-driven HOLD cases or high-priority review cases with the same certainty as ordinary supported matches
- the follow-up audit pass tightened three remaining Phase 2 weak spots too: same-paragraph rule normalization now promotes rate-bearing rules over leading narrative ones, accepted country aliases like `PRC` / `Holland` / `Dutch` no longer get killed by the runtime evidence guardrail, and PDF parse-failure reports now preserve `source_id` lineage instead of dropping governed source identity on error

## Active Direction

Important naming note:

- the older `Phase 1 / Phase 2 / Phase 3 / Phase 4` language below describes the broad product evolution arc
- the current execution-control system uses `Stage 1 / Stage 3 / Stage 3.5 / Stage 4 / Stage 2`
- when there is any conflict, trust the execution-control stages, gate files, and execution memo over the older broad-phase shorthand

Use the broad product roadmap only as long-range context:

- Phase 1: constrained LLM input understanding
- Phase 2: real document-driven data generation
- Phase 3: dynamic review guidance
- Phase 4: later expansion after bounded interaction work is proven

Current priority correction:

- do not let Phase A packaging work outrun product usefulness
- before more GitHub-polish work, re-evaluate how this tool can help in a narrow real workflow rather than only looking impressive as a portfolio piece
- future sessions should anchor decisions to the original motivation: this repo exists to help the user build toward an `AI + international tax` direction through a real bounded product, not just a polished showcase
- control expansion actively: after a meaningful checkpoint, prefer the next real pipeline advance over adjacent nice-to-have refinements
- the current active slice is Phase 2: improve offline treaty extraction quality while keeping the runtime conservative, auditable, and defaulted to stable curated data
- the biggest remaining credibility gap is no longer “where are the sources?” in the abstract; it is now whether the project wants to stop near the Phase 2 line and explain the two-layer architecture clearly, or take one more narrow source-aware ingest step by letting ingest entries declare official `source_id` lineage
- external-audit-aligned strategy now matters too: if scope expands, prove scalability with one measured second country-pair onboarding rather than racing for broad country coverage
- public positioning should stay as a smart triage layer that feeds professional research or human review, not as a standalone expert platform
- any move beyond single-turn should favor constrained clarification prompts over open-ended advisory chat
- latest audit refinement: add a lightweight user-calibration checkpoint before committing to true multi-turn work, because improved single-turn conservative outputs may already satisfy much of the real workflow need
- latest audit refinement: treat automated regression, data versioning, audit logs, and continuously updated evidence docs as a cross-cutting infrastructure track rather than a late polish task
- latest audit refinement: stage progression needs explicit gate reviews; avoid advancing on “close enough” without recording pass/fail against stated exit criteria
- latest audit convergence: the discussion phase is effectively closing; the next operational artifact should be a short execution decision memo that freezes stage order, gate criteria, evidence-pack requirements, and explicit non-goals before implementation pressure starts eroding discipline
- latest execution state: Stage 1, Stage 2, Stage 3, Stage 3.5, Stage 4, Stage 5, and Stage 6 are complete; the next decision is which post-Stage-6 slice to pursue without weakening the new source-chain closure contract
- Stage 3 closed with live review_state / confirmed_scope / next_actions wiring, five-state trigger evidence, a documented CN-SG pressure test, and a clean Stage 1 regression rerun
- latest Stage 2 checkpoint: evidence is now in place across onboarding plan, cost record, validation summary, unexpected findings, and gate-review notes; the only explicit near-close gap is that `G2.4` still needs a recorded change-threshold decision instead of an implicit “bounded enough” reading

The concrete execution checklist for the current stage now lives in:

- `docs/superpowers/plans/2026-03-12-tax-treaty-agent-stage-2-onboarding-plan.md`
- `docs/superpowers/plans/gate-reviews/stage-2-gate-review.md`

## Next Likely Work

1. Phase 1 is now effectively locked: supported natural-language routing works, the runtime path is auditable, and clearly bad inputs refuse conservatively without widening model authority.
2. Current mainline is still Phase 2, but the project has now crossed the highest-value technical proof point: the repo can demonstrate both a simple royalties extraction path and a harder dividend branch path (`5% / 10%`) through the full `LLM extraction -> generated dataset -> conservative runtime` loop.
3. The next valuable slice is no longer “make the branch sample work” — that now works, and the most important post-sample conservative guardrails are now in place too. The recent source-governance package plus catalog `source_id` validation means the repo has also taken one narrow step toward governed source ingestion. The next highest-value follow-up is to decide whether to stop Phase 2 and start tightening the public architecture story, or to take exactly one more narrow source-aware ingest slice only if it materially strengthens the proof.
4. The controlled `stable` vs `llm_generated` runtime switch now gives the repo a safe way to prove the full offline-to-online loop without handing the default demo path to uncertain AI data.
5. Avoid turning this milestone into new pipeline sprawl. At this point, extra wrappers, extra ingest formats, or broad scope expansion are lower value than documenting the now-real closed loop clearly.
6. Treat the current post-Article-10 state as “very near the Phase 2 stop line” for a high-value GitHub/resume project.
7. The Stage 1 whitepaper upgrade has now landed: the Chinese whitepaper includes a compact `System Behavior Commitments` section plus first-pass capability-and-restraint metrics with scope notes and fixed-suite limitations.
8. If the repo decides to test expansion, prefer exactly one second country-pair pilot and record schema / builder / parser reuse, human governance time, new edge cases, and online-engine change count.
9. If the product behavior expands, the highest-value UX step is not open chat; it is actionable conservative output and, later, tightly bounded clarification questions that close one missing fact at a time.
10. Stage 1 evidence work is now materially real rather than planned: the fixed suite includes boundary, incomplete, out-of-scope, adversarial, and branch-ambiguity cases, and overreach is tracked as Critical / Major / Minor instead of one blended score.
11. If the repo chooses a second country pair for scalability proof, default first to `CN-SG` for cleaner architecture-reuse validation; defer `CN-DE` until the team specifically wants to test MLI/version-stacking complexity.
12. Insert a user-calibration checkpoint after conservative-output improvements: gather lightweight feedback from 3-5 target users on whether the output already narrows work enough before prioritizing true multi-turn interaction.
13. Before building true multi-turn, test a cheaper pseudo-multi-turn path in the UI, such as fact-completion controls on the result page, to validate whether missing-fact capture actually improves triage outcomes without conversation-state complexity.
14. When expansion begins, require full regression reruns on the existing China-Netherlands suite; preserving prior behavior is more important than adding a new country pair quickly.
15. The handoff layer should evolve in two forms: human-readable review brief plus machine-readable structured output for downstream workflow integration.
16. Add a paper-fit check before locking conservative-output or fact-completion contracts: test the draft schema mentally against a likely second treaty (`CN-SG`) to catch hidden China-Netherlands assumptions early.
17. Treat adversarial test suites as living assets: every new edge case or failure mode should feed back into the permanent evaluation set with source-stage notes and regression reruns.
18. Add a fifth user-facing state between partial completion and human-review escalation: a `can_be_completed` / `可补全` state that explicitly invites bounded fact completion.
19. If pseudo-multi-turn allows fact changes across one session, treat that as exploratory what-if behavior and mark the output accordingly rather than presenting it as one continuous formal pre-review.
20. Before later-stage external expansion or monetization discussions, add a narrative-consistency checkpoint across whitepaper, README, demo claims, and system behavior commitments.
21. Phase 5 should also yield an integration architecture guide for downstream adopters, not only user-facing handoff artifacts.
22. Treat the external-audit phase as near-complete unless a later deliverable materially changes the plan; the highest-value next step is still execution discipline, not more roadmap debate.
23. The execution memo and control layer are now live rather than aspirational; new sessions should trust them as the current stage-order and gate authority.
24. The next anti-drift step is no longer designing more process; it is keeping `.codex/execution-progress.json` current and syncing it into gate/evidence docs after meaningful progress so new sessions can see the real current checkpoint at a glance.
25. The bounded Stage 4 proof slice is now complete: the CN-NL dividends lane has fact completion, change-summary output, four explicit guided stop-path families (`terminated_unknown_facts`, `terminated_conflicting_user_facts`, `terminated_pe_exclusion`, and `terminated_beneficial_owner_unconfirmed`), and a replayable 16-case precision pack.
26. Stage 2 is now formally closed: CN-SG stable onboarding met the gate with explicit G2.4 reuse-threshold wording rather than an implicit “bounded enough” reading.
27. Stage 5 is now formally closed: the deterministic handoff layer is replayable, non-breaking, and documented for both human-review and machine-consumer use.
28. The project has now crossed the Stage 6 stop line: source-chain closure is real, so the next slice should be chosen from a position of traceability rather than from a need to fix citation credibility first.

## Risks To Watch

- letting v1 sprawl beyond the narrow MVP
- using LLM output as fact instead of structured treaty data
- building a flashy demo that cannot later evolve into the B version
- over-optimizing code complexity before the first clean demo exists
- trying to prove scalability by raw coverage count instead of second-pair marginal-cost evidence
- adding multi-turn interaction in a way that makes the tool feel like an unsafely open-ended advisor
- letting conservative states read like dead-end refusals instead of useful analytical narrowing
- waiting until full commercialization work to hear from real users, instead of using early lightweight feedback to calibrate workflow assumptions
- improving headline usefulness metrics by relaxing guardrails instead of improving structured narrowing quality
- allowing stage transitions to happen on vague “good enough” judgment instead of explicit gate-review discipline
- letting external comparison pressure or marketing pressure distort scope, claims, or execution tempo


