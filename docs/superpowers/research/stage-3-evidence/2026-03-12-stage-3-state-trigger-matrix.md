# Stage 3 State Trigger Matrix

Date: 2026-03-12
Stage: `stage_3`
Status: Active evidence artifact
Purpose: record the current live trigger coverage for all five Stage 3 user states across backend and frontend tests.

## 1. Scope

This artifact documents the first live `Stage 3` state-contract slice.

It answers two questions:

1. can the current backend produce each intended user-facing state?
2. does the frontend actually render each state instead of flattening everything into generic success/failure wording?

This is not yet the final Stage 3 gate package, but it is the current trigger baseline.

## 2. Current State Matrix

| State code | 中文状态 | Representative scenario | Backend evidence | Frontend evidence | Current status |
|---|---|---|---|---|---|
| `pre_review_complete` | `预审完成` | `中国居民企业向荷兰支付特许权使用费` | `test_stage3_state_contract_marks_supported_clear_case_as_pre_review_complete` | `shows structured treaty analysis after submitting a supported scenario` | `PASS` |
| `can_be_completed` | `可补全` | `向荷兰公司支付股息` | `test_stage3_state_contract_marks_incomplete_case_as_can_be_completed` | `shows missing-input guidance for unsupported or incomplete scenarios` | `PASS` |
| `partial_review` | `预审部分完成` | supported royalties with medium extraction confidence | `test_stage3_state_contract_marks_priority_review_case_as_partial_review` | `shows a stronger review warning for medium-confidence treaty extraction` | `PASS` |
| `needs_human_intervention` | `需要人工介入` | supported royalties with very low extraction confidence | `test_stage3_state_contract_marks_low_confidence_hold_as_human_intervention` | `holds automatic treaty conclusion when source confidence is very low` | `PASS` |
| `out_of_scope` | `不在支持范围` | `中国居民企业向美国支付特许权使用费` | `test_stage3_state_contract_marks_unsupported_scope_as_out_of_scope` | `shows explicit out-of-scope state when the scenario is outside the treaty boundary` | `PASS` |

## 3. Rendering Notes

Current frontend rendering now exposes:

- `review_state.state_label_zh`
- `review_state.state_summary`
- `confirmed_scope` when present
- `next_actions` when present

This means the UI now shows the Stage 3 state contract directly instead of relying only on:

- legacy record title
- legacy stamp
- legacy supported / unsupported framing

## 4. What This Matrix Proves

### G3.1 progress

This matrix is the first explicit evidence that all five intended user states are now:

- reachable in the backend
- asserted in tests
- visible in the frontend

### G3.2 progress

All current narrowing / non-final examples covered here now also expose at least one `next_action`.

## 5. What This Matrix Does Not Yet Prove

This artifact alone does not close the full Stage 3 gate.

Still open:

- fuller evidence that `incomplete` and `no_auto_conclusion` paths are comprehensively covered, not only the current representative cases
- `CN-SG` schema pressure test conclusion
- final gate write-up tying usefulness gain to unchanged Stage 1 guardrails

## 6. Verification Commands

Backend:

```powershell
..\ .venv\Scripts\python -m pytest tests/test_analyze.py
```

Frontend:

```powershell
npm test -- --run App.test.tsx
```
