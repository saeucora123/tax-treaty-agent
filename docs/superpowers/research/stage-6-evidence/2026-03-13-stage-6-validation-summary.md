# Stage 6 Validation Summary

Date: `2026-03-13`

## Evaluation Result

- suite: `data/evals/stage6/stage-6-source-chain-cases.json`
- report: `docs/superpowers/research/stage-6-evidence/2026-03-13-stage-6-validation-report.json`
- overall result: `PASS`

## Headline Metrics

- total replay cases: `6`
- passed: `6`
- failed: `0`
- real excerpt rate: `1.0`
- fact-based MLI / PPT rate: `1.0`

## Coverage

- `CN -> SG dividends`
- `CN -> SG interest`
- `CN -> SG royalties`
- `CN -> NL dividends`
- `CN -> NL interest`
- `CN -> NL royalties`

## What Stage 6 Changed

- China-Singapore dividend truth-check corrected the runtime from `7% / 12%` to `5% / 10%`
- China-Singapore interest and royalties now carry treaty-verified paragraph excerpts instead of placeholder samples
- China-Netherlands interest and royalties now cite `Article 11(2)` and `Article 12(2)` directly rather than broader article-level anchors
- both treaty pairs now carry fact-based `MLI / PPT` summaries with deposit / entry-into-force timing and CTA / PPT context
- supported outputs now expose source-trace metadata that points back to Stage 6 working papers

## Validation Commands

- `python -m pytest backend/tests/test_stage2_runtime.py backend/tests/test_analyze.py backend/tests/test_stage6_eval.py backend/tests/test_stage6_eval_fixture.py backend/tests/test_build_treaty_dataset_script.py`
- `python scripts/run_stage6_eval.py`
- `npm test`
- `npm run build`

## Reading

Stage 6 is no longer only “better citations.” It is a real source-chain closure slice:

- the treaty truth has been re-checked where it mattered most
- the write-back is visible in both source fixtures and runtime datasets
- the replay pack now proves that every supported pair / income-type combination can surface a real treaty excerpt plus a fact-based PPT prompt
