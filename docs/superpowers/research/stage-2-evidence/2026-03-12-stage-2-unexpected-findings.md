# Stage 2 Unexpected Findings

Date: `2026-03-12`

## Finding 1: CN-SG interest has an exemption-like side lane

- observation:
  - the `CN-SG` interest structure is not exhausted by the `7% / 10%` branch pair
- risk:
  - forcing every future variation into a pure rate-branch model may blur exemption semantics
- Stage 2 decision:
  - record the lane as a future schema-design topic
  - do not expand the runtime contract or UI in this stage

## Finding 2: supported-scope copy was more pair-coupled than expected

- observation:
  - unsupported guidance, examples, and treaty labels were still written as if `CN-NL` were the only pilot pair
- risk:
  - product copy would drift away from actual runtime support even if the engine behaved correctly
- Stage 2 decision:
  - make supported examples and pair labels registry-driven

## Finding 3: legacy builder naming masked a reusable core

- observation:
  - [build_cn_nl_dataset.py](D:\AI_Projects\first agent\scripts\build_cn_nl_dataset.py) was named after one pair, but most logic was already generic
- risk:
  - cloning it pair-by-pair would have created fake architecture complexity
- Stage 2 decision:
  - keep one builder entry and generalize the metadata layer instead of copying the script
