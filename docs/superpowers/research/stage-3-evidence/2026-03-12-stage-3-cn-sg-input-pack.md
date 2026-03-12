# Stage 3 CN-SG Pressure Test Input Pack

Date: 2026-03-12
Stage: `stage_3`
Status: Active source-summary pack
Purpose: collect the minimal official-source-backed material needed for the `CN-SG` Stage 3 schema pressure test.

## 1. Source Used

Primary source for this pack:

- Ministry of Foreign Affairs of the People's Republic of China
- `AGREEMENT BETWEEN THE GOVERNMENT OF THE PEOPLE'S REPUBLIC OF CHINA AND THE GOVERNMENT OF THE REPUBLIC OF SINGAPORE FOR THE AVOIDANCE OF DOUBLE TAXATION AND THE PREVENTION OF FISCAL EVASION WITH RESPECT TO TAXES ON INCOME`
- Source URL:
  [https://www.fmprc.gov.cn/eng/wjb_663304/zzjg_663340/gjs_gjb/tyylb_665314/tyk/201211/t20121102_767549.html](https://www.fmprc.gov.cn/eng/wjb_663304/zzjg_663340/gjs_gjb/tyylb_665314/tyk/201211/t20121102_767549.html)

Stage 3 use of this source is intentionally narrow:

- `Article 10`
- `Article 11`
- `Article 12`

## 2. Stage-3-Relevant Rule Summaries

### Article 10 - Dividends

Working summary from the official text:

- a general source-state cap exists for dividends
- a lower cap exists where the beneficial owner is a company or partnership and directly holds at least `25%`
- the source text also contains a Singapore-specific paragraph about additional dividend taxation not being charged in Singapore, unless such tax is introduced in the future

Stage 3 relevance:

- useful for testing bounded branch display
- useful for testing whether one treaty can contain both ordinary rate branching and direction-sensitive asymmetry

### Article 11 - Interest

Working summary from the official text:

- a general source-state cap exists for interest
- a lower cap exists for bank / financial-institution lending
- a full exemption lane exists for certain government / central-bank related interest

Stage 3 relevance:

- useful for testing branch display beyond the current `CN-NL` dividend example
- useful for testing whether the current contract can represent exemption-like outcomes without pretending they are just ordinary numeric rates

### Article 12 - Royalties

Working summary from the official text:

- royalties may be taxed in the source state
- the source-state rate cap is `10%`

Stage 3 relevance:

- straightforward compatibility check for a simple single-rate article

## 3. Why This Input Pack Is Sufficient For Stage 3

This pack is not meant to prove second-country onboarding.

It is sufficient for Stage 3 because it gives us:

- one simple single-rate article
- one multi-branch dividends article
- one article with both preferential rate and exemption-like structure

That combination is enough to pressure-test:

- schema fit
- output-state fit
- bounded-completion fit
- hidden `CN-NL` assumptions

## 4. Encoding Targets For The Hand-Encoded Sample

The pressure-test sample should cover at least these candidate rules:

1. `Article 10` general dividend cap
2. `Article 10` reduced dividend cap for `>= 25%` ownership
3. `Article 11` general interest cap
4. `Article 11` reduced bank / financial-institution cap
5. `Article 12` royalty cap

Optional extension:

6. `Article 11` government / central-bank exemption lane

## 5. Expected Pressure Points

The following are the most likely friction points the pressure test should check:

- whether Stage 3 branch messaging is overfit to the current `CN-NL` dividend story
- whether direction-sensitive treaty asymmetry can still sit under the same output contract
- whether exemption-like outcomes need a clearer field than a plain `rate`
