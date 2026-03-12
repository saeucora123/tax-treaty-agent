# Stage 6 Comparison Output Note

Date: `2026-03-13`

## Purpose

This note compares the two supported treaty pairs across all three supported income types after Stage 6 source-chain closure.

## Output Comparison

| Pair / income | Review state | Rate display | Source reference | Version note |
| --- | --- | --- | --- | --- |
| `CN-NL dividends` | `can_be_completed` | `5% / 10%` | `Article 10(2)(b)` | `2013 agreement reflected in the official English treaty text used for the stable runtime dataset.` |
| `CN-NL interest` | `pre_review_complete` | `10%` | `Article 11(2)` | `2013 agreement reflected in the official English treaty text used for the stable runtime dataset.` |
| `CN-NL royalties` | `pre_review_complete` | `10%` | `Article 12(2)` | `2013 agreement reflected in the official English treaty text used for the stable runtime dataset.` |
| `CN-SG dividends` | `can_be_completed` | `5% / 10%` | `CN-SG Article 10(2)(b)` | `2007 agreement ... with the Second Protocol effective from 1 January 2010 and the Third Protocol effective from 1 January 2013 incorporated into the operative Articles 10 to 12.` |
| `CN-SG interest` | `can_be_completed` | `7% / 10%` | `CN-SG Article 11(2)(b)` | `2007 agreement ... with the Second Protocol effective from 1 January 2010 and the Third Protocol effective from 1 January 2013 incorporated into the operative Articles 10 to 12.` |
| `CN-SG royalties` | `pre_review_complete` | `10%` | `CN-SG Article 12(2)` | `2007 agreement ... with the Second Protocol effective from 1 January 2010 and the Third Protocol effective from 1 January 2013 incorporated into the operative Articles 10 to 12.` |

## Key Reading

- the same runtime/output architecture now handles both treaty pairs without pair-specific UI logic
- the two dividend lanes both preserve ambiguity in single-turn mode, but each pair now carries its own treaty-version note and paragraph-level reference
- China-Singapore and China-Netherlands now both expose fact-based MLI / PPT prompts instead of one pair being “real” and the other remaining template-like
- the comparison is especially important for China-Singapore because the Stage 6 truth-check corrected an outdated dividend branch assumption before the pair was allowed to claim source-chain closure

## Conclusion

This comparison is the strongest current proof that the repo is not merely reusing a generic shell. It is reusing architecture while keeping treaty-specific parameters, treaty-version notes, and source references distinct.
