# Stage 5 Validation Summary

Date: `2026-03-12`

## Evaluation Result

- suite: [stage-5-handoff-cases.json](D:\AI_Projects\first%20agent\data\evals\stage5\stage-5-handoff-cases.json)
- report: [2026-03-12-stage-5-validation-report.json](D:\AI_Projects\first%20agent\docs\superpowers\research\stage-5-evidence\2026-03-12-stage-5-validation-report.json)
- overall result: `PASS`

## Headline Metrics

- total replay cases: `6`
- passed: `6`
- failed: `0`
- handoff coverage: `1.0`
- route match rate: `1.0`
- null-field behavior: `1.0`
- user-declared fact preservation: `1.0`

## Coverage

- supported clear:
  - `CN -> NL royalties`
- supported ambiguous:
  - `CN -> SG dividends`
- bounded Stage 4 carry-through:
  - `CN -> NL dividends` with user-declared facts preserved
- unsupported:
  - `CN -> US`
- incomplete:
  - missing payer context
- unavailable data source:
  - `CN-SG + llm_generated`

## Interpretation

The current Stage 5 slice now has replayable gate evidence rather than only scattered assertions:

- every replay case emits `handoff_package`
- `recommended_route` stays aligned with `review_state`
- unsupported, incomplete, and unavailable-data-source cases return explicit `null` treaty/article fields instead of fabricated values
- the Stage 4 bounded lane keeps `user_declared_facts` inside `machine_handoff`

This is enough to support the narrow Stage 5 claim that the product can now hand off its bounded pre-review output to either a human reviewer or a downstream machine consumer without widening the request contract.

## Validation

- `python -m pytest backend/tests/test_analyze.py backend/tests/test_stage2_runtime.py backend/tests/test_stage2_eval.py backend/tests/test_stage5_eval.py backend/tests/test_stage5_eval_fixture.py`
- `python scripts/run_stage1_eval.py`
- `python scripts/run_stage2_eval.py`
- `python scripts/run_stage4_eval.py`
- `python scripts/run_stage5_eval.py`
- `npm test`
- `npm run build`
- `python scripts/check_execution_control.py`
