# CN-KR Initial Onboarding Proof

Date: 2026-03-18  
Pair: `CN-KR`  
Mode: `initial_onboarding` with thin-baseline OECD reference  
Manifest: `data/onboarding/manifests/cn-kr.initial-oecd.json`

## Purpose

Run the first real onboarding pilot for a new treaty pair and carry it through:

- formal source build
- baseline-aware compile
- reviewer JSON review
- approval
- promotion into public runtime support

## Live Run

### 1. Source Build

Command:

```powershell
python scripts/run_source_ingest.py --manifest data/source_documents/manifests/cn-kr-main-treaty.build.json
```

Observed result:

- `Completed source-build manifest: 3 articles, missing_target_articles=0`

Build report highlights:

- `source_count = 2`
- `article_count = 3`
- `paragraph_count = 16`
- `rule_count = 17`

Notes:

- the mixed raw-text / PDF source-build path completed successfully
- the resulting governed draft still required reviewer correction before promotion, which is expected for `initial_onboarding`

### 2. Baseline-Aware Compile

Command:

```powershell
python scripts/run_treaty_onboarding.py compile --manifest data/onboarding/manifests/cn-kr.initial-oecd.json
```

Observed result:

- `Compile status: ok (3 articles, 16 paragraphs, 14 rules, 15 unresolved)`

Delta summary from `compiled.delta.report.json`:

- `delta_item_count = 4`
- `high_materiality_count = 2`
- `delta_type_counts.rate_changed = 2`
- `delta_type_counts.scope_note = 2`

### 3. Reviewer JSON Review

Reviewer action:

- `reviewed.source.json` was promoted to a reviewer-approved source payload for Articles `10/11/12`
- the review step then ran against the reviewer-edited source payload

Command:

```powershell
python scripts/run_treaty_onboarding.py review --manifest data/onboarding/manifests/cn-kr.initial-oecd.json
```

Observed result:

- `Review status: ready_for_approval (unresolved_item_count=0, missing_target_articles=0)`

Review gate facts:

- all target articles present
- primary candidate gap count = `0`
- unresolved item count = `0`
- required source-chain metadata complete = `true`

### 4. Approval

Command:

```powershell
python scripts/run_treaty_onboarding.py approve --manifest data/onboarding/manifests/cn-kr.initial-oecd.json --reviewer "Codex Reviewer" --note "Approved after source-build, compile, and reviewer JSON validation."
```

Observed result:

- `Approve status: approved (reviewer=Codex Reviewer)`

### 5. Promotion

Command:

```powershell
python scripts/run_treaty_onboarding.py promote --manifest data/onboarding/manifests/cn-kr.initial-oecd.json
```

Observed result:

- `Promote status: promoted (target=D:\AI_Projects\first agent\data\treaties\cn-kr.v3.json)`

Promotion record written:

- `data/onboarding/workdirs/cn-kr-initial-oecd/promotion.record.json`

## Runtime Outcome

After promotion, `CN-KR` is wired into the stable public runtime as the third supported treaty pair for:

- dividends
- interest
- royalties

Regression coverage confirms:

- supported `CN-KR dividends`
- supported `CN-KR interest`
- supported `CN-KR royalties`
- unsupported cases still fail conservatively

## Conclusion

This is the first completed `initial_onboarding` proof in the repo:

- the formal source-build path now exists and runs on official raw/PDF inputs
- the thin-baseline compiler can generate reviewer-facing delta artifacts for a new pair
- reviewer JSON approval is now part of the formal promotion contract
- the promoted output is now live in public runtime support as `China-Korea`
