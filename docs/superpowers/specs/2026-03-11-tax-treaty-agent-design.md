# Tax Treaty Agent Design

Date: 2026-03-11
Status: Approved for planning

## 1. Project Goal

Build a public-facing, resume-strong GitHub project that demonstrates the ability to translate international tax business logic into a practical AI system.

The first version should feel like a real tool instead of a generic chatbot:

- useful
- explainable
- bounded
- demo-friendly
- easy to evolve later

## 2. Positioning

Primary positioning:

- a cross-disciplinary builder who can translate international tax problems into AI systems

This project should not mainly signal "pure engineer" or "business-only student." It should signal:

- understands international tax context
- can use AI and modern coding workflows effectively
- can structure a problem into a real product

## 3. Public Release Strategy

Recommended release style: semi-public open source.

Public:

- source code
- README
- architecture notes
- sample data
- screenshots or demo assets

Not required in v1:

- all raw source materials
- sensitive config
- fully productionized pipelines

Reason:

- strong enough for resume and GitHub visibility
- lower maintenance burden
- easier to iterate safely

## 4. Experience Shape

Recommended first experience:

- API + simple web shell

Why:

- the web layer improves demo value and first impression
- the API layer improves technical credibility
- this shape supports future expansion better than a CLI-only demo

## 5. Core Product Concept

Working concept:

- user enters a cross-border transaction scenario
- system identifies the relevant treaty context
- system returns structured treaty analysis

Example input:

`中国居民企业向荷兰支付特许权使用费`

Example output shape:

- applicable treaty
- likely article
- tax rate
- conditions for application
- caution notes
- whether human review is recommended

## 6. MVP Scope

The first release must stay narrow.

Countries:

- China-Netherlands only

Transaction types:

- dividends
- interest
- royalties

Interaction:

- single-turn input only

Out of scope for v1:

- multi-country support
- multi-turn tax dialogue
- permanent establishment analysis
- complex factual judgment
- open-ended legal reasoning beyond supported treaty entries

## 7. Product Principles

The project should behave like a bounded professional tool.

Principles:

- do not let the model invent tax rates
- answers must be anchored to structured treaty data
- uncertain or unsupported cases should fail conservatively
- output must be structured, not free-form rambling
- the system should reveal boundaries clearly

## 8. System Architecture

Recommended architecture:

1. Frontend
2. Backend API
3. Treaty data layer
4. Response generation layer
5. Risk control layer

### 8.1 Frontend

Purpose:

- give a clean first-touch demo
- let users test a scenario immediately

Needs:

- one input box
- submit action
- structured result display
- explicit unsupported-case messaging

### 8.2 Backend API

Purpose:

- receive input
- parse the scenario
- lock scope
- fetch structured treaty facts
- assemble final response

The backend is the main credibility layer of the project.

### 8.3 Data Layer

Purpose:

- hold structured treaty content
- separate facts from model-generated language

Important:

- v1 should use a small, manually curated, high-quality dataset
- the data schema should be designed as if the system will later scale to fuller treaty coverage

### 8.4 Response Layer

Purpose:

- transform structured facts into readable analysis

Model role:

- understand the user input
- help organize explanation
- improve readability

Model must not:

- fabricate unsupported legal conclusions
- decide rates from memory

### 8.5 Risk Control Layer

Purpose:

- detect unsupported scenarios
- trigger conservative fallback behavior

Fallback examples:

- unsupported country pair
- unsupported income type
- missing facts in the prompt
- cases requiring deeper legal judgment

## 9. Internal Flow

Recommended flow:

1. Input parsing
2. Scope locking
3. Treaty fact retrieval
4. Structured answer generation
5. Risk check and review guidance

### 9.1 Input Parsing

Use AI where helpful to identify:

- payer country
- payee country
- transaction type
- notable keywords

### 9.2 Scope Locking

Use rules and data, not free-form model reasoning, to:

- lock to China-Netherlands
- map to supported article candidates

### 9.3 Treaty Fact Retrieval

Retrieve from structured treaty entries:

- article number
- rate
- conditions
- notes

### 9.4 Structured Answer Generation

Use AI to turn retrieved facts into a readable answer with a fixed shape.

### 9.5 Risk Handling

If confidence or support is insufficient:

- say the current version cannot reliably determine the answer
- recommend human review

## 10. Human-AI Collaboration Model

This project should use AI aggressively for speed, while preserving human control where judgment matters.

### 10.1 Human Responsibilities

- define the product goal
- define scope boundaries
- decide trust standards
- review whether outputs are actually sound
- explain the project story publicly

### 10.2 AI Responsibilities

- scaffold frontend and backend code
- generate implementation drafts
- draft documentation
- accelerate refactors
- help produce examples and testing cases

### 10.3 Collaboration Philosophy

The user is not expected to act as a traditional line-by-line programmer.

The intended role is:

- problem definer
- AI orchestrator
- final reviewer

Learning should come from:

- system thinking
- task decomposition
- AI instruction and review skill
- product communication

## 11. A-to-B Evolution Strategy

Recommended path:

- A version: small-data, real-architecture MVP
- B version: real-treaty-driven system

### 11.1 A Version

Use a manually curated subset of treaty data for:

- dividends
- interest
- royalties

This version must still include:

- real API boundaries
- real data schema
- real structured output
- real fallback behavior

Avoid fake MVP patterns such as:

- hardcoded one-off answers
- UI-only demos with no system boundary
- tangled code that cannot evolve

### 11.2 B Version

Later upgrades may replace or extend:

- fuller treaty data coverage
- richer article metadata
- stronger retrieval logic
- PDF extraction or RAG pipeline

The goal is that frontend and API contracts survive mostly unchanged, while data and retrieval mature underneath them.

## 12. Recommended Repository Shape

Suggested repo layout:

```text
README.md
frontend/
backend/
data/
docs/
examples/
```

### 12.1 README.md

Must communicate:

- what problem the project solves
- why it matters
- what the MVP supports
- how to run it
- screenshots or demo visuals
- example input/output

### 12.2 frontend/

Holds the lightweight demo interface.

### 12.3 backend/

Holds API and core orchestration logic.

### 12.4 data/

Holds structured treaty entries and sample datasets, not a messy pile of raw files.

### 12.5 docs/

Holds:

- architecture notes
- data schema notes
- boundary and trust notes

### 12.6 examples/

Holds carefully selected example scenarios, including at least one unsupported case.

## 13. Quality Bar for v1

The first version is successful if:

- a stranger can understand the project quickly
- the demo runs locally
- supported cases produce stable structured outputs
- unsupported cases fail safely
- the repository feels intentional and professional
- the user can explain how and why the system works

## 14. What This Project Should Signal

If executed well, the repository should signal:

- international tax awareness
- practical AI workflow capability
- product judgment
- systems thinking
- the ability to use vibe coding responsibly rather than blindly

## 15. Next Planning Step

The next phase should turn this design into an implementation plan covering:

- technical stack choice
- data schema definition
- API contract
- frontend page scope
- example scenarios
- GitHub presentation assets
