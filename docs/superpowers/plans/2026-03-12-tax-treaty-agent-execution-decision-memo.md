# Tax Treaty Agent Execution Decision Memo

Date: 2026-03-12
Status: Active
Purpose: freeze the current audit-aligned execution order, stage gates, evidence-pack standard, and explicit non-goals before implementation pressure erodes discipline.

## 1. Final Stage Order

The project will follow this sequence unless a later gate review explicitly records a justified change:

1. `Stage 1`: credibility evidence pack
2. `Stage 3`: conservative-output value design
3. `Schema pressure test`: lightweight `CN-SG` paper-fit and manual compatibility check at the end of Stage 3
4. `Stage 3.5`: user calibration checkpoint
5. Decision branch:
   - if user feedback shows bounded fact completion is needed, enter `Stage 4` pseudo-multiturn
   - if user feedback shows improved single-turn output is already sufficient, skip `Stage 4` and move to `Stage 2`
6. `Stage 2`: second country-pair formal onboarding
7. `Stage 5`: workflow handoff and integration fit
8. `Stage 6`: controlled expansion
9. `Stage 7`: commercialization validation

## 2. Hard Gate Reviews

Stage progress is binary: pass or fail. “Almost ready” is not a passing state.

### Stage 1 Gate

- `G1.1`: the test set covers all six categories: happy path, boundary input, out-of-scope, incomplete, adversarial, and multi-branch
- `G1.2`: `Critical overreach = 0` and `Major overreach = 0`
- `G1.3`: every reported metric includes definition, sample scope, known limitations, and bias note
- `G1.4`: every `Hard Commitment` has at least one validating test case
- `G1.5`: the whitepaper contains both a metrics section and a `System Behavior Commitments` section

Blocking rules:

- If `G1.2` fails, stop all downstream work and fix the issue first.
- If `G1.1` or `G1.3` fails, do not enter `Stage 3.5`.
- If a `Critical` or `Major` case is found, the repaired case must be kept as a permanent regression test.

### Stage 3 Gate

- `G3.1`: all five user states are triggerable and rendered correctly:
  - `预审完成`
  - `可补全`
  - `预审部分完成`
  - `需要人工介入`
  - `不在支持范围`
- `G3.2`: `incomplete` and `no_auto_conclusion` outputs always include at least one concrete `next_action`
- `G3.3`: effective-output improvement does not come from weaker guardrails
- `G3.4`: the `CN-SG` schema pressure test is complete and documented

Blocking rules:

- If `G3.2` fails, conservative output is still a dead end and cannot enter user calibration.
- If `G3.4` fails, output and state design are not yet general enough to trust.

### Stage 3.5 Gate

- `G3.5.1`: collect structured feedback from at least 3 target users, including at least 1 adjacent-workflow user who is not a treaty specialist
- `G3.5.2`: produce a structured user calibration summary with explicit priority implications
- `G3.5.3`: record an explicit decision on whether to enter `Stage 4`

Blocking rules:

- If `G3.5.3` fails, do not start `Stage 4`.
- If user feedback indicates improved single-turn output is sufficient, skipping `Stage 4` is allowed but must be recorded.

### Stage 4 Gate

- `G4.1`: pseudo-multiturn improves triage precision across at least 10 multi-branch or incomplete scenarios
- `G4.2`: every user-supplied fact is labeled as unverified user-declared information
- `G4.3`: all four termination paths are triggerable and lead to the correct guided exit
- `G4.4`: `Critical` and `Major` overreach remain zero after full regression

Blocking rules:

- If `G4.4` fails, stop and repair before any further multiturn work.
- If `G4.1` fails, do not escalate from pseudo-multiturn to true multiturn.

### Stage 2 Gate

- `G2.1`: second country-pair full test pass rate is at least 90%
- `G2.2`: `CN-NL` regression pass rate remains 100%, including zero `Critical` and `Major` overreach
- `G2.3`: the onboarding cost template is fully completed, including `unexpected_findings`
- `G2.4`: core online-engine change stays below the agreed threshold
- `G2.5`: no breaking change to the frontend/API contract

Blocking rules:

- If `G2.2` fails, fix regression before continuing expansion.
- If `G2.4` fails, treat it as a sign that the reusable architecture layer is not mature enough.

## 3. Stage 1 Evidence Pack Standard

`Stage 1` is not complete unless the repo can present a minimal external-auditable evidence pack.

### Minimum test-set size

- Happy path: `18`
- Boundary input: `12`
- Out-of-scope: `12`
- Incomplete: `10`
- Adversarial: `10`
- Multi-branch: `8`
- Total minimum: `70`

### Quality rules

- Every test case must have a human-written expected result.
- At least 3 adversarial cases must be deliberately designed to try to trick the system into overreach.
- No test case may be back-constructed from a successful system answer.
- The test-set file must include a short construction-method note and known blind spots.
- The test set is append-only: it can grow, but failing cases are never removed.

### Required metrics

- input interpretation accuracy
- article matching accuracy
- effective output rate
- conservative refusal rate
- false-positive refusal rate
- overreach rate split into `Critical / Major / Minor`

Each metric must include:

- definition
- denominator or scope
- known limitations
- sample / bias note

## 4. Schema Pressure Test

This is a lightweight compatibility check, not full second-country onboarding.

Input:

- `CN-SG` Article 10, Article 11, and Article 12 source text

Method:

1. manually encode 3-5 core rules into the current schema
2. feed them into the current runtime path
3. verify:
   - schema compatibility
   - output template compatibility
   - state-classification compatibility
   - fact-completion logic compatibility
4. record all incompatibilities

Deliverable:

- a short compatibility report with pass/fail conclusion and required fixes

## 5. Pseudo-To-True Multiturn Promotion Rule

True multiturn is not the default next step. It is allowed only if all three conditions are true:

1. pseudo-multiturn produces measurable triage improvement
2. user feedback shows form-based fact completion is materially insufficient
3. role-drift protection for true multiturn has been documented and reviewed

If any one of these conditions is missing, remain at pseudo-multiturn.

## 6. Required Execution Artifacts

The project must keep these artifacts current as execution proceeds:

- regression test suite
- stage gate review records
- evidence-pack report
- user calibration summary
- second country-pair cost record
- whitepaper metrics + commitments sections
- narrative consistency check before later expansion or commercialization work

## 7. Explicit Non-Goals

The project will not:

- loosen guardrails to make `effective output rate` look better
- expand country coverage just to show scale without marginal-cost evidence
- treat open-ended chat as the default future direction
- claim accuracy or capability without transparent metric scope
- let external comparison pressure distort scope or execution order
- market the tool as a final tax opinion engine or standalone expert replacement

## 8. Operating Reminder

The roadmap defines direction. These gates define discipline.

When delivery pressure rises, this memo takes precedence over “close enough” judgment. Any decision to move forward despite a failed gate must be explicitly written down with the reason.
