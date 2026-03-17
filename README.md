# Tax Treaty Agent

面向跨境支付场景的税收协定适用性预审工具。支持中荷、中新协定下的股息、利息及特许权使用费场景，基于结构化协定数据，输出保守审慎、来源可追溯、可直接交接的预审结论。

---

A pre-screening tool for cross-border payment scenarios under bilateral tax treaties. Designed for tax and compliance teams who need structured, source-cited preliminary assessments before formal review.

## What It Does

Given a cross-border payment scenario, the tool:
- Guides the user through a type-specific fact collection wizard
- Runs a rule-based eligibility pre-screen against treaty source data
- Returns a conservative structured assessment with full treaty citation
- Packages results into a workflow-ready handoff output for downstream review

Outputs are deliberately conservative. The tool flags uncertainty rather than resolving it, and surfaces review signals (beneficial owner status, MLI/PPT exposure, holding period risk) rather than making final determinations.

## Current Coverage

| Treaty Pair | Income Types |
|---|---|
| China – Netherlands | Dividends, Interest, Royalties |
| China – Singapore | Dividends, Interest, Royalties |

Coverage is intentionally narrow. Each supported scenario has complete treaty source citation and tested narrowing logic. Unsupported scenarios return an explicit out-of-scope response rather than a best-effort guess.

## Architecture

- **Frontend**: React wizard-first guided input, per-income-type fact panels
- **Backend**: Python rule engine — normalize → scope lock → treaty lookup → risk tiering → JSON assembly
- **Data layer**: Source-anchored treaty JSON with article-level citation
- **Output contract**: Versioned JSON schema (`slice3.v1`), machine-readable handoff package, BO precheck signal, conflict detection

## Input Modes

- **Guided** (primary): Step-by-step fact collection with type-specific fields
- **Free-text** (legacy/demo): Unstructured scenario input, deprecated

## What It Does Not Do

- Make final treaty eligibility determinations
- Provide legal or tax advice
- Cover income types or treaty pairs outside the supported scope
- Handle domestic anti-avoidance rules independently of the treaty pre-screen

## Design Principles

- **Conservative by default**: unknown facts terminate rather than assume
- **Source-anchored**: every output references the specific treaty article
- **Workflow-ready**: outputs are structured for handoff, not just display
- **Scope-honest**: unsupported scenarios are explicitly rejected

## Running Locally

### Backend
```powershell
.\.venv\Scripts\python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --app-dir backend
```

### Frontend
```powershell
cd frontend
npm install
npm run dev -- --host 127.0.0.1 --port 4173
```
Then open:

`http://127.0.0.1:4173`

The Vite dev server proxies `/api` to the local FastAPI backend.
