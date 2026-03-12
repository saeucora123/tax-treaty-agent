# Tax Treaty Agent Stage 3 CN-SG Schema Pressure Test Plan

Date: 2026-03-12
Stage: `stage_3`
Status: Planned
Purpose: use a lightweight `CN-SG` paper-fit check to test whether the Stage 3 output contract and bounded fact-completion framing are secretly overfit to `CN-NL`.

## 1. Why This Exists

This is not formal second-country onboarding.

It exists to answer one narrower question:

> If we apply the Stage 3 output/state contract to a likely second treaty shape, do the schema, state mapping, and future bounded fact-completion affordances still hold?

This check must happen before `Stage 3` can pass.

## 2. Test Scope

Use three `CN-SG` treaty areas as the pressure-test sample:

- `Article 10` - dividends
- `Article 11` - interest
- `Article 12` - royalties

The purpose is not to build a full dataset. The purpose is to hand-encode a small number of realistic rules and push them through the current Stage 3 contract mentally and, where possible, through the runtime shape.

## 3. Required Inputs

Prepare a small manual input pack containing:

- the clean source text for `CN-SG` Articles 10, 11, and 12
- paragraph boundaries for the sample text
- a short note for any obvious structural difference from `CN-NL`

Minimum target:

- at least 3 manually encoded rules
- ideally 1 rate-bearing sample from each article
- at least 1 sample that creates a bounded branch distinction or special condition worth testing

## 4. Method

### Step 1: manual rule encoding

Without building a full ingest pipeline, manually encode 3-5 `CN-SG` rules into the current schema shape used by the runtime.

Check for:

- article number/title compatibility
- paragraph-level source anchoring
- rate / condition representation
- any missing field that Stage 3 output would need later

### Step 2: Stage 3 contract fit check

For each hand-encoded rule, test whether the current Stage 3 contract can express:

- `confirmed_scope`
- `state_code`
- `state_summary`
- `next_actions`
- `candidate_branches` when appropriate
- escalation vs scope-boundary separation

### Step 3: bounded fact-completion fit check

Where the `CN-SG` sample contains a branch or condition split, test whether the missing fact can be represented as a bounded completion item rather than a generic refusal.

Key question:

- does the draft `可补全` contract still make sense, or is it implicitly tailored to the `CN-NL` dividend branch story only?

### Step 4: incompatibility log

Record every mismatch explicitly instead of smoothing it over.

Examples:

- schema lacks a field needed by the `CN-SG` sample
- state mapping assumes a `CN-NL`-specific branch pattern
- `next_actions` wording depends on one treaty structure too heavily
- future fact-completion form would not generalize

## 5. Compatibility Checklist

Mark each item as `PASS`, `PARTIAL`, or `FAIL`.

### Schema fit

- current article / paragraph / rule schema can represent the `CN-SG` sample
- source anchors remain sufficient
- no treaty-specific field is hardcoded into the shape

### Output contract fit

- `confirmed_scope` remains valid
- five-state contract still covers the realistic outcomes
- `不在支持范围` and `需要人工介入` stay clearly separate

### Bounded completion fit

- bounded missing facts can still be named clearly
- `candidate_branches` can express the sample without silently choosing one
- completion logic does not depend on `CN-NL` dividend wording

### UI fit

- state header wording remains intelligible
- branch display does not assume one fixed rate pattern
- manual-review guidance still reads as operational, not dead-end refusal

## 6. Report Template

Use the following structure for the final pressure-test report:

```markdown
# Stage 3 CN-SG Pressure Test Report

Date:
Reviewer:
Result: PASS / PARTIAL / FAIL

## Sample Scope
- Articles tested:
- Rules encoded:

## Compatibility Summary
- Schema fit:
- Output contract fit:
- Bounded completion fit:
- UI fit:

## Unexpected Findings
- finding:
  impact:
  required change:

## Final Conclusion
- Can Stage 3 continue without contract changes?
- If no, what must be fixed before the gate can pass?
```

## 7. Pass / Fail Rule

### PASS

- no blocking incompatibility is found
- any minor issues can be handled as wording or implementation details

### PARTIAL

- the overall contract is reusable, but one or more Stage 3 fields or mapping rules need small adjustments before the gate should pass

### FAIL

- the Stage 3 contract is materially overfit to `CN-NL`
- state or output design would need structural rework before user calibration

## 8. Immediate Next Move

After this plan is in place:

1. gather the three `CN-SG` article texts
2. hand-encode the minimal sample set
3. write the pressure-test report before closing `Stage 3`
