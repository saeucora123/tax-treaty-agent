# Tax Treaty Agent

An international tax AI tool that turns a bounded treaty-analysis problem into a practical system.

![Tax Treaty Agent demo](D:/AI_Projects/first%20agent/docs/superpowers/assets/tax-treaty-agent-demo.png)

## What This MVP Does

The current MVP is intentionally narrow:

- China-Netherlands only
- dividends, interest, royalties only
- single-turn scenario input
- structured output
- conservative fallback for unsupported cases

Example input:

`中国居民企业向荷兰支付特许权使用费`

Example output:

- treaty article
- rate
- conditions
- caution notes
- human review guidance

## Why This Project Exists

This project is designed to show how international tax business logic can be translated into a usable AI tool, instead of a generic chatbot.

The product goal is simple:

- act like a bounded professional tool
- make the business logic visible
- avoid free-form hallucinated tax answers

## Current Repo Status

Already working:

- project design spec
- implementation plan
- backend MVP skeleton
- seed treaty data
- tested supported and unsupported backend paths
- frontend demo shell connected to the backend

Planned next:

- richer supported examples
- stronger README presentation
- more treaty coverage
- more realistic retrieval/data pipelines

## Local Run

### Backend

From the repo root:

```powershell
.\.venv\Scripts\python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --app-dir backend
```

### Frontend

In a second terminal:

```powershell
cd frontend
npm install
npm run dev -- --host 127.0.0.1 --port 4173
```

Then open:

`http://127.0.0.1:4173`

The Vite dev server proxies `/api` requests to the local FastAPI backend.

## Verification

Backend tests:

```powershell
.\.venv\Scripts\python -m pytest backend/tests/test_analyze.py
```

Frontend tests:

```powershell
cd frontend
npm test
```

Frontend build:

```powershell
cd frontend
npm run build
```

## Key Docs

- `docs/superpowers/specs/2026-03-11-tax-treaty-agent-design.md`
- `docs/superpowers/plans/2026-03-11-tax-treaty-agent-implementation-plan.md`
- `.codex/project-memory.md`
- `.codex/project-status.md`
