const STORAGE_KEY = "tta-site-language";

const translations = {
  zh: {
    pageTitle: "Tax Treaty Agent | 跨境税收协定预审工具",
    pageDescription:
      "面向国际税务团队的跨境税收协定预审工具，帮助团队更快完成第一轮筛查，再进入正式法律或税务分析。",
    navWorkflow: "工作方式",
    navWalkthrough: "案例演示",
    navOnboarding: "协定接入",
    navEvidence: "证据层",
    navCoverage: "当前支持",
    navLimits: "使用边界",
    navRepo: "查看代码仓库",
    heroEyebrow: "面向国际税务团队",
    heroTitle: "面向国际税预审的可信 AI 工作流",
    heroLead:
      "先更快完成第一轮筛查，再进入正式法律或税务分析。这个工具会引导关键事实、收束到当前支持的协定路径，并输出一个可直接交接给下一位审核人的结构化结果。",
    heroSub:
      "它的目标是节省流程前段的时间，不是取代最终税务意见或法律判断。",
    heroPrimary: "打开 GitHub 仓库",
    heroSecondary: "看 90 秒案例演示",
    chipPairs: "3 个协定对",
    chipIncome: "股息、利息、特许权使用费",
    chipGuided: "引导式预审优先",
    chipHandoff: "人工复核交接包",
    cardGuided: "引导式事实采集",
    cardReview: "结构化预审输出",
    cardHandoff: "工作流交接摘要",
    valueKicker1: "先节省时间",
    valueTitle1: "更快完成第一轮筛查",
    valueBody1:
      "团队不必再从空白文档开始。工具会先收集关键协定事实、收束预审路径，并整理成后续复核可以直接接手的结构化材料。",
    valueKicker2: "保持保守",
    valueTitle2: "关键事实不明时停止，而不是猜测",
    valueBody2:
      "遇到不支持或事实不足的场景，系统会明确提示，而不是给出看似完整但风险过高的结论。",
    valueKicker3: "让链路可见",
    valueTitle3: "把预审过程带着证据交给下一位审核人",
    valueBody3:
      "输出会保留协定路径、复核信号和可交接备注，帮助后续审核人接续工作，而不是重新还原第一轮筛查。",
    workflowEyebrow: "工作方式",
    workflowTitle: "三步完成，贴近国际税团队的真实流程",
    workflowIntro:
      "这不是一个开放式聊天机器人，而是一个边界清晰的预审流程，帮助第一位审核人更快整理事实，并把案件交给下一步复核。",
    workflowStep1Title: "先收集真正影响协定路径的事实",
    workflowStep1Body:
      "引导式流程只问决定路径所需的事实，例如支付类型、协定对、受益所有人状态，以及股息场景下的持股门槛等。",
    workflowStep2Title: "再收束到当前支持的协定路径",
    workflowStep2Body:
      "系统使用结构化协定数据和保守规则逻辑，判断案件是留在支持范围内、需要补充事实，还是应当直接标记为不支持。",
    workflowStep3Title: "最后交付一个可继续讨论的预审包",
    workflowStep3Body:
      "结果不仅给出当前预审状态，还会带出下一步动作、来源线索和交接说明，方便后续人工复核继续推进。",
    showcaseEyebrow: "团队最终拿到什么",
    showcaseTitle: "不是一段聊天回复，而是可以内部讨论的预审输出",
    feature1Title: "引导式事实摘要",
    feature1Body: "让后续审核人先看到已声明的事实，再决定是否采纳当前收束路径。",
    feature2Title: "结构化预审状态",
    feature2Body: "帮助团队快速区分：已支持、待补全、部分完成，还是超出范围。",
    feature3Title: "工作流交接包",
    feature3Body: "让下游审核人无需从头重新理解第一轮预审过程。",
    feature4Title: "复核信号",
    feature4Body: "让 BO、MLI/PPT、短持有期和冲突提示保持可见，但不假装替代最终判断。",
    walkthroughEyebrow: "90 秒案例演示",
    walkthroughTitle: "用一条真实的中荷股息案例，把输入到边界一次讲清楚",
    walkthroughIntro:
      "这一段不试图解释整个系统，只展示一条真实产品路径：输入、引导式事实、协定分支、来源依据、handoff artifact，以及产品最终停下来的边界。",
    walkthroughStep1Title: "输入",
    walkthroughStep1Body:
      "从一条边界明确的场景开始：一笔 `CN -> NL` 的 dividend payment，属于当前公开支持范围内的真实预审路径。",
    walkthroughCasePill: "CN -> NL dividends",
    walkthroughStep2Title: "引导式事实",
    walkthroughStep2Body:
      "系统不会靠自由聊天猜答案，而是要求真正影响分支判断的事实：直接持股比例、付款日、持有期等。",
    walkthroughStep3Title: "协定分支",
    walkthroughStep3Body:
      "引擎把案件收束到 Article 10 dividend branch，并把 5% / 10% 这种分支逻辑保持为显式规则，而不是藏在模型回答里。",
    walkthroughStep4Title: "来源依据",
    walkthroughStep4Body:
      "输出不会只给一个税率。审核人还能看到条款路径、段落级来源和当前 review context，而不是一个没有出处的数字。",
    walkthroughStep5Title: "交接材料",
    walkthroughStep5Body:
      "结果会被打包成交接材料，让下一位审核人直接接续 workflow，而不是从头重建第一轮筛查。",
    walkthroughStep6Title: "最终边界",
    walkthroughStep6Body:
      "产品在该停的地方会停下来：不是最终税务意见，`MLI/PPT` 仍然只是 review signal，不会在 runtime 里被假装自动解决。",
    evidenceCard1Label: "单次实测",
    onboardingEyebrow: "新协定如何接入",
    onboardingTitle: "不再从零手工写规则，而是走人工把关的协定编译流程",
    onboardingIntro:
      "新协定路径现在通过受控 source document 离线编译进入系统。编译器会把双边协定的第 10、11、12 条与 OECD 基准做差分分析，生成结构化候选结果，只有在人工 review 和 approval 之后才会 promote 到 runtime。",
    onboardingStep1Title: "先做 baseline-aware delta extraction",
    onboardingStep1Body:
      "离线 authoring 流水线会把双边协定与 OECD Model 2017 Articles 10/11/12 做对照，输出 delta artifacts，同时仍然生成完整的 runtime candidate dataset，而不是让线上引擎去处理 patch 链。",
    onboardingStep2Title: "人工复核仍然是硬门槛",
    onboardingStep2Body:
      "编译结果不会自动上线。review、approval、promote 仍是明确的工作流步骤，确保最终税务判断继续由人类控制，而不是交给模型自动决定。",
    onboardingStep3Title: "单次受控 CN-KR pilot 已留下实测耗时证据",
    onboardingStep3Body:
      "第一次真实 onboarding pilot 在受控官方来源输入下记录到了 `26 seconds` 的 reviewer session 和 `10m45s` 的 repo 内部 `source build -> promote` 总耗时。这是单次实测证据，不是对所有新协定的通用 SLA 承诺。",
    evidenceEyebrow: "对外证据层",
    evidenceTitle: "把公共证明单独摆出来，而不是让故事替代证据",
    evidenceIntro:
      "这里对外强调的是已经被 repo 证明的内容：单次实测摘要、协定接入证明矩阵，以及回归/重放快照。目标是清楚说明当前已经实现了什么，同时避免把 repo 还没证明的能力提前写成事实。",
    evidenceMetricReviewer: "Reviewer elapsed",
    evidenceMetricReviewerValue: "26 seconds",
    evidenceMetricEndToEnd: "End-to-end elapsed",
    evidenceMetricEndToEndValue: "10m45s",
    evidenceMetricPilotType: "Pilot type",
    evidenceMetricPilotTypeValue: "Single controlled pilot",
    evidenceCard1Title: "单次实测摘要",
    evidenceCard1Body:
      "这组数字来自受控官方来源输入下的真实流程。它证明的是 workflow 已经可测、可审计，而不是在承诺一条通用 onboarding SLA。",
    evidenceCard2Label: "证明矩阵",
    evidenceCard2Title: "接入证明矩阵",
    evidenceProof1: "CN-SG shadow rebuild",
    evidenceProof2: "CN-NL shadow rebuild",
    evidenceProof3: "CN-SG OECD delta proof",
    evidenceProof4: "CN-NL OECD delta proof",
    evidenceProof5: "CN-KR initial onboarding",
    evidenceCard2Body:
      "编译器路径已经跨过多个 lane：双 pair shadow rebuild、双 OECD delta proof，以及一个真实的新 pair initial onboarding。",
    evidenceCard3Label: "回归快照",
    evidenceCard3Title: "回归与重放快照",
    evidenceSnapshotBackend: "backend passed",
    evidenceSnapshotFrontend: "frontend passed",
    evidenceSnapshotSite: "site tests passed",
    evidenceSnapshotBuildValue: "Build",
    evidenceSnapshotBuild: "frontend build passed",
    evidenceCard3Body:
      "公开 runtime、onboarding workflow 和产品页本身都受回归测试保护，所以外部叙事不是只靠截图，而是能回到实际测试结果上。",
    verifierEyebrow: "3 分钟快速验证",
    verifierTitle: "3 分钟快速验证这个 repo",
    verifierIntro:
      "如果你只有几分钟，不要先从完整本地启动开始。先按下面这条最短路径验证 moat 是否真实存在。",
    verifierStep1Title: "先看 90 秒案例演示",
    verifierStep1Body: "用一条真实的 `CN-NL dividends` 案例快速判断产品是不是只会讲概念。",
    verifierStep2Title: "再看 measured pilot card",
    verifierStep2Body: "确认 `CN-KR` onboarding 已经留下 machine-written timing evidence，而不是口头声称。",
    verifierStep3Title: "再扫 proof matrix",
    verifierStep3Body: "确认 moat 不是单点成立，而是 shadow rebuild、delta proof 和 real onboarding 都有证据。",
    verifierStep4Title: "最后才看本地 quick proof",
    verifierStep4Body: "如果你还想本地验证 runtime，再回 README 跑 smoke path；那是最后一步，不是第一步。",
    verifierPrimary: "打开 README 验证路径",
    verifierSecondary: "回到证据层",
    claimsEyebrow: "已实现与未宣称",
    claimsTitle: "把已经做成的讲清楚，也把还没宣称的边界讲清楚",
    claimsIntro:
      "这个产品的可信度来自两件事：真正做成的能力，以及明确承认还没有自动解决的问题。",
    claimsLeftTitle: "当前已实现",
    claimsLeftBody:
      "基于来源的协定预审、引导式事实采集、可交接的 workflow handoff、人工复核的协定接入编译器、OECD baseline-aware delta extraction，以及一次带 timing evidence 的 `CN-KR` 实测 onboarding。",
    claimsRightTitle: "当前不宣称",
    claimsRightBody:
      "不宣称最终税务意见、不宣称自动解决 `MLI/PPT`、不宣称通用 onboarding SLA，也不宣称所有未来协定都能在同样时间窗口内完成接入。",
    coverageEyebrow: "当前支持范围",
    coverageTitle: "故意保持收敛，因为可信度比广度更重要",
    coverageIntro:
      "产品只覆盖一个边界明确的协定范围和收入类型集合，以保证预审路径可追溯、可审计，也足够保守。",
    coveragePair1Title: "中国 - 荷兰",
    coveragePair2Title: "中国 - 新加坡",
    coveragePair3Title: "中国 - 韩国",
    coveragePairIncome: "股息、利息、特许权使用费",
    limitsEyebrow: "使用边界",
    limitsTitle: "这个工具不替代最终税务意见",
    limitsIntro:
      "它帮助团队更快完成前段预审，但不会自动作出最终法律判断或税务结论。",
    limit1Title: "不是最终裁决",
    limit1Body: "输出属于第一轮预审，不替代法律意见、税务意见或内部正式审批。",
    limit2Title: "MLI/PPT 仍是复核信号",
    limit2Body: "系统会把这些问题明确抬出来交给人工复核，而不是假装已经自动解决。",
    limit3Title: "超出范围就直接拒绝",
    limit3Body: "当案件超出当前支持的协定对或路径时，系统会直接说明，而不是给出勉强的推断。",
    footerEyebrow: "下一步",
    footerTitle: "GitHub 负责保存实现和证据链，产品页负责把产品讲清楚",
    footerBody:
      "代码仓库继续承担实现细节和证据材料，这个页面则用于先帮助非技术背景的国际税专家理解产品到底是干什么的。",
    footerPrimary: "打开仓库",
    footerSecondary: "阅读 README",
    altGuidedFacts: "Tax Treaty Agent 的引导式事实采集界面",
    altReviewOutput: "Tax Treaty Agent 的结构化预审输出界面",
    altWorkflowHandoff: "Tax Treaty Agent 的工作流交接摘要界面",
    altProductOverview: "Tax Treaty Agent 产品概览视觉图",
    altWalkthroughInput: "中荷股息案例输入概览",
    altWalkthroughGuided: "股息场景的引导式事实采集面板",
    altWalkthroughBranch: "Article 10 股息分支收束界面",
    altWalkthroughProvenance: "带来源依据的协定预审输出界面",
    altWalkthroughHandoff: "股息预审的 workflow handoff 材料",
    altWalkthroughBoundary: "最终边界与 review-only signal 展示",
  },
  en: {
    pageTitle: "Tax Treaty Agent | Cross-border treaty pre-screening",
    pageDescription:
      "Cross-border treaty pre-screening for international tax teams. Start with a faster first-pass review before full legal or tax analysis.",
    navWorkflow: "How it works",
    navWalkthrough: "Case walkthrough",
    navOnboarding: "New treaty onboarding",
    navEvidence: "Evidence",
    navCoverage: "Coverage",
    navLimits: "Boundaries",
    navRepo: "View repository",
    heroEyebrow: "For international tax teams",
    heroTitle: "Trusted AI workflow for international tax pre-review",
    heroLead:
      "Start with a faster first-pass review before full legal or tax analysis. The tool guides key facts, narrows to the treaty lane in scope, and returns a structured handoff for the next reviewer.",
    heroSub:
      "It is designed to save time at the front of the workflow, not to replace a final tax opinion.",
    heroPrimary: "Open GitHub repository",
    heroSecondary: "See the 90-second walkthrough",
    chipPairs: "3 treaty pairs",
    chipIncome: "Dividends, interest, royalties",
    chipGuided: "Guided review first",
    chipHandoff: "Human-reviewed handoff",
    cardGuided: "Guided facts",
    cardReview: "Structured review output",
    cardHandoff: "Workflow handoff",
    valueKicker1: "Save analyst time",
    valueTitle1: "Move faster through the first-pass review",
    valueBody1:
      "Instead of starting every case from a blank document, the tool gathers the key treaty facts, narrows the review lane, and returns a structured package for follow-up work.",
    valueKicker2: "Stay conservative",
    valueTitle2: "Terminate on missing critical facts instead of guessing",
    valueBody2:
      "Unsupported or ambiguous cases are surfaced explicitly. The workflow is designed to help teams avoid accidental overreach in high-stakes tax scenarios.",
    valueKicker3: "Keep the chain visible",
    valueTitle3: "Carry the review forward with traceable handoff detail",
    valueBody3:
      "Results are packaged with treaty lane references, review signals, and workflow-ready notes so the next reviewer does not have to reconstruct the first pass from scratch.",
    workflowEyebrow: "How it works",
    workflowTitle: "Three steps, built for the way tax teams already work",
    workflowIntro:
      "The product is not an open-ended chatbot. It is a bounded pre-screening workflow that helps the first reviewer organize facts quickly and hand the case forward cleanly.",
    workflowStep1Title: "Collect the facts that actually matter",
    workflowStep1Body:
      "The guided path asks for the facts needed to place the payment in the right treaty branch, such as payment type, treaty pair, ownership status, and dividend-specific thresholds where relevant.",
    workflowStep2Title: "Narrow to the treaty lane in scope",
    workflowStep2Body:
      "The engine uses structured treaty data and conservative rule logic to determine whether the case stays in scope, needs more facts, or should be rejected as unsupported.",
    workflowStep3Title: "Return a review package, not just an answer",
    workflowStep3Body:
      "Outputs include the pre-review state, next actions, source-aware references, and handoff notes for the human reviewer who takes the case further.",
    showcaseEyebrow: "What the team receives",
    showcaseTitle: "A pre-screening output that is ready to discuss internally",
    feature1Title: "Guided fact summary",
    feature1Body: "So reviewers can see what was declared before they rely on the narrowed branch.",
    feature2Title: "Structured review state",
    feature2Body: "So the team can distinguish supported, incomplete, and out-of-scope scenarios quickly.",
    feature3Title: "Workflow handoff package",
    feature3Body: "So downstream reviewers do not need to re-interpret the first pass from scratch.",
    feature4Title: "Review signals",
    feature4Body:
      "So BO, MLI/PPT, short holding period, and conflict prompts remain visible without pretending to be final determinations.",
    walkthroughEyebrow: "90-second case walkthrough",
    walkthroughTitle: "One real CN-NL dividends case, shown from input to final boundary",
    walkthroughIntro:
      "This walkthrough does not try to explain the whole system. It shows one concrete path through the current product: the initial case, the guided facts, the treaty branch, the source-aware record, the handoff artifact, and the final boundary the product keeps.",
    walkthroughStep1Title: "Input",
    walkthroughStep1Body:
      "Start with one bounded scenario: a China-to-Netherlands dividend payment that belongs in the current supported review scope.",
    walkthroughCasePill: "CN -> NL dividends",
    walkthroughStep2Title: "Guided facts",
    walkthroughStep2Body:
      "The product asks for the facts that actually matter here: direct holding percentage, payment date, and holding period, instead of relying on free-form chat.",
    walkthroughStep3Title: "Treaty branch",
    walkthroughStep3Body:
      "The engine narrows the case into the Article 10 dividend branch and keeps the direct-holding threshold logic explicit rather than hiding the branch choice inside a model answer.",
    walkthroughStep4Title: "Provenance",
    walkthroughStep4Body:
      "The result stays source-aware: the reviewer can see the treaty article lane, paragraph-level provenance, and the supporting review context instead of a bare percentage with no traceability.",
    walkthroughStep5Title: "Handoff artifact",
    walkthroughStep5Body:
      "The output is packaged for the next reviewer, with machine-readable handoff detail instead of leaving downstream review to reconstruct the first pass from scratch.",
    walkthroughStep6Title: "Final boundary",
    walkthroughStep6Body:
      "The product still stops at the right boundary: not a final tax opinion, and MLI/PPT remains a review signal rather than an automatic runtime override.",
    evidenceCard1Label: "Measured pilot",
    onboardingEyebrow: "How new treaties are onboarded",
    onboardingTitle: "A human-reviewed compiler replaces manual treaty-to-rule coding from scratch",
    onboardingIntro:
      "New treaty lanes are compiled offline from governed source documents. The compiler compares bilateral Articles 10 to 12 against the OECD reference, writes structured candidates, and only promotes a reviewed dataset into runtime after explicit approval.",
    onboardingStep1Title: "Baseline-aware delta extraction",
    onboardingStep1Body:
      "The authoring pipeline compares the bilateral treaty against the OECD Model 2017 reference for Articles 10, 11, and 12, then emits delta artifacts together with a full runtime candidate dataset.",
    onboardingStep2Title: "Human review remains the gate",
    onboardingStep2Body:
      "Compile output does not go live automatically. Review, approval, and promotion remain explicit workflow steps so tax-domain judgment stays human-controlled.",
    onboardingStep3Title: "Single controlled CN-KR pilot has measured timing evidence",
    onboardingStep3Body:
      "The first real onboarding pilot recorded a 26-second reviewer session and a 10m45s repo-internal source-build-to-promote elapsed time on governed official inputs. This is measured pilot evidence, not a guaranteed onboarding SLA.",
    evidenceEyebrow: "Public evidence layer",
    evidenceTitle: "Public proof is separated from product claims",
    evidenceIntro:
      "The public story is backed by concrete evidence artifacts: a measured pilot summary, a treaty onboarding proof matrix, and a regression snapshot. The goal is to show what is already implemented without claiming more than the repo has actually proven.",
    evidenceMetricReviewer: "Reviewer elapsed",
    evidenceMetricReviewerValue: "26 seconds",
    evidenceMetricEndToEnd: "End-to-end elapsed",
    evidenceMetricEndToEndValue: "10m45s",
    evidenceMetricPilotType: "Pilot type",
    evidenceMetricPilotTypeValue: "Single controlled pilot",
    evidenceCard1Label: "Measured pilot",
    evidenceCard1Title: "Measured pilot summary",
    evidenceCard1Body:
      "Measured on governed official source inputs. The result is evidence of a real workflow, not a general onboarding SLA.",
    evidenceCard2Label: "Proof matrix",
    evidenceCard2Title: "Onboarding proof matrix",
    evidenceProof1: "CN-SG shadow rebuild",
    evidenceProof2: "CN-NL shadow rebuild",
    evidenceProof3: "CN-SG OECD delta proof",
    evidenceProof4: "CN-NL OECD delta proof",
    evidenceProof5: "CN-KR initial onboarding",
    evidenceCard2Body:
      "The offline treaty compiler is not proven on one toy case only; it now holds across shadow rebuilds, baseline-aware delta proofs, and one real new-pair onboarding path.",
    evidenceCard3Label: "Regression snapshot",
    evidenceCard3Title: "Regression and replay snapshot",
    evidenceSnapshotBackend: "backend passed",
    evidenceSnapshotFrontend: "frontend passed",
    evidenceSnapshotSite: "site tests passed",
    evidenceSnapshotBuildValue: "Build",
    evidenceSnapshotBuild: "frontend build passed",
    evidenceCard3Body:
      "Public runtime, onboarding workflow, and product-site assertions all sit under replayable checks rather than screenshots alone.",
    verifierEyebrow: "3-minute verifier path",
    verifierTitle: "How to verify this repo quickly",
    verifierIntro:
      "If you only have a few minutes, do not start with the full local setup. Verify the moat in this order.",
    verifierStep1Title: "Watch the 90-second walkthrough",
    verifierStep1Body: "See one real CN-NL dividends case go from input to final boundary.",
    verifierStep2Title: "Check the measured pilot card",
    verifierStep2Body: "Confirm that a real CN-KR onboarding pilot has recorded timing evidence.",
    verifierStep3Title: "Scan the proof matrix",
    verifierStep3Body: "Verify that the compiler path holds across shadow rebuilds, delta proofs, and a real new-pair onboarding.",
    verifierStep4Title: "Only then open the local quick proof",
    verifierStep4Body: "Use the README smoke path if you want to validate the public runtime locally after the evidence layer makes sense.",
    verifierPrimary: "Open the README verifier path",
    verifierSecondary: "Jump back to the evidence layer",
    claimsEyebrow: "Implemented vs not claimed",
    claimsTitle: "Show what is real, and say out loud what is still not claimed",
    claimsIntro:
      "This product is stronger when it is explicit about both its current capability and its current limits.",
    claimsLeftTitle: "Implemented today",
    claimsLeftBody:
      "Source-anchored treaty pre-screening, guided fact collection, workflow-ready handoff, a human-reviewed onboarding compiler, OECD baseline-aware delta extraction, and a measured CN-KR pilot.",
    claimsRightTitle: "Not claimed",
    claimsRightBody:
      "No final tax opinion, no automatic MLI/PPT override, no guaranteed onboarding SLA, and no claim that future treaty pairs will always complete inside the same measured window.",
    coverageEyebrow: "Current coverage",
    coverageTitle: "Deliberately narrow, because trust matters more than breadth",
    coverageIntro:
      "The product focuses on a bounded set of treaty pairs and income types so the review path remains auditable and conservative.",
    coveragePair1Title: "China - Netherlands",
    coveragePair2Title: "China - Singapore",
    coveragePair3Title: "China - Korea",
    coveragePairIncome: "Dividends, interest, royalties",
    limitsEyebrow: "Boundaries",
    limitsTitle: "This tool does not replace a final tax opinion",
    limitsIntro:
      "It helps teams move faster through the front of the workflow, but it does not automate the final legal judgment.",
    limit1Title: "Not a final determination",
    limit1Body: "The output is a first-pass pre-review, not a substitute for legal, tax, or internal approval.",
    limit2Title: "MLI/PPT stays a review signal",
    limit2Body: "The tool surfaces these items for human follow-up instead of pretending to resolve them automatically.",
    limit3Title: "Unsupported scope is rejected",
    limit3Body: "When a case falls outside the supported treaty pairs or lanes, the workflow says so directly.",
    footerEyebrow: "Next step",
    footerTitle: "Use GitHub as the audit trail. Use the product page to explain the product.",
    footerBody:
      "The repository keeps the implementation and evidence pack. This overview page is here to help non-technical reviewers understand what the product is for before they open the code.",
    footerPrimary: "Open repository",
    footerSecondary: "Read the README",
    altGuidedFacts: "Guided fact collection panel in Tax Treaty Agent",
    altReviewOutput: "Structured treaty review output in Tax Treaty Agent",
    altWorkflowHandoff: "Workflow handoff summary in Tax Treaty Agent",
    altProductOverview: "Tax Treaty Agent product overview artwork",
    altWalkthroughInput: "CN-NL dividend case overview",
    altWalkthroughGuided: "Guided facts panel for dividend review",
    altWalkthroughBranch: "Treaty branch narrowing for Article 10 dividends",
    altWalkthroughProvenance: "Source-aware provenance in treaty review output",
    altWalkthroughHandoff: "Workflow handoff artifact for dividend review",
    altWalkthroughBoundary: "Final boundary and review-only signals",
  },
};

