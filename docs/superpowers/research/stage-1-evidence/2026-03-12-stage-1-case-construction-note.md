# Stage 1 Case Construction Note

Date: 2026-03-12
Scope: deterministic `Stage 1` credibility evidence pack for `Tax Treaty Agent`
Case file: `data/evals/stage1/stage-1-initial-cases.json`

## Purpose

This note explains how the fixed `Stage 1` case suite was constructed and what it does and does not prove.

The current suite is built to satisfy the memo minimum category counts while keeping runtime execution deterministic and replayable. Its job is to provide a first external-auditable evidence pack with:

- fixed inputs
- human-written expectations
- deterministic runtime execution
- saved report artifacts

## Current Coverage

The current suite contains `70` cases and meets the current memo minimum:

- `happy_path`: `18`
- `boundary_input`: `12`
- `out_of_scope`: `12`
- `incomplete`: `10`
- `adversarial`: `10`
- `multi_branch`: `8`

## Construction Method

The current cases were selected from already verified runtime behaviors in the repo and then encoded into a fixed expectation format.

Selection principles:

- cover all required categories to the memo minimum count
- keep supported deterministic cases on the stable curated runtime path
- use real runtime-supported alias normalization cases for boundary coverage (`软件许可费`, `软件授权费`, `技术授权费`, `品牌费`)
- include unsupported country-pair, unsupported income-type, and unavailable-data-source refusals
- include incomplete cases that isolate missing payer, missing payee, or missing routing structure
- include adversarial cases that try to induce overreach by hinting preferred rates or conclusions
- include multi-branch dividend cases through the explicit `llm_generated` lane, while still running through the same conservative runtime engine

## Important Guardrail

These cases were not reverse-built from arbitrary successful outputs in the same evaluation run.

They were chosen from already understood product behaviors and then encoded as explicit expectations so the evaluation layer can detect drift later.

## Known Limitations

- the suite is team-authored and not externally audited
- the suite is still China-Netherlands-only and intentionally does not speak to multi-country generalization
- live runtime LLM parsing is disabled during this evaluation to keep replay deterministic and cost-controlled
- non-Chinese and mixed-language inputs remain underrepresented in this fixed suite
- the multi-branch lane is covered through a controlled `llm_generated` dataset path, not through arbitrary generated datasets

## Next Expansion Priorities

The next case expansion should target coverage quality, not raw count inflation.

Priority order:

1. add more mixed-language and alias-heavy cases without weakening deterministic replay
2. add more adversarial cases that try to coerce unsupported country pairs or wrong treaty rates
3. expand incomplete cases that isolate one missing fact at a time for later Stage 3 usefulness design
4. add more multi-branch and confidence-sensitive cases through controlled generated datasets
5. keep every new failure case as permanent regression coverage after repair
