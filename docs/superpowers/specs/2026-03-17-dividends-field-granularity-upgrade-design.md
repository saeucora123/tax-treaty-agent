# CN-NL Dividends Field Granularity Upgrade Design

Date: 2026-03-17  
Status: Approved for Slice 3 implementation  
Purpose: Upgrade CN-NL dividends guided input from threshold-level
user-declared facts to computable raw facts, enabling system-calculated
threshold determination. Implements A3 migration strategy: add raw fact
fields and system calculation this slice; deprecate threshold-level fields
this slice; remove deprecated fields next slice.

## Background

Slice 2 dividend narrowing relies on user-declared threshold facts
(`direct_holding_confirmed`, `direct_holding_threshold_met`). The user
declares whether the 25% threshold is met; the system does not verify.
This slice upgrades to raw fact input so the system calculates threshold
satisfaction from actual percentage and date values.

Migration strategy A3 applies:
- This slice adds raw fact fields and system calculation logic
- `direct_holding_threshold_met` is deprecated this slice (bridge only,
  same pattern as `fact_inputs` in Slice 2 Part A)
- `direct_holding_confirmed` is deprecated this slice (redundant once
  percentage is provided)
- Removal of deprecated fields is deferred to Slice 4

## Fields Deprecated in This Slice (A3 Bridge)

These fields remain accepted at the API level as a bridge but are marked
`@deprecated` in schema and docs. If both a deprecated field and its raw
replacement are present in the same request, the raw fact field takes
precedence. Do not remove these fields in this slice.

| fact_key | deprecated_by |
|---|---|
| `direct_holding_confirmed` | `direct_holding_percentage` |
| `direct_holding_threshold_met` | `direct_holding_percentage` + system calculation |

## New Raw Fact Fields

| fact_key | prompt | review_need_mapping | type | allowed_values / format |
|---|---|---|---|---|
| `direct_holding_percentage` | What is the recipient's direct shareholding percentage in the paying company as of the payment date? | Maps to Art. 10(2)(a) 25% threshold determination. System calculates whether threshold is met from this value. | numeric string | `"0"` to `"100"`, decimal permitted (e.g. `"25.5"`). `"unknown"` if not yet confirmed. |
| `payment_date` | What is the dividend payment date (or declared payment date)? | Anchors the shareholding percentage to a specific date for threshold testing. Required when `direct_holding_percentage` is provided. | date string | ISO 8601: `"YYYY-MM-DD"`. `"unknown"` if not yet confirmed. |
| `holding_period_months` | How many months has the recipient continuously held the shares as of the payment date? | Maps to short-holding-period review signal. CN-NL Art. 10(2)(a) does not impose a minimum holding period, but SAT practice applies scrutiny to holdings under 12 months. Does not block narrowing. Generates `short_holding_period_review_required` handoff signal when below threshold. | numeric string | Non-negative integer as string (e.g. `"18"`). `"unknown"` if not yet confirmed. |

## System Calculation Logic

### 25% Threshold Determination

When `direct_holding_percentage` is present and not `"unknown"`:
- Parse as float
- `>= 25.0` → threshold met
- `< 25.0` → threshold not met
- System-calculated result overrides any deprecated
  `direct_holding_threshold_met` declaration

When `direct_holding_percentage == "unknown"`:
- Terminate: insufficient facts (same as `direct_holding_threshold_met:
  "unknown"` in Slice 2)

When `direct_holding_percentage` is absent:
- Fall back to deprecated `direct_holding_threshold_met` bridge behavior
- Log deprecation warning in service layer

### Holding Period Signal

When `holding_period_months` is present and not `"unknown"`:
- Parse as integer
- `< 12` → set `short_holding_period_review_required: true` in handoff
- `>= 12` → set `short_holding_period_review_required: false` in handoff
- Does not affect rate selection or termination under any condition

When `holding_period_months == "unknown"` or absent:
- Set `short_holding_period_review_required: true` in handoff
  (conservative default: unknown period treated as requiring review)

### payment_date Handling

`payment_date` is required context for `direct_holding_percentage` but
does not independently gate narrowing in this slice. If
`direct_holding_percentage` is provided but `payment_date` is `"unknown"`
or absent:
- Proceed with threshold calculation using the provided percentage
- Add `payment_date_unconfirmed: true` to handoff output as an audit signal

## Updated Narrowing Logic

The following replaces the Slice 2 decision table for
`resolve_dividend_branch_from_facts()`. Conditions are evaluated in
priority order. Conflict pre-check is applied before conditions 4–10
per the Slice 2 implementation note.

