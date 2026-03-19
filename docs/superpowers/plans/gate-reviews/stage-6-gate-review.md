# Stage 6 Gate Review

Gate: `stage_6`
Stage label: `Stage 6: source chain closure`
Gate result: `PASS`
Review date: `2026-03-13`
Decision owner: `project owner + user-approved execution route`

## Current Progress Snapshot

<!-- STAGE_6_PROGRESS:START -->
Last synced: `2026-03-19`
Status summary: Stage 6 has passed gate: the system now exposes treaty-version notes, paragraph-level excerpts, working-paper lineage, and fact-based MLI/PPT prompts across three supported treaty pairs and all three supported income types, and the first real new-pair onboarding now has measured timing evidence.
Current checkpoint: Stage 6 gate remains PASS, and the post-Stage-6 hardening track now includes dual-pair baseline-aware OECD delta proofing, a formal source-build entrypoint, an internal reviewer workspace, the first completed initial_onboarding promotion of CN-KR into public runtime support, a measured CN-KR timing proof for reviewer-only and end-to-end onboarding elapsed time, and a live GitHub Pages product overview for non-technical tax-domain visitors.

Completed so far:
- Stage 6 target narrowed from generic controlled expansion to source chain closure
- CN-SG dividends truth-check corrected the runtime branch from 7% / 12% to 5% / 10%
- CN-SG interest and royalties now carry treaty-verified paragraph excerpts instead of placeholder samples
- CN-SG official source registry now includes OECD MLI status and peer-review sources
- CN-SG source fixture, curated dataset, and generated dataset now preserve source_trace and fact-based mli_context
- CN-NL dividends, interest, and royalties now have Stage 6 alignment checks and paragraph-level source anchors
- Analyze responses now expose treaty version notes, working-paper references, and fact-based MLI/PPT prompts in result and handoff layers
- Stage 6 evaluation module, fixture tests, runner, and 6-case replay pack added
- Stage 6 evidence pack recorded under docs/superpowers/research/stage-6-evidence
- Stage 6 gate review is now PASS
- The offline treaty compiler now has a second shadow proof: CN-NL passes the same manifest-driven compile/review flow already proven on CN-SG
- The thin-baseline V2 compiler path is now proven on CN-SG: live baseline-aware compile emits delta artifacts and still canonical-passes review against cn-sg.v3.json
- CN-NL now also passes a live baseline-aware OECD delta proof with canonical-pass review under the same strict gate
- Formal source-build now supports pair-level manifests and official raw/PDF inputs through run_source_ingest --manifest
- CN-KR completed the first initial_onboarding path: source build, baseline-aware compile, reviewer JSON review, approval, promotion, and public runtime support
- The frontend now exposes an internal reviewer workspace behind ?internal=onboarding for source build, compile, review, approve, and promote actions
- The repo now ships an expert-facing GitHub Pages product overview at the site root, with the README top section rewritten to introduce the product directly to international tax specialists
- The GitHub Pages product overview now supports a persistent Chinese/English language switch so tax-domain visitors can read the site in their preferred language without changing the product layout
- The Chinese version of the GitHub Pages product overview now uses dedicated Noto Sans SC typography and zh-CN-specific spacing rules so the page reads like one coherent product surface instead of a mixed fallback stack
- A single controlled CN-KR measured pilot now records reviewer-only elapsed time and repo-internal end-to-end onboarding elapsed time in a formal timing.record.json artifact with a matching stage-6 evidence note
- The repo now includes a top-level MIT license and a public-proof upgrade: a CN-NL 90-second walkthrough on GitHub Pages, evidence summary cards, and a 3-minute verifier path in the README

In progress:

Next up:
- Continue physically decomposing backend/app/service.py along the new contract/provider/dividend boundaries without changing runtime behavior
- Plan Slice 4 removal of deprecated dividend bridge fields after all fixtures and replay packs migrate to raw-fact inputs
- Decide whether the next onboarding-compiler slice should deepen the OECD reference artifact or improve reviewer diff ergonomics before broader treaty expansion

Current blockers:
<!-- STAGE_6_PROGRESS:END -->

## Pass / Fail Checklist

- `[x]` `G6.1` treaty rates now match verified treaty text across both supported pairs and all three supported income types
- `[x]` `G6.2` treaty conditions and paragraph references now match the verified clauses rather than broad article placeholders
- `[x]` `G6.3` supported outputs now expose real treaty excerpts and working-paper lineage instead of placeholder samples
- `[x]` `G6.4` CN-NL and CN-SG now reach the same source-chain quality bar
- `[x]` `G6.5` a 15-minute human review exercise can be completed from product output plus source-chain fields without reopening treaty text from zero
- `[x]` `G6.6` MLI / PPT prompts are now based on checked facts rather than generic template language

## Blocking Issues

- `None.`

## Evidence Reviewed

- `data/evals/stage6/stage-6-source-chain-cases.json`
- `docs/superpowers/research/stage-6-evidence/2026-03-13-stage-6-validation-report.json`
- `docs/superpowers/research/stage-6-evidence/2026-03-13-stage-6-validation-summary.md`
- `docs/superpowers/research/stage-6-evidence/2026-03-13-stage-6-comparison-output-note.md`
- `docs/superpowers/research/stage-6-evidence/2026-03-13-stage-6-human-review-test-note.md`
- `docs/superpowers/research/stage-6-evidence/2026-03-13-cn-sg-dividends-working-paper.md`
- `docs/superpowers/research/stage-6-evidence/2026-03-13-cn-sg-interest-working-paper.md`
- `docs/superpowers/research/stage-6-evidence/2026-03-13-cn-sg-royalties-working-paper.md`
- `docs/superpowers/research/stage-6-evidence/2026-03-13-cn-nl-dividends-alignment-check.md`
- `docs/superpowers/research/stage-6-evidence/2026-03-13-cn-nl-interest-alignment-check.md`
- `docs/superpowers/research/stage-6-evidence/2026-03-13-cn-nl-royalties-alignment-check.md`
- `backend/tests/test_analyze.py`
- `backend/tests/test_stage2_runtime.py`
- `backend/tests/test_stage6_eval.py`
- `backend/tests/test_stage6_eval_fixture.py`
- `frontend/src/App.test.tsx`
- `scripts/run_stage6_eval.py`

## Decision

- result: `PASS`
- next step: `Hold the Stage 6 source-chain contract stable and choose any next expansion slice only after deciding whether the project should move toward integration, deeper governed ingest, or another bounded capability.`
- override used: `no`
- override reason: `N/A`

## Notes

- `Stage 6 is a trust upgrade, not a breadth upgrade: no new country pairs, endpoints, or free-form workflow features were added to close this gate.`
- `The most important corrective finding is that the earlier CN-SG dividend branch values were outdated; Stage 6 closes that gap with a recorded treaty truth-check and write-back.`
- `The Stage 6 human review exercise is developer-simulated rather than an external user study, so it proves reviewability rather than broader workflow adoption.`
