# CN-NL Shadow Rebuild Proof

Date: 2026-03-18
Scope: post-Stage-6 hardening, second treaty-pair shadow rebuild proof

## Summary

`CN-NL` now passes the same manifest-driven shadow onboarding workflow that was previously proven on `CN-SG`.

This slice did not loosen canonical comparison. Instead, the deterministic onboarding layer now reconciles governed metadata from the stable reference dataset before canonical equality is checked. The change is pair-agnostic and keeps runtime rule substance unchanged.

## Live Compiler Run

Command:

```bash
python scripts/run_treaty_onboarding.py compile --manifest data/onboarding/manifests/cn-nl.shadow.json
```

Observed result:

- `Compile status: ok`
- `3` target articles
- `4` paragraphs
- `4` rule candidates
- `4` unresolved items

The live provider path succeeded with the existing DeepSeek configuration.

## Review Gate

Command:

```bash
python scripts/run_treaty_onboarding.py review --manifest data/onboarding/manifests/cn-nl.shadow.json
```

Observed result:

- `status = pass`
- `canonical_match = true`
- `mismatch_path_count = 0`

The previously known `articles[].notes` mismatch is now resolved by deterministic reference-metadata reconciliation rather than by weakening the proof contract.

## Promote Decision

Temp-target promotion is covered by `backend/tests/test_treaty_onboarding.py` and passes for both `CN-SG` and `CN-NL`.

Real-manifest promotion for `data/treaties/cn-nl.v3.json` was intentionally skipped in this slice because a dry bytewise comparison against `data/onboarding/workdirs/cn-nl-shadow/reviewed.dataset.json` still produced a non-zero tracked diff. The canonical review already passed, so the stable runtime dataset was left untouched to avoid a no-behavior-change rewrite.

## Regression Status

- `python -m pytest backend/tests/` -> `169 passed, 27 warnings`
- `cd frontend && npm test -- --run src/App.test.tsx` -> `18 passed`
- `cd frontend && npm run build` -> pass

## Outcome

The offline treaty compiler v1 is now proven on both existing treaty pairs:

- `CN-SG` shadow rebuild: green
- `CN-NL` shadow rebuild: green

This closes the “second instance” robustness proof for the current schema and CLI contract without introducing OECD baseline/delta logic yet.