| Priority | Condition | Outcome |
|---|---|---|
| 1 | `pe_effectively_connected == yes` | Terminate: PE exclusion. Art. 10(4). |
| 2 | `beneficial_owner_confirmed == no` | Terminate: BO prerequisite not met. |
| 3 | `beneficial_owner_confirmed == unknown` | Terminate: insufficient facts. |
| 4 | `direct_holding_percentage` present and `< 25.0` | Narrow to 10%. Art. 10(2)(b). |
| 5 | `direct_holding_percentage == "unknown"` | Terminate: insufficient facts. |
| 6 | `direct_holding_percentage` absent → `direct_holding_confirmed == no` | Narrow to 10%. Art. 10(2)(b). (deprecated bridge) |
| 7 | `direct_holding_percentage` absent → `direct_holding_confirmed == unknown` | Terminate: insufficient facts. (deprecated bridge) |
| 8 | `direct_holding_percentage` absent → `direct_holding_threshold_met == no` | Narrow to 10%. Art. 10(2)(b). (deprecated bridge) |
| 9 | `direct_holding_percentage` absent → `direct_holding_threshold_met == unknown` | Terminate: insufficient facts. (deprecated bridge) |
| 10 | `holding_structure_is_direct == no` | Narrow to 10%. Art. 10(2)(b). |
| 11 | `holding_structure_is_direct == unknown` | Terminate: insufficient facts. |
| 12 | `direct_holding_percentage >= 25.0` AND `holding_structure_is_direct == yes` AND `beneficial_owner_confirmed == yes` | Narrow to 5%. Art. 10(2)(a). |
| 13 | Conflict between user-declared facts | Terminate: conflict state. Preserve in handoff. |

`mli_ppt_risk_flag` and `holding_period_months` do not appear in this
table. They only affect handoff signals.

## Updated Handoff Output Requirements

Add to `machine_handoff` for CN-NL dividend supported responses:

- `short_holding_period_review_required: boolean` — true when
  `holding_period_months < 12`, unknown, or absent
- `payment_date_unconfirmed: boolean` — true when `payment_date` is
  absent or `"unknown"` while `direct_holding_percentage` is provided
- `calculated_threshold_met: boolean | null` — system-calculated result
  when `direct_holding_percentage` is numeric; null when falling back to
  deprecated bridge fields
- Existing fields from Slice 2 (`mli_ppt_review_required`,
  `determining_condition_priority`) remain unchanged

## Frontend Changes

Replace the two deprecated fields in the dividends guided facts panel with
the three new raw fact fields. New panel order:

1. `direct_holding_percentage`
2. `payment_date`
3. `holding_period_months`
4. `beneficial_owner_confirmed` (unchanged)
5. `pe_effectively_connected` (unchanged)
6. `holding_structure_is_direct` (unchanged)
7. `mli_ppt_risk_flag` (unchanged)

`direct_holding_confirmed` and `direct_holding_threshold_met` are removed
from the frontend guided panel. They remain accepted at the API level as
bridge fields only.

## Slice 3 Constraints

- `direct_holding_confirmed` and `direct_holding_threshold_met` remain in
  backend schema as deprecated bridge fields. Do not remove them.
- `holding_period_months` never blocks narrowing or changes rate selection.
- `payment_date` never gates narrowing in this slice.
- CN-SG, interest, and royalties logic unchanged.
- Schema version bump is required: `slice1.v1` → `slice3.v1`.

## Test Requirements

New cases required:

1. `direct_holding_percentage: "27"` + all other conditions met → 5%
2. `direct_holding_percentage: "20"` → 10%
3. `direct_holding_percentage: "25.0"` (exact boundary) → 5%
4. `direct_holding_percentage: "unknown"` → terminated: insufficient facts
5. `holding_period_months: "8"` + 5% outcome → `short_holding_period_review_required: true`
6. `holding_period_months: "18"` + 5% outcome → `short_holding_period_review_required: false`
7. `holding_period_months: "unknown"` + 5% outcome → `short_holding_period_review_required: true`
8. `payment_date` absent + percentage provided → `payment_date_unconfirmed: true`
9. Deprecated bridge: `direct_holding_threshold_met: "yes"` without
   `direct_holding_percentage` → still narrows correctly via bridge
10. Deprecated bridge: `direct_holding_threshold_met: "no"` without
    `direct_holding_percentage` → still narrows to 10% via bridge

Existing dividend tests must continue to pass. For existing tests that
use deprecated fields and have no `direct_holding_percentage`, confirm
bridge fallback fires correctly without changing assertions.

## Exit Criteria

- All 10 new test cases pass
- Deprecated bridge fallback works for both `yes` and `no` threshold cases
- `short_holding_period_review_required` appears in all CN-NL dividend
  supported responses
- `calculated_threshold_met` is non-null when `direct_holding_percentage`
  is numeric
- Schema version is `slice3.v1` across top-level response and
  `machine_handoff`
- `python -m pytest backend/tests/` fully green
- `cd frontend && npm test -- --run src/App.test.tsx` passes
- `cd frontend && npm run build` passes
- Stage 4 and Stage 5 fixture suites remain green

## Known Gaps for Future Slices

1. **Deprecated field removal**: `direct_holding_confirmed` and
   `direct_holding_threshold_met` are removed in Slice 4. All fixture
   cases must be migrated to `direct_holding_percentage` before Slice 4
   begins.

2. **payment_date as a gating condition**: This slice accepts
   `payment_date` for audit context only. A future slice may use it to
   validate that the holding percentage is measured at the correct date,
   particularly for cases where shareholding changed during the year.

3. **Holding period as a gating condition**: If SAT guidance or treaty
   practice evolves to impose a minimum holding period for CN-NL dividends,
   `holding_period_months` should be upgraded from a risk signal to a
   narrowing condition in a dedicated slice with a new design artifact.

4. **Percentage precision edge cases**: The current implementation treats
   `25.0` as threshold-met. Cases involving nominee arrangements or
   indirect economic interests that nominally meet 25% but may not satisfy
   the spirit of Art. 10(2)(a) are not handled. Future slices should
   consider adding a `nominee_arrangement_flag`.
