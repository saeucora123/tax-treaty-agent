# Royalties Guided Facts Design

Date: 2026-03-17
Status: Approved for Slice 1 implementation
Purpose: lock the pre-approved guided-input fields for the `royalties` lane before implementation.

## Field List

| fact_key | prompt | review_need_mapping | allowed_values |
| --- | --- | --- | --- |
| `royalty_character_confirmed` | Is the payment actually for the use of, or the right to use, qualifying intellectual property? | Maps to the existing review need to confirm the payment fits the treaty royalties lane. | `yes`, `no`, `unknown` |
| `beneficial_owner_status` | Has the recipient's beneficial-owner status for the royalty income been separately confirmed? | Maps to the existing review need to confirm beneficial ownership before relying on treaty relief. | `yes`, `no`, `unknown` |
| `contract_payment_flow_consistent` | Do the contract, invoice, and payment flow support the current royalty characterization? | Maps to the existing review need to verify that the documentary trail supports the treaty characterization. | `yes`, `no`, `unknown` |

## Slice 1 Constraints

- These fields are approved for the Slice 1 guided royalties panel.
- No additional royalties guided-input fields may be added in Slice 1 without updating this artifact.
- Slice 1 may use these fields for workflow guidance and BO precheck only.
- Slice 1 does not change the substantive royalties treaty-eligibility logic based on these fields.

## Known Gaps for Future Slices

The following gaps are out of scope for Slice 1 but must be addressed before the royalties path is substantively deepened:

1. **Technical service fee vs. royalty characterization**: No field explicitly captures whether the payment could be recharacterized from a technical service fee to a royalty (or vice versa) under Chinese tax authority practice. SAT has historically applied an expansive interpretation of royalties (see Guoshuihan [2009] No. 507 and subsequent guidance). A user who does not know this dispute risk may answer `royalty_character_confirmed: yes` while actual recharacterization exposure exists.

2. **Explicit recharacterization risk prompt**: A future slice should add a field that surfaces this dispute scenario directly, before any substantive narrowing is applied.

These gaps must be resolved in a dedicated design artifact before any slice that changes the substantive royalties treaty-eligibility logic.
