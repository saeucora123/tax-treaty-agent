# Stage 4 Precision Pack Summary

Date: 2026-03-12
Stage: `Stage 4`
Status: Gate-closing evidence recorded

## Purpose

This precision pack is the first structured evidence artifact aimed directly at `G4.1`.

It does not widen scope. It replays only the current bounded Stage 4 lane:

- `CN -> NL`
- `dividends`
- bounded fact completion only

## Pack Shape

- case file: `data/evals/stage4/stage-4-precision-pack.json`
- total cases: `16`
- category coverage: `multi_branch_dividend`

The pack now includes:

- awaiting-facts cases
- narrowed-to-5% cases
- narrowed-to-10% cases
- terminated-unknown-facts cases
- terminated-conflicting-user-facts cases
- terminated-PE-exclusion cases
- terminated-beneficial-owner-unconfirmed cases

## Current Result

The current Stage 4 precision run completed with:

- `16 / 16` cases passed
- `awaiting_user_facts`: `3`
- `completed_narrowed`: `4`
- `terminated_unknown_facts`: `2`
- `terminated_conflicting_user_facts`: `3`
- `terminated_pe_exclusion`: `2`
- `terminated_beneficial_owner_unconfirmed`: `2`
- `G4.1` case-count threshold: met

## Interpretation

This pack now closes the bounded evidence needed for the current Stage 4 gate:

- `G4.1` now has a replayable 10-case precision pack rather than only ad hoc scenario demos
- the bounded pseudo-multiturn lane shows measurable triage progression:
  - some cases stay in `待补事实`
  - some narrow to a single rate
  - some stop conservatively with one of four guided exit families

The lane remains deliberately narrow, but the current gate does not require broader coverage than this first bounded dividend target.

## Validation

- `python -m pytest backend/tests/test_stage4_eval.py backend/tests/test_stage4_eval_fixture.py backend/tests/test_analyze.py`
- `npm test -- --run src/App.test.tsx`
- `python scripts/run_stage1_eval.py`
- `python scripts/run_stage4_eval.py`
- `python scripts/check_execution_control.py`
