# CN-SG Dividends Working Paper

Date: `2026-03-13`  
Stage: `stage_6`  
Income type: `dividends`

## Purpose

This working paper closes the Stage 6 source-chain gap for the China-Singapore dividend lane and records the treaty truth-check that replaced the earlier Stage 2 placeholder-like understanding.

## Source Basis

- official treaty text:
  - `iras-cn-sg-dta-full-text-pdf`
  - URL: <https://www.iras.gov.sg/media/docs/default-source/uploadedfiles/pdf/ratificationsingaporechinadtafinalwithprotocol.pdf?sfvrsn=9b057a88_2>
- protocol history cross-check:
  - `iras-cn-sg-second-protocol-newsroom`
  - `iras-cn-sg-third-protocol-newsroom`
- MLI status support:
  - `oecd-mli-signatories-and-parties`
  - `oecd-singapore-mli-peer-review-2024`

## Treaty / Version Note

- agreement title:
  - `Agreement between the Government of the Republic of Singapore and the Government of the People's Republic of China for the Avoidance of Double Taxation and the Prevention of Fiscal Evasion with respect to Taxes on Income`
- version reading used for runtime:
  - IRAS full treaty text showing the 2007 agreement with later protocol history noted on page 1
- protocol timing noted in the source package:
  - Second Protocol effective from `2010-01-01`
  - Third Protocol effective from `2013-01-01`

## Verified Clause

- location:
  - `Article 10(2)(a)` and `Article 10(2)(b)`
- language used in runtime:
  - `English`
- verified operative excerpts:
  - `Article 10(2)(a)`: `5 per cent of the gross amount of the dividends if the beneficial owner is a company (other than a partnership) which holds directly at least 25 per cent of the capital of the company paying the dividends;`
  - `Article 10(2)(b)`: `10 per cent of the gross amount of the dividends in all other cases.`

## Verification Result

- system parameter before Stage 6 review:
  - `7% / 12%`
- treaty-verified parameter after source check:
  - `5% / 10%`
- comparison outcome:
  - `not consistent`
- required correction:
  - yes; Stage 2 `7% / 12%` values were replaced

## Important Finding

The IRAS PDF also contains older treaty text later in the document, including a legacy `7% / 12%` dividend formulation. The operative Article 10 text used for the current runtime basis is the updated `5% / 10%` branch shown in the consolidated treaty text section. This explains why the earlier Stage 2 numbers could appear plausible while still being wrong for the operative version.

## Write-Back Outcome

- updated source fixture:
  - `data/source_documents/cn-sg-main-treaty.json`
- updated runtime dataset:
  - `data/treaties/cn-sg.v3.json`
- updated generated dataset:
  - `data/treaties/cn-sg.v3.generated.json`
- updated evaluation baseline:
  - `data/evals/stage2/stage-2-cn-sg-cases.json`
  - `data/evals/stage6/stage-6-source-chain-cases.json`

## MLI / PPT Note

- China MLI deposit / entry into force:
  - `2022-05-25` / `2022-09-01`
- Singapore MLI deposit / entry into force:
  - `2018-12-21` / `2019-04-01`
- treaty treated as CTA:
  - `yes`, based on OECD peer-review material
- PPT:
  - `applicable`
- product handling:
  - output now gives a fact-based PPT prompt and still requires manual confirmation

## Final Reading

Stage 6 closes the main CN-SG dividends credibility gap by proving that the runtime branch is now grounded in the operative treaty text rather than in remembered or placeholder numbers.
