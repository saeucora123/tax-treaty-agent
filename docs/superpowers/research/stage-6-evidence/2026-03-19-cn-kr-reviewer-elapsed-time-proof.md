# CN-KR Reviewer Elapsed-Time Proof

Date: `2026-03-19`  
Pair: `CN-KR`  
Mode: `initial_onboarding`  
Manifest: `data/onboarding/manifests/cn-kr.initial-oecd.json`  
Timing artifact: `data/onboarding/workdirs/cn-kr-initial-oecd/timing.record.json`

## Purpose

Record one **single controlled pilot** that measures:

- reviewer-only elapsed time, from explicit `start-review` to `approve`
- repo-internal end-to-end elapsed time, from `source build` start to `promote` completion

The goal of this note is not to claim a universal onboarding SLA. The goal is to prove that the repo now has a measurable, auditable onboarding workflow for a real new treaty pair.

## Measured Scope

Included in the measurement:

- governed official source inputs already present in the repo
- formal `source build`
- baseline-aware `compile`
- explicit review-session start
- reviewer JSON validation
- `review`
- `approve`
- `promote`

Excluded from the measurement:

- external discovery or download time for official materials
- design or schema work done before this pilot
- any broader legal analysis beyond the formal repo workflow

## Live Run Commands

```powershell
python scripts/run_source_ingest.py --manifest data/source_documents/manifests/cn-kr-main-treaty.build.json
python scripts/run_treaty_onboarding.py compile --manifest data/onboarding/manifests/cn-kr.initial-oecd.json
python scripts/run_treaty_onboarding.py start-review --manifest data/onboarding/manifests/cn-kr.initial-oecd.json --reviewer "Codex Reviewer" --note "Measured pilot reviewer validation run after clean live compile."
python scripts/run_treaty_onboarding.py review --manifest data/onboarding/manifests/cn-kr.initial-oecd.json
python scripts/run_treaty_onboarding.py approve --manifest data/onboarding/manifests/cn-kr.initial-oecd.json --reviewer "Codex Reviewer" --note "Approved after measured reviewer validation pass on the clean CN-KR onboarding pilot (sequential replay)."
python scripts/run_treaty_onboarding.py promote --manifest data/onboarding/manifests/cn-kr.initial-oecd.json
```

## Machine Timestamps

From `timing.record.json`:

- `source_build_started_at_utc`: `2026-03-19T06:41:43.731176+00:00`
- `source_build_completed_at_utc`: `2026-03-19T06:44:06.223662+00:00`
- `compile_started_at_utc`: `2026-03-19T06:48:40.803092+00:00`
- `compile_completed_at_utc`: `2026-03-19T06:50:35.778547+00:00`
- `review_session_started_at_utc`: `2026-03-19T06:51:53.622379+00:00`
- `review_completed_at_utc`: `2026-03-19T06:52:12.327729+00:00`
- `approved_at_utc`: `2026-03-19T06:52:19.714067+00:00`
- `promoted_at_utc`: `2026-03-19T06:52:29.485198+00:00`

## Recorded Durations

- `source_build_seconds = 142`
- `compile_seconds = 114`
- `review_seconds = 26`
- `end_to_end_seconds = 645`

Readable summary:

- reviewer-only elapsed time: **26 seconds**
- repo-internal end-to-end elapsed time: **10 minutes 45 seconds**

## Interpretation

What this run proves:

- the onboarding workflow is now time-measurable end to end
- reviewer time is no longer only anecdotal; it is tied to an explicit `start-review` action and a machine-written approval timestamp
- the first real new-pair onboarding (`CN-KR`) can move through governed source build, baseline-aware compile, human review, approval, and promotion inside one auditable workflow

What this run does **not** prove:

- that every new treaty pair will onboard in the same time window
- that the workflow is now fully automatic
- that human review is unnecessary

## Caveats

- This is a **single controlled pilot**, not a benchmark series.
- The measured end-to-end run includes one live-provider retry gap before the final successful compile, so the elapsed time should be read as a bounded real workflow measurement, not as an optimized lower bound.
- The reviewer-only timing is deliberately narrow: it begins at explicit `start-review` and ends at `approve`; it does not include earlier schema design, source governance setup, or external source discovery.

## Public Wording Guidance

Safe public wording:

- the repo includes a human-reviewed offline LLM treaty-onboarding compiler
- a single controlled `CN-KR` pilot recorded reviewer elapsed time and repo-internal end-to-end onboarding elapsed time
- the measured pilot used governed official source inputs and kept promotion behind explicit review and approval

Unsafe public wording:

- all new treaty pairs now onboard in hours
- onboarding time is guaranteed
- the system eliminates human review
