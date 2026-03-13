# Tax Treaty Agent Implementation Plan

Date: 2026-03-11
Based on: `docs/superpowers/specs/2026-03-11-tax-treaty-agent-design.md`

## 1. Implementation Goal

Turn the approved design into a fast-moving but credible MVP that is:

- demoable
- GitHub-friendly
- easy to explain
- structurally ready for later treaty-data upgrades

## 2. Recommended Stack

### Frontend

- React
- Vite
- TypeScript

Reason:

- fast to scaffold
- clean for a small demo shell
- easy to polish visually
- good balance between simplicity and professionalism

### Backend

- Python
- FastAPI

Reason:

- strong fit for future data-processing and retrieval work
- easy local API development
- readable project shape
- a better upgrade path for later treaty parsing or RAG experiments

### Data

- JSON files for v1 seed data

Reason:

- transparent
- easy to review manually
- easy to evolve into richer structured data later

### Optional Later Additions

- SQLite for richer local storage
- PDF extraction pipeline
- vector retrieval or hybrid retrieval
- deployment targets for public demo

## 3. Phase Plan

### Phase 0: Repo Foundation

Outcome:

- repo has durable context
- implementation path is documented

Tasks:

- create repo bootstrap files
- create git repository when ready
- add a clean `.gitignore`

### Phase 1: Shape the Contracts Before Coding

Outcome:

- future code is anchored to stable boundaries

Tasks:

- define input contract
- define output contract
- define seed treaty data schema
- define unsupported-case behavior

Deliverables:

- API request/response examples
- sample JSON treaty entries
- supported vs unsupported example list

### Phase 2: Seed Data Layer

Outcome:

- v1 has trusted structured facts for supported scenarios

Tasks:

- create structured entries for China-Netherlands
- cover dividends, interest, royalties
- include article number, rate, conditions, notes, review guidance

Important:

- prefer a small curated dataset over large messy source ingestion

### Phase 3: Backend MVP

Outcome:

- API can accept a scenario and return a structured result

Core modules:

- scenario parser
- scope checker
- treaty matcher
- response builder
- refusal/review handler

Suggested endpoints:

- `POST /analyze`
- `GET /health`
- `GET /examples`

Phase target:

- one supported case works end-to-end
- one unsupported case fails safely

### Phase 4: Frontend MVP

Outcome:

- users can try the product in one screen

Page elements:

- short project description
- one scenario input
- analyze button
- structured result panel
- unsupported-case message area
- example prompts

Do not add:

- chat history
- accounts
- multi-page flows
- unnecessary dashboard complexity

### Phase 5: Testing and Trust Pass

Outcome:

- the demo feels stable and bounded

Tests to run:

- supported royalties example
- supported interest example
- supported dividends example
- unsupported country pair
- unsupported tax type
- ambiguous prompt

Review questions:

- did the model invent anything?
- does the output clearly expose uncertainty?
- does the project stay inside its own stated boundary?

### Phase 6: GitHub Presentation Pass

Outcome:

- the repo looks star-worthy and resume-worthy

Tasks:

- write a strong README
- add screenshots or GIFs
- add architecture diagram
- add example scenarios
- explain the A-to-B roadmap clearly

README should answer:

- what problem does this solve?
- why this narrow scope?
- how does it work?
- how do I run it?
- what does the demo look like?
- how will it evolve later?

### Phase 7: B-Version Upgrade Path

Outcome:

- clear route to a more realistic treaty-driven system

Likely upgrades:

- richer treaty coverage
- more fields and rules
- fuller article mapping
- source-document processing
- improved retrieval pipeline

Important:

- keep frontend contract and API shape as stable as possible
- evolve the data layer and retrieval logic underneath

## 4. Data Schema Draft

Recommended v1 treaty entry shape:

```json
{
  "treaty_id": "cn-nl",
  "country_pair": ["CN", "NL"],
  "transaction_type": "royalties",
  "article_number": "12",
  "article_title": "Royalties",
  "rate": "10%",
  "conditions": [
    "recipient must qualify under supported interpretation",
    "reduced rate depends on treaty applicability"
  ],
  "notes": [
    "beneficial ownership may matter",
    "case-specific facts can change the result"
  ],
  "human_review_required": true,
  "review_reason": "final eligibility depends on facts beyond v1 scope"
}
```

This schema is intentionally simple but expandable.

## 5. API Contract Draft

### Request

```json
{
  "scenario": "中国居民企业向荷兰支付特许权使用费"
}
```

### Success Response

```json
{
  "supported": true,
  "normalized_input": {
    "payer_country": "CN",
    "payee_country": "NL",
    "transaction_type": "royalties"
  },
  "result": {
    "treaty_id": "cn-nl",
    "article_number": "12",
    "rate": "10%",
    "conditions": [
      "..."
    ],
    "notes": [
      "..."
    ],
    "human_review_required": true,
    "review_reason": "..."
  }
}
```

### Unsupported Response

```json
{
  "supported": false,
  "reason": "unsupported_country_pair",
  "message": "Current MVP supports only China-Netherlands treaty scenarios."
}
```

## 6. Human-AI Workflow During Implementation

### Human

- approve scope
- validate business truthfulness
- reject over-claiming
- decide what is publishable

### AI-Assisted Delivery

- scaffold files
- draft modules
- generate UI shell
- create docs
- propose refactors
- help write tests and examples

### Review Loop

For each meaningful feature:

1. AI-assisted draft prepares structure
2. human reviews scope and truthfulness
3. implementation pass revises
4. run the smallest real verification path

## 7. What To Build First

Recommended first implementation order:

1. initialize git repo
2. add `.gitignore`
3. scaffold `backend/` FastAPI app
4. define seed treaty JSON in `data/`
5. implement `POST /analyze`
6. verify supported and unsupported cases
7. scaffold `frontend/`
8. connect frontend to backend
9. polish README and example assets

## 8. Success Criteria

This plan succeeds when the repo reaches a first public-quality MVP with:

- one-screen usable demo
- stable API
- clear treaty-backed outputs
- safe unsupported-case behavior
- a README that makes the project understandable and attractive

## 9. Immediate Next Move

The next execution step should be:

- scaffold the repository foundation and technical stack

That means:

- initialize git
- create `.gitignore`
- create frontend and backend folders
- create the first FastAPI app and React app shell
- add the first seed treaty data file
