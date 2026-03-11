# Project Status

Last updated: 2026-03-11

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

## Active Direction

Move from planning into repository scaffolding and MVP implementation.

## Next Likely Work

1. Choose the initial technical stack and project layout.
2. Scaffold the frontend demo shell.
3. Expand backend behavior beyond the first supported path.
4. Add more examples and unsupported-case polish in the UI.
5. Strengthen public repo presentation and demo assets.

## Risks To Watch

- letting v1 sprawl beyond the narrow MVP
- using LLM output as fact instead of structured treaty data
- building a flashy demo that cannot later evolve into the B version
- over-optimizing code complexity before the first clean demo exists
