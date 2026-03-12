# Stage 4 Slice 1 Checkpoint

Date: 2026-03-12
Stage: `Stage 4`
Status: In progress
Slice: `CN-NL dividends bounded fact completion`

## What Landed

The first bounded Stage 4 slice is now live for the default `CN -> NL` dividends path.

It adds:

- structured `Article 10(2)(a)` and `Article 10(2)(b)` branches to the stable CN-NL dataset
- a bounded `fact_completion` contract on ambiguous dividend outputs
- optional `fact_inputs` on `POST /analyze`
- conditional narrowing to `5%` or `10%` based on user-declared direct-holding facts
- explicit `user_declared_facts` rendering in the frontend
- a result-page re-run loop instead of open-ended chat

## What It Does Now

When the user submits `中国公司向荷兰公司支付股息`, the tool no longer pretends the result is a flat `10%`.

Instead it:

- returns `5% / 10%` as a branch-ambiguous rate range
- marks the case as `可补全`
- exposes two bounded fact questions:
  - whether the Dutch recipient directly holds the Chinese payer
  - whether the direct holding is at least `25%`
- keeps beneficial-owner treatment outside automatic determination

If the user supplies:

- `yes + yes` -> the result narrows to `5%`
- `yes + no` -> the result narrows to `10%`
- `no` on direct holding -> the result narrows to `10%`
- any unresolved fact -> the result stays in the bounded fact-completion state

## What This Slice Still Does Not Do

This slice deliberately does not:

- open a free-form follow-up chat
- judge beneficial ownership
- fully branch on PE / effectively connected exclusions
- expand to `NL -> CN` dividend fact completion
- expand to interest or royalties
- expand to a second country pair

## Validation

Code-level validation completed:

- `python -m pytest backend/tests/test_analyze.py`
- `npm test -- --run src/App.test.tsx`

Regression validation completed:

- `python scripts/run_stage1_eval.py`
- `python scripts/render_stage1_eval_summary.py`

Current regression result after syncing the fixed suite to the new intended dividend behavior:

- `70 / 70` passed
- `Critical overreach = 0`
- `Major overreach = 0`
- `Minor overreach = 0`

## Files Touched In This Slice

- `backend/app/main.py`
- `backend/app/service.py`
- `backend/tests/test_analyze.py`
- `frontend/src/App.tsx`
- `frontend/src/App.test.tsx`
- `data/treaties/cn-nl.v3.json`
- `data/evals/stage1/stage-1-initial-cases.json`

## Immediate Next Work

The next bounded Stage 4 work should stay inside pseudo-multiturn discipline:

- add a small change-summary block after re-run
- add explicit termination-path evidence for `unknown` / unresolved facts
- prepare the first Stage 4 scenario pack toward `G4.1`
