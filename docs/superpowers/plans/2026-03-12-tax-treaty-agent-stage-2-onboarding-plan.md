# Tax Treaty Agent Stage 2 Onboarding Plan

Date: `2026-03-12`  
Stage: `stage_2`  
Target pair: `CN-SG`

## Purpose

`Stage 2` proves that the project can onboard a second treaty pair without widening the product contract or rewriting the runtime into pair-specific business logic.

## Locked Scope

- stable pilot pairs after this stage:
  - `CN <-> NL`
  - `CN <-> SG`
- `llm_generated` remains `CN-NL` only
- request shape remains unchanged:
  - `scenario`
  - `data_source`
  - `fact_inputs`
- `Stage 4` bounded pseudo-multiturn remains `CN -> NL dividends` only

## Implementation Lanes

### 1. Runtime registry

- replace hardcoded `CN-NL` runtime routing with pair-aware treaty registries
- keep `stable` and `llm_generated` lanes separate
- return controlled `unavailable_data_source` for `CN-SG + llm_generated`

### 2. Stable `CN-SG` dataset

- add `CN-SG` stable runtime dataset using the existing `v3` article / paragraph / rule schema
- initial coverage remains bounded to:
  - `Article 10` dividends: `7% / 12%`
  - `Article 11` interest: `7% / 10%`
  - `Article 12` royalties: `10%`
- keep dividend / interest ambiguity conservative:
  - surface candidate branches
  - do not auto-select a branch

### 3. Source governance

- add `CN-SG` official source registry
- add `CN-SG` source usage map
- add parser-like `CN-SG` source payload fixture
- prove the builder can ingest the second pair without pair-specific code duplication

### 4. Regression discipline

- rerun:
  - backend analyze tests
  - frontend smoke tests
  - `Stage 1` fixed suite
  - `Stage 4` precision pack
- confirm no breaking API change and no spillover into the bounded `CN-NL` pseudo-multiturn lane

## Acceptance Intent

This stage is successful only if the second pair is added mainly as data and governance work.

It is not successful if `CN-SG` support requires:

- a new request contract
- a second fact-completion UX lane
- new pair-specific runtime branches beyond registry routing
- weaker refusal behavior
