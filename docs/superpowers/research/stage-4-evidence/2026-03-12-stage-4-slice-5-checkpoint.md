# Stage 4 Slice 5 Checkpoint

Date: 2026-03-12
Stage: `Stage 4`
Status: Complete
Slice: `CN-NL dividends conflicting-user-facts termination path`

## What Landed

This slice stays inside the same bounded `CN -> NL` dividends pseudo-multiturn lane.

It adds the fourth explicit guided stop family needed by the current Stage 4 gate:

- a conservative termination exit when user-declared direct-holding facts conflict with each other
- replayable precision-pack coverage for contradictory dividend fact inputs
- a frontend-visible guided exit that removes the re-run form after the contradiction is detected

## What It Does Now

When the user enters `中国公司向荷兰公司支付股息`, the bounded fact-completion flow now stops conservatively if the submitted facts conflict.

Current examples:

- `direct_holding_confirmed = no` plus `direct_holding_threshold_met = yes`
- `direct_holding_confirmed = unknown` plus `direct_holding_threshold_met = yes`

In these cases, the system now:

- keeps the treaty-rate display at `5% / 10%`
- moves the result into `需要人工介入`
- records `terminated_conflicting_user_facts`
- removes the bounded fact-completion form
- tells the user to reconcile the conflicting shareholding facts offline before retrying

## Why This Matters

Before this slice, the runtime could silently collapse a contradictory declaration into the ordinary `10%` branch.

That behavior was too permissive for a bounded pseudo-multiturn lane. This slice fixes that:

- contradictory inputs no longer look like a clean narrowed answer
- the tool now treats contradictory user declarations as a data-quality stop signal
- `G4.3` now has an explicit fourth guided exit family instead of only three

## Stage 4 Gate Impact

The current bounded Stage 4 lane now has four replayable guided stop families:

- `terminated_unknown_facts`
- `terminated_pe_exclusion`
- `terminated_beneficial_owner_unconfirmed`
- `terminated_conflicting_user_facts`

Together with the existing `awaiting_user_facts` and `completed_narrowed` states, this gives the lane a complete bounded pseudo-multiturn lifecycle for the current `CN -> NL dividends` target.

## Validation

Code-level validation completed:

- `python -m pytest backend/tests/test_stage4_eval.py backend/tests/test_stage4_eval_fixture.py backend/tests/test_analyze.py`
- `cd frontend && npm test -- --run src/App.test.tsx`

Regression validation completed:

- `python scripts/run_stage1_eval.py`
- `python scripts/run_stage4_eval.py`
- `python scripts/check_execution_control.py`

Current regression result:

- `Stage 1`: `70 / 70` passed, `Critical / Major / Minor overreach = 0`
- `Stage 4`: `16 / 16` passed
- termination summary now includes:
  - `terminated_unknown_facts = 2`
  - `terminated_conflicting_user_facts = 3`
  - `terminated_pe_exclusion = 2`
  - `terminated_beneficial_owner_unconfirmed = 2`

## Files Touched In This Slice

- `backend/app/service.py`
- `backend/tests/test_analyze.py`
- `backend/tests/test_stage4_eval.py`
- `frontend/src/App.tsx`
- `frontend/src/App.test.tsx`
- `data/evals/stage4/stage-4-precision-pack.json`

## Immediate Next Work

This slice closes the current bounded Stage 4 lane.

The next stage should not widen pseudo-multiturn further. It should move to `Stage 2` and test second-country onboarding discipline against the existing bounded contracts.
