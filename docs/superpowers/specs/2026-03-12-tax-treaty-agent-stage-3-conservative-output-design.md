# Tax Treaty Agent Stage 3 Conservative Output Design

Date: 2026-03-12
Stage: `stage_3`
Status: Active design artifact
Purpose: define the bounded user-facing output-state contract that turns conservative behavior into operational value instead of dead-end refusal.

## 1. Stage Goal

Stage 3 does not widen product scope. Its job is to make the current bounded runtime more useful by:

- expressing conservative outcomes in a clearer user-facing state system
- showing what the system has already narrowed down
- exposing the next best action in structured form
- avoiding any gain in usefulness that comes from weaker guardrails

This design sits on top of the current China-Netherlands runtime and must remain compatible with later `CN-SG` paper-fit checks.

## 2. Current Baseline

The current product already produces useful pieces of the future Stage 3 behavior:

- supported results include `summary`, `immediate_action`, `key_missing_facts`, `review_checklist`, and `review_priority`
- unsupported and incomplete results already include `immediate_action`
- branch ambiguity already triggers `auto_conclusion_allowed = false` and `alternative_rate_candidates`

What is still missing is a stable **user-state contract** that turns these pieces into a small set of predictable output modes.

## 3. Five User States

Stage 3 formalizes five user-facing states.

### 3.1 `预审完成`

Meaning:

- the system has located the treaty lane, article, and a single usable rate path
- the result is still first-pass only, but the user can continue with ordinary manual review

Typical runtime shape:

- `supported = true`
- `auto_conclusion_allowed = true`
- `review_priority = none | normal`

Primary user message:

- “系统已完成第一轮预审，请按标准复核流程继续。”

### 3.2 `可补全`

Meaning:

- the system has narrowed the case to a small number of concrete branches
- one or a few bounded facts supplied by the user could materially improve the result
- this state is the later entry point for pseudo-multiturn fact completion

Typical runtime shape:

- currently most likely to arise from branch ambiguity or bounded missing facts
- target examples include dividend `5% / 10%` branch splits with one key discriminating fact

Primary user message:

- “系统已缩小范围；补充以下有限事实后，可进一步明确结果。”

### 3.3 `预审部分完成`

Meaning:

- the system has done meaningful narrowing work
- but the remaining gap is not a small bounded fact-completion step
- the user should continue with manual analysis using the narrowed output

Typical runtime shape:

- `supported = true`
- `review_priority = high`
- or `auto_conclusion_allowed = false` without a clean bounded completion path

Primary user message:

- “系统已完成结构化缩减，但后续仍需继续分析。”

### 3.4 `需要人工介入`

Meaning:

- the system can identify the handling path or the cause of the stop
- but the case should be escalated instead of pushed through bounded completion

Typical runtime shape:

- low-confidence source lane
- unavailable governed dataset
- conflicts that are outside the current review contract

Primary user message:

- “当前问题已超出安全自动推进边界，应进入人工处理。”

### 3.5 `不在支持范围`

Meaning:

- the scenario falls outside the current country-pair or income-type scope

Typical runtime shape:

- `unsupported_country_pair`
- `unsupported_transaction_type`

Primary user message:

- “当前输入不在本产品支持范围内，请调整范围或改用人工/专业工具。”

## 4. State Mapping Rules

The user-facing state must be derived from runtime facts, not free-form UI wording.

| User-facing state | Current runtime trigger | Notes |
|---|---|---|
| `预审完成` | `supported = true` and `auto_conclusion_allowed = true` and `review_priority != high` | ordinary first-pass success |
| `可补全` | `supported = true` and bounded missing facts can resolve the ambiguity | first live candidate: dividend branch ambiguity with one discriminating fact |
| `预审部分完成` | `supported = true` and output has meaningful narrowing, but no bounded completion step yet | high-review supported cases can temporarily map here |
| `需要人工介入` | low-confidence hold, unavailable governed data, or complex unresolved conflict | not a scope failure |
| `不在支持范围` | `unsupported_country_pair` or `unsupported_transaction_type` | hard boundary |

### Explicit non-rule

`incomplete` must not automatically equal `不在支持范围`.

If the system can explain the missing facts in a way that keeps the user inside the current review lane, the state should be `可补全` or `预审部分完成`, not a scope failure.

## 5. Required Output Blocks

Every Stage 3 state should render a stable top-to-bottom structure.

### Shared header fields

