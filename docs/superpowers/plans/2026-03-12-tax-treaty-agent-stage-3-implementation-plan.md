# Tax Treaty Agent Stage 3 Implementation Plan

Date: 2026-03-12
Stage: `stage_3`
Status: Active
Purpose: translate the Stage 3 conservative-output design into bounded backend/frontend work without widening scope or weakening guardrails.

## 1. Goal

Stage 3 implementation should make conservative output operational.

The target is not a broader product. The target is:

- stable five-state output semantics
- concrete `next_actions` for every non-final state
- cleaner separation between analytical narrowing and hard scope refusal
- UI language that matches the runtime boundary instead of flattening everything into `SUPPORTED` or `UNSUPPORTED`

## 2. Current Gap

The repo already has useful runtime pieces:

- supported outputs include `summary`, `immediate_action`, `key_missing_facts`, `review_checklist`, `review_priority`, and optional `alternative_rate_candidates`
- unsupported/incomplete outputs include `immediate_action`, repair guidance, and optional `input_interpretation`
- branch ambiguity already triggers `auto_conclusion_allowed = false`

What is missing is a stable Stage 3 contract:

- no `state_code`
- no `state_summary`
- no unified `next_actions`
- no explicit `candidate_branches` block
- no frontend rendering based on the five user states

## 3. Delivery Order

### Slice 1: backend state contract

Add a bounded response layer that maps current runtime facts into:

- `state_code`
- `state_label_zh`
- `state_summary`
- `confirmed_scope`
- `next_actions`

Rules:

- do not remove current fields yet; Stage 3 should be additive first
- do not invent legal facts or new rate logic
- if the current runtime does not support a clean bounded completion path, map the case to `预审部分完成` rather than pretending it is `可补全`

### Slice 2: branch-aware conservative enrichment

For branch-ambiguity cases, add a structured `candidate_branches` block that is narrower than the current raw `alternative_rate_candidates`.

The first supported live pattern is:

- dividend branch ambiguity
- rate alternatives exist
- one or a few missing facts can be named explicitly

Rules:

- no branch should be silently chosen
- the new block must remain traceable to current rate candidates and current review logic

### Slice 3: frontend five-state rendering

Refactor the result card so the header and summary are driven by the Stage 3 state contract.

Required visible behavior:

- `预审完成`: ordinary pre-review completion framing
- `可补全`: clear bounded fact-completion framing
- `预审部分完成`: analytical narrowing without fake finality
- `需要人工介入`: escalation framing
- `不在支持范围`: explicit scope-boundary framing

Rules:

- keep existing evidence rows visible
- do not hide `source_reference`, treaty article, or review guidance
- if the backend state is absent during rollout, fail gracefully to current rendering

### Slice 4: Stage 3 verification pack

Before the gate can pass:

- create triggerable examples for all five user states
- confirm every `incomplete` and `no_auto_conclusion` path has at least one concrete `next_action`
- rerun Stage 1 suite and confirm no guardrail regression
- complete the `CN-SG` schema pressure test and record its conclusion

## 4. Proposed Backend Contract Additions

Supported or narrowing responses should gradually expose:

```json
{
  "state_code": "can_be_completed",
  "state_label_zh": "可补全",
  "state_summary": "已锁定股息条款，但还需一个关键事实来区分税率分支。",
  "confirmed_scope": {
    "applicable_treaty": "中国-荷兰税收协定",
    "applicable_article": "Article 10 - Dividends",
    "payment_direction": "CN -> NL",
    "income_type": "dividends"
  },
  "next_actions": [
    {
      "priority": "high",
      "action": "确认直接持股比例是否达到 25%",
      "reason": "这是区分 5% 与 10% 分支的关键事实"
    }
  ]
}
```

Optional additive blocks:

- `candidate_branches`
- `review_guidance`
- `repair_guidance`

## 5. Proposed Frontend Migration Rules

### Phase A

- introduce local types for Stage 3 fields
- preserve current rendering as fallback
- start rendering `state_label_zh`, `state_summary`, and `next_actions`

### Phase B

- convert current supported/unsupported headers into state-driven headers
- show `candidate_branches` only when present
- separate `key_missing_facts` from `next_actions`

### Phase C

- add state-specific record titles and stamps
- ensure `可补全` does not look like a hard failure
- ensure `不在支持范围` never looks like a treaty answer

## 6. Testing and Verification

Minimum verification for Stage 3 implementation work:

- backend unit coverage for state mapping
- at least one supported supported-case smoke run
- at least one unsupported-case smoke run
- at least one branch-ambiguity smoke run
- Stage 1 regression rerun after meaningful backend contract changes

Stage 3 gate-specific verification:

- `G3.1`: all five states can be triggered and render intentionally
- `G3.2`: every `incomplete` and `no_auto_conclusion` output has at least one `next_action`
- `G3.3`: usefulness improvement does not change Stage 1 overreach results
- `G3.4`: `CN-SG` pressure-test report exists and records compatibility conclusion

## 7. Non-Goals For This Plan

This plan does not include:

- true multi-turn interaction
- open-ended follow-up chat
- second country-pair formal onboarding
- any widening beyond `CN-NL` and the three supported income types

## 8. Immediate Next Move

The next construction step is:

1. prepare the `CN-SG` pressure-test plan and template
2. then implement the minimal backend state contract
3. then wire the frontend to the new state-driven fields
