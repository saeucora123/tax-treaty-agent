# Stage 3 CN-SG Pressure Test Report

Date: 2026-03-12
Reviewer: internal review pass
Result: `PARTIAL`
Stage: `stage_3`
Purpose: determine whether the current Stage 3 state contract and bounded conservative-output design are secretly overfit to `CN-NL`.

## 1. Inputs Reviewed

Source summary pack:

- [2026-03-12-stage-3-cn-sg-input-pack.md](D:\AI_Projects\first agent\docs\superpowers\research\stage-3-evidence\2026-03-12-stage-3-cn-sg-input-pack.md)

Hand-encoded pressure-test sample:

- [cn-sg.stage3.hand-encoded.json](D:\AI_Projects\first agent\data\pressure_tests\cn-sg.stage3.hand-encoded.json)

Reference design / plan:

- [2026-03-12-tax-treaty-agent-stage-3-conservative-output-design.md](D:\AI_Projects\first agent\docs\superpowers\specs\2026-03-12-tax-treaty-agent-stage-3-conservative-output-design.md)
- [2026-03-12-tax-treaty-agent-stage-3-cn-sg-pressure-test-plan.md](D:\AI_Projects\first agent\docs\superpowers\plans\2026-03-12-tax-treaty-agent-stage-3-cn-sg-pressure-test-plan.md)

## 2. Sample Scope

Articles reviewed:

- `Article 10` - dividends
- `Article 11` - interest
- `Article 12` - royalties

Rules hand-encoded into the current schema shape:

- `Article 10` general dividend branch (`12%`)
- `Article 10` reduced dividend branch (`7%`, >= `25%` direct holding)
- `Article 11` general interest branch (`10%`)
- `Article 11` bank / financial institution branch (`7%`)
- `Article 12` royalty branch (`10%`)

## 3. Compatibility Summary

### Schema fit: `PASS`

The current paragraph/rule schema can represent the sampled `CN-SG` rules without structural breakage.

What worked:

- article / paragraph / rule layering is sufficient
- bidirectional rate branches are representable
- source references remain attachable
- candidate branches can be encoded without changing the frontend contract first

### Output contract fit: `PASS`

The Stage 3 output contract remains reusable on this sample.

What worked:

- `confirmed_scope` is still meaningful
- the five-state vocabulary still makes sense
- the current distinction between `可补全` and `需要人工介入` remains useful

### Bounded completion fit: `PASS`

The current `可补全` concept is not unique to the `CN-NL` dividend example.

The hand-encoded `CN-SG` sample shows that bounded branch questions can also arise from:

- dividend ownership threshold branches
- interest preferential-lender branches

### UI fit: `PASS`

The current Stage 3 card structure can still display:

- single-rate results
- candidate-branch results
- out-of-scope / escalation results

## 4. Unexpected Findings

### Finding 1

- finding: `CN-SG` dividend wording includes a Singapore-specific asymmetry around additional dividend tax
- impact: the current Stage 3 state contract can tolerate it, but later Stage 2 onboarding will need careful direction-sensitive handling rather than a naive symmetric dividend assumption
- required change: no immediate Stage 3 code change required; record as a Stage 2 onboarding risk

### Finding 2

- finding: `CN-SG` interest treatment includes an exemption-like government / central-bank lane in addition to rate branches
- impact: the current schema can still carry this as a branch, but a later reusable treaty schema may benefit from a clearer exemption representation than only `rate`
- required change: no immediate Stage 3 code change required; capture as a future schema refinement candidate

## 5. Final Conclusion

### Overall judgment

`PARTIAL` here means:

- the Stage 3 contract itself is reusable enough to continue
- but the pressure test surfaced two real second-pair risks that should be remembered before Stage 2 begins

### Can Stage 3 continue without contract changes?

Yes.

The pressure test did **not** find evidence that the current Stage 3 state contract is secretly hardcoded to `CN-NL`.

### What remains open after this report?

- Stage 3 still needs its final gate evidence write-up
- Stage 3 still needs the gate checklist updated against this report
- Stage 2 should later treat `CN-SG` dividend asymmetry and exemption-like interest branches as explicit onboarding watch items