- `state_code`
- `state_label_zh`
- `state_summary`
- `immediate_action`

### Shared evidence block

- `confirmed_scope`
  - applicable treaty or scope boundary
  - direction
  - income type
- `input_interpretation` when present

### Shared action block

- `next_actions`
  - each item should include `priority`, `action`, `reason`

### Conditional blocks

- `candidate_branches`
  - required for `可补全` and some `预审部分完成`
- `review_guidance`
  - required for `预审部分完成` and `需要人工介入`
- `repair_guidance`
  - required for `不在支持范围`

## 6. Per-State Rendering Contract

### `预审完成`

Must show:

- confirmed treaty article
- single rate outcome
- standard verification checklist
- first-pass boundary note

Must not show:

- branch ambiguity framing
- pseudo-multiturn affordance

### `可补全`

Must show:

- what has already been confirmed
- candidate branches rather than one chosen branch
- exact missing facts that would narrow the result
- next actions ordered by priority

Must not show:

- wording that implies the system has already chosen a final branch

### `预审部分完成`

Must show:

- what narrowing has already been achieved
- why the remaining gap is not yet a bounded completion step
- review priority and rationale

Must not show:

- pure refusal wording with no analytical residue

### `需要人工介入`

Must show:

- why the system stopped
- why this is an escalation rather than a scope failure
- what package of facts or outputs should be handed off

Must not show:

- blame-shifting wording like “cannot help”

### `不在支持范围`

Must show:

- exact boundary reason
- supported examples or rewrite guidance when appropriate

Must not show:

- source-article or tax-rate output for unsupported country pairs

## 7. Example Output Skeletons

### 7.1 `可补全`

```yaml
state_code: can_be_completed
state_label_zh: 可补全
state_summary: 已定位到股息条款，但仍需一个关键事实来区分 5% 与 10% 分支
immediate_action: 确认持股比例及受益所有人事实后，再继续预审

confirmed_scope:
  applicable_treaty: 中国-荷兰税收协定
  applicable_article: Article 10 - Dividends
  payment_direction: 中国 -> 荷兰
  income_type: 股息

candidate_branches:
  - rate: 5%
    condition: 收款方为公司且直接持股至少 25%
    missing_facts: [direct_holding_percentage]
  - rate: 10%
    condition: 其他情况
    missing_facts: []

next_actions:
  - priority: high
    action: 确认收款方是否直接持有支付方至少 25% 资本
    reason: 这是区分 5% 与 10% 的主分支事实
```

### 7.2 `预审部分完成`

```yaml
state_code: partial_review
state_label_zh: 预审部分完成
state_summary: 已完成协定与条款缩减，但当前资料仍不足以进入有界补全
immediate_action: 带着当前条款和复核清单进入人工分析

review_guidance:
  human_review_priority: high
  rationale: 已锁定条款，但剩余判断超出当前自动化边界
```

### 7.3 `不在支持范围`

```yaml
state_code: out_of_scope
state_label_zh: 不在支持范围
state_summary: 当前查询不在中国-荷兰、股息/利息/特许权使用费的支持范围内
immediate_action: 调整为支持范围内查询，或改用人工分析

repair_guidance:
  reason: unsupported_country_pair
  suggested_examples:
    - 中国居民企业向荷兰公司支付股息
    - 中国居民企业向荷兰银行支付利息
```

## 8. Implementation Boundaries For Later Work

This design intentionally does **not** require immediate Stage 4 behavior.

Stage 3 implementation may:

- add `state_code` and `state_summary`
- restructure existing result cards
- convert current refusal and hold outputs into the five-state vocabulary

Stage 3 implementation must not:

- introduce open-ended follow-up chat
- let higher usefulness come from weaker refusal rules
- hardcode logic that assumes only China-Netherlands treaty structure will ever exist

## 9. Verification Rules

Before Stage 3 can pass:

1. all five user states must be triggerable and rendered intentionally
2. every `incomplete` and `no_auto_conclusion` output must include at least one concrete `next_action`
3. any gain in effective output must leave Stage 1 overreach results intact
4. the `CN-SG` pressure test must confirm this state contract is not secretly China-Netherlands-specific

## 10. Immediate Next Move

The next construction step after this design artifact is:

1. create a lightweight implementation plan for introducing `state_code` and per-state rendering
2. prepare the `CN-SG` schema pressure-test template and input pack
3. only then begin Stage 3 code edits and regression checks
