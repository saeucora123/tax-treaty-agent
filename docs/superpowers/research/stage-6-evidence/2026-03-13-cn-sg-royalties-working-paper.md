# CN-SG Royalties Working Paper

Date: `2026-03-13`  
Stage: `stage_6`  
Income type: `royalties`

## Purpose

This working paper records the Stage 6 treaty verification for the China-Singapore royalties lane and confirms that the runtime now exposes a real treaty excerpt instead of a placeholder sample.

## Source Basis

- official treaty text:
  - `iras-cn-sg-dta-full-text-pdf`
- MLI status support:
  - `oecd-mli-signatories-and-parties`
  - `oecd-singapore-mli-peer-review-2024`

## Verified Clause

- location:
  - `Article 12(2)`
- verified operative excerpt:
  - `However, such royalties may also be taxed in the Contracting State in which they arise and according to the laws of that State, but if the beneficial owner of the royalties is a resident of the other Contracting State, the tax so charged shall not exceed 10 per cent of the gross amount of the royalties.`

## Verification Result

- treaty-verified parameter:
  - `10%`
- source reference in runtime:
  - `CN-SG Article 12(2)`
- source write-back:
  - completed in `data/source_documents/cn-sg-main-treaty.json`
  - completed in `data/treaties/cn-sg.v3.json`
  - completed in `data/treaties/cn-sg.v3.generated.json`

## MLI / PPT Note

- China / Singapore MLI dates and CTA status:
  - same fact basis as the dividends working paper
- product handling:
  - response now includes a treaty-specific PPT prompt rather than a generic anti-abuse warning

## Final Reading

The royalties lane is now source-governed at the same level as the other China-Singapore income types, so Stage 6 no longer leaves one supported category behind as a placeholder-only output.
