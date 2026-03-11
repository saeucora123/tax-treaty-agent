# Project Memory

Last updated: 2026-03-11

## Identity

- Project name: `Tax Treaty Agent`
- Repo path: `D:/AI_Projects/first agent`
- Project type: public-facing AI tool / GitHub portfolio project

## Primary Goal

Create a GitHub-worthy project that shows the ability to translate international tax business logic into a practical AI system.

## Positioning

Target signal:

- understands international tax context
- can use AI and vibe coding effectively
- can turn business logic into a usable system

This repo should not drift toward:

- generic chatbot experiments
- broad legal-tech platform ambitions
- engineering complexity that does not improve the demo

## Recommended Product Shape

- frontend web shell
- backend API
- structured treaty data
- bounded output format

## Release Strategy

Recommended release style:

- semi-public open source

Public:

- code
- docs
- architecture explanation
- sample data
- screenshots or demo assets

Not required in v1:

- all raw source materials
- full production hardening
- heavy enterprise workflow complexity

## MVP Scope

Country pair:

- China-Netherlands only

Transaction types:

- dividends
- interest
- royalties

Interaction:

- single-turn scenario input

Required output sections:

- applicable treaty
- likely article
- tax rate
- conditions
- caution notes
- whether human review is recommended

## Architecture Direction

Preferred path:

- A version: small-data, real-architecture MVP
- B version: real-treaty-driven upgrade

Important rule:

- A must not be a fake hardcoded toy
- A should already use real boundaries, real schema, and real refusal behavior

## Trust Guardrails

- The model may help parse and phrase answers, but not invent rates.
- Treaty facts should live in structured data.
- Unsupported cases should refuse or recommend review.
- This should feel like a professional tool, not a casual chatbot.

## Current Durable Working Surface

- `docs/superpowers/specs/2026-03-11-tax-treaty-agent-design.md`
- `docs/superpowers/plans/2026-03-11-tax-treaty-agent-implementation-plan.md`
- `AGENTS.md`
- `.codex/project-status.md`

## Likely Future Working Surface

- `frontend/`
- `backend/`
- `data/`
- `README.md`

