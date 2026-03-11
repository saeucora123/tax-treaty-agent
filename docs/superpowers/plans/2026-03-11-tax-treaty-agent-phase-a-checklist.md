# Tax Treaty Agent Phase A Checklist

Date: 2026-03-11
Status: Active
Purpose: turn the current repo into a GitHub-strong project form without changing the public-facing product identity.

## Phase A Outcome

By the end of Phase A, the repo should feel like a coherent, professional treaty pre-review tool prototype.

A stranger should be able to understand:

- what problem the tool solves
- what narrow scope it supports
- why the output is more trustworthy than a generic AI chat demo
- where the system is intentionally conservative
- how the project could later evolve into a real-document-driven demo

## Must Keep

These are already core assets and should be preserved:

- China-Netherlands only
- dividends, interest, royalties only
- structured treaty-backed output
- unsupported and incomplete-case refusal behavior
- source anchors, source quality, and review-priority signals
- bounded pre-review positioning

## Must Do

### 1. Public Story

- rewrite the README opening so the product identity is obvious in the first screen
- make the README explain what the tool does, what it does not do, and why the scope is intentionally narrow
- add a short “Why not a chatbot?” section
- add a short “How trust is handled” section

### 2. Demo Quality

- ensure the demo examples reflect the strongest supported scenarios
- make supported, unsupported, and incomplete cases all look intentional
- verify the UI language matches the public product identity everywhere
- keep the interface simple and professional rather than feature-heavy

### 3. Trust Communication

- explain how treaty facts come from structured data
- explain how source anchors and confidence signals affect review guidance
- explain when the tool refuses or escalates to stronger manual review
- make sure the repo never implies final legal or tax advice

### 4. Repo Presentation

- add or refine screenshots that show one supported case and one guarded case
- ensure the architecture story is easy to follow
- make the file and doc structure feel intentional, not accidental
- keep public-facing terminology consistent across README, docs, and UI

### 5. Verification

- keep backend and frontend tests green
- keep at least one supported case, one unsupported case, and one confidence-sensitive case easy to demonstrate
- verify the README matches the actual current behavior

## Should Do

- add a small “How it works” diagram tuned for GitHub readers
- add a compact roadmap section showing `Phase A -> Phase B -> Phase C`
- tighten any UI wording that still sounds too generic or too internal

## Do Not Do Yet

- multi-country expansion
- customer onboarding or customer operations flows
- broad AI chat behavior
- full document search pipeline
- deployment and production hardening work beyond what helps the demo
- any claim that the tool is customer-ready

## Exit Criteria

Phase A is done when:

1. the README tells one clear story from top to bottom
2. the live demo feels deliberate in both success and refusal paths
3. trust boundaries are easy to understand
4. the repo looks like a polished professional prototype, not a pile of experiments
5. the next step into real-document work is obvious but not prematurely mixed into the Phase A core

## Suggested Order

1. align README structure and language
2. define screenshot/demo asset needs
3. polish user-facing wording in the current UI
4. verify supported, unsupported, and confidence-sensitive examples
5. only then decide whether another implementation task still helps Phase A directly