const metaDescription = document.querySelector('meta[name="description"]');
const languageButtons = Array.from(document.querySelectorAll("[data-lang-toggle]"));

function normalizeLanguage(value) {
  if (value === "zh" || value === "en") {
    return value;
  }
  return null;
}

function resolvePreferredLanguage() {
  try {
    const stored = normalizeLanguage(window.localStorage.getItem(STORAGE_KEY));
    if (stored) {
      return stored;
    }
  } catch {
    // Ignore storage access issues and fall back to browser language.
  }

  const browserLanguage = (navigator.language || "en").toLowerCase();
  return browserLanguage.startsWith("zh") ? "zh" : "en";
}

function persistLanguage(language) {
  try {
    window.localStorage.setItem(STORAGE_KEY, language);
  } catch {
    // Ignore storage access issues so the site still works without persistence.
  }
}

function applyLanguage(language) {
  const copy = translations[language] || translations.en;

  document.documentElement.lang = language === "zh" ? "zh-CN" : "en";
  document.title = copy.pageTitle;

  if (metaDescription) {
    metaDescription.setAttribute("content", copy.pageDescription);
  }

  document.querySelectorAll("[data-i18n]").forEach((element) => {
    const key = element.dataset.i18n;
    if (key && key in copy) {
      element.textContent = copy[key];
    }
  });

  document.querySelectorAll("[data-i18n-alt]").forEach((element) => {
    const key = element.dataset.i18nAlt;
    if (key && key in copy) {
      element.setAttribute("alt", copy[key]);
    }
  });

  languageButtons.forEach((button) => {
    const isActive = button.dataset.langToggle === language;
    button.classList.toggle("is-active", isActive);
    button.setAttribute("aria-pressed", String(isActive));
  });
}

for (const button of languageButtons) {
  button.addEventListener("click", () => {
    const language = normalizeLanguage(button.dataset.langToggle);
    if (!language) {
      return;
    }

    applyLanguage(language);
    persistLanguage(language);
  });
}

applyLanguage(resolvePreferredLanguage());

const observer = new IntersectionObserver(
  (entries) => {
    for (const entry of entries) {
      if (entry.isIntersecting) {
        entry.target.classList.add("is-visible");
        observer.unobserve(entry.target);
      }
    }
  },
  { threshold: 0.18, rootMargin: "0px 0px -8% 0px" },
);

for (const element of document.querySelectorAll(".reveal")) {
  observer.observe(element);
}
