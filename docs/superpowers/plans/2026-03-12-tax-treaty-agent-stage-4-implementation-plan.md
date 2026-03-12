# Tax Treaty Agent Stage 4 Implementation Plan

Date: 2026-03-12
Stage: `Stage 4`
Status: Active
Scope owner: Codex

## 1. Purpose

Stage 4 exists to prove one narrow product upgrade:

- the tool can ask for a very small number of missing facts
- the facts are closed-ended and auditable
- the result becomes conditionally narrower without pretending to be a final tax opinion

This is a pseudo-multiturn stage, not an open chat stage.

## 2. First Bounded Slice

The first Stage 4 slice is limited to:

- country pair: `CN-NL`
- income type: `dividends`
- direction: `CN -> NL`
- interaction shape: result-page fact completion, not open conversation

The first milestone must make the default dividend path stop sounding like a flat `10%` answer.

## 3. Stage 4 Product Contract

When the user submits `中国公司向荷兰公司支付股息`, the system should:

1. locate `Article 10 - Dividends`
2. show that two treaty branches may exist: `5%` and `10%`
3. explain the branch conditions in structured form
4. ask only bounded facts that materially affect the branch
5. label all user-entered facts as unverified user declarations
6. keep beneficial-owner treatment conservative

The first bounded fact set is:

- whether the recipient directly holds the payer
- whether the direct holding threshold is at least `25%`

The system must not auto-determine beneficial ownership. Instead, it should surface:

- a reminder that beneficial-owner status remains a separate prerequisite
- a checklist entry showing that the user still needs to confirm it outside the tool

## 4. Fact Tree Rule

The Stage 4 dividend fact tree should mirror treaty structure rather than free-form dialogue.

First-pass fact tree:

- Article 10(2)(a) reduced branch
  - recipient is a company
  - recipient directly holds the payer
  - direct holding threshold is at least `25%`
- Article 10(2)(b) general branch
  - above reduced-rate conditions are not established
- Article 10(4) exclusion reminder
  - if the dividend is effectively connected with a PE or fixed base, the user must escalate to human review and consider a different article lane

The first code slice may keep the PE lane as an exclusion warning rather than a fully interactive branch.

## 5. Response Contract Changes

Supported dividend branch-ambiguity responses should gain a bounded `fact_completion` block.

Minimum shape:

```json
{
  "fact_completion": {
    "flow_type": "bounded_form",
    "session_type": "pseudo_multiturn",
    "facts": [
      {
        "fact_key": "direct_holding_confirmed",
        "prompt": "Does the Dutch recipient directly hold capital in the Chinese payer?",
        "input_type": "single_select",
        "options": ["yes", "no", "unknown"]
      },
      {
        "fact_key": "direct_holding_threshold_met",
        "prompt": "If the holding is direct, is the direct holding at least 25%?",
        "input_type": "single_select",
        "options": ["yes", "no", "unknown"]
      }
    ],
    "user_declaration_note": "Facts entered here are user-declared and not independently verified."
  }
}
```

If enough facts are supplied:

- `yes + yes` -> narrow toward the `5%` branch
- `no` on direct holding or threshold -> narrow toward the `10%` branch
- any `unknown` -> remain in `can_be_completed`

Even after narrowing:

- beneficial-owner confirmation remains pending
- output remains a pre-review, not a final treaty eligibility determination

## 6. Request Contract Changes

`POST /analyze` will accept an optional bounded fact payload.

Minimum shape:

```json
{
  "scenario": "中国公司向荷兰公司支付股息",
  "fact_inputs": {
    "direct_holding_confirmed": "yes",
    "direct_holding_threshold_met": "yes"
  }
}
```

Allowed values:

- `yes`
- `no`
- `unknown`

Out-of-schema fact values must not widen behavior. They should be ignored or rejected conservatively.

## 7. UI Contract

The frontend should add a bounded fact-completion panel only when `fact_completion` is present.

The first UI slice should support:

- rendering the two dividend fact questions
- selecting `yes / no / unknown`
- re-running the same scenario with the selected fact payload
- clearly marking the updated result as based partly on user-declared facts
- showing a small change summary when the returned rate range narrows

The UI should not:

- open a chat box
- allow arbitrary follow-up text
- imply that user-declared facts are independently validated

## 8. TDD Sequence

1. backend failing test for default dividend branch ambiguity with fact-completion payload
2. backend failing test for narrowing to `5%`
3. backend failing test for narrowing to `10%`
4. backend failing test proving beneficial-owner status stays unresolved
5. frontend failing test proving the fact-completion form renders and re-submits
6. frontend failing test proving user-declared-fact labeling appears in the updated result

## 9. Non-Goals For This Slice

This slice will not:

- add true multiturn dialogue
- add open-ended text follow-up
- expand to `NL -> CN` dividend branching
- expand to interest or royalties fact completion
- expand to a second country pair
- auto-judge beneficial ownership
- fully automate PE exclusion analysis

## 10. Success Checkpoint

This slice reaches a meaningful checkpoint when:

- `中国公司向荷兰公司支付股息` no longer looks like a flat single-rate answer
- the response offers bounded fact completion
- the system can narrow to `5%` or `10%` based on user-declared direct-holding facts
- user-declared facts are visibly marked as unverified
- unsupported/incomplete behavior outside this narrow slice does not regress
