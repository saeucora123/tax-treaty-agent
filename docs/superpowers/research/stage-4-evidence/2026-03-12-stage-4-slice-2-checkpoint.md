# Stage 4 Slice 2 Checkpoint

Date: 2026-03-12
Stage: `Stage 4`
Status: In progress
Slice: `CN-NL dividends change summary + unknown-facts termination`

## What Landed

The second bounded Stage 4 slice stays inside the same `CN -> NL` dividend pseudo-multiturn lane.

It adds:

- a visible `fact_completion_status` block for bounded fact-completion progress
- a `change_summary` block after fact-driven re-runs
- an explicit terminated exit when key dividend branch facts remain unresolved
- a UI distinction between:
  - `待补事实`
  - `已缩减`
  - `停止自动缩减`

## What It Does Now

When the user enters `中国公司向荷兰公司支付股息`, the tool can now show three bounded Stage 4 states:

1. `待补事实`
   - the tool asks for direct holding facts
   - the result remains in `可补全`

2. `已缩减`
   - if the user supplies enough direct-holding facts, the tool narrows from `5% / 10%` to a single branch
   - the result shows a `Result Change Summary`
   - the output still labels the facts as unverified user declarations

3. `停止自动缩减`
   - if the user still cannot confirm a key fact, the bounded fact-completion loop stops
   - the UI no longer shows the re-run form
   - the result moves from `可补全` to `需要人工介入`
   - the output tells the user to confirm the unresolved holding facts offline before retrying or escalating

## Why This Matters

This slice makes the pseudo-multiturn flow more auditable and less misleading.

The tool no longer behaves as if every fact-completion attempt must end in a narrower result. It can now:

- show what changed
- show why it changed
- stop conservatively when the missing branch fact still cannot be established

That is a better fit for the Stage 4 contract than silently looping in the same form forever.

## What This Slice Still Does Not Do

This slice still does not:

- judge beneficial ownership
- fully branch on PE / effectively connected exclusions
- cover all four Stage 4 termination paths required by `G4.3`
- widen pseudo-multiturn beyond `CN -> NL` dividends
- open free-form follow-up chat

## Validation

Code-level validation completed:

- `python -m pytest backend/tests/test_analyze.py`
- `npm test -- --run src/App.test.tsx`

Regression validation completed:

- `python scripts/run_stage1_eval.py`
- `python scripts/check_execution_control.py`

Current regression result:

- `70 / 70` passed
- `Critical overreach = 0`
- `Major overreach = 0`
- `Minor overreach = 0`

## Files Touched In This Slice

- `backend/app/service.py`
- `backend/tests/test_analyze.py`
- `frontend/src/App.tsx`
- `frontend/src/App.test.tsx`

## Immediate Next Work

The next bounded Stage 4 work should stay inside the memo's gate contract:

- build the first 10-scenario Stage 4 precision pack toward `G4.1`
- record the remaining termination-path evidence required by `G4.3`
- keep all additional work inside bounded fact completion rather than open conversation
