# Interest Guided Facts Design

Date: 2026-03-17
Status: Approved for Slice 1 implementation
Purpose: lock the pre-approved guided-input fields for the `interest` lane before implementation.

## Field List

| fact_key | prompt | review_need_mapping | allowed_values |
| --- | --- | --- | --- |
| `interest_character_confirmed` | Is the payment legally characterized as interest under the financing arrangement? | Maps to the existing review need to confirm the payment is truly interest rather than another payment type. | `yes`, `no`, `unknown` |
| `beneficial_owner_status` | Has the recipient's beneficial-owner status for the interest income been separately confirmed? | Maps to the existing review need to confirm the recipient is the beneficial owner before relying on treaty relief. | `yes`, `no`, `unknown` |
| `lending_documents_consistent` | Do the loan agreement, interest calculation, and payment records support the current interest characterization? | Maps to the existing review need to verify that core supporting documents line up with the treaty characterization. | `yes`, `no`, `unknown` |

## Slice 1 Constraints

- These fields are approved for the Slice 1 guided interest panel.
- No additional interest guided-input fields may be added in Slice 1 without updating this artifact.
- Slice 1 may use these fields for workflow guidance and BO precheck only.
- Slice 1 does not change the substantive interest treaty-eligibility logic based on these fields.

## Known Gaps for Future Slices

The following gaps are out of scope for Slice 1 but must be addressed before the interest path is substantively deepened:

1. **Related-party flag**: No field currently captures whether the lending arrangement is between related parties. In CN-NL scenarios, related-party interest is subject to transfer pricing scrutiny, and rates outside arm's-length range may be recharacterized or denied deduction by Chinese tax authorities.

2. **Transfer pricing support for interest rate**: No field captures whether the interest rate has been benchmarked or supported by a TP study. This is a required input for any future substantive interest-eligibility narrowing.

These gaps must be resolved in a dedicated design artifact before any slice that changes the substantive interest treaty-eligibility logic.
