# Stage 2 Cost Record

Date: `2026-03-12`  
Stage: `stage_2`  
Target pair: `CN-SG`

## Summary

This record captures where the second-pair onboarding effort actually landed. The key result is that most new work concentrated in governed data, builder reuse, and evaluation artifacts rather than in a second pair-specific runtime engine.

## Source Governance

- source identification: `done`
- artifacts added:
  - [cn-sg-official-sources.json](D:\AI_Projects\first agent\data\source_registry\cn-sg-official-sources.json)
  - [cn-sg-source-usage-map.json](D:\AI_Projects\first agent\data\source_registry\cn-sg-source-usage-map.json)
- outcome:
  - second-pair source registry now exists
  - usage map explicitly ties runtime / builder artifacts back to governed sources

## Offline Extraction / Data Shaping

- artifacts added:
  - [cn-sg-main-treaty.json](D:\AI_Projects\first agent\data\source_documents\cn-sg-main-treaty.json)
  - [cn-sg.v3.json](D:\AI_Projects\first agent\data\treaties\cn-sg.v3.json)
  - [cn-sg.v3.generated.json](D:\AI_Projects\first agent\data\treaties\cn-sg.v3.generated.json)
- builder reuse:
  - existing builder entry was generalized instead of cloning a second pair-specific script
  - second-pair fixture now runs through the same builder path

## Online Engine Changes

- files touched:
  - [service.py](D:\AI_Projects\first agent\backend\app\service.py)
  - [main.py](D:\AI_Projects\first agent\backend\app\main.py)
- substantive runtime changes were limited to:
  - registry-driven treaty lookup
  - `SG` alias / footprint recognition
  - dynamic supported-scope examples and treaty labels
  - controlled `unavailable_data_source` response for `CN-SG + llm_generated`
- explicit non-change:
  - no new `CN-SG` fact-completion lane
  - no request-schema change
  - no open-chat expansion

## Validation

- replay suite:
  - [2026-03-12-stage-2-validation-report.json](D:\AI_Projects\first agent\docs\superpowers\research\stage-2-evidence\2026-03-12-stage-2-validation-report.json)
- result:
  - `10 / 10` cases passed
  - pass rate: `1.0`
- regression reruns:
  - `Stage 1`: `70 / 70`
  - `Stage 4`: `16 / 16`
  - backend tests: `51 / 51`
  - frontend tests: `15 / 15`

## Unexpected Findings

1. `CN-SG` interest still exposes an exemption-like government / central-bank lane beyond the current `7% / 10%` branch representation.
   - current handling: record as future schema refinement work, not a Stage 2 UI or schema expansion
2. Reverse-direction support works under registry routing, but static examples and scope wording had to be made pair-aware to avoid product-copy drift.
   - current handling: dynamic supported-scope examples now flow from the registry instead of one hardcoded pair

## Gate Readiness Reading

- `G2.3`: supported by this cost record plus the linked governance artifacts
- `G2.4`: online-engine scope stayed bounded to registry routing and alias detection rather than second-pair business logic branches
