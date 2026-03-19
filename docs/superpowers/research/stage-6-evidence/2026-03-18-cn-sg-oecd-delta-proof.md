# CN-SG OECD Baseline / Delta Proof

Date: 2026-03-18
Status: Completed
Purpose: record the first baseline-aware onboarding-compiler proof using a thin OECD baseline reference for `CN-SG` while keeping the runtime contract unchanged.

## Scope

- Pair: `CN-SG`
- Articles: `10`, `11`, `12`
- Mode: `shadow_rebuild`
- Baseline mode: thin baseline / reference-only
- Runtime impact: none

## Live Compile

Command:

```bash
python scripts/run_treaty_onboarding.py compile --manifest data/onboarding/manifests/cn-sg.oecd-delta.shadow.json
```

Observed result:

- status: `ok`
- articles: `3`
- paragraphs: `5`
- rules: `5`
- unresolved items: `0`

Generated baseline-aware artifacts:

- `compiled.rules.json`
- `compiled.source.json`
- `compiled.dataset.json`
- `compiled.report.json`
- `compiled.delta.json`
- `compiled.delta.report.json`

## Delta Summary

From `compiled.delta.report.json`:

- `delta_item_count`: `5`
- `high_materiality_count`: `2`
- `materiality_counts`: `high=2`, `medium=2`, `low=1`
- `delta_type_counts`:
  - `rate_changed=2`
  - `condition_changed=1`
  - `branch_added=1`
  - `scope_note=1`
  - `branch_removed=0`

## Review Gate

Command:

```bash
python scripts/run_treaty_onboarding.py review --manifest data/onboarding/manifests/cn-sg.oecd-delta.shadow.json
```

Observed result:

- `status=pass`
- `canonical_match=true`
- `mismatch_path_count=0`

This confirms that baseline-aware compile still returns to the current stable `cn-sg.v3.json` after human-reviewed source payloads are passed through the existing `review -> dataset -> canonical compare` gate.

## Promotion Note

`promote` was not executed against the tracked repo target in this proof slice because no runtime behavior change was needed.

End-to-end promotion coverage remains present via the temp-target integration test:

- `backend/tests/test_treaty_onboarding.py::test_baseline_aware_cn_sg_compile_review_promote_round_trip`

## Implementation Note

The live DeepSeek compiler response used several synonymous `delta_type` and `materiality` labels (for example `rate_difference`, `condition_difference`, `additional_provision`, `taxation_approach_difference`, `none`). The deterministic normalization layer now canonicalizes those variants into the fixed V2 enums instead of weakening proof strictness.

## Conclusion

The first OECD-baseline-aware proof is green:

- thin baseline artifact works as an authoring-time reference
- live compile emits delta artifacts
- review still canonical-passes back to stable runtime data
- no HTTP or runtime schema changes were introduced
