# Stage 2 Validation Summary

Date: `2026-03-12`

## Evaluation Result

- suite: [stage-2-cn-sg-cases.json](D:\AI_Projects\first agent\data\evals\stage2\stage-2-cn-sg-cases.json)
- report: [2026-03-12-stage-2-validation-report.json](D:\AI_Projects\first agent\docs\superpowers\research\stage-2-evidence\2026-03-12-stage-2-validation-report.json)
- overall result: `PASS`

## Headline Metrics

- total replay cases: `10`
- passed: `10`
- failed: `0`
- pass rate: `1.0`
- `G2.1` threshold (`>= 90%`): `met`

## Coverage

- stable `CN -> SG`: dividends, interest, royalties
- stable `SG -> CN`: dividends, interest, royalties
- controlled rejection: `CN-SG + llm_generated`
- regression spot checks:
  - unsupported `CN-US`
  - supported `CN-NL` royalties
  - existing `CN-NL dividends` Stage 4 bounded lane

## Interpretation

The second pair is now live in the stable lane without:

- changing the public request contract
- widening `Stage 4` pseudo-multiturn beyond `CN -> NL dividends`
- weakening unsupported / unavailable guardrails

The current result supports the Stage 2 claim that second-pair onboarding is primarily a data + governance + routing exercise, not a fresh runtime-engine rewrite.
