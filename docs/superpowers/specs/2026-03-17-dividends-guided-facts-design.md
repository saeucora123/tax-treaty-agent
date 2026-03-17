# CN-NL Dividends Guided Facts Design

Date: 2026-03-17  
Status: Approved for Slice 2 implementation  
Purpose: Lock the pre-approved guided-input fields and narrowing logic for the
CN-NL dividends lane deepening, before Slice 2 Part B implementation begins.

## Background

The current Slice 1 dividend implementation uses four threshold-level
user-declared facts to drive narrowing. `direct_holding_confirmed` in the
current implementation is consumed as a plain declared value only — the code
does not check for intermediate holding entities. This design artifact governs
Slice 2 deepening within the same threshold-level contract and adds one field
to close the intermediate-structure gap. Field granularity upgrade (to
computable raw facts such as actual holding percentage or holding period in
months) is explicitly out of scope for Slice 2 and is documented under Known
Gaps.

## Existing Fields (Carried Forward From Slice 1)

These four fields are already implemented. Do not redefine or rename them in
Slice 2. Slice 2 may only clarify their handling in the edge cases described
in the narrowing logic table below.

| fact_key | prompt | allowed_values |
|---|---|---|
| `direct_holding_confirmed` | Has it been confirmed that the recipient directly holds shares in the paying company (not through an intermediary)? | `yes`, `no`, `unknown` |
| `direct_holding_threshold_met` | Does the recipient's direct shareholding meet or exceed 25% of the capital of the paying company? | `yes`, `no`, `unknown` |
| `beneficial_owner_confirmed` | Has the recipient's status as beneficial owner of the dividend income been separately confirmed? | `yes`, `no`, `unknown` |
| `pe_effectively_connected` | Is the shareholding effectively connected to a permanent establishment of the recipient in China? | `yes`, `no`, `unknown` |

## New Fields Added in Slice 2

| fact_key | prompt | review_need_mapping | allowed_values |
|---|---|---|---|
| `holding_structure_is_direct` | Is the holding structure confirmed to be direct with no intermediate holding entity between the recipient and the paying company? | The current `direct_holding_confirmed` field is consumed as a plain declared value and does not check for intermediate entities. This field closes that gap. A `no` answer blocks the 5% path even if the threshold is met, because intermediate structures cannot satisfy Art. 10(2)(a) without look-through analysis. A `yes` answer is required alongside `direct_holding_confirmed: yes` and `direct_holding_threshold_met: yes` for the 5% path to proceed. | `yes`, `no`, `unknown` |
| `mli_ppt_risk_flag` | Has a principal purpose test (PPT) risk assessment been performed for this dividend payment under the MLI? | Maps to the review need to surface MLI/PPT exposure before relying on the 5% reduced rate. The CN-NL treaty is covered by the MLI and the PPT applies. A `no` or `unknown` answer does not block narrowing but must appear in handoff output as a mandatory review signal. | `yes`, `no`, `unknown` |

## Narrowing Logic (Slice 2)

The following is the authoritative decision table for
`resolve_dividend_branch_from_facts()` in Slice 2. Conditions are evaluated
in the order listed. The first matching condition determines the outcome.

| Priority | Condition | Outcome |
|---|---|---|
| 1 | `pe_effectively_connected == yes` | Terminate: PE exclusion. Art. 10(4). |
| 2 | `beneficial_owner_confirmed == no` | Terminate: BO prerequisite not met. |
| 3 | `beneficial_owner_confirmed == unknown` | Terminate: insufficient facts. |
| 4 | `direct_holding_confirmed == no` | Narrow to 10% general rate. Art. 10(2)(b). |
| 5 | `direct_holding_confirmed == unknown` | Terminate: insufficient facts. |
| 6 | `direct_holding_threshold_met == no` | Narrow to 10% general rate. Art. 10(2)(b). |
| 7 | `direct_holding_threshold_met == unknown` | Terminate: insufficient facts. |
| 8 | `holding_structure_is_direct == no` | Narrow to 10% general rate. Art. 10(2)(b). Intermediate structure blocks 5% path. |
| 9 | `holding_structure_is_direct == unknown` | Terminate: insufficient facts. |
| 10 | `direct_holding_confirmed == yes` AND `direct_holding_threshold_met == yes` AND `holding_structure_is_direct == yes` AND `beneficial_owner_confirmed == yes` | Narrow to 5% reduced rate. Art. 10(2)(a). |
| 11 | Conflict between user-declared facts | Terminate: conflict state. Preserve in handoff. |

`mli_ppt_risk_flag` does not appear in this table. It never affects rate
selection or termination. It only generates a mandatory handoff signal (see
Handoff Output Requirements).

## BO Precheck Integration

- `beneficial_owner_confirmed` feeds into `bo_precheck` as the primary BO signal.
- `holding_structure_is_direct` also feeds into `bo_precheck`: an indirect
  structure (`no`) with a claimed threshold met is a structural BO risk
  indicator and must appear in `facts_considered`.
- `bo_precheck` must never upgrade or change a conclusion. It is a handoff
  signal only.

## Handoff Output Requirements

Slice 2 CN-NL dividend supported responses must include in `machine_handoff`:

- Applied rate and the specific condition row that determined it
- Source reference to Art. 10(2)(a) for 5% outcomes
- Source reference to Art. 10(2)(b) for 10% outcomes  
- PE exclusion reference to Art. 10(4) when triggered
- `bo_precheck` block with `facts_considered` listing at minimum
  `beneficial_owner_confirmed` and `holding_structure_is_direct`
- `mli_ppt_review_required: true` whenever `mli_ppt_risk_flag` is not `yes`,
  regardless of rate outcome

## Slice 2 Constraints

- No field granularity upgrade in this slice.
- No new income types.
- CN-SG remains supported and untouched.
- Interest and royalties substantive logic unchanged.
- `mli_ppt_risk_flag` does not block narrowing in this slice.
- `holding_structure_is_direct` affects rate selection but does not constitute
  a BO determination.

## Known Gaps for Future Slices

1. **Field granularity**: Current fields are threshold-level (yes/no/unknown).
   Future deepening requires computable raw facts: `direct_holding_percentage`,
   `holding_period_months`, `tested_date`. This is a system-level redesign
   and must be a separate slice.

2. **Holding period**: The CN-NL treaty Art. 10(2)(a) does not specify a
   minimum holding period, but Chinese domestic anti-avoidance practice and
   SAT guidance have applied holding period scrutiny in dividend withholding
   cases. No field captures this risk in Slice 2. Requires field granularity
   upgrade first.

3. **MLI PPT substantive assessment**: `mli_ppt_risk_flag` is a workflow flag
   only. A future slice should introduce a structured PPT pre-assessment
   sub-module once there is sufficient SAT/SBR practice to parameterize the
   relevant factors.

4. **Indirect holding look-through**: `holding_structure_is_direct == no`
   blocks the 5% path but does not analyze the intermediate entity. Future
   slices should add intermediate entity characterization fields to support
   look-through analysis.

These gaps must be resolved in dedicated design artifacts before any slice
that addresses them.

## Implementation Notes

**Conflict pre-check ordering (Slice 2):** The narrowing logic table lists
conflict termination as Priority 11. In the Slice 2 implementation,
conflict detection is applied before conditions 4–9 in order to preserve
existing conflict test assertions. The handoff field `determining_condition_priority`
still reports `11` for conflict outcomes to maintain table label consistency.
This is an intentional deviation from strict table ordering and is not a bug.
