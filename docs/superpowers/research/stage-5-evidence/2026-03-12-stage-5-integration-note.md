# Stage 5 Integration Note

Date: `2026-03-12`
Stage: `Stage 5`
Purpose: freeze the first workflow-handoff contract for downstream human review and machine consumption.

## Contract Shape

The current `/analyze` response keeps the existing shape and adds one optional top-level field:

- `handoff_package`

The first-stage contract inside that field is frozen as:

- `machine_handoff`
- `human_review_brief`

No new endpoint is introduced.
No request-field change is introduced.

## Stable Machine-Readable Fields

Downstream rule systems may rely on these `machine_handoff` fields in the current slice:

- `schema_version`
- `record_kind`
- `review_state_code`
- `recommended_route`
- `applicable_treaty`
- `payment_direction`
- `income_type`
- `article_number`
- `article_title`
- `rate_display`
- `auto_conclusion_allowed`
- `human_review_required`
- `data_source_used`
- `source_reference`
- `review_priority`
- `blocking_facts`
- `next_actions`
- `user_declared_facts`

Current null behavior is explicit:

- unsupported / incomplete / unavailable-data-source outputs keep treaty/article/rate fields as `null`
- the system does not fabricate article or rate values for non-supported outcomes

## Minimum Human-Review Brief Fields

Human reviewers may treat these `human_review_brief` fields as the minimum first-slice display:

- `brief_title`
- `headline`
- `disposition`
- `summary_lines`
- `facts_to_verify`
- `handoff_note`

The brief is deterministic template output.
It is not a generated memo and should not be treated as a final opinion narrative.

## Current Boundaries

This first handoff slice does support:

- supported results
- incomplete results
- unsupported results
- unavailable-data-source results
- bounded Stage 4 outputs with preserved user-declared facts

This first handoff slice does not support:

- external transport protocols
- downloadable export files
- workflow orchestration
- free-form brief generation
- new country-pair or Stage 4 scope expansion

## Integration Reading Rule

For downstream consumers, the recommended minimum reading order is:

1. `record_kind`
2. `review_state_code`
3. `recommended_route`
4. treaty/article/rate fields if present
5. `blocking_facts`
6. `user_declared_facts`

That order keeps unsupported or incomplete cases from being misread as if they were treaty-resolved cases.
