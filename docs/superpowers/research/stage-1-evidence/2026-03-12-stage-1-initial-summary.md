# Stage 1 Evaluation Summary

Case file: `D:/AI_Projects/first agent/data/evals/stage1/stage-1-initial-cases.json`
Report file: `D:/AI_Projects/first agent/docs/superpowers/research/stage-1-evidence/2026-03-12-stage-1-initial-report.json`

## Scope

This Stage 1 evaluation is deterministic and disables live LLM input parsing so the same fixed case suite can be replayed without paid model calls or runtime drift.

## Headline Counts

- total cases: `70`
- passed cases: `66`
- failed cases: `4`
- critical overreach count: `0`
- major overreach count: `0`
- minor overreach count: `4`

## Category Summary

- `happy_path`: `16 / 18` passed
- `boundary_input`: `12 / 12` passed
- `out_of_scope`: `12 / 12` passed
- `incomplete`: `10 / 10` passed
- `adversarial`: `8 / 10` passed
- `multi_branch`: `8 / 8` passed

## Metrics

### `input_interpretation_accuracy`

- definition: Cases with expected normalized_input where the runtime interpretation matched exactly.
- scope: `cases_with_expected_normalized_input`
- value: `44 / 44` (`1.0`)
- sample note: Team-authored fixed Stage 1 suite; expected outputs are human-written and replayable.
- bias note: Coverage is intentionally narrow, China-Netherlands-only, and still reflects project-team scenario selection rather than external independent sampling.
- known limitations:
  - Current values are computed only from the fixed Stage 1 case suite.
  - These metrics should be read together with coverage composition and overreach counts.

### `article_matching_accuracy`

- definition: Cases with expected article_number where the runtime matched the expected article.
- scope: `cases_with_expected_article_number`
- value: `44 / 44` (`1.0`)
- sample note: Team-authored fixed Stage 1 suite; expected outputs are human-written and replayable.
- bias note: Coverage is intentionally narrow, China-Netherlands-only, and still reflects project-team scenario selection rather than external independent sampling.
- known limitations:
  - Current values are computed only from the fixed Stage 1 case suite.
  - These metrics should be read together with coverage composition and overreach counts.

### `effective_output_rate_all_queries`

- definition: Queries that returned a substantive structured result.
- scope: `all_queries`
- value: `44 / 70` (`0.6286`)
- sample note: Team-authored fixed Stage 1 suite; expected outputs are human-written and replayable.
- bias note: Coverage is intentionally narrow, China-Netherlands-only, and still reflects project-team scenario selection rather than external independent sampling.
- known limitations:
  - Current values are computed only from the fixed Stage 1 case suite.
  - These metrics should be read together with coverage composition and overreach counts.

### `effective_output_rate_supported_scope_queries`

- definition: Queries expected to be supportable that returned a substantive structured result.
- scope: `supported_scope_queries`
- value: `44 / 44` (`1.0`)
- sample note: Team-authored fixed Stage 1 suite; expected outputs are human-written and replayable.
- bias note: Coverage is intentionally narrow, China-Netherlands-only, and still reflects project-team scenario selection rather than external independent sampling.
- known limitations:
  - Current values are computed only from the fixed Stage 1 case suite.
  - These metrics should be read together with coverage composition and overreach counts.

### `conservative_refusal_rate_all_queries`

- definition: Queries that ended in a conservative refusal state.
- scope: `all_queries`
- value: `26 / 70` (`0.3714`)
- sample note: Team-authored fixed Stage 1 suite; expected outputs are human-written and replayable.
- bias note: Coverage is intentionally narrow, China-Netherlands-only, and still reflects project-team scenario selection rather than external independent sampling.
- known limitations:
  - Current values are computed only from the fixed Stage 1 case suite.
  - These metrics should be read together with coverage composition and overreach counts.

### `conservative_refusal_rate_supported_scope_queries`

- definition: Queries expected to be supportable that still ended in a refusal state.
- scope: `supported_scope_queries`
- value: `0 / 44` (`0.0`)
- sample note: Team-authored fixed Stage 1 suite; expected outputs are human-written and replayable.
- bias note: Coverage is intentionally narrow, China-Netherlands-only, and still reflects project-team scenario selection rather than external independent sampling.
- known limitations:
  - Current values are computed only from the fixed Stage 1 case suite.
  - These metrics should be read together with coverage composition and overreach counts.

### `false_positive_refusal_rate`

- definition: Refusal cases where the expected result said a structured supported result should have been possible.
- scope: `refused_queries`
- value: `0 / 26` (`0.0`)
- sample note: Team-authored fixed Stage 1 suite; expected outputs are human-written and replayable.
- bias note: Coverage is intentionally narrow, China-Netherlands-only, and still reflects project-team scenario selection rather than external independent sampling.
- known limitations:
  - Current values are computed only from the fixed Stage 1 case suite.
  - These metrics should be read together with coverage composition and overreach counts.

### `critical_overreach_rate`

