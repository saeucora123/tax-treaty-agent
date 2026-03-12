# Tax Treaty Agent Stage 3.5 User Calibration Brief

Date: 2026-03-12
Stage: `stage_3_5`
Status: Active
Purpose: run a lightweight but decision-grade user-calibration checkpoint before committing the project to Stage 4 pseudo-multiturn or skipping directly to Stage 2.

## 1. Goal

Stage 3.5 is not a courtesy review. It is a gate whose job is to answer one narrow product question:

`After Stage 3 conservative-output improvements, is bounded single-turn output already useful enough, or is fact-completion interaction the next highest-value slice?`

This stage should produce evidence for:

- `G3.5.1`: feedback from at least 3 target users, including at least 1 adjacent-workflow user who is not a treaty specialist
- `G3.5.2`: a structured calibration summary with explicit priority implications
- `G3.5.3`: a recorded decision on whether to enter `Stage 4`

## 2. Non-Goals

This stage does not:

- validate true multiturn conversation design
- onboard a second country pair
- optimize UI polish for its own sake
- seek commercial willingness-to-pay evidence
- widen product scope beyond the current `CN-NL + dividends / interest / royalties` boundary

## 3. Participant Mix

Minimum required participants: `3`

Recommended participant mix:

1. `Ideal professional user`
   - tax manager / tax adviser / international tax practitioner
   - goal: test whether conservative structured output is professionally useful
2. `Operational user`
   - finance specialist / treasury / tax operations / accounting staff
   - goal: test whether outputs help a real pre-review workflow
3. `Adjacent-workflow user`
   - business-side operator, finance generalist, or cross-border process participant with limited treaty depth
   - goal: test whether the result format is usable for a real adjacent workflow role rather than only for treaty specialists

Stretch target:

- `4-5` users if scheduling is easy, but do not hold the gate hostage to broader recruiting

## 4. Materials To Show

Each participant session should stay narrow. Show no more than `3` prepared result states plus one short product framing.

Required demonstration pack:

1. `预审完成`
   - supported single-rate case
   - goal: confirm the result looks credible and operational
2. `可补全`
   - bounded missing-fact case
   - goal: test whether users understand that one missing fact can further narrow the result
3. `预审部分完成` or `需要人工介入`
   - branch ambiguity or higher-review case
   - goal: test whether conservative output still reduces work even without a final answer

Optional fourth item:

4. `不在支持范围`
   - only if needed to test whether scope boundaries are clear without sounding broken

## 5. Session Structure

Recommended session length: `20-30` minutes

Suggested flow:

1. `2 min` product framing
   - this is a bounded treaty pre-review tool, not a final opinion engine
2. `8-12 min` walk through the prepared result states
3. `8-10 min` structured feedback questions
4. `2-4 min` wrap-up and priority probe

## 6. Minimum Question Set

Use the same core questions in every session so later comparison is clean.

Required questions:

1. `你现在的第一反应是什么？`
   - goal: capture whether the result feels useful, confusing, or too conservative
2. `你最先会看哪一块输出？为什么？`
   - goal: learn which result blocks actually matter in a workflow
3. `如果这是你手上的真实场景，这个结果会让你下一步怎么做？`
   - goal: test whether output narrows work rather than only describing it
4. `你觉得这个结果已经够用，还是你会希望系统再追问 1-2 个关键事实？`
   - goal: directly calibrate Stage 4 urgency
5. `哪一部分最不清楚，或者最像“系统在说很多但帮得不够多”？`
   - goal: identify dead-weight output or ambiguous phrasing
6. `如果你要把这个结果转发给别人，你会转发给谁？用什么形式？`
   - goal: inform later handoff design

Optional probes:

7. `候选税率分支 / 下一步动作 / 已确认范围，哪一项最有价值？`
8. `你会更想要表单式补事实，还是现在这样先自己补完再重查？`

## 7. Evidence Capture Rules

Every session must produce:

- participant profile
- current workflow description
- structured answers to the core question set
- observed confusion points
- priority implication for product sequencing

Evidence format:

- one session note per participant
- one aggregated calibration summary after all required sessions finish

Use:

- `docs/superpowers/plans/templates/2026-03-12-tax-treaty-agent-user-calibration-session-template.md`
- `docs/superpowers/plans/templates/2026-03-12-tax-treaty-agent-user-calibration-summary-template.md`

Store completed session notes and summaries under:

- `docs/superpowers/research/stage-3-5-evidence/`

## 8. Decision Rules

At the end of the minimum session set, classify the result into one of three outcomes:

### Outcome A: Enter Stage 4

Use this if:

- users repeatedly say bounded fact completion would materially improve usefulness
- current single-turn output is valuable but not enough to close the most common workflow gap
- the missing facts users want are narrow and closed-ended

### Outcome B: Skip Stage 4 and go to Stage 2

Use this if:

- users say improved single-turn output is already sufficient for their first-pass workflow
- the main next value is coverage / scalability evidence rather than interaction depth
- users do not strongly ask for in-flow fact completion

### Outcome C: Hold and refine Stage 3 output

Use this if:

- users still find the current output structurally confusing
- the main failure is not lack of interaction, but lack of clarity or prioritization

## 9. Gate Mapping

This brief supports gate review in the following way:

- `G3.5.1`: participant mix and session count are satisfied by the session notes
- `G3.5.2`: structured summary template produces a decision-grade calibration summary
- `G3.5.3`: the aggregated summary must end with an explicit next-stage recommendation and rationale

## 10. Immediate Next Move

The next construction step is:

1. recruit or identify the minimum `3` participants
2. run the sessions using the fixed question set
3. write the structured summary
4. record the decision: `Stage 4` or `Stage 2`
