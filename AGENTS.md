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

## Durable Context Rule

If a stable repo fact or recurring workflow appears, update the smallest relevant file:

- repo rule -> `AGENTS.md`
- stable repo fact -> `.codex/project-memory.md`
- current direction or next likely work -> `.codex/project-status.md`
