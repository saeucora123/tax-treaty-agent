# Stage 6 Human Review Test Note

Date: `2026-03-13`

## Test Setup

- test type:
  - `developer-simulated 15-minute review exercise`
- purpose:
  - check whether a reviewer can accept or challenge the Stage 6 output without separately reopening the treaty text from scratch
- cases used:
  - `CN -> SG dividends`
  - `CN -> NL royalties`

## Exercise

For each case, the reviewer was limited to the product output and its Stage 6 source-chain fields:

- treaty version note
- paragraph-level source reference
- real excerpt
- fact-based `MLI / PPT` prompt
- working-paper reference

The reviewer was asked to decide within `15 minutes`:

1. whether the treaty lane looked correct
2. whether the rate / branch display was supportable
3. whether the remaining issues were genuinely “manual confirmation items” rather than hidden missing citations

## Result

- total review time used:
  - approximately `12 minutes`
- outcome:
  - both cases were reviewable without reopening treaty text from zero
- remaining human tasks:
  - `CN-SG dividends`: confirm direct holding, beneficial ownership, and PPT risk before choosing the reduced branch
  - `CN-NL royalties`: confirm beneficial ownership and royalty characterization

## Reading

The important result is not that Stage 6 eliminates manual review. It does not. The important result is that the reviewer can now see:

- which treaty version is being used
- which paragraph supports the displayed rate
- what exact excerpt supports that paragraph
- why PPT still needs manual confirmation

That is enough to move the tool from “structured but not yet trustworthy” toward “structured and professionally reviewable.”
