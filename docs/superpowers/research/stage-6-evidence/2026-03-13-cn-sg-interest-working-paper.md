# CN-SG Interest Working Paper

Date: `2026-03-13`  
Stage: `stage_6`  
Income type: `interest`

## Purpose

This working paper records the Stage 6 clause-level verification for the China-Singapore interest lane and replaces the earlier source-placeholder treatment with paragraph-level treaty excerpts.

## Source Basis

- official treaty text:
  - `iras-cn-sg-dta-full-text-pdf`
- MLI status support:
  - `oecd-mli-signatories-and-parties`
  - `oecd-singapore-mli-peer-review-2024`

## Verified Clause

- location:
  - `Article 11(2)(a)` and `Article 11(2)(b)`
- verified operative excerpts:
  - `Article 11(2)(a)`: `7 per cent of the gross amount of the interest if it is received by any bank or financial institution;`
  - `Article 11(2)(b)`: `10 per cent of the gross amount of the interest in all other cases.`
- related manual-review note:
  - `Article 11(3)` contains government / central institution exemption language that remains outside the current automated narrowing lane

## Verification Result

- treaty-verified parameter:
  - `7% / 10%`
- branch conditions:
  - reduced branch depends on recipient being a bank or financial institution
  - general branch applies in all other cases
- source write-back:
  - completed in source fixture, curated dataset, and generated dataset

## Runtime Handling Decision

- single-turn result:
  - still `can_be_completed`, not auto-concluded
- reason:
  - the tool can show the two rate branches but will not infer institutional status automatically
- unchanged conservative boundary:
  - the exemption-like lane remains an unexpected finding for human review rather than a new schema invention

## MLI / PPT Note

- China / Singapore MLI dates and CTA status:
  - same fact basis as the dividends working paper
- product handling:
  - response carries a fact-based PPT prompt and explicit manual-review note

## Final Reading

The interest lane now has clause-level traceability across rate branches without expanding the product into exemption automation or open-ended treaty reasoning.