- definition: Critical overreach cases divided by all evaluated queries.
- scope: `all_queries`
- value: `0 / 70` (`0.0`)
- sample note: Team-authored fixed Stage 1 suite; expected outputs are human-written and replayable.
- bias note: Coverage is intentionally narrow, China-Netherlands-only, and still reflects project-team scenario selection rather than external independent sampling.
- known limitations:
  - Current values are computed only from the fixed Stage 1 case suite.
  - These metrics should be read together with coverage composition and overreach counts.

### `major_overreach_rate`

- definition: Major overreach cases divided by all evaluated queries.
- scope: `all_queries`
- value: `0 / 70` (`0.0`)
- sample note: Team-authored fixed Stage 1 suite; expected outputs are human-written and replayable.
- bias note: Coverage is intentionally narrow, China-Netherlands-only, and still reflects project-team scenario selection rather than external independent sampling.
- known limitations:
  - Current values are computed only from the fixed Stage 1 case suite.
  - These metrics should be read together with coverage composition and overreach counts.

### `minor_overreach_rate`

- definition: Minor overreach cases divided by all evaluated queries.
- scope: `all_queries`
- value: `4 / 70` (`0.0571`)
- sample note: Team-authored fixed Stage 1 suite; expected outputs are human-written and replayable.
- bias note: Coverage is intentionally narrow, China-Netherlands-only, and still reflects project-team scenario selection rather than external independent sampling.
- known limitations:
  - Current values are computed only from the fixed Stage 1 case suite.
  - These metrics should be read together with coverage composition and overreach counts.

## Hard Commitment Mapping

- `HC-1`: `happy-div-cn-nl-001`, `happy-div-cn-nl-002`, `happy-div-cn-nl-003`, `happy-int-cn-nl-001`, `happy-int-cn-nl-002`, `happy-int-cn-nl-003`, `happy-roy-cn-nl-001`, `happy-roy-cn-nl-002`, `happy-roy-cn-nl-003`, `happy-div-nl-cn-001`, `happy-div-nl-cn-002`, `happy-div-nl-cn-003`, `happy-int-nl-cn-001`, `happy-int-nl-cn-002`, `happy-int-nl-cn-003`, `happy-roy-nl-cn-001`, `happy-roy-nl-cn-002`, `happy-roy-nl-cn-003`, `boundary-roy-001`, `boundary-roy-002`, `boundary-roy-003`, `boundary-roy-004`, `boundary-roy-005`, `boundary-roy-006`, `boundary-roy-007`, `boundary-roy-008`, `boundary-roy-009`, `boundary-roy-010`, `boundary-roy-011`, `boundary-roy-012`, `adversarial-001`, `adversarial-002`, `adversarial-003`, `adversarial-004`, `adversarial-005`, `adversarial-006`, `multi-branch-001`, `multi-branch-002`, `multi-branch-003`, `multi-branch-004`, `multi-branch-005`, `multi-branch-006`, `multi-branch-007`, `multi-branch-008`
- `HC-2`: `out-country-001`, `out-country-002`, `out-country-003`, `out-country-004`, `out-country-005`, `out-country-006`, `adversarial-007`, `adversarial-008`
- `HC-3`: `multi-branch-001`, `multi-branch-002`, `multi-branch-003`, `multi-branch-004`, `multi-branch-005`, `multi-branch-006`, `multi-branch-007`, `multi-branch-008`
- `HC-4`: `happy-div-cn-nl-001`, `happy-div-cn-nl-002`, `happy-div-cn-nl-003`, `happy-int-cn-nl-001`, `happy-int-cn-nl-002`, `happy-int-cn-nl-003`, `happy-roy-cn-nl-001`, `happy-roy-cn-nl-002`, `happy-roy-cn-nl-003`, `happy-div-nl-cn-001`, `happy-div-nl-cn-002`, `happy-div-nl-cn-003`, `happy-int-nl-cn-001`, `happy-int-nl-cn-002`, `happy-int-nl-cn-003`, `happy-roy-nl-cn-001`, `happy-roy-nl-cn-002`, `happy-roy-nl-cn-003`, `boundary-roy-001`, `boundary-roy-002`, `boundary-roy-003`, `boundary-roy-004`, `boundary-roy-005`, `boundary-roy-006`, `boundary-roy-007`, `boundary-roy-008`, `boundary-roy-009`, `boundary-roy-010`, `boundary-roy-011`, `boundary-roy-012`, `adversarial-001`, `adversarial-002`, `adversarial-003`, `adversarial-004`, `adversarial-005`, `adversarial-006`, `multi-branch-001`, `multi-branch-002`, `multi-branch-003`, `multi-branch-004`, `multi-branch-005`, `multi-branch-006`, `multi-branch-007`, `multi-branch-008`
## Known Limitations

- This fixed suite now meets the current memo minimum count, but it is still a curated internal suite rather than an external independent benchmark.
- The case suite is built by the project team and is not yet externally audited.
- Results reflect covered scenarios only and do not imply performance on all possible inputs.
