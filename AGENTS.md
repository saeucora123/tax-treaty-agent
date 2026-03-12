# Project Instructions

## Mission

Build a public-facing international tax AI tool that is strong for resume use, GitHub presentation, and later expansion.

Primary goal:

- turn an international tax problem into a credible AI system
- optimize for demo quality, clarity, and future extensibility
- use AI aggressively for speed, while keeping business judgment human-controlled

## Work Track

Default track for this repo:

- `repo-product-work`

Do not drift into generic Codex-system tuning unless the user explicitly asks for it.

## Current Project Shape

This repo is for the `Tax Treaty Agent` project.

Current recommended product shape:

- simple web frontend
- backend API
- structured treaty data
- bounded MVP, not a generic chatbot

## Read First

At the start of substantive work in this repo, read:

- `AGENTS.md`
- `.codex/project-memory.md`
- `.codex/project-status.md`
- `docs/superpowers/plans/2026-03-12-tax-treaty-agent-execution-decision-memo.md`
- `docs/superpowers/specs/2026-03-11-tax-treaty-agent-design.md`
- `docs/superpowers/plans/2026-03-11-tax-treaty-agent-implementation-plan.md` when it exists

## Working Surface

Until code exists, default working surfaces are:

- `docs/superpowers/specs/2026-03-11-tax-treaty-agent-design.md`
- `docs/superpowers/plans/2026-03-11-tax-treaty-agent-implementation-plan.md`

After scaffolding, expect the main working surfaces to become:

- `frontend/`
- `backend/`
- `data/`
- `README.md`

## Product Guardrails

- The project is a tool, not a free-form chat toy.
- Do not let the model invent treaty rates or legal conclusions from memory.
- Facts should come from structured treaty data or clearly cited source material.
- Unsupported or ambiguous cases should fail conservatively.
- Keep v1 narrow and polished instead of broad and messy.

## MVP Guardrails

The first release should stay within:

- China-Netherlands only
- dividends, interest, royalties only
- single-turn input
- structured output with review guidance

Avoid expanding scope unless the user explicitly asks to do so.

## Expansion Control

- Treat this repo as a staged work product, not an unbounded long-running platform build.
- Prefer one clear advancement slice at a time.
- Do not stack more than 1-2 consecutive “polish/detail” slices without also advancing a harder core capability.
- When choosing between extra refinement and a small real pipeline step, prefer the real pipeline step.
- Stop a slice once it reaches a meaningful checkpoint with tests and a real run path; do not keep adding adjacent nice-to-haves in the same burst.
- Keep temporary stubs narrow and auditable; do not let them grow into pseudo-general frameworks too early.

## Human-AI Collaboration

Treat the user as:

- problem definer
- AI orchestrator
- final reviewer

Use AI for:

- scaffolding
- drafting code
- refining structure
- generating docs and examples

But keep these decisions human-reviewed:

- business boundaries
- trust and refusal behavior
- data correctness
- public project claims

## Verification Baseline

Before claiming meaningful progress:

- verify the relevant layer that changed
- if code exists, prefer the smallest real run path over theoretical confidence
- if behavior depends on treaty data, test at least one supported case and one unsupported case

## Execution Discipline

For all substantive work after 2026-03-12:

- treat `docs/superpowers/plans/2026-03-12-tax-treaty-agent-execution-decision-memo.md` as the stage-order and gate-review authority unless the user explicitly replaces it
- run `python scripts/check_execution_control.py` before substantial implementation or planning work, and use its output as the current execution preflight
- at the start of a task, identify which stage the task belongs to before editing
- do not silently skip a gate, reorder stages, or widen scope because something feels "close enough"
- if a task would move the project into the next stage, first verify that the current stage gate has been passed or explicitly record why the user wants to override it
- if a task touches output templates, state handling, or fact-completion UX, check them against the memo's `CN-SG` schema pressure-test requirement instead of assuming China-Netherlands-specific behavior is general
- if a task improves usefulness metrics, make sure the gain does not come from weaker guardrails
- if uncertainty remains about whether to keep exploring or to stop, prefer the memo's non-goals and gate rules over momentum or novelty
- after meaningful progress inside an active stage, update `.codex/execution-progress.json` and run `python scripts/sync_execution_progress.py` so the gate review and evidence artifacts reflect the real current checkpoint

## Durable Context Rule

If a stable repo fact or recurring workflow appears, update the smallest relevant file:

- repo rule -> `AGENTS.md`
- stable repo fact -> `.codex/project-memory.md`
- current direction or next likely work -> `.codex/project-status.md`
