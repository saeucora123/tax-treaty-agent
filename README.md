# Tax Treaty Agent

面向国际税团队的跨境税收协定预审工具。它先帮助团队快速完成第一轮筛查，整理关键事实、潜在协定路径与复核提示，但**不替代最终税务意见**。

An international tax treaty pre-screening tool for cross-border payment scenarios. It helps tax teams move faster through the first-pass review by organizing key facts, narrowing the treaty lane in scope, and returning a workflow-ready handoff, while **not replacing a final tax opinion**.

![Tax Treaty Agent product cover](assets/tax-treaty-agent-demo.png)

[Open product overview / 打开产品介绍页](https://saeucora123.github.io/tax-treaty-agent/)

当前支持范围：
- China – Netherlands
- China – Singapore
- China – Korea
- Dividends, Interest, Royalties

它帮助团队：
- 更快完成第一轮协定适用性筛查
- 在关键事实缺失时停止猜测、转入人工复核
- 把结果、风险点和后续动作整理给下一位复核者

## Quick Proof / 快速验证

### 中文

1. 启动后端：

   ```powershell
   .\.venv\Scripts\python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --app-dir backend
   ```

2. 启动前端：

   ```powershell
   cd frontend
   npm install
   npm run dev -- --host 127.0.0.1 --port 4173
   ```

3. 运行公开 smoke proof：

   ```powershell
   python scripts/run_public_smoke.py
   ```

4. 打开 `http://127.0.0.1:4173`，默认看到 guided workspace；按 GIF 中的路径填写一条 `CN -> NL dividends` 场景，可得到结构化结果、workflow handoff 和 review signals。

预期观察结果：
- smoke script 返回 `2/2 checks passed`
- guided dividend 示例返回 `Article 10`、`5%`、`standard_review`
- out-of-scope 示例返回 `unsupported_country_pair`

### English

1. Start the backend:

   ```powershell
   .\.venv\Scripts\python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --app-dir backend
   ```

2. Start the frontend:

   ```powershell
   cd frontend
   npm install
   npm run dev -- --host 127.0.0.1 --port 4173
   ```

3. Run the public smoke proof:

   ```powershell
   python scripts/run_public_smoke.py
   ```

4. Open `http://127.0.0.1:4173`. The app opens in the guided workspace by default; following the GIF flow with a `CN -> NL dividends` case returns a structured result, workflow handoff, and review signals.

Expected outcome:
- the smoke script returns `2/2 checks passed`
- the guided dividend example returns `Article 10`, `5%`, and `standard_review`
- the out-of-scope example returns `unsupported_country_pair`

## Current Coverage / 当前支持范围

| Treaty Pair | Income Types |
|---|---|
| China – Korea | Dividends, Interest, Royalties |
| China – Netherlands | Dividends, Interest, Royalties |
| China – Singapore | Dividends, Interest, Royalties |

当前支持范围是刻意收窄的。对外部访客来说，这个项目要证明的是“高风险税务问题可以被做成可信的 AI 工具”，而不是“随意扩国家和收入类型”。

Coverage is intentionally narrow. The point of the project is not broad treaty count; it is to show that a high-risk tax problem can be turned into a credible, bounded AI workflow.

## Why This Is Credible / 为什么可信

### 中文

- **Source-anchored treaty data**：税率、条款和 working-paper 引用都来自结构化协定数据，不依赖 runtime 模型记忆。
- **Conservative refusal**：关键事实缺失时终止，而不是猜测；超范围场景返回明确拒绝。
- **Wizard-first guided input**：主要路径是按收入类型收集事实，而不是自由聊天。
- **Workflow-ready handoff**：输出不仅给出初步结论，还提供 machine-readable handoff、BO precheck、conflict / review signals。

### English

- **Source-anchored treaty data**: treaty rates, article references, and working-paper links come from structured datasets rather than runtime model recall.
- **Conservative refusal**: the system terminates on missing critical facts and rejects unsupported scope explicitly instead of guessing.
- **Wizard-first guided input**: the primary path is a type-specific fact collection flow, not open-ended chat.
- **Workflow-ready handoff**: outputs include machine-readable handoff payloads, BO precheck, and review/conflict signals instead of a bare answer.

## Treaty Onboarding Compiler / 协定接入编译器

### 中文

- 新协定并不是靠程序员和税务专家手工逐条把 PDF 翻译成运行时规则。repo 现在已经包含一个 **human-reviewed offline LLM treaty-onboarding compiler**，用受控 source document 生成结构化规则草稿，再走 `compile -> review -> approve -> promote` 的正式流程。
- 这个编译器已经接入 **OECD baseline-aware delta extraction**：离线编译阶段会把双边协定与 OECD Model 2017 Articles 10/11/12 做差分分析，同时仍然产出完整 runtime dataset，而不是让线上引擎去吃 patch 链。
- 当前证据里有一条 **single controlled CN-KR pilot**。在受控官方来源输入下，repo 记录到了：
  - reviewer-only elapsed time：`26 seconds`
  - repo-internal end-to-end elapsed time（`source build -> promote`）：`10m45s`
- 这条 timing evidence 证明的是流程已经可测、可复核、可落地；**它不是普遍 SLA，也不代表所有新协定都能稳定在相同时间内完成接入**。本次 measured run 还包含一次 live provider retry gap，详细限定见 stage-6 evidence。

### English

- New treaty lanes are no longer onboarded only by manually translating treaty PDFs into runtime rules. The repo now includes a **human-reviewed offline LLM treaty-onboarding compiler** that turns governed source documents into structured rule candidates and routes them through a formal `compile -> review -> approve -> promote` workflow.
- The compiler is already **OECD baseline-aware**: bilateral Articles 10/11/12 are compared against the OECD Model 2017 reference during offline authoring, while the runtime still receives a complete full dataset rather than a patch chain.
- The current evidence pack includes a **single controlled CN-KR pilot** using governed official source inputs. The measured run recorded:
  - reviewer-only elapsed time: `26 seconds`
  - repo-internal end-to-end elapsed time (`source build -> promote`): `10m45s`
- This timing evidence shows that the onboarding workflow is measurable and reviewable. It is **not** a blanket SLA and should not be read as proof that every future treaty pair will onboard in the same time window. The measured run also included one live provider retry gap before the final successful compile; the caveat is documented in the stage-6 evidence pack.

## Known Limits / 当前边界

### 中文

- 这不是最终税务意见，也不替代律师、税务顾问或内部复核。
- `MLI/PPT` 当前只作为 **review signal** 暴露，不在 runtime 中自动作出实体性 override 判断。
- free-text 仍保留，但只是 legacy/demo 兼容路径；主路径是 guided input。
- 不支持当前范围之外的国家对、收入类型或开放式税务问答。

### English

- This is not a final tax opinion and does not replace legal, tax, or internal review.
- `MLI/PPT` is currently exposed as a **review signal only**; the runtime does not attempt a substantive treaty override determination.
- Free-text remains available as a legacy/demo compatibility lane; guided input is the primary path.
- Unsupported treaty pairs, income types, and open-ended tax questions are intentionally rejected.

## Running Locally / 本地运行

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

## Internal Docs Note / 内部文档说明

中文：仓库中保留了 `docs/superpowers` 目录，用于内部执行控制、证据包、研究记录和 gate review 产物。这些材料有助于审计和开发过程，但**不是**运行或评估公开 demo 的前置条件。

English: The repo keeps `docs/superpowers` as an internal execution, evidence, research, and gate-review archive. Those materials support auditability and project discipline, but they are **not required** to run or evaluate the public demo.
