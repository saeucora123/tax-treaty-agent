# Tax Treaty Agent Stage 1 Evidence Pack Checklist

Date: 2026-03-12
Status: Active
Purpose: define the minimum evidence bundle required before `Stage 1` can pass gate review.

## Current Progress Snapshot

<!-- STAGE_1_PROGRESS:START -->
Last synced: `2026-03-17`
Status summary: Stage 1 has passed gate with a deterministic 70-case evidence pack, zero Critical/Major/Minor overreach in the fixed suite, and whitepaper-backed metrics plus System Behavior Commitments.
Current checkpoint: Stage 1 gate is now PASS; the repo has a replayable 70-case evidence pack, generated report/summary artifacts, and published Chinese whitepaper metrics + commitments sections.

Completed so far:
- Execution decision memo created
- Stage 1 gate-review scaffold created
- Stage 1 evidence-pack checklist created
- Execution preflight control script installed
- Initial Stage 1 fixed case file created under data/evals/stage1
- Stage 1 evaluation module added in backend/app/stage1_eval.py
- Stage 1 runner script added in scripts/run_stage1_eval.py
- Initial Stage 1 JSON report generated under docs/superpowers/research/stage-1-evidence
- Initial Stage 1 markdown summary generated under docs/superpowers/research/stage-1-evidence
- Initial Stage 1 case construction note added
- Stage 1 suite expanded to the memo minimum counts across all six categories
- Stage 1 metrics now include scope, sample note, bias note, supported-scope denominators, and Minor overreach tracking
- Stage 1 hard-commitment mapping artifact generated
- Chinese whitepaper now includes metrics and System Behavior Commitments sections

In progress:

Next up:

Current blockers:
<!-- STAGE_1_PROGRESS:END -->

## Required Inputs

- the audit-aligned execution memo
- the current whitepaper draft
- a fixed test set with expected outputs
- a metrics report derived from that test set
- published `Hard Commitments` and `Design Commitments`

## Test Set Minimum

- Happy path: `18`
- Boundary input: `12`
- Out-of-scope: `12`
- Incomplete: `10`
- Adversarial: `10`
- Multi-branch: `8`
- Total minimum: `70`

## Test Set Quality Rules

- each test case has a human-written expected result
- at least 3 adversarial cases are deliberately designed to induce overreach
- no case is reverse-built from a successful system output
- the test set includes a short construction note and known blind spots
- failing cases remain in the test set after repair

## Required Metrics

- input interpretation accuracy
- article matching accuracy
- effective output rate
- conservative refusal rate
- false-positive refusal rate
- overreach rate split into `Critical / Major / Minor`

For each metric, include:

- definition
- denominator or scope
- known limitations
- sample / bias note

## Required Whitepaper Sections

- metrics report section
- `System Behavior Commitments` section
- known limitations section
- at least 1 happy-path worked example
- at least 1 conservative-behavior worked example

## Gate Reminder

`Stage 1` does not pass unless:

- `Critical overreach = 0`
- `Major overreach = 0`
- every hard commitment maps to at least one validating test case

If a new `Critical` or `Major` case is found, repair it and keep it permanently in regression coverage.
