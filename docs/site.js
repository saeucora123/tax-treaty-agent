const STORAGE_KEY = "tta-site-language";

const translations = {
  zh: {
    pageTitle: "Tax Treaty Agent | 跨境税收协定预审工具",
    pageDescription:
      "面向国际税务团队的跨境税收协定预审工具，帮助团队更快完成第一轮筛查，再进入正式法律或税务分析。",
    navWorkflow: "工作方式",
    navCoverage: "当前支持",
    navLimits: "使用边界",
    navRepo: "查看代码仓库",
    heroEyebrow: "面向国际税务团队",
    heroTitle: "帮助国际税团队更快完成跨境税收协定预审",
    heroLead:
      "先更快完成第一轮筛查，再进入正式法律或税务分析。这个工具会引导关键事实、收束到当前支持的协定路径，并输出一个可直接交接给下一位审核人的结构化结果。",
    heroSub:
      "它的目标是节省流程前段的时间，不是取代最终税务意见或法律判断。",
    heroPrimary: "打开 GitHub 仓库",
    heroSecondary: "查看当前支持范围",
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
  },
  en: {
    pageTitle: "Tax Treaty Agent | Cross-border treaty pre-screening",
    pageDescription:
      "Cross-border treaty pre-screening for international tax teams. Start with a faster first-pass review before full legal or tax analysis.",
    navWorkflow: "How it works",
    navCoverage: "Coverage",
    navLimits: "Boundaries",
    navRepo: "View repository",
    heroEyebrow: "For international tax teams",
    heroTitle: "Cross-border treaty pre-screening for international tax teams",
    heroLead:
      "Start with a faster first-pass review before full legal or tax analysis. The tool guides key facts, narrows to the treaty lane in scope, and returns a structured handoff for the next reviewer.",
    heroSub:
      "It is designed to save time at the front of the workflow, not to replace a final tax opinion.",
    heroPrimary: "Open GitHub repository",
    heroSecondary: "See supported coverage",
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
