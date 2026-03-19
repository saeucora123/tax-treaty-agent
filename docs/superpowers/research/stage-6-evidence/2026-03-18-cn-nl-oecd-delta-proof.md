# CN-NL OECD Delta Proof

Date: 2026-03-18  
Pair: `CN-NL`  
Mode: `shadow_rebuild` with thin-baseline OECD reference  
Manifest: `data/onboarding/manifests/cn-nl.oecd-delta.shadow.json`

## Purpose

Use `CN-NL` as the second baseline-aware proof instance after `CN-SG`, without weakening canonical review.

## Live Run

### Compile

Command:

```powershell
python scripts/run_treaty_onboarding.py compile --manifest data/onboarding/manifests/cn-nl.oecd-delta.shadow.json
```

Observed result:

- `Compile status: ok (3 articles, 4 paragraphs, 4 rules, 0 unresolved)`

### Review

Command:

```powershell
python scripts/run_treaty_onboarding.py review --manifest data/onboarding/manifests/cn-nl.oecd-delta.shadow.json
```

Observed result:

- `Review status: pass (canonical_match=true, mismatch_path_count=0)`

## Delta Summary

From `data/onboarding/workdirs/cn-nl-oecd-delta-shadow/compiled.delta.report.json`:

- `delta_item_count = 4`
- `high_materiality_count = 2`
- `delta_type_counts.rate_changed = 1`
- `delta_type_counts.condition_changed = 1`
- `delta_type_counts.scope_note = 2`

## Promote Decision

Real-manifest `promote` was intentionally **not** executed.

Reason:

- canonical review passed
- bytewise dataset hashes still differed between:
  - `data/treaties/cn-nl.v3.json`
  - `data/onboarding/workdirs/cn-nl-oecd-delta-shadow/reviewed.dataset.json`
- this proof slice kept the tracked stable dataset untouched because no runtime behavior change was required

Recorded hash check:

- `target=605607A28AF834F6BD51334A7B59BF53E0F103ED89562DE61408DD808631DAB8`
- `reviewed=AAACDE0845D15E655272F6331ACA5AD71D702B37198837BEDD5524299519EB0A`
- `same=False`

## Conclusion

`CN-NL` now passes the same baseline-aware compile/review contract already proven on `CN-SG`.

This confirms the thin-baseline OECD delta path is not pair-specific and can support a second existing treaty pair without relaxing strict canonical review.
