# Tax Treaty Agent Alignment Roadmap Design

Date: 2026-03-11
Status: Approved for execution

## 1. Why This Document Exists

The project now has real implementation progress, but its public story and internal build priorities are at risk of drifting apart.

This document realigns the project around two separate layers:

- external product identity
- internal project-selection criteria

The goal is not to restart the project. The goal is to preserve what already works, cut ambiguity, and make future work serve the original mission more directly.

## 2. External Product Identity

Publicly, `Tax Treaty Agent` should be presented as:

- a cross-border payment tax treaty review tool
- a bounded professional tool
- a first-pass pre-review system, not a final legal or tax opinion engine

It should not be presented as:

- a generic tax chatbot
- an all-country treaty platform
- a customer-ready compliance product
- a resume project in disguise

### External one-sentence positioning

`Tax Treaty Agent` is a bounded tax treaty review tool that helps users run a first-pass, source-aware analysis of cross-border payment scenarios using structured treaty data and explicit review guidance.

## 3. Internal Success Criteria

Internally, the current priority is to make this repo a strong GitHub and resume project.

That means the project should signal, in this order:

1. ability to turn a complex business problem into a credible AI product
2. understanding of cross-border tax and treaty-review constraints
3. ability to ship a real, explainable, demoable full-stack system

This internal goal should shape build decisions, but it should not appear in the product-facing copy.

## 4. Current Assets To Preserve

These are already working and should be treated as core assets, not side quests:

- bounded MVP scope: China-Netherlands only
- structured treaty-backed output
- explicit unsupported and incomplete behavior
- article and paragraph source anchors
- parser-like source-document import layer
- extraction confidence and source-language metadata
- confidence-aware review escalation
- simple one-screen frontend demo

The project already has the beginnings of a credible trust model. Future work should strengthen that, not dilute it.

## 5. New Phase Structure

### Phase A: GitHub-Strong Product Form

Primary goal:

- make the project easy to understand, trust, and explain to a stranger

What Phase A must deliver:

- a very strong README
- a stable demo story
- crisp explanation of supported vs unsupported scope
- architecture and trust narrative
- polished examples and screenshots
- consistent language across code, docs, and UI

What Phase A must not try to do:

- become production-ready
- add many countries
- promise customer deployment
- add broad AI behavior without trust controls

Completion markers:

- someone can understand the problem, scope, and trust model in under 2 minutes
- supported cases look intentional
- unsupported cases feel professional, not broken
- the repo tells one coherent story

### Phase B: Real-Document-Driven Demo

Primary goal:

- prove the system can move beyond manually curated treaty entries

What Phase B should deliver:

- at least one real document acquisition path
- document segmentation and structured extraction workflow
- validation and fallback behavior for low-confidence extraction
- continued source traceability into the user-facing result

What Phase B must not try to do:

- expand to many countries too early
- replace all rules with free-form model output
- skip validation in the name of looking more “AI”

Completion markers:

- one narrow real-document path works end to end
- extraction quality affects system behavior
- the system can explain where its supported result came from

### Phase C: Trial-Tool Evaluation

Primary goal:

- decide whether the project should ever move toward limited real-world use

What Phase C would require before serious consideration:

- stronger update discipline
- clear document-maintenance assumptions
- stronger failure and review boundaries
- explicit human-review workflow

This phase is intentionally later. It is not the current job.

## 6. Immediate Priority Stack

For the next 2 to 6 weeks, prioritize in this order:

1. product narrative and repo presentation
2. trust and review behavior polish
3. example quality and demo strength
4. narrow, believable document-driven upgrade steps

This means the project should prefer:

- better README and visuals over broad feature growth
- clearer refusal behavior over wider support
- stronger review cues over flashy AI behavior

## 7. Explicit Non-Goals For Now

Do not prioritize these yet:

- multi-country expansion
- customer-facing onboarding flows
- generic tax conversation
- aggressive deployment work
- broad RAG claims without reliable extraction and validation
- any feature that weakens the “bounded professional tool” identity

## 8. What Future Work Should Be Measured Against

Every next step should answer:

1. does this make the product more credible?
2. does this improve the GitHub/project story?
3. does this preserve trust boundaries?
4. would a stranger understand why this feature exists?

If the answer to most of these is no, it is likely not the right next step.

## 9. Recommended Next Execution Steps

The next practical work items should be:

1. align README intro and structure to the approved external product identity
2. create a tighter public-facing project story and feature framing
3. define the concrete checklist for “Phase A complete”
4. only after that, resume scoped implementation work that strengthens trust and demo quality
