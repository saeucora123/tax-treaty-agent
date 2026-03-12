# Stage 4 Slice 4 Checkpoint

Date: 2026-03-12
Stage: `Stage 4`
Status: In progress
Slice: `CN-NL dividends PE-exclusion termination path`

## What Landed

This slice stays inside the same bounded `CN -> NL` dividends pseudo-multiturn lane.

It adds one more explicit Stage 4 termination path:

- a closed-ended `PE / fixed base` exclusion question in the dividend fact-completion form
- a new guided stop state when the user says the dividend may be effectively connected with a China PE or fixed base of the Dutch recipient
- a replayable precision-pack extension that now records both:
  - `terminated_unknown_facts`
  - `terminated_pe_exclusion`

## What It Does Now

When the user enters `中国公司向荷兰公司支付股息`, the bounded fact-completion form now asks three closed-ended questions:

1. whether the Dutch recipient directly holds capital in the Chinese payer
2. whether the direct holding is at least `25%`
3. whether the dividend is effectively connected with a China PE or fixed base of the Dutch recipient

If the user answers `yes` to the PE / fixed-base question:

- the current Article 10 branch-completion flow stops
- the result moves into `需要人工介入`
- the UI no longer offers another pseudo-multiturn rerun inside the same branch flow
- the next action tells the user to confirm the exclusion facts and consider a different article lane with human review

## Why This Matters

This slice improves `G4.3` without widening Stage 4 into open legal analysis.

The system still does **not** try to automate the downstream treaty conclusion once Article 10 may be displaced. Instead, it does the safer thing:

- detect the exclusion trigger
- stop the current branch automation
- route the user toward guided human review

That is consistent with the memo, the teacher feedback, and the bounded pseudo-multiturn contract.

## What This Slice Still Does Not Do

This slice still does not:

- determine whether a PE or fixed base truly exists as a legal conclusion
- decide the downstream article automatically after the exclusion trigger
- open free-form follow-up chat
- close all remaining Stage 4 termination paths required by `G4.3`
- expand beyond the bounded `CN -> NL` dividend lane

## Validation

Code-level validation completed:

- `python -m pytest backend/tests/test_stage4_eval.py backend/tests/test_stage4_eval_fixture.py backend/tests/test_analyze.py`
- `npm test -- --run src/App.test.tsx`

Regression validation completed:

- `python scripts/run_stage1_eval.py`
- `python scripts/run_stage4_eval.py`
- `python scripts/check_execution_control.py`

Current regression result:

- `Stage 1`: `70 / 70` passed, `Critical / Major / Minor overreach = 0`
- `Stage 4`: `12 / 12` passed
- termination summary now includes:
  - `terminated_unknown_facts = 3`
  - `terminated_pe_exclusion = 2`

## Files Touched In This Slice

- `backend/app/main.py`
- `backend/app/service.py`
- `backend/app/stage4_eval.py`
- `backend/tests/test_analyze.py`
- `backend/tests/test_stage4_eval.py`
- `data/evals/stage4/stage-4-precision-pack.json`
- `frontend/src/App.tsx`
- `frontend/src/App.test.tsx`

## Immediate Next Work

The next bounded Stage 4 work should still stay inside `G4.3` rather than widening scope:

- record the remaining guided termination paths required by the memo
- keep all new exits closed-ended and auditable
- do not expand into open chat or second-country onboarding
