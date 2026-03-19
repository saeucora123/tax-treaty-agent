import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";

import App from "./App";

function setLocationSearch(search: string) {
  window.history.pushState({}, "", search);
}

afterEach(() => {
  setLocationSearch("/");
});


test("shows reference cases only for states the live demo can actually reach", () => {
  globalThis.fetch = vi.fn() as typeof fetch;

  render(<App />);

  expect(screen.getAllByText("[Supported]")).toHaveLength(2);
  expect(screen.getByText("[Unsupported]")).toBeInTheDocument();
  expect(screen.getByText("[Incomplete]")).toBeInTheDocument();
  expect(screen.queryByText("[Priority Review]")).not.toBeInTheDocument();
  expect(screen.queryByText("[Hold]")).not.toBeInTheDocument();
});


test("shows structured treaty analysis after submitting a supported scenario", async () => {
  const user = userEvent.setup();

  globalThis.fetch = vi.fn().mockResolvedValue({
    ok: true,
    json: async () => ({
      supported: true,
      review_state: {
        state_code: "pre_review_complete",
        state_label_zh: "预审完成",
        state_summary: "系统已完成第一轮预审，请按标准复核流程继续。",
      },
      confirmed_scope: {
        applicable_treaty: "中国-荷兰税收协定",
        applicable_article: "Article 12 - Royalties",
        payment_direction: "CN -> NL",
        income_type: "royalties",
      },
      next_actions: [
        {
          priority: "medium",
          action: "按标准人工复核流程确认条款适用条件与受益所有人事实。",
          reason: "当前结果属于第一轮预审完成，不等于最终税务结论。",
        },
      ],
      handoff_package: {
        machine_handoff: {
          schema_version: "stage5.v1",
          record_kind: "supported",
          review_state_code: "pre_review_complete",
          recommended_route: "standard_review",
          applicable_treaty: "中国-荷兰税收协定",
          payment_direction: "CN -> NL",
          income_type: "royalties",
          article_number: "12",
          article_title: "Royalties",
          rate_display: "10%",
          auto_conclusion_allowed: true,
          human_review_required: true,
          data_source_used: "stable",
          source_reference: "Article 12(2)",
          source_excerpt:
            "However, such royalties may also be taxed in the Contracting State in which they arise, and according to the laws of that State, but if the beneficial owner of the royalties is a resident of the other Contracting State, the tax so charged shall not exceed 10 per cent of the gross amount of the royalties.",
          treaty_version:
            "2013 agreement reflected in the official English treaty text used for the stable runtime dataset.",
          mli_summary:
            "China deposited its MLI instrument on 25 May 2022 with entry into force on 1 September 2022, and the Netherlands deposited on 29 March 2019 with entry into force on 1 July 2019. The SAT synthesised text and OECD peer-review materials treat the China-Netherlands agreement as an MLI-covered tax agreement and show MLI Article 7 (PPT) as applicable. The system does not determine PPT satisfaction automatically.",
          review_priority: "normal",
          blocking_facts: [
            "Whether the payment is truly for qualifying intellectual property use.",
          ],
          next_actions: [
            {
              priority: "medium",
              action: "按标准人工复核流程确认条款适用条件与受益所有人事实。",
              reason: "当前结果属于第一轮预审完成，不等于最终税务结论。",
            },
          ],
          user_declared_facts: [],
        },
        human_review_brief: {
          brief_title: "Treaty Pre-Review Brief",
          headline: "CN -> NL royalties falls inside current treaty scope.",
          disposition: "Proceed with standard human review.",
          summary_lines: [
            "Article 12 royalties is the current treaty lane.",
            "2013 agreement reflected in the official English treaty text used for the stable runtime dataset.",
            "China deposited its MLI instrument on 25 May 2022 with entry into force on 1 September 2022, and the Netherlands deposited on 29 March 2019 with entry into force on 1 July 2019. The SAT synthesised text and OECD peer-review materials treat the China-Netherlands agreement as an MLI-covered tax agreement and show MLI Article 7 (PPT) as applicable. The system does not determine PPT satisfaction automatically.",
          ],
          facts_to_verify: [
            "Confirm beneficial ownership before relying on the treaty position.",
          ],
          handoff_note: "This is a bounded pre-review output, not a final tax opinion.",
        },
      },
      input_interpretation: {
        parser_source: "llm",
        payer_country: "CN",
        payee_country: "NL",
        transaction_type: "royalties",
        matched_transaction_label: "software license",
      },
      normalized_input: {
        payer_country: "CN",
        payee_country: "NL",
        transaction_type: "royalties",
      },
      result: {
        summary:
          "Preliminary view: Article 12 Royalties appears relevant, with a treaty rate ceiling of 10%. Manual review is still recommended.",
        boundary_note:
          "This is a first-pass treaty pre-review based on limited scenario facts. Final eligibility still depends on additional facts, documents, and analysis outside the current review scope.",
        immediate_action:
          "Proceed with standard manual review before relying on the treaty position.",
        article_number: "12",
        article_title: "Royalties",
        source_reference: "Article 12(2)",
        source_language: "en",
        source_excerpt:
          "However, such royalties may also be taxed in the Contracting State in which they arise, and according to the laws of that State, but if the beneficial owner of the royalties is a resident of the other Contracting State, the tax so charged shall not exceed 10 per cent of the gross amount of the royalties.",
        source_trace: {
          treaty_full_name:
            "Convention between the Government of the People's Republic of China and the Government of the Kingdom of the Netherlands for the Avoidance of Double Taxation and the Prevention of Fiscal Evasion with respect to Taxes on Income",
          version_note:
            "2013 agreement reflected in the official English treaty text used for the stable runtime dataset.",
          source_document_title:
            "Convention between the Government of the People's Republic of China and the Government of the Kingdom of the Netherlands for the Avoidance of Double Taxation and the Prevention of Fiscal Evasion with respect to Taxes on Income",
          language_version: "en",
          official_source_ids: ["sat-cn-nl-2013-en-pdf", "nl-2013-consolidated-text"],
          protocol_note: null,
          working_paper_ref:
            "docs/superpowers/research/stage-6-evidence/2026-03-13-cn-nl-royalties-alignment-check.md",
        },
        mli_context: {
          covered_tax_agreement: true,
          ppt_applies: true,
          summary:
            "China deposited its MLI instrument on 25 May 2022 with entry into force on 1 September 2022, and the Netherlands deposited on 29 March 2019 with entry into force on 1 July 2019. The SAT synthesised text and OECD peer-review materials treat the China-Netherlands agreement as an MLI-covered tax agreement and show MLI Article 7 (PPT) as applicable. The system does not determine PPT satisfaction automatically.",
          human_review_note:
            "Confirm during manual review whether obtaining treaty benefits was one of the principal purposes of the arrangement.",
          official_source_ids: ["oecd-mli-signatories-and-parties", "sat-cn-nl-mli-en-pdf"],
        },
        rate: "10%",
        extraction_confidence: 0.98,
        auto_conclusion_allowed: true,
        key_missing_facts: [
          "Whether the payment is truly for qualifying intellectual property use.",
          "Whether the recipient is the beneficial owner of the royalty income.",
          "Whether the contract and payment flow support treaty characterization.",
        ],
        review_checklist: [
          "Confirm the payment is actually for the use of, or right to use, qualifying intellectual property.",
          "Confirm the recipient is the beneficial owner of the royalty income.",
          "Check the underlying contract, invoice, and payment flow for factual consistency.",
        ],
        conditions: ["Treaty applicability depends on the facts of the payment."],
        notes: ["Beneficial ownership and factual details may affect the final conclusion."],
        human_review_required: true,
        review_priority: "normal",
        review_reason: "Final eligibility depends on facts outside the current review scope.",
      },
    }),
  }) as typeof fetch;

  render(<App />);

  await user.type(
    screen.getByLabelText(/cross-border scenario/i),
    "中国居民企业向荷兰支付特许权使用费",
  );
  await user.click(screen.getByRole("button", { name: /run review/i }));

  expect(
    await screen.findByText(/preliminary view: article 12 royalties appears relevant/i),
  ).toBeInTheDocument();
  expect(screen.getByText("预审完成")).toBeInTheDocument();
  expect(screen.getByText("系统已完成第一轮预审，请按标准复核流程继续。")).toBeInTheDocument();
  expect(screen.getByText(/how we read this input/i)).toBeInTheDocument();
  expect(screen.getByText(/parsed by llm input parser/i)).toBeInTheDocument();
  expect(screen.getByText(/software license/i)).toBeInTheDocument();
  expect(await screen.findByText("Article 12 · Royalties")).toBeInTheDocument();
  expect(screen.getByText("Article 12(2)")).toBeInTheDocument();
  expect(
    screen.getByText(
      "However, such royalties may also be taxed in the Contracting State in which they arise, and according to the laws of that State, but if the beneficial owner of the royalties is a resident of the other Contracting State, the tax so charged shall not exceed 10 per cent of the gross amount of the royalties.",
    ),
  ).toBeInTheDocument();
  expect(screen.getByText("10%")).toBeInTheDocument();
  expect(screen.getByText(/english source/i)).toBeInTheDocument();
  expect(screen.getByText(/98% extraction confidence/i)).toBeInTheDocument();
  expect(screen.getByText(/source chain/i)).toBeInTheDocument();
  expect(
    screen.getAllByText(/2013 agreement reflected in the official english treaty text/i).length,
  ).toBeGreaterThan(0);
  expect(screen.getAllByText(/mli article 7 \(ppt\)/i).length).toBeGreaterThan(0);
  expect(screen.getByText(/docs\/superpowers\/research\/stage-6-evidence\/2026-03-13-cn-nl-royalties-alignment-check\.md/i)).toBeInTheDocument();
  expect(screen.getByText(/human review recommended/i)).toBeInTheDocument();
  expect(screen.getByText(/what this review means/i)).toBeInTheDocument();
  expect(
    screen.getByText(/first-pass treaty pre-review based on limited scenario facts/i),
  ).toBeInTheDocument();
  expect(screen.getByText(/immediate action/i)).toBeInTheDocument();
  expect(
    screen.getByText(/proceed with standard manual review before relying on the treaty position/i),
  ).toBeInTheDocument();
  expect(screen.getByText(/next verification steps/i)).toBeInTheDocument();
  expect(screen.getByText(/key missing facts/i)).toBeInTheDocument();
  expect(
    screen.getByText(/whether the recipient is the beneficial owner of the royalty income/i),
  ).toBeInTheDocument();
  expect(
    screen.getByText(/confirm the recipient is the beneficial owner of the royalty income/i),
  ).toBeInTheDocument();
  expect(screen.getByText(/按标准人工复核流程确认条款适用条件与受益所有人事实/i)).toBeInTheDocument();
  expect(screen.getByText(/workflow handoff/i)).toBeInTheDocument();
  expect(screen.getByText(/proceed with standard human review/i)).toBeInTheDocument();
  expect(screen.getByText(/cn -> nl royalties falls inside current treaty scope/i)).toBeInTheDocument();
});


test("shows a stronger review warning for medium-confidence treaty extraction", async () => {
  const user = userEvent.setup();

  globalThis.fetch = vi.fn().mockResolvedValue({
    ok: true,
    json: async () => ({
      supported: true,
      review_state: {
        state_code: "partial_review",
        state_label_zh: "预审部分完成",
        state_summary: "系统已完成结构化缩减，但当前结果仍需优先人工复核。",
      },
      confirmed_scope: {
        applicable_treaty: "中国-荷兰税收协定",
        applicable_article: "Article 12 - Royalties",
        payment_direction: "CN -> NL",
        income_type: "royalties",
      },
      next_actions: [
        {
          priority: "high",
          action: "优先核验条款适用条件、来源质量和关键事实后再引用该结果。",
          reason: "当前来源置信度不足以支持常规依赖，但已完成条款缩减。",
        },
      ],
      normalized_input: {
        payer_country: "CN",
        payee_country: "NL",
        transaction_type: "royalties",
      },
      result: {
        summary:
          "Preliminary view: Article 12 Royalties appears relevant, with a treaty rate ceiling of 10%. Prioritize manual review before relying on this result.",
        boundary_note:
          "This is a first-pass treaty pre-review based on limited scenario facts. Final eligibility still depends on additional facts, documents, and analysis outside the current review scope.",
        immediate_action:
          "Escalate this case for priority manual review before using the treaty result.",
        article_number: "12",
        article_title: "Royalties",
        source_reference: "Article 12(1)",
        source_language: "en",
        source_excerpt:
          "Royalty treatment is governed by Article 12(1), subject to treaty conditions and factual qualification.",
        rate: "10%",
        extraction_confidence: 0.88,
        auto_conclusion_allowed: true,
        key_missing_facts: [
          "Whether the payment is truly for qualifying intellectual property use.",
          "Whether the recipient is the beneficial owner of the royalty income.",
          "Whether the contract and payment flow support treaty characterization.",
        ],
        review_checklist: [
          "Confirm the payment is actually for the use of, or right to use, qualifying intellectual property.",
          "Confirm the recipient is the beneficial owner of the royalty income.",
          "Check the underlying contract, invoice, and payment flow for factual consistency.",
        ],
        conditions: ["Treaty applicability depends on the facts of the payment."],
        notes: ["Beneficial ownership and factual details may affect the final conclusion."],
        human_review_required: true,
        review_priority: "high",
        review_reason:
          "Final eligibility depends on facts outside the current review scope. Source extraction confidence is not high enough for routine reliance, so prioritize manual verification.",
      },
    }),
  }) as typeof fetch;

  render(<App />);

  await user.type(
    screen.getByLabelText(/cross-border scenario/i),
    "中国居民企业向荷兰支付特许权使用费",
  );
  await user.click(screen.getByRole("button", { name: /run review/i }));

  expect(
    await screen.findByText(/prioritize manual review before relying on this result/i),
  ).toBeInTheDocument();
  expect(screen.getByText("预审部分完成")).toBeInTheDocument();
  expect(screen.getByText("系统已完成结构化缩减，但当前结果仍需优先人工复核。")).toBeInTheDocument();
  expect(
    screen.getByText(/escalate this case for priority manual review before using the treaty result/i),
  ).toBeInTheDocument();
  expect(screen.getByText(/优先核验条款适用条件、来源质量和关键事实后再引用该结果/i)).toBeInTheDocument();
  expect(await screen.findByText(/\[ priority review \]/i)).toBeInTheDocument();
  expect(screen.getByText(/priority review required/i)).toBeInTheDocument();
  expect(screen.getByText(/^review$/i)).toBeInTheDocument();
  expect(screen.getByText(/88% extraction confidence/i)).toBeInTheDocument();
  expect(screen.getByText(/prioritize manual verification/i)).toBeInTheDocument();
});


test("holds automatic treaty conclusion when source confidence is very low", async () => {
  const user = userEvent.setup();

  globalThis.fetch = vi.fn().mockResolvedValue({
    ok: true,
    json: async () => ({
      supported: true,
      review_state: {
        state_code: "needs_human_intervention",
        state_label_zh: "需要人工介入",
        state_summary: "当前结果已触发保守停止，应转入人工处理而不是继续自动推进。",
      },
      confirmed_scope: {
        applicable_treaty: "中国-荷兰税收协定",
        applicable_article: "Article 12 - Royalties",
        payment_direction: "CN -> NL",
        income_type: "royalties",
      },
      next_actions: [
        {
          priority: "high",
          action: "停止自动结论流程，并将当前条款、来源和待核事实交给人工复核。",
          reason: "当前来源置信度过低，系统不应继续自动推进。",
        },
      ],
      normalized_input: {
        payer_country: "CN",
        payee_country: "NL",
        transaction_type: "royalties",
      },
      result: {
        summary:
          "Preliminary view: Article 12 Royalties appears relevant, but this version should not issue an automatic conclusion. The current indicative treaty rate is 10%.",
        boundary_note:
          "This is a first-pass treaty pre-review based on limited scenario facts. Final eligibility still depends on additional facts, documents, and analysis outside the current review scope.",
        immediate_action:
          "Do not rely on this result yet. Resolve the missing facts and supporting documents before any treaty conclusion.",
        article_number: "12",
        article_title: "Royalties",
        source_reference: "Article 12(1)",
        source_language: "en",
        source_excerpt:
          "Royalty treatment is governed by Article 12(1), subject to treaty conditions and factual qualification.",
        rate: "10%",
        extraction_confidence: 0.72,
        auto_conclusion_allowed: false,
        key_missing_facts: [
          "Whether the payment is truly for qualifying intellectual property use.",
          "Whether the recipient is the beneficial owner of the royalty income.",
          "Whether the contract and payment flow support treaty characterization.",
        ],
        review_checklist: [
          "Confirm the payment is actually for the use of, or right to use, qualifying intellectual property.",
          "Confirm the recipient is the beneficial owner of the royalty income.",
          "Check the underlying contract, invoice, and payment flow for factual consistency.",
        ],
        conditions: ["Treaty applicability depends on the facts of the payment."],
        notes: ["Beneficial ownership and factual details may affect the final conclusion."],
        human_review_required: true,
        review_priority: "high",
        review_reason:
          "Final eligibility depends on facts outside the current review scope. Source extraction confidence is too low for this version to issue an automatic treaty conclusion.",
      },
    }),
  }) as typeof fetch;

  render(<App />);

  await user.type(
    screen.getByLabelText(/cross-border scenario/i),
    "中国居民企业向荷兰支付特许权使用费",
  );
  await user.click(screen.getByRole("button", { name: /run review/i }));

  expect(
    await screen.findByText(/this version should not issue an automatic conclusion/i),
  ).toBeInTheDocument();
  expect(screen.getByText("需要人工介入")).toBeInTheDocument();
  expect(screen.getByText("当前结果已触发保守停止，应转入人工处理而不是继续自动推进。")).toBeInTheDocument();
  expect(
    screen.getByText(/do not rely on this result yet\. resolve the missing facts and supporting documents/i),
  ).toBeInTheDocument();
  expect(screen.getByText(/停止自动结论流程，并将当前条款、来源和待核事实交给人工复核/i)).toBeInTheDocument();
  expect(await screen.findByText(/provisional review only/i)).toBeInTheDocument();
  expect(screen.getByText(/\[ hold \] confidence too low for automatic conclusion/i)).toBeInTheDocument();
  expect(screen.getByText(/72% extraction confidence/i)).toBeInTheDocument();
  expect(screen.getByText(/automatic treaty conclusion/i)).toBeInTheDocument();
});


test("describes branch-ambiguity hold states without pretending the issue is low confidence", async () => {
  const user = userEvent.setup();

  globalThis.fetch = vi.fn().mockResolvedValue({
    ok: true,
    json: async () => ({
      supported: true,
      review_state: {
        state_code: "can_be_completed",
        state_label_zh: "可补全",
        state_summary: "系统已缩小范围；补充少量关键事实后，可进一步明确结果。",
      },
      confirmed_scope: {
        applicable_treaty: "中国-荷兰税收协定",
        applicable_article: "Article 10 - Dividends",
        payment_direction: "CN -> NL",
        income_type: "dividends",
      },
      next_actions: [
        {
          priority: "high",
          action: "先核实股息分支所需的关键事实，再判断候选税率分支。",
          reason: "当前存在多个可信税率分支，系统不会自动替你选择其一。",
        },
      ],
      normalized_input: {
        payer_country: "CN",
        payee_country: "NL",
        transaction_type: "dividends",
      },
      result: {
        summary:
          "Preliminary view: Article 10 Dividends appears relevant, but multiple treaty rate branches (5% / 10%) are possible and this version should not issue an automatic conclusion.",
        boundary_note:
          "This is a first-pass treaty pre-review based on limited scenario facts. Final eligibility still depends on additional facts, documents, and analysis outside the current review scope.",
        immediate_action:
          "Do not rely on this result yet. Resolve the missing facts and supporting documents before any treaty conclusion.",
        article_number: "10",
        article_title: "Dividends",
        source_reference: "Article 10(2)",
        source_language: "en",
        source_excerpt:
          "However, such dividends may also be taxed in the State of source, but the tax so charged shall not exceed: (a) 5 per cent ... (b) 10 per cent in all other cases.",
        rate: "5% / 10%",
        extraction_confidence: 0.9,
        auto_conclusion_allowed: false,
        key_missing_facts: [
          "Whether the payment is legally a dividend rather than another type of return.",
          "Whether the recipient is the beneficial owner of the dividend income.",
          "Whether shareholding facts support relying on the treaty position.",
        ],
        review_checklist: [
          "Confirm the payment is legally characterized as a dividend rather than another return.",
          "Confirm the recipient is the beneficial owner of the dividend income.",
          "Check shareholding facts and supporting corporate records before relying on the treaty rate.",
        ],
        conditions: [
          "If the beneficial owner is a company which holds directly at least 25 per cent of the capital of the company paying the dividends.",
        ],
        notes: [],
        human_review_required: true,
        review_priority: "high",
        review_reason:
          "Multiple treaty rate branches were found in this article, and the current scenario does not provide enough facts to choose one automatically.",
        alternative_rate_candidates: [
          {
            source_reference: "Article 10(2)",
            rate: "10%",
            conditions: ["In all other cases."],
          },
        ],
      },
    }),
  }) as typeof fetch;

  render(<App />);

  await user.type(screen.getByLabelText(/cross-border scenario/i), "中国公司向荷兰公司支付股息");
  await user.click(screen.getByRole("button", { name: /run review/i }));

  expect(await screen.findByText(/manual branch review required/i)).toBeInTheDocument();
  expect(screen.getByText("可补全")).toBeInTheDocument();
  expect(screen.getByText("系统已缩小范围；补充少量关键事实后，可进一步明确结果。")).toBeInTheDocument();
  expect(screen.getByText(/先核实股息分支所需的关键事实，再判断候选税率分支/i)).toBeInTheDocument();
  expect(screen.getByText(/\[ hold \] multiple treaty branches require manual selection/i)).toBeInTheDocument();
  expect(screen.queryByText(/\[ hold \] confidence too low for automatic conclusion/i)).not.toBeInTheDocument();
});


test("shows missing-input guidance for unsupported or incomplete scenarios", async () => {
  const user = userEvent.setup();

  globalThis.fetch = vi.fn().mockResolvedValue({
    ok: true,
    json: async () => ({
      supported: false,
      review_state: {
        state_code: "can_be_completed",
        state_label_zh: "可补全",
        state_summary: "系统仍在当前预审范围内，但需要补充缺失事实后才能继续缩小结果。",
      },
      next_actions: [
        {
          priority: "high",
          action: "补充付款方国家或付款方主体信息后重新提交查询。",
          reason: "当前缺少足够的付款方事实，系统无法确认交易方向。",
        },
      ],
      handoff_package: {
        machine_handoff: {
          schema_version: "stage5.v1",
          record_kind: "incomplete",
          review_state_code: "can_be_completed",
          recommended_route: "complete_facts_then_rerun",
          applicable_treaty: null,
          payment_direction: null,
          income_type: "dividends",
          article_number: null,
          article_title: null,
          rate_display: null,
          auto_conclusion_allowed: false,
          human_review_required: true,
          data_source_used: "stable",
          source_reference: null,
          review_priority: "normal",
          blocking_facts: ["payer_country"],
          next_actions: [
            {
              priority: "high",
              action: "补充付款方国家或付款方主体信息后重新提交查询。",
              reason: "当前缺少足够的付款方事实，系统无法确认交易方向。",
            },
          ],
          user_declared_facts: [],
        },
        human_review_brief: {
          brief_title: "Treaty Pre-Review Brief",
          headline:
            "Current scenario needs additional facts before treaty pre-review can continue.",
          disposition: "Complete the missing facts and rerun the pre-review.",
          summary_lines: [
            "Please provide a clearer scenario with both payer and payee country context.",
          ],
          facts_to_verify: ["payer_country"],
          handoff_note: "This is a bounded pre-review output, not a final tax opinion.",
        },
      },
      reason: "incomplete_scenario",
      message: "Please provide a clearer scenario with both payer and payee country context.",
      immediate_action: "Add the missing scenario facts before running the treaty review again.",
      missing_fields: ["payer_country"],
      suggested_format: "Try a sentence like: 中国居民企业向荷兰公司支付股息",
      suggested_examples: [
        "中国居民企业向荷兰公司支付股息",
        "荷兰公司向中国公司支付利息",
      ],
    }),
  }) as typeof fetch;

  render(<App />);

  await user.type(
    screen.getByLabelText(/cross-border scenario/i),
    "向荷兰公司支付股息",
  );
  await user.click(screen.getByRole("button", { name: /run review/i }));

  expect(await screen.findByText("可补全")).toBeInTheDocument();
  expect(screen.getByText("系统仍在当前预审范围内，但需要补充缺失事实后才能继续缩小结果。")).toBeInTheDocument();
  expect(screen.getByText(/immediate action/i)).toBeInTheDocument();
  expect(
    screen.getByText(/add the missing scenario facts before running the treaty review again/i),
  ).toBeInTheDocument();
  expect(screen.getByText(/补充付款方国家或付款方主体信息后重新提交查询/i)).toBeInTheDocument();
  expect(screen.getByText(/how to fix this input/i)).toBeInTheDocument();
  expect(screen.getByText(/payer country/i)).toBeInTheDocument();
  expect(screen.getByText(/try a sentence like/i)).toBeInTheDocument();
  expect(screen.getByText("荷兰公司向中国公司支付利息")).toBeInTheDocument();
  expect(screen.getByText(/workflow handoff/i)).toBeInTheDocument();
  expect(screen.getByText(/complete the missing facts and rerun the pre-review/i)).toBeInTheDocument();
});


test("shows multiple possible rates instead of a single anchored treaty rate when branch facts are missing", async () => {
  const user = userEvent.setup();

  globalThis.fetch = vi.fn().mockResolvedValue({
    ok: true,
    json: async () => ({
      supported: true,
      normalized_input: {
        payer_country: "CN",
        payee_country: "NL",
        transaction_type: "dividends",
      },
      result: {
        summary:
          "Preliminary view: Article 10 Dividends appears relevant, but multiple treaty rate branches (5% / 10%) are possible and this version should not issue an automatic conclusion.",
        boundary_note:
          "This is a first-pass treaty pre-review based on limited scenario facts. Final eligibility still depends on additional facts, documents, and analysis outside the current review scope.",
        immediate_action:
          "Do not rely on this result yet. Resolve the missing facts and supporting documents before any treaty conclusion.",
        article_number: "10",
        article_title: "Dividends",
        source_reference: "Article 10(2)",
        source_language: "en",
        source_excerpt:
          "However, such dividends may also be taxed in the State of source, but the tax so charged shall not exceed: (a) 5 per cent ... (b) 10 per cent in all other cases.",
        rate: "5% / 10%",
        extraction_confidence: 0.9,
        auto_conclusion_allowed: false,
        key_missing_facts: [
          "Whether the payment is legally a dividend rather than another type of return.",
          "Whether the recipient is the beneficial owner of the dividend income.",
          "Whether shareholding facts support relying on the treaty position.",
        ],
        review_checklist: [
          "Confirm the payment is legally characterized as a dividend rather than another return.",
          "Confirm the recipient is the beneficial owner of the dividend income.",
          "Check shareholding facts and supporting corporate records before relying on the treaty rate.",
        ],
        conditions: [
          "If the beneficial owner is a company which holds directly at least 25 per cent of the capital of the company paying the dividends.",
        ],
        notes: [],
        human_review_required: true,
        review_priority: "high",
        review_reason:
          "Multiple treaty rate branches were found in this article, and the current scenario does not provide enough facts to choose one automatically.",
        alternative_rate_candidates: [
          {
            source_reference: "Article 10(2)",
            rate: "10%",
            conditions: ["In all other cases."],
          },
        ],
      },
    }),
  }) as typeof fetch;

  render(<App />);

  await user.type(screen.getByLabelText(/cross-border scenario/i), "中国公司向荷兰公司支付股息");
  await user.click(screen.getByRole("button", { name: /run review/i }));

  expect(await screen.findByText(/multiple treaty rate branches \(5% \/ 10%\) are possible/i)).toBeInTheDocument();
  expect(screen.getByText(/possible treaty rates/i)).toBeInTheDocument();
  expect(screen.getByText("5% / 10%")).toBeInTheDocument();
  expect(screen.getByText(/alternative rate candidates/i)).toBeInTheDocument();
  expect(screen.getByText(/10% · Article 10\(2\)/i)).toBeInTheDocument();
});


test("renders a bounded fact-completion form for CN-NL dividend branch ambiguity", async () => {
  const user = userEvent.setup();

  globalThis.fetch = vi.fn().mockResolvedValue({
    ok: true,
    json: async () => ({
      supported: true,
      review_state: {
        state_code: "can_be_completed",
        state_label_zh: "可补全",
        state_summary: "系统已缩小范围；补充少量关键事实后，可进一步明确结果。",
      },
      confirmed_scope: {
        applicable_treaty: "中国-荷兰税收协定",
        applicable_article: "Article 10 - Dividends",
        payment_direction: "CN -> NL",
        income_type: "dividends",
      },
      next_actions: [
        {
          priority: "high",
          action: "先核实股息分支所需的关键事实，再判断候选税率分支。",
          reason: "当前存在多个可信税率分支，系统不会自动替你选择其一。",
        },
      ],
      fact_completion_status: {
        status_code: "awaiting_user_facts",
        status_label_zh: "待补事实",
        status_summary: "请先补充关键持股事实，系统才能继续缩小股息税率分支。",
      },
      fact_completion: {
        flow_type: "bounded_form",
        session_type: "pseudo_multiturn",
        user_declaration_note: "Facts entered here are user-declared and not independently verified.",
        facts: [
          {
            fact_key: "direct_holding_confirmed",
            prompt: "Does the Dutch recipient directly hold capital in the Chinese payer?",
            input_type: "single_select",
            options: ["yes", "no", "unknown"],
          },
          {
            fact_key: "direct_holding_threshold_met",
            prompt: "If the holding is direct, is the direct holding at least 25%?",
            input_type: "single_select",
            options: ["yes", "no", "unknown"],
          },
        ],
      },
      user_declared_facts: null,
      normalized_input: {
        payer_country: "CN",
        payee_country: "NL",
        transaction_type: "dividends",
      },
      result: {
        summary:
          "Preliminary view: Article 10 Dividends appears relevant, but multiple treaty rate branches (5% / 10%) are possible and this version should not issue an automatic conclusion.",
        boundary_note:
          "This is a first-pass treaty pre-review based on limited scenario facts. Final eligibility still depends on additional facts, documents, and analysis outside the current review scope.",
        immediate_action:
          "Do not rely on this result yet. Resolve the missing facts and supporting documents before any treaty conclusion.",
        article_number: "10",
        article_title: "Dividends",
        source_reference: "Article 10(2)(b)",
        source_language: "en",
        source_excerpt:
          "In all other cases, the tax charged in the State of source shall not exceed 10 per cent of the gross amount of the dividends.",
        rate: "5% / 10%",
        extraction_confidence: 0.98,
        auto_conclusion_allowed: false,
        key_missing_facts: [
          "Whether the payment is legally a dividend rather than another type of return.",
          "Whether the recipient is the beneficial owner of the dividend income.",
          "Whether shareholding facts support relying on the treaty position.",
        ],
        review_checklist: [
          "Confirm the payment is legally characterized as a dividend rather than another return.",
          "Confirm the recipient is the beneficial owner of the dividend income.",
          "Check shareholding facts and supporting corporate records before relying on the treaty rate.",
        ],
        conditions: ["Applies when the reduced-rate branch is not established."],
        notes: [],
        human_review_required: true,
        review_priority: "high",
        review_reason:
          "Multiple treaty rate branches were found in this article, and the current scenario does not provide enough facts to choose one automatically.",
        alternative_rate_candidates: [
          {
            source_reference: "Article 10(2)(a)",
            rate: "5%",
            conditions: [
              "The beneficial owner is a company which holds directly at least 25 per cent of the capital of the company paying the dividends.",
            ],
          },
        ],
      },
    }),
  }) as typeof fetch;

  render(<App />);

  await user.type(screen.getByLabelText(/cross-border scenario/i), "中国公司向荷兰公司支付股息");
  await user.click(screen.getByRole("button", { name: /run review/i }));

  expect(await screen.findByText(/complete missing facts/i)).toBeInTheDocument();
  expect(screen.getByText("待补事实")).toBeInTheDocument();
  expect(screen.getByText(/请先补充关键持股事实/i)).toBeInTheDocument();
  expect(screen.getByText(/does the dutch recipient directly hold capital in the chinese payer/i)).toBeInTheDocument();
  expect(screen.getByText(/if the holding is direct, is the direct holding at least 25%/i)).toBeInTheDocument();
  expect(screen.getByText(/facts entered here are user-declared and not independently verified/i)).toBeInTheDocument();
});


test("re-runs the review with bounded fact inputs and shows user-declared facts", async () => {
  const user = userEvent.setup();

  globalThis.fetch = vi
    .fn()
    .mockResolvedValueOnce({
      ok: true,
      json: async () => ({
        supported: true,
        review_state: {
          state_code: "can_be_completed",
          state_label_zh: "可补全",
          state_summary: "系统已缩小范围；补充少量关键事实后，可进一步明确结果。",
        },
        confirmed_scope: {
          applicable_treaty: "中国-荷兰税收协定",
          applicable_article: "Article 10 - Dividends",
          payment_direction: "CN -> NL",
          income_type: "dividends",
        },
        next_actions: [
          {
            priority: "high",
            action: "先核实股息分支所需的关键事实，再判断候选税率分支。",
            reason: "当前存在多个可信税率分支，系统不会自动替你选择其一。",
          },
        ],
        fact_completion_status: {
          status_code: "awaiting_user_facts",
          status_label_zh: "待补事实",
          status_summary: "请先补充关键持股事实，系统才能继续缩小股息税率分支。",
        },
        fact_completion: {
          flow_type: "bounded_form",
          session_type: "pseudo_multiturn",
          user_declaration_note: "Facts entered here are user-declared and not independently verified.",
          facts: [
            {
              fact_key: "direct_holding_confirmed",
              prompt: "Does the Dutch recipient directly hold capital in the Chinese payer?",
              input_type: "single_select",
              options: ["yes", "no", "unknown"],
            },
            {
              fact_key: "direct_holding_threshold_met",
              prompt: "If the holding is direct, is the direct holding at least 25%?",
              input_type: "single_select",
              options: ["yes", "no", "unknown"],
            },
            {
              fact_key: "beneficial_owner_confirmed",
              prompt: "Has beneficial-owner status been separately confirmed outside this tool?",
              input_type: "single_select",
              options: ["yes", "no", "unknown"],
            },
            {
              fact_key: "pe_effectively_connected",
              prompt: "Is the dividend effectively connected with a permanent establishment or fixed base of the Dutch recipient in China?",
              input_type: "single_select",
              options: ["yes", "no", "unknown"],
            },
            {
              fact_key: "holding_structure_is_direct",
              prompt: "Is the holding structure confirmed to be direct with no intermediate holding entity between the recipient and the paying company?",
              input_type: "single_select",
              options: ["yes", "no", "unknown"],
            },
            {
              fact_key: "mli_ppt_risk_flag",
              prompt: "Has a principal purpose test (PPT) risk assessment been performed for this dividend payment under the MLI?",
              input_type: "single_select",
              options: ["yes", "no", "unknown"],
            },
          ],
        },
        user_declared_facts: null,
        normalized_input: {
          payer_country: "CN",
          payee_country: "NL",
          transaction_type: "dividends",
        },
        result: {
          summary:
            "Preliminary view: Article 10 Dividends appears relevant, but multiple treaty rate branches (5% / 10%) are possible and this version should not issue an automatic conclusion.",
          boundary_note:
            "This is a first-pass treaty pre-review based on limited scenario facts. Final eligibility still depends on additional facts, documents, and analysis outside the current review scope.",
          immediate_action:
            "Do not rely on this result yet. Resolve the missing facts and supporting documents before any treaty conclusion.",
          article_number: "10",
          article_title: "Dividends",
          source_reference: "Article 10(2)(b)",
          source_language: "en",
          source_excerpt: "In all other cases, the tax charged in the State of source shall not exceed 10 per cent.",
          rate: "5% / 10%",
          extraction_confidence: 0.98,
          auto_conclusion_allowed: false,
          key_missing_facts: [
            "Whether the payment is legally a dividend rather than another type of return.",
            "Whether the recipient is the beneficial owner of the dividend income.",
            "Whether shareholding facts support relying on the treaty position.",
          ],
          review_checklist: [
            "Confirm the payment is legally characterized as a dividend rather than another return.",
            "Confirm the recipient is the beneficial owner of the dividend income.",
            "Check shareholding facts and supporting corporate records before relying on the treaty rate.",
          ],
          conditions: ["Applies when the reduced-rate branch is not established."],
          notes: [],
          human_review_required: true,
          review_priority: "high",
          review_reason:
            "Multiple treaty rate branches were found in this article, and the current scenario does not provide enough facts to choose one automatically.",
          alternative_rate_candidates: [
            {
              source_reference: "Article 10(2)(a)",
              rate: "5%",
              conditions: [
                "The beneficial owner is a company which holds directly at least 25 per cent of the capital of the company paying the dividends.",
              ],
            },
          ],
        },
      }),
    })
    .mockResolvedValueOnce({
      ok: true,
      json: async () => ({
        supported: true,
        review_state: {
          state_code: "pre_review_complete",
          state_label_zh: "预审完成",
          state_summary: "系统已完成第一轮预审，请按标准复核流程继续。",
        },
        confirmed_scope: {
          applicable_treaty: "中国-荷兰税收协定",
          applicable_article: "Article 10 - Dividends",
          payment_direction: "CN -> NL",
          income_type: "dividends",
        },
        next_actions: [
          {
            priority: "medium",
            action: "按标准人工复核流程确认条款适用条件与受益所有人事实。",
            reason: "当前结果属于第一轮预审完成，不等于最终税务结论。",
          },
        ],
        fact_completion_status: {
          status_code: "completed_narrowed",
          status_label_zh: "已缩减",
          status_summary: "系统已根据用户声明事实将股息分支缩减为单一候选税率。",
        },
        change_summary: {
          summary_label: "Result Change Summary",
          state_change: "可补全 -> 预审完成",
          rate_change: "5% / 10% -> 5%",
          trigger_facts: [
            "Direct holding confirmed: yes",
            "Direct holding is at least 25%: yes",
          ],
        },
        fact_completion: null,
        user_declared_facts: {
          declaration_label: "User-declared facts (unverified)",
          facts: [
            {
              fact_key: "direct_holding_confirmed",
              value: "yes",
              label: "Direct holding confirmed",
            },
            {
              fact_key: "direct_holding_threshold_met",
              value: "yes",
              label: "Direct holding is at least 25%",
            },
          ],
        },
        normalized_input: {
          payer_country: "CN",
          payee_country: "NL",
          transaction_type: "dividends",
        },
        result: {
          summary:
            "Preliminary view: Article 10 Dividends appears relevant, with a treaty rate ceiling of 5%. Manual review is still recommended.",
          boundary_note:
            "This is a first-pass treaty pre-review based on limited scenario facts. Final eligibility still depends on additional facts, documents, and analysis outside the current review scope.",
          immediate_action:
            "Proceed with standard manual review before relying on the treaty position.",
          article_number: "10",
          article_title: "Dividends",
          source_reference: "Article 10(2)(a)",
          source_language: "en",
          source_excerpt:
            "However, such dividends may also be taxed in the State of source, but the tax so charged shall not exceed 5 per cent.",
          rate: "5%",
          extraction_confidence: 0.98,
          auto_conclusion_allowed: true,
          key_missing_facts: [
            "Whether the payment is legally a dividend rather than another type of return.",
            "Whether the recipient is the beneficial owner of the dividend income.",
            "Whether shareholding facts support relying on the treaty position.",
          ],
          review_checklist: [
            "Confirm the payment is legally characterized as a dividend rather than another return.",
            "Confirm the recipient is the beneficial owner of the dividend income.",
            "Check shareholding facts and supporting corporate records before relying on the treaty rate.",
          ],
          conditions: [
            "The beneficial owner is a company which holds directly at least 25 per cent of the capital of the company paying the dividends.",
          ],
          notes: [],
          human_review_required: true,
          review_priority: "normal",
          review_reason:
            "Final eligibility depends on facts outside the current review scope. The current branch view reflects unverified user-declared direct holding facts.",
        },
      }),
    }) as typeof fetch;

  render(<App />);

  await user.type(screen.getByLabelText(/cross-border scenario/i), "中国公司向荷兰公司支付股息");
  await user.click(screen.getByRole("button", { name: /run review/i }));

  await user.selectOptions(
    await screen.findByLabelText(/does the dutch recipient directly hold capital in the chinese payer/i),
    "yes",
  );
  await user.selectOptions(
    screen.getByLabelText(/if the holding is direct, is the direct holding at least 25%/i),
    "yes",
  );
  await user.selectOptions(
    screen.getByLabelText(/has beneficial-owner status been separately confirmed outside this tool/i),
    "yes",
  );
  expect(
    screen.getByLabelText(
      /is the dividend effectively connected with a permanent establishment or fixed base of the dutch recipient in china/i,
    ),
  ).toBeInTheDocument();
  expect(
    screen.getByLabelText(
      /is the holding structure confirmed to be direct with no intermediate holding entity between the recipient and the paying company/i,
    ),
  ).toBeInTheDocument();
  expect(
    screen.getByLabelText(
      /has a principal purpose test \(ppt\) risk assessment been performed for this dividend payment under the mli/i,
    ),
  ).toBeInTheDocument();
  await user.selectOptions(
    screen.getByLabelText(
      /is the holding structure confirmed to be direct with no intermediate holding entity between the recipient and the paying company/i,
    ),
    "yes",
  );
  await user.click(screen.getByRole("button", { name: /re-run with these facts/i }));

  expect(await screen.findByText(/user-declared facts \(unverified\)/i)).toBeInTheDocument();
  expect(screen.getByText("已缩减")).toBeInTheDocument();
  expect(screen.getByText(/将股息分支缩减为单一候选税率/i)).toBeInTheDocument();
  expect(screen.getByText(/result change summary/i)).toBeInTheDocument();
  expect(screen.getByText(/可补全 -> 预审完成/i)).toBeInTheDocument();
  expect(screen.getByText(/5% \/ 10% -> 5%/i)).toBeInTheDocument();
  expect(screen.getByText(/direct holding confirmed: yes/i)).toBeInTheDocument();
  expect(screen.getByText(/direct holding is at least 25%: yes/i)).toBeInTheDocument();
  expect(screen.getByText("5%")).toBeInTheDocument();
  expect(globalThis.fetch).toHaveBeenLastCalledWith(
    "/api/analyze",
    expect.objectContaining({
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        input_mode: "guided",
        guided_input: {
          payer_country: "CN",
          payee_country: "NL",
          income_type: "dividends",
          facts: {
            direct_holding_confirmed: "yes",
            direct_holding_threshold_met: "yes",
            beneficial_owner_confirmed: "yes",
            pe_effectively_connected: "unknown",
            holding_structure_is_direct: "yes",
            mli_ppt_risk_flag: "unknown",
          },
          scenario_text: "中国公司向荷兰公司支付股息",
        },
      }),
    }),
  );
});


test("shows a terminated exit when the user still cannot confirm the key branch fact", async () => {
  const user = userEvent.setup();

  globalThis.fetch = vi
    .fn()
    .mockResolvedValueOnce({
      ok: true,
      json: async () => ({
        supported: true,
        review_state: {
          state_code: "can_be_completed",
          state_label_zh: "可补全",
          state_summary: "系统已缩小范围；补充少量关键事实后，可进一步明确结果。",
        },
        confirmed_scope: {
          applicable_treaty: "中国-荷兰税收协定",
          applicable_article: "Article 10 - Dividends",
          payment_direction: "CN -> NL",
          income_type: "dividends",
        },
        next_actions: [
          {
            priority: "high",
            action: "先核实股息分支所需的关键事实，再判断候选税率分支。",
            reason: "当前存在多个可信税率分支，系统不会自动替你选择其一。",
          },
        ],
        fact_completion_status: {
          status_code: "awaiting_user_facts",
          status_label_zh: "待补事实",
          status_summary: "请先补充关键持股事实，系统才能继续缩小股息税率分支。",
        },
        fact_completion: {
          flow_type: "bounded_form",
          session_type: "pseudo_multiturn",
          user_declaration_note: "Facts entered here are user-declared and not independently verified.",
          facts: [
            {
              fact_key: "direct_holding_confirmed",
              prompt: "Does the Dutch recipient directly hold capital in the Chinese payer?",
              input_type: "single_select",
              options: ["yes", "no", "unknown"],
            },
            {
              fact_key: "direct_holding_threshold_met",
              prompt: "If the holding is direct, is the direct holding at least 25%?",
              input_type: "single_select",
              options: ["yes", "no", "unknown"],
            },
            {
              fact_key: "pe_effectively_connected",
              prompt: "Is the dividend effectively connected with a permanent establishment or fixed base of the Dutch recipient in China?",
              input_type: "single_select",
              options: ["yes", "no", "unknown"],
            },
            {
              fact_key: "beneficial_owner_confirmed",
              prompt: "Has beneficial-owner status been separately confirmed outside this tool?",
              input_type: "single_select",
              options: ["yes", "no", "unknown"],
            },
          ],
        },
        user_declared_facts: null,
        normalized_input: {
          payer_country: "CN",
          payee_country: "NL",
          transaction_type: "dividends",
        },
        result: {
          summary:
            "Preliminary view: Article 10 Dividends appears relevant, but multiple treaty rate branches (5% / 10%) are possible and this version should not issue an automatic conclusion.",
          boundary_note:
            "This is a first-pass treaty pre-review based on limited scenario facts. Final eligibility still depends on additional facts, documents, and analysis outside the current review scope.",
          immediate_action:
            "Do not rely on this result yet. Resolve the missing facts and supporting documents before any treaty conclusion.",
          article_number: "10",
          article_title: "Dividends",
          source_reference: "Article 10(2)(b)",
          source_language: "en",
          source_excerpt: "In all other cases, the tax charged in the State of source shall not exceed 10 per cent.",
          rate: "5% / 10%",
          extraction_confidence: 0.98,
          auto_conclusion_allowed: false,
          key_missing_facts: [
            "Whether the payment is legally a dividend rather than another type of return.",
            "Whether the recipient is the beneficial owner of the dividend income.",
            "Whether shareholding facts support relying on the treaty position.",
          ],
          review_checklist: [
            "Confirm the payment is legally characterized as a dividend rather than another return.",
            "Confirm the recipient is the beneficial owner of the dividend income.",
            "Check shareholding facts and supporting corporate records before relying on the treaty rate.",
          ],
          conditions: ["Applies when the reduced-rate branch is not established."],
          notes: [],
          human_review_required: true,
          review_priority: "high",
          review_reason:
            "Multiple treaty rate branches were found in this article, and the current scenario does not provide enough facts to choose one automatically.",
          alternative_rate_candidates: [
            {
              source_reference: "Article 10(2)(a)",
              rate: "5%",
              conditions: [
                "The beneficial owner is a company which holds directly at least 25 per cent of the capital of the company paying the dividends.",
              ],
            },
          ],
        },
      }),
    })
    .mockResolvedValueOnce({
      ok: true,
      json: async () => ({
        supported: true,
        review_state: {
          state_code: "needs_human_intervention",
          state_label_zh: "需要人工介入",
          state_summary: "当前结果已触发保守停止，应转入人工处理而不是继续自动推进。",
        },
        confirmed_scope: {
          applicable_treaty: "中国-荷兰税收协定",
          applicable_article: "Article 10 - Dividends",
          payment_direction: "CN -> NL",
          income_type: "dividends",
        },
        next_actions: [
          {
            priority: "high",
            action: "先在线下确认直接持股比例和持股方式，再重新发起预审或转交人工复核。",
            reason: "当前关键分支事实仍未确认，系统不会继续自动缩减股息税率分支。",
          },
        ],
        fact_completion_status: {
          status_code: "terminated_unknown_facts",
          status_label_zh: "停止自动缩减",
          status_summary: "关键事实仍未确认，系统结束当前补事实流程并建议先在线下核实。",
        },
        change_summary: {
          summary_label: "Result Change Summary",
          state_change: "可补全 -> 需要人工介入",
          rate_change: "5% / 10% -> 5% / 10%",
          trigger_facts: [
            "Direct holding confirmed: yes",
            "Direct holding is at least 25%: unknown",
          ],
        },
        fact_completion: null,
        user_declared_facts: {
          declaration_label: "User-declared facts (unverified)",
          facts: [
            {
              fact_key: "direct_holding_confirmed",
              value: "yes",
              label: "Direct holding confirmed",
            },
            {
              fact_key: "direct_holding_threshold_met",
              value: "unknown",
              label: "Direct holding is at least 25%",
            },
          ],
        },
        normalized_input: {
          payer_country: "CN",
          payee_country: "NL",
          transaction_type: "dividends",
        },
        result: {
          summary:
            "Preliminary view: Article 10 Dividends appears relevant, but multiple treaty rate branches (5% / 10%) are possible and this version should not issue an automatic conclusion.",
          boundary_note:
            "This is a first-pass treaty pre-review based on limited scenario facts. Final eligibility still depends on additional facts, documents, and analysis outside the current review scope.",
          immediate_action:
            "Do not rely on this result yet. Resolve the missing facts and supporting documents before any treaty conclusion.",
          article_number: "10",
          article_title: "Dividends",
          source_reference: "Article 10(2)(b)",
          source_language: "en",
          source_excerpt: "In all other cases, the tax charged in the State of source shall not exceed 10 per cent.",
          rate: "5% / 10%",
          extraction_confidence: 0.98,
          auto_conclusion_allowed: false,
          key_missing_facts: [
            "Whether the payment is legally a dividend rather than another type of return.",
            "Whether the recipient is the beneficial owner of the dividend income.",
            "Whether shareholding facts support relying on the treaty position.",
          ],
          review_checklist: [
            "Confirm the payment is legally characterized as a dividend rather than another return.",
            "Confirm the recipient is the beneficial owner of the dividend income.",
            "Check shareholding facts and supporting corporate records before relying on the treaty rate.",
          ],
          conditions: ["Applies when the reduced-rate branch is not established."],
          notes: [],
          human_review_required: true,
          review_priority: "high",
          review_reason:
            "Multiple treaty rate branches were found in this article, and the current scenario does not provide enough facts to choose one automatically.",
          alternative_rate_candidates: [
            {
              source_reference: "Article 10(2)(a)",
              rate: "5%",
              conditions: [
                "The beneficial owner is a company which holds directly at least 25 per cent of the capital of the company paying the dividends.",
              ],
            },
          ],
        },
      }),
    }) as typeof fetch;

  render(<App />);

  await user.type(screen.getByLabelText(/cross-border scenario/i), "中国公司向荷兰公司支付股息");
  await user.click(screen.getByRole("button", { name: /run review/i }));

  await user.selectOptions(
    await screen.findByLabelText(/does the dutch recipient directly hold capital in the chinese payer/i),
    "yes",
  );
  await user.selectOptions(
    screen.getByLabelText(/if the holding is direct, is the direct holding at least 25%/i),
    "unknown",
  );
  await user.click(screen.getByRole("button", { name: /re-run with these facts/i }));

  expect(await screen.findByText("停止自动缩减")).toBeInTheDocument();
  expect(screen.getByText(/关键事实仍未确认，系统结束当前补事实流程并建议先在线下核实/i)).toBeInTheDocument();
  expect(screen.getByText(/可补全 -> 需要人工介入/i)).toBeInTheDocument();
  expect(screen.getByText(/5% \/ 10% -> 5% \/ 10%/i)).toBeInTheDocument();
  expect(screen.getByText(/先在线下确认直接持股比例和持股方式/i)).toBeInTheDocument();
  expect(screen.queryByRole("button", { name: /re-run with these facts/i })).not.toBeInTheDocument();
});


test("shows a terminated PE-exclusion exit when the user flags effectively connected dividends", async () => {
  const user = userEvent.setup();

  globalThis.fetch = vi
    .fn()
    .mockResolvedValueOnce({
      ok: true,
      json: async () => ({
        supported: true,
        review_state: {
          state_code: "can_be_completed",
          state_label_zh: "可补全",
          state_summary: "系统已缩小范围；补充少量关键事实后，可进一步明确结果。",
        },
        confirmed_scope: {
          applicable_treaty: "中国-荷兰税收协定",
          applicable_article: "Article 10 - Dividends",
          payment_direction: "CN -> NL",
          income_type: "dividends",
        },
        next_actions: [
          {
            priority: "high",
            action: "先核实股息分支所需的关键事实，再判断候选税率分支。",
            reason: "当前存在多个可信税率分支，系统不会自动替你选择其一。",
          },
        ],
        fact_completion_status: {
          status_code: "awaiting_user_facts",
          status_label_zh: "待补事实",
          status_summary: "请先补充关键持股事实，系统才能继续缩小股息税率分支。",
        },
        fact_completion: {
          flow_type: "bounded_form",
          session_type: "pseudo_multiturn",
          user_declaration_note: "Facts entered here are user-declared and not independently verified.",
          facts: [
            {
              fact_key: "direct_holding_confirmed",
              prompt: "Does the Dutch recipient directly hold capital in the Chinese payer?",
              input_type: "single_select",
              options: ["yes", "no", "unknown"],
            },
            {
              fact_key: "direct_holding_threshold_met",
              prompt: "If the holding is direct, is the direct holding at least 25%?",
              input_type: "single_select",
              options: ["yes", "no", "unknown"],
            },
            {
              fact_key: "pe_effectively_connected",
              prompt: "Is the dividend effectively connected with a permanent establishment or fixed base of the Dutch recipient in China?",
              input_type: "single_select",
              options: ["yes", "no", "unknown"],
            },
            {
              fact_key: "beneficial_owner_confirmed",
              prompt: "Has beneficial-owner status been separately confirmed outside this tool?",
              input_type: "single_select",
              options: ["yes", "no", "unknown"],
            },
          ],
        },
        user_declared_facts: null,
        normalized_input: {
          payer_country: "CN",
          payee_country: "NL",
          transaction_type: "dividends",
        },
        result: {
          summary:
            "Preliminary view: Article 10 Dividends appears relevant, but multiple treaty rate branches (5% / 10%) are possible and this version should not issue an automatic conclusion.",
          boundary_note:
            "This is a first-pass treaty pre-review based on limited scenario facts. Final eligibility still depends on additional facts, documents, and analysis outside the current review scope.",
          immediate_action:
            "Do not rely on this result yet. Resolve the missing facts and supporting documents before any treaty conclusion.",
          article_number: "10",
          article_title: "Dividends",
          source_reference: "Article 10(2)(b)",
          source_language: "en",
          source_excerpt: "In all other cases, the tax charged in the State of source shall not exceed 10 per cent.",
          rate: "5% / 10%",
          extraction_confidence: 0.98,
          auto_conclusion_allowed: false,
          key_missing_facts: [
            "Whether the payment is legally a dividend rather than another type of return.",
            "Whether the recipient is the beneficial owner of the dividend income.",
            "Whether shareholding facts support relying on the treaty position.",
          ],
          review_checklist: [
            "Confirm the payment is legally characterized as a dividend rather than another return.",
            "Confirm the recipient is the beneficial owner of the dividend income.",
            "Check shareholding facts and supporting corporate records before relying on the treaty rate.",
          ],
          conditions: ["Applies when the reduced-rate branch is not established."],
          notes: [],
          human_review_required: true,
          review_priority: "high",
          review_reason:
            "Multiple treaty rate branches were found in this article, and the current scenario does not provide enough facts to choose one automatically.",
          alternative_rate_candidates: [
            {
              source_reference: "Article 10(2)(a)",
              rate: "5%",
              conditions: [
                "The beneficial owner is a company which holds directly at least 25 per cent of the capital of the company paying the dividends.",
              ],
            },
          ],
        },
      }),
    })
    .mockResolvedValueOnce({
      ok: true,
      json: async () => ({
        supported: true,
        review_state: {
          state_code: "needs_human_intervention",
          state_label_zh: "需要人工介入",
          state_summary: "当前结果已触发保守停止，应转入人工处理而不是继续自动推进。",
        },
        confirmed_scope: {
          applicable_treaty: "中国-荷兰税收协定",
          applicable_article: "Article 10 - Dividends",
          payment_direction: "CN -> NL",
          income_type: "dividends",
        },
        next_actions: [
          {
            priority: "high",
            action: "停止依赖当前股息分支自动缩减，并确认荷兰收款方是否在中国存在与该股息实际联系的常设机构或固定基地。",
            reason: "如果该排除情形成立，当前场景可能需要转入其他条款并进行人工复核，而不是继续沿用 Article 10 分支结果。",
          },
        ],
        fact_completion_status: {
          status_code: "terminated_pe_exclusion",
          status_label_zh: "转入排除情形复核",
          status_summary: "当前场景触发了与中国常设机构或固定基地实际联系的排除提醒，系统结束 Article 10 分支自动缩减。",
        },
        change_summary: {
          summary_label: "Result Change Summary",
          state_change: "可补全 -> 需要人工介入",
          rate_change: "5% / 10% -> Article 10 branch excluded",
          trigger_facts: [
            "Dividend effectively connected with a China PE / fixed base: yes",
          ],
        },
        fact_completion: null,
        user_declared_facts: {
          declaration_label: "User-declared facts (unverified)",
          facts: [
            {
              fact_key: "pe_effectively_connected",
              value: "yes",
              label: "Dividend effectively connected with a China PE / fixed base",
            },
          ],
        },
        normalized_input: {
          payer_country: "CN",
          payee_country: "NL",
          transaction_type: "dividends",
        },
        result: {
          summary:
            "Preliminary view: Article 10 Dividends appears relevant, but multiple treaty rate branches (5% / 10%) are possible and this version should not issue an automatic conclusion.",
          boundary_note:
            "This is a first-pass treaty pre-review based on limited scenario facts. Final eligibility still depends on additional facts, documents, and analysis outside the current review scope.",
          immediate_action:
            "Do not rely on this result yet. Resolve the missing facts and supporting documents before any treaty conclusion.",
          article_number: "10",
          article_title: "Dividends",
          source_reference: "Article 10(2)(b)",
          source_language: "en",
          source_excerpt: "In all other cases, the tax charged in the State of source shall not exceed 10 per cent.",
          rate: "5% / 10%",
          extraction_confidence: 0.98,
          auto_conclusion_allowed: false,
          key_missing_facts: [
            "Whether the payment is legally a dividend rather than another type of return.",
            "Whether the recipient is the beneficial owner of the dividend income.",
            "Whether shareholding facts support relying on the treaty position.",
          ],
          review_checklist: [
            "Confirm the payment is legally characterized as a dividend rather than another return.",
            "Confirm the recipient is the beneficial owner of the dividend income.",
            "Check shareholding facts and supporting corporate records before relying on the treaty rate.",
          ],
          conditions: ["Applies when the reduced-rate branch is not established."],
          notes: [],
          human_review_required: true,
          review_priority: "high",
          review_reason:
            "Multiple treaty rate branches were found in this article, and the current scenario does not provide enough facts to choose one automatically.",
          alternative_rate_candidates: [
            {
              source_reference: "Article 10(2)(a)",
              rate: "5%",
              conditions: [
                "The beneficial owner is a company which holds directly at least 25 per cent of the capital of the company paying the dividends.",
              ],
            },
          ],
        },
      }),
    }) as typeof fetch;

  render(<App />);

  await user.type(screen.getByLabelText(/cross-border scenario/i), "中国公司向荷兰公司支付股息");
  await user.click(screen.getByRole("button", { name: /run review/i }));

  await user.selectOptions(
    await screen.findByLabelText(
      /is the dividend effectively connected with a permanent establishment or fixed base of the dutch recipient in china/i,
    ),
    "yes",
  );
  await user.click(screen.getByRole("button", { name: /re-run with these facts/i }));

  expect(await screen.findByText("转入排除情形复核")).toBeInTheDocument();
  expect(screen.getByText(/当前场景触发了与中国常设机构或固定基地实际联系的排除提醒/i)).toBeInTheDocument();
  expect(screen.getByText(/article 10 branch excluded/i)).toBeInTheDocument();
  expect(screen.getByText(/确认荷兰收款方是否在中国存在与该股息实际联系的常设机构或固定基地/i)).toBeInTheDocument();
  expect(screen.queryByRole("button", { name: /re-run with these facts/i })).not.toBeInTheDocument();
  expect(globalThis.fetch).toHaveBeenLastCalledWith(
    "/api/analyze",
    expect.objectContaining({
      body: JSON.stringify({
        input_mode: "guided",
        guided_input: {
          payer_country: "CN",
          payee_country: "NL",
          income_type: "dividends",
          facts: {
            direct_holding_confirmed: "unknown",
            direct_holding_threshold_met: "unknown",
            pe_effectively_connected: "yes",
            beneficial_owner_confirmed: "unknown",
          },
          scenario_text: "中国公司向荷兰公司支付股息",
        },
      }),
    }),
  );
});


test("shows a beneficial-owner termination exit when the prerequisite has not been separately confirmed", async () => {
  const user = userEvent.setup();

  globalThis.fetch = vi
    .fn()
    .mockResolvedValueOnce({
      ok: true,
      json: async () => ({
        supported: true,
        review_state: {
          state_code: "can_be_completed",
          state_label_zh: "可补全",
          state_summary: "系统已缩小范围；补充少量关键事实后，可进一步明确结果。",
        },
        confirmed_scope: {
          applicable_treaty: "中国-荷兰税收协定",
          applicable_article: "Article 10 - Dividends",
          payment_direction: "CN -> NL",
          income_type: "dividends",
        },
        next_actions: [
          {
            priority: "high",
            action: "先核实股息分支所需的关键事实，再判断候选税率分支。",
            reason: "当前存在多个可信税率分支，系统不会自动替你选择其一。",
          },
        ],
        fact_completion_status: {
          status_code: "awaiting_user_facts",
          status_label_zh: "待补事实",
          status_summary: "请先补充关键持股事实，系统才能继续缩小股息税率分支。",
        },
        fact_completion: {
          flow_type: "bounded_form",
          session_type: "pseudo_multiturn",
          user_declaration_note: "Facts entered here are user-declared and not independently verified.",
          facts: [
            {
              fact_key: "direct_holding_confirmed",
              prompt: "Does the Dutch recipient directly hold capital in the Chinese payer?",
              input_type: "single_select",
              options: ["yes", "no", "unknown"],
            },
            {
              fact_key: "direct_holding_threshold_met",
              prompt: "If the holding is direct, is the direct holding at least 25%?",
              input_type: "single_select",
              options: ["yes", "no", "unknown"],
            },
            {
              fact_key: "pe_effectively_connected",
              prompt: "Is the dividend effectively connected with a permanent establishment or fixed base of the Dutch recipient in China?",
              input_type: "single_select",
              options: ["yes", "no", "unknown"],
            },
            {
              fact_key: "beneficial_owner_confirmed",
              prompt: "Has beneficial-owner status been separately confirmed outside this tool?",
              input_type: "single_select",
              options: ["yes", "no", "unknown"],
            },
          ],
        },
        user_declared_facts: null,
        normalized_input: {
          payer_country: "CN",
          payee_country: "NL",
          transaction_type: "dividends",
        },
        result: {
          summary:
            "Preliminary view: Article 10 Dividends appears relevant, but multiple treaty rate branches (5% / 10%) are possible and this version should not issue an automatic conclusion.",
          boundary_note:
            "This is a first-pass treaty pre-review based on limited scenario facts. Final eligibility still depends on additional facts, documents, and analysis outside the current review scope.",
          immediate_action:
            "Do not rely on this result yet. Resolve the missing facts and supporting documents before any treaty conclusion.",
          article_number: "10",
          article_title: "Dividends",
          source_reference: "Article 10(2)(b)",
          source_language: "en",
          source_excerpt: "In all other cases, the tax charged in the State of source shall not exceed 10 per cent.",
          rate: "5% / 10%",
          extraction_confidence: 0.98,
          auto_conclusion_allowed: false,
          key_missing_facts: [
            "Whether the payment is legally a dividend rather than another type of return.",
            "Whether the recipient is the beneficial owner of the dividend income.",
            "Whether shareholding facts support relying on the treaty position.",
          ],
          review_checklist: [
            "Confirm the payment is legally characterized as a dividend rather than another return.",
            "Confirm the recipient is the beneficial owner of the dividend income.",
            "Check shareholding facts and supporting corporate records before relying on the treaty rate.",
          ],
          conditions: ["Applies when the reduced-rate branch is not established."],
          notes: [],
          human_review_required: true,
          review_priority: "high",
          review_reason:
            "Multiple treaty rate branches were found in this article, and the current scenario does not provide enough facts to choose one automatically.",
          alternative_rate_candidates: [
            {
              source_reference: "Article 10(2)(a)",
              rate: "5%",
              conditions: [
                "The beneficial owner is a company which holds directly at least 25 per cent of the capital of the company paying the dividends.",
              ],
            },
          ],
        },
      }),
    })
    .mockResolvedValueOnce({
      ok: true,
      json: async () => ({
        supported: true,
        review_state: {
          state_code: "needs_human_intervention",
          state_label_zh: "需要人工介入",
          state_summary: "当前结果已触发保守停止，应转入人工处理而不是继续自动推进。",
        },
        confirmed_scope: {
          applicable_treaty: "中国-荷兰税收协定",
          applicable_article: "Article 10 - Dividends",
          payment_direction: "CN -> NL",
          income_type: "dividends",
        },
        next_actions: [
          {
            priority: "high",
            action: "先单独确认受益所有人身份及其支持材料，在未确认前不要依赖当前协定优惠税率分支。",
            reason: "受益所有人是协定优惠适用的前提条件；系统不会仅凭当前输入替你判断这一点是否成立。",
          },
        ],
        fact_completion_status: {
          status_code: "terminated_beneficial_owner_unconfirmed",
          status_label_zh: "受益所有人前提未确认",
          status_summary: "协定优惠前提中的受益所有人身份尚未被单独确认，系统结束当前股息分支自动缩减。",
        },
        change_summary: {
          summary_label: "Result Change Summary",
          state_change: "可补全 -> 需要人工介入",
          rate_change: "5% -> treaty rate cannot be relied on yet",
          trigger_facts: [
            "Direct holding confirmed: yes",
            "Direct holding is at least 25%: yes",
            "Beneficial owner status separately confirmed: no",
          ],
        },
        fact_completion: null,
        user_declared_facts: {
          declaration_label: "User-declared facts (unverified)",
          facts: [
            {
              fact_key: "direct_holding_confirmed",
              value: "yes",
              label: "Direct holding confirmed",
            },
            {
              fact_key: "direct_holding_threshold_met",
              value: "yes",
              label: "Direct holding is at least 25%",
            },
            {
              fact_key: "beneficial_owner_confirmed",
              value: "no",
              label: "Beneficial owner status separately confirmed",
            },
          ],
        },
        normalized_input: {
          payer_country: "CN",
          payee_country: "NL",
          transaction_type: "dividends",
        },
        result: {
          summary:
            "Preliminary view: Article 10 Dividends appears relevant, but multiple treaty rate branches (5% / 10%) are possible and this version should not issue an automatic conclusion.",
          boundary_note:
            "This is a first-pass treaty pre-review based on limited scenario facts. Final eligibility still depends on additional facts, documents, and analysis outside the current review scope.",
          immediate_action:
            "Do not rely on this result yet. Resolve the missing facts and supporting documents before any treaty conclusion.",
          article_number: "10",
          article_title: "Dividends",
          source_reference: "Article 10(2)(b)",
          source_language: "en",
          source_excerpt: "In all other cases, the tax charged in the State of source shall not exceed 10 per cent.",
          rate: "5% / 10%",
          extraction_confidence: 0.98,
          auto_conclusion_allowed: false,
          key_missing_facts: [
            "Whether the payment is legally a dividend rather than another type of return.",
            "Whether the recipient is the beneficial owner of the dividend income.",
            "Whether shareholding facts support relying on the treaty position.",
          ],
          review_checklist: [
            "Confirm the payment is legally characterized as a dividend rather than another return.",
            "Confirm the recipient is the beneficial owner of the dividend income.",
            "Check shareholding facts and supporting corporate records before relying on the treaty rate.",
          ],
          conditions: ["Applies when the reduced-rate branch is not established."],
          notes: [],
          human_review_required: true,
          review_priority: "high",
          review_reason:
            "Multiple treaty rate branches were found in this article, and the current scenario does not provide enough facts to choose one automatically.",
          alternative_rate_candidates: [
            {
              source_reference: "Article 10(2)(a)",
              rate: "5%",
              conditions: [
                "The beneficial owner is a company which holds directly at least 25 per cent of the capital of the company paying the dividends.",
              ],
            },
          ],
        },
      }),
    }) as typeof fetch;

  render(<App />);

  await user.type(screen.getByLabelText(/cross-border scenario/i), "中国公司向荷兰公司支付股息");
  await user.click(screen.getByRole("button", { name: /run review/i }));

  await user.selectOptions(
    await screen.findByLabelText(/does the dutch recipient directly hold capital in the chinese payer/i),
    "yes",
  );
  await user.selectOptions(
    screen.getByLabelText(/if the holding is direct, is the direct holding at least 25%/i),
    "yes",
  );
  await user.selectOptions(
    screen.getByLabelText(/has beneficial-owner status been separately confirmed outside this tool/i),
    "no",
  );
  await user.click(screen.getByRole("button", { name: /re-run with these facts/i }));

  expect(await screen.findByText("受益所有人前提未确认")).toBeInTheDocument();
  expect(screen.getByText(/协定优惠前提中的受益所有人身份尚未被单独确认/i)).toBeInTheDocument();
  expect(screen.getByText(/5% -> treaty rate cannot be relied on yet/i)).toBeInTheDocument();
  expect(screen.getByText(/先单独确认受益所有人身份及其支持材料/i)).toBeInTheDocument();
  expect(screen.queryByRole("button", { name: /re-run with these facts/i })).not.toBeInTheDocument();
});


test("shows a conflicting-facts termination exit when user-declared answers contradict each other", async () => {
  const user = userEvent.setup();

  globalThis.fetch = vi
    .fn()
    .mockResolvedValueOnce({
      ok: true,
      json: async () => ({
        supported: true,
        review_state: {
          state_code: "can_be_completed",
          state_label_zh: "可补全",
          state_summary: "系统已缩小范围；补充少量关键事实后，可进一步明确结果。",
        },
        confirmed_scope: {
          applicable_treaty: "中国-荷兰税收协定",
          applicable_article: "Article 10 - Dividends",
          payment_direction: "CN -> NL",
          income_type: "dividends",
        },
        next_actions: [
          {
            priority: "high",
            action: "先核实股息分支所需的关键事实，再判断候选税率分支。",
            reason: "当前存在多个可信税率分支，系统不会自动替你选择其一。",
          },
        ],
        fact_completion_status: {
          status_code: "awaiting_user_facts",
          status_label_zh: "待补事实",
          status_summary: "请先补充关键持股事实，系统才能继续缩小股息税率分支。",
        },
        fact_completion: {
          flow_type: "bounded_form",
          session_type: "pseudo_multiturn",
          user_declaration_note: "Facts entered here are user-declared and not independently verified.",
          facts: [
            {
              fact_key: "direct_holding_confirmed",
              prompt: "Does the Dutch recipient directly hold capital in the Chinese payer?",
              input_type: "single_select",
              options: ["yes", "no", "unknown"],
            },
            {
              fact_key: "direct_holding_threshold_met",
              prompt: "If the holding is direct, is the direct holding at least 25%?",
              input_type: "single_select",
              options: ["yes", "no", "unknown"],
            },
            {
              fact_key: "pe_effectively_connected",
              prompt: "Is the dividend effectively connected with a permanent establishment or fixed base of the Dutch recipient in China?",
              input_type: "single_select",
              options: ["yes", "no", "unknown"],
            },
            {
              fact_key: "beneficial_owner_confirmed",
              prompt: "Has beneficial-owner status been separately confirmed outside this tool?",
              input_type: "single_select",
              options: ["yes", "no", "unknown"],
            },
          ],
        },
        user_declared_facts: null,
        normalized_input: {
          payer_country: "CN",
          payee_country: "NL",
          transaction_type: "dividends",
        },
        result: {
          summary:
            "Preliminary view: Article 10 Dividends appears relevant, but multiple treaty rate branches (5% / 10%) are possible and this version should not issue an automatic conclusion.",
          boundary_note:
            "This is a first-pass treaty pre-review based on limited scenario facts. Final eligibility still depends on additional facts, documents, and analysis outside the current review scope.",
          immediate_action:
            "Do not rely on this result yet. Resolve the missing facts and supporting documents before any treaty conclusion.",
          article_number: "10",
          article_title: "Dividends",
          source_reference: "Article 10(2)(b)",
          source_language: "en",
          source_excerpt: "In all other cases, the tax charged in the State of source shall not exceed 10 per cent.",
          rate: "5% / 10%",
          extraction_confidence: 0.98,
          auto_conclusion_allowed: false,
          key_missing_facts: [
            "Whether the payment is legally a dividend rather than another type of return.",
            "Whether the recipient is the beneficial owner of the dividend income.",
            "Whether shareholding facts support relying on the treaty position.",
          ],
          review_checklist: [
            "Confirm the payment is legally characterized as a dividend rather than another return.",
            "Confirm the recipient is the beneficial owner of the dividend income.",
            "Check shareholding facts and supporting corporate records before relying on the treaty rate.",
          ],
          conditions: ["Applies when the reduced-rate branch is not established."],
          notes: [],
          human_review_required: true,
          review_priority: "high",
          review_reason:
            "Multiple treaty rate branches were found in this article, and the current scenario does not provide enough facts to choose one automatically.",
          alternative_rate_candidates: [
            {
              source_reference: "Article 10(2)(a)",
              rate: "5%",
              conditions: [
                "The beneficial owner is a company which holds directly at least 25 per cent of the capital of the company paying the dividends.",
              ],
            },
          ],
        },
      }),
    })
    .mockResolvedValueOnce({
      ok: true,
      json: async () => ({
        supported: true,
        review_state: {
          state_code: "needs_human_intervention",
          state_label_zh: "需要人工介入",
          state_summary: "当前结果已触发保守停止，应转入人工处理而不是继续自动推进。",
        },
        confirmed_scope: {
          applicable_treaty: "中国-荷兰税收协定",
          applicable_article: "Article 10 - Dividends",
          payment_direction: "CN -> NL",
          income_type: "dividends",
        },
        next_actions: [
          {
            priority: "high",
            action: "先核对直接持股方式和持股比例的真实情况；当前答案彼此冲突，系统不会继续自动缩减股息税率分支。",
            reason: "例如，在未直接持股的情况下不能同时把直接持股门槛判断为已满足；请先在线下核实后再重新预审。",
          },
        ],
        fact_completion_status: {
          status_code: "terminated_conflicting_user_facts",
          status_label_zh: "用户声明事实冲突",
          status_summary: "已提交的补事实答案彼此冲突，系统结束当前股息分支自动缩减。",
        },
        change_summary: {
          summary_label: "Result Change Summary",
          state_change: "可补全 -> 需要人工介入",
          rate_change: "5% / 10% -> treaty rate cannot be narrowed due to conflicting facts",
          trigger_facts: [
            "Direct holding confirmed: no",
            "Direct holding is at least 25%: yes",
          ],
        },
        fact_completion: null,
        user_declared_facts: {
          declaration_label: "User-declared facts (unverified)",
          facts: [
            {
              fact_key: "direct_holding_confirmed",
              value: "no",
              label: "Direct holding confirmed",
            },
            {
              fact_key: "direct_holding_threshold_met",
              value: "yes",
              label: "Direct holding is at least 25%",
            },
          ],
        },
        normalized_input: {
          payer_country: "CN",
          payee_country: "NL",
          transaction_type: "dividends",
        },
        result: {
          summary:
            "Preliminary view: Article 10 Dividends appears relevant, but multiple treaty rate branches (5% / 10%) are possible and this version should not issue an automatic conclusion.",
          boundary_note:
            "This is a first-pass treaty pre-review based on limited scenario facts. Final eligibility still depends on additional facts, documents, and analysis outside the current review scope.",
          immediate_action:
            "Do not rely on this result yet. Resolve the missing facts and supporting documents before any treaty conclusion.",
          article_number: "10",
          article_title: "Dividends",
          source_reference: "Article 10(2)(b)",
          source_language: "en",
          source_excerpt: "In all other cases, the tax charged in the State of source shall not exceed 10 per cent.",
          rate: "5% / 10%",
          extraction_confidence: 0.98,
          auto_conclusion_allowed: false,
          key_missing_facts: [
            "Whether the payment is legally a dividend rather than another type of return.",
            "Whether the recipient is the beneficial owner of the dividend income.",
            "Whether shareholding facts support relying on the treaty position.",
          ],
          review_checklist: [
            "Confirm the payment is legally characterized as a dividend rather than another return.",
            "Confirm the recipient is the beneficial owner of the dividend income.",
            "Check shareholding facts and supporting corporate records before relying on the treaty rate.",
          ],
          conditions: ["Applies when the reduced-rate branch is not established."],
          notes: [],
          human_review_required: true,
          review_priority: "high",
          review_reason:
            "Multiple treaty rate branches were found in this article, and the current scenario does not provide enough facts to choose one automatically.",
          alternative_rate_candidates: [
            {
              source_reference: "Article 10(2)(a)",
              rate: "5%",
              conditions: [
                "The beneficial owner is a company which holds directly at least 25 per cent of the capital of the company paying the dividends.",
              ],
            },
          ],
        },
      }),
    }) as typeof fetch;

  render(<App />);

  await user.type(screen.getByLabelText(/cross-border scenario/i), "中国公司向荷兰公司支付股息");
  await user.click(screen.getByRole("button", { name: /run review/i }));

  await user.selectOptions(
    await screen.findByLabelText(/does the dutch recipient directly hold capital in the chinese payer/i),
    "no",
  );
  await user.selectOptions(
    screen.getByLabelText(/if the holding is direct, is the direct holding at least 25%/i),
    "yes",
  );
  await user.click(screen.getByRole("button", { name: /re-run with these facts/i }));

  expect(await screen.findByText("用户声明事实冲突")).toBeInTheDocument();
  expect(screen.getByText(/已提交的补事实答案彼此冲突/i)).toBeInTheDocument();
  expect(screen.getByText(/treaty rate cannot be narrowed due to conflicting facts/i)).toBeInTheDocument();
  expect(screen.getByText(/先核对直接持股方式和持股比例的真实情况/i)).toBeInTheDocument();
  expect(screen.queryByRole("button", { name: /re-run with these facts/i })).not.toBeInTheDocument();
  expect(globalThis.fetch).toHaveBeenLastCalledWith(
    "/api/analyze",
    expect.objectContaining({
      body: JSON.stringify({
        input_mode: "guided",
        guided_input: {
          payer_country: "CN",
          payee_country: "NL",
          income_type: "dividends",
          facts: {
            direct_holding_confirmed: "no",
            direct_holding_threshold_met: "yes",
            pe_effectively_connected: "unknown",
            beneficial_owner_confirmed: "unknown",
          },
          scenario_text: "中国公司向荷兰公司支付股息",
        },
      }),
    }),
  );
});


test("shows a bridge note when business wording is normalized into a treaty category", async () => {
  const user = userEvent.setup();

  globalThis.fetch = vi.fn().mockResolvedValue({
    ok: true,
    json: async () => ({
      supported: false,
      reason: "incomplete_scenario",
      message: "Please provide a clearer scenario with both payer and payee country context.",
      immediate_action: "Add the missing scenario facts before running the treaty review again.",
      missing_fields: ["payer_country"],
      classification_note:
        "Current review maps `软件许可费` into the royalties lane for first-pass treaty review. Use a fuller scenario so the tool can test the treaty position under the standard treaty royalties framework.",
      suggested_format: "Try a sentence like: 中国居民企业向荷兰公司支付特许权使用费",
      suggested_examples: [
        "中国居民企业向荷兰公司支付股息",
        "荷兰公司向中国公司支付利息",
      ],
    }),
  }) as typeof fetch;

  render(<App />);

  await user.type(screen.getByLabelText(/cross-border scenario/i), "向荷兰公司支付软件许可费");
  await user.click(screen.getByRole("button", { name: /run review/i }));

  expect(await screen.findByText(/review unavailable/i)).toBeInTheDocument();
  expect(screen.getByText(/classification note/i)).toBeInTheDocument();
  expect(screen.getByText(/maps `软件许可费` into the royalties lane/i)).toBeInTheDocument();
  expect(screen.getByText(/中国居民企业向荷兰公司支付特许权使用费/)).toBeInTheDocument();
});


test("shows explicit out-of-scope state when the scenario is outside the treaty boundary", async () => {
  const user = userEvent.setup();

  globalThis.fetch = vi.fn().mockResolvedValue({
    ok: true,
    json: async () => ({
      supported: false,
      review_state: {
        state_code: "out_of_scope",
        state_label_zh: "不在支持范围",
        state_summary: "当前查询超出本产品的国家对或收入类型支持范围。",
      },
      next_actions: [
        {
          priority: "high",
          action: "改写为中国-荷兰且属于股息、利息或特许权使用费的查询后再重试。",
          reason: "当前场景属于产品边界之外，系统不会返回实质性协定结论。",
        },
      ],
      handoff_package: {
        machine_handoff: {
          schema_version: "stage5.v1",
          record_kind: "unsupported",
          review_state_code: "out_of_scope",
          recommended_route: "out_of_scope_rewrite",
          applicable_treaty: null,
          payment_direction: null,
          income_type: null,
          article_number: null,
          article_title: null,
          rate_display: null,
          auto_conclusion_allowed: false,
          human_review_required: true,
          data_source_used: "stable",
          source_reference: null,
          review_priority: "high",
          blocking_facts: [],
          next_actions: [
            {
              priority: "high",
              action: "改写为中国-荷兰且属于股息、利息或特许权使用费的查询后再重试。",
              reason: "当前场景属于产品边界之外，系统不会返回实质性协定结论。",
            },
          ],
          user_declared_facts: [],
        },
        human_review_brief: {
          brief_title: "Treaty Pre-Review Brief",
          headline: "This scenario is outside the current pilot treaty scope.",
          disposition: "Rewrite the scenario inside the supported pilot scope.",
          summary_lines: ["No treaty article will be returned for this scenario."],
          facts_to_verify: [],
          handoff_note: "This is a bounded pre-review output, not a final tax opinion.",
        },
      },
      reason: "unsupported_country_pair",
      message: "Current MVP supports only China-Netherlands treaty scenarios.",
      immediate_action: "Rewrite the scenario into the supported China-Netherlands scope before running another review.",
      missing_fields: [],
      suggested_format: "Try a sentence like: 中国居民企业向荷兰公司支付特许权使用费",
      suggested_examples: [
        "中国居民企业向荷兰公司支付股息",
        "中国居民企业向荷兰银行支付利息",
        "中国居民企业向荷兰公司支付特许权使用费",
      ],
    }),
  }) as typeof fetch;

  render(<App />);

  await user.type(screen.getByLabelText(/cross-border scenario/i), "中国居民企业向美国支付特许权使用费");
  await user.click(screen.getByRole("button", { name: /run review/i }));

  expect(await screen.findByText("不在支持范围")).toBeInTheDocument();
  expect(screen.getByText("当前查询超出本产品的国家对或收入类型支持范围。")).toBeInTheDocument();
  expect(screen.getByText(/改写为中国-荷兰且属于股息、利息或特许权使用费的查询后再重试/i)).toBeInTheDocument();
  expect(screen.getByText(/current mvp supports only china-netherlands treaty scenarios/i)).toBeInTheDocument();
  expect(screen.getByText(/workflow handoff/i)).toBeInTheDocument();
  expect(screen.getByText(/rewrite the scenario inside the supported pilot scope/i)).toBeInTheDocument();
});


test("keeps workflow handoff visible alongside stage-4 fact completion controls", async () => {
  const user = userEvent.setup();

  globalThis.fetch = vi.fn().mockResolvedValue({
    ok: true,
    json: async () => ({
      supported: true,
      review_state: {
        state_code: "can_be_completed",
        state_label_zh: "可补全",
        state_summary: "系统已缩小范围；补充少量关键事实后，可进一步明确结果。",
      },
      confirmed_scope: {
        applicable_treaty: "中国-荷兰税收协定",
        applicable_article: "Article 10 - Dividends",
        payment_direction: "CN -> NL",
        income_type: "dividends",
      },
      next_actions: [
        {
          priority: "high",
          action: "先核实股息分支所需的关键事实，再判断候选税率分支。",
          reason: "当前存在多个可信税率分支，系统不会自动替你选择其一。",
        },
      ],
      handoff_package: {
        machine_handoff: {
          schema_version: "slice1.v1",
          record_kind: "supported",
          review_state_code: "can_be_completed",
          recommended_route: "complete_facts_then_rerun",
          applicable_treaty: "中国-荷兰税收协定",
          payment_direction: "CN -> NL",
          income_type: "dividends",
          article_number: "10",
          article_title: "Dividends",
          rate_display: "5% / 10%",
          auto_conclusion_allowed: false,
          human_review_required: true,
          data_source_used: "stable",
          source_reference: "Article 10(2)(b)",
          review_priority: "high",
          determining_condition_priority: null,
          mli_ppt_review_required: true,
          blocking_facts: [
            "Whether shareholding facts support relying on the treaty position.",
          ],
          next_actions: [
            {
              priority: "high",
              action: "先核实股息分支所需的关键事实，再判断候选税率分支。",
              reason: "当前存在多个可信税率分支，系统不会自动替你选择其一。",
            },
          ],
          user_declared_facts: [],
        },
        human_review_brief: {
          brief_title: "Treaty Pre-Review Brief",
          headline: "The current dividend result still needs one more fact-completion pass.",
          disposition: "Complete the missing facts and rerun the pre-review.",
          summary_lines: ["Multiple dividend branches remain plausible under Article 10."],
          facts_to_verify: ["Confirm direct holding facts before narrowing the rate branch."],
          handoff_note: "This is a bounded pre-review output, not a final tax opinion.",
        },
      },
      fact_completion_status: {
        status_code: "awaiting_user_facts",
        status_label_zh: "待补事实",
        status_summary: "请先补充关键持股事实，系统才能继续缩小股息税率分支。",
      },
      fact_completion: {
        flow_type: "bounded_form",
        session_type: "pseudo_multiturn",
        user_declaration_note: "Facts entered here are user-declared and not independently verified.",
        facts: [
          {
            fact_key: "direct_holding_confirmed",
            prompt: "Does the Dutch recipient directly hold capital in the Chinese payer?",
            input_type: "single_select",
            options: ["yes", "no", "unknown"],
          },
        ],
      },
      user_declared_facts: null,
      normalized_input: {
        payer_country: "CN",
        payee_country: "NL",
        transaction_type: "dividends",
      },
      result: {
        summary:
          "Preliminary view: Article 10 Dividends appears relevant, but multiple treaty rate branches (5% / 10%) are possible and this version should not issue an automatic conclusion.",
        boundary_note:
          "This is a first-pass treaty pre-review based on limited scenario facts. Final eligibility still depends on additional facts, documents, and analysis outside the current review scope.",
        immediate_action:
          "Do not rely on this result yet. Resolve the missing facts and supporting documents before any treaty conclusion.",
        article_number: "10",
        article_title: "Dividends",
        source_reference: "Article 10(2)(b)",
        source_language: "en",
        source_excerpt: "In all other cases, the tax charged in the State of source shall not exceed 10 per cent.",
        rate: "5% / 10%",
        extraction_confidence: 0.98,
        auto_conclusion_allowed: false,
        key_missing_facts: [
          "Whether shareholding facts support relying on the treaty position.",
        ],
        review_checklist: [
          "Check shareholding facts and supporting corporate records before relying on the treaty rate.",
        ],
        conditions: ["Applies when the reduced-rate branch is not established."],
        notes: [],
        human_review_required: true,
        review_priority: "high",
        review_reason:
          "Multiple treaty rate branches were found in this article, and the current scenario does not provide enough facts to choose one automatically.",
        alternative_rate_candidates: [
          {
            source_reference: "Article 10(2)(a)",
            rate: "5%",
            conditions: [
              "The beneficial owner is a company which holds directly at least 25 per cent of the capital of the company paying the dividends.",
            ],
          },
        ],
      },
    }),
  }) as typeof fetch;

  render(<App />);

  await user.type(screen.getByLabelText(/cross-border scenario/i), "中国公司向荷兰公司支付股息");
  await user.click(screen.getByRole("button", { name: /run review/i }));

  expect(await screen.findByText(/complete missing facts/i)).toBeInTheDocument();
  expect(screen.getByText(/workflow handoff/i)).toBeInTheDocument();
  expect(screen.getByText(/complete the missing facts and rerun the pre-review/i)).toBeInTheDocument();
  expect(screen.getByText(/determining condition priority: n\/a/i)).toBeInTheDocument();
  expect(screen.getByText(/mli ppt review required: yes/i)).toBeInTheDocument();
});


test("submits a guided royalties review from the wizard-first workspace", async () => {
  const user = userEvent.setup();

  globalThis.fetch = vi.fn().mockResolvedValue({
    ok: true,
    json: async () => ({
      schema_version: "slice1.v1",
      input_mode_used: "guided",
      supported: true,
      review_state: {
        state_code: "pre_review_complete",
        state_label_zh: "预审完成",
        state_summary: "系统已完成第一轮预审，请按标准复核流程继续。",
      },
      bo_precheck: {
        status: "no_initial_flag",
        reason_code: "beneficial_owner_confirmed",
        reason_summary:
          "The guided beneficial-owner fact is marked confirmed, so the system does not raise an initial BO workflow flag.",
        facts_considered: [
          {
            fact_key: "beneficial_owner_status",
            value: "yes",
          },
        ],
        review_note: "Beneficial-owner status still requires human verification outside this tool.",
      },
      normalized_input: {
        payer_country: "CN",
        payee_country: "NL",
        transaction_type: "royalties",
      },
      result: {
        summary:
          "Preliminary view: Article 12 Royalties appears relevant, with a treaty rate ceiling of 10%. Manual review is still recommended.",
        boundary_note:
          "This is a first-pass treaty pre-review based on limited scenario facts. Final eligibility still depends on additional facts, documents, and analysis outside the current review scope.",
        immediate_action:
          "Proceed with standard manual review before relying on the treaty position.",
        article_number: "12",
        article_title: "Royalties",
        source_reference: "Article 12(2)",
        source_language: "en",
        source_excerpt: "Treaty excerpt.",
        rate: "10%",
        extraction_confidence: 0.98,
        auto_conclusion_allowed: true,
        key_missing_facts: [],
        review_checklist: [],
        conditions: ["Treaty applicability depends on the facts of the payment."],
        notes: [],
        human_review_required: true,
        review_priority: "normal",
        review_reason: "Final eligibility depends on facts outside the current review scope.",
      },
      handoff_package: {
        machine_handoff: {
          schema_version: "slice1.v1",
          record_kind: "supported",
          review_state_code: "pre_review_complete",
          recommended_route: "standard_review",
          applicable_treaty: "中国-荷兰税收协定",
          payment_direction: "CN -> NL",
          income_type: "royalties",
          article_number: "12",
          article_title: "Royalties",
          rate_display: "10%",
          auto_conclusion_allowed: true,
          human_review_required: true,
          data_source_used: "stable",
          source_reference: "Article 12(2)",
          review_priority: "normal",
          blocking_facts: [],
          next_actions: [],
          user_declared_facts: [],
          bo_precheck: {
            status: "no_initial_flag",
            reason_code: "beneficial_owner_confirmed",
            reason_summary:
              "The guided beneficial-owner fact is marked confirmed, so the system does not raise an initial BO workflow flag.",
            facts_considered: [
              {
                fact_key: "beneficial_owner_status",
                value: "yes",
              },
            ],
            review_note: "Beneficial-owner status still requires human verification outside this tool.",
          },
        },
        human_review_brief: {
          brief_title: "Treaty Pre-Review Brief",
          headline: "CN -> NL royalties falls inside current treaty scope.",
          disposition: "Proceed with standard human review.",
          summary_lines: [],
          facts_to_verify: [],
          handoff_note: "This is a bounded pre-review output, not a final tax opinion.",
        },
      },
    }),
  }) as typeof fetch;

  render(<App />);

  await user.selectOptions(screen.getByLabelText(/payer jurisdiction/i), "CN");
  await user.selectOptions(screen.getByLabelText(/payee jurisdiction/i), "NL");
  await user.selectOptions(screen.getByLabelText(/income type/i), "royalties");
  await user.selectOptions(
    await screen.findByLabelText(/qualifying intellectual property/i),
    "yes",
  );
  await user.selectOptions(
    screen.getByLabelText(/beneficial-owner status for the royalty income/i),
    "yes",
  );
  await user.selectOptions(
    screen.getByLabelText(/contract, invoice, and payment flow support/i),
    "yes",
  );
  await user.click(screen.getByRole("button", { name: /run guided review/i }));

  expect((await screen.findAllByText(/bo precheck/i)).length).toBeGreaterThan(0);
  expect((await screen.findAllByText(/no_initial_flag/i)).length).toBeGreaterThan(0);
  expect(globalThis.fetch).toHaveBeenLastCalledWith(
    "/api/analyze",
    expect.objectContaining({
      body: JSON.stringify({
        input_mode: "guided",
        guided_input: {
          payer_country: "CN",
          payee_country: "NL",
          income_type: "royalties",
          facts: {
            royalty_character_confirmed: "yes",
            beneficial_owner_status: "yes",
            contract_payment_flow_consistent: "yes",
          },
        },
      }),
    }),
  );
});


test("renders a guided-input conflict warning while keeping legacy free-text secondary", async () => {
  const user = userEvent.setup();

  globalThis.fetch = vi.fn().mockResolvedValue({
    ok: true,
    json: async () => ({
      schema_version: "slice1.v1",
      input_mode_used: "guided",
      supported: true,
      review_state: {
        state_code: "needs_human_intervention",
        state_label_zh: "需要人工介入",
        state_summary: "当前结果已触发保守停止，应转入人工处理而不是继续自动推进。",
      },
      guided_conflict: {
        status: "conflict_detected",
        reason_code: "supplemental_text_conflicts_with_structured_facts",
        reason_summary:
          "Supplemental scenario text conflicts with the structured guided facts, so the system preserved the structured facts and escalated for manual review.",
        structured_facts_win: true,
        conflicting_claims: [
          "scenario_text claims the reduced dividend branch can be used, but the structured facts do not support that branch",
        ],
      },
      bo_precheck: {
        status: "insufficient_facts",
        reason_code: "beneficial_owner_unknown",
        reason_summary: "The guided BO fact is still unknown.",
        facts_considered: [
          {
            fact_key: "beneficial_owner_confirmed",
            value: "unknown",
          },
        ],
        review_note: "Confirm BO evidence before relying on treaty benefits.",
      },
      normalized_input: {
        payer_country: "CN",
        payee_country: "NL",
        transaction_type: "dividends",
      },
      result: {
        summary:
          "Preliminary view: Article 10 Dividends appears relevant, but multiple treaty rate branches (5% / 10%) are possible and this version should not issue an automatic conclusion.",
        boundary_note:
          "This is a first-pass treaty pre-review based on limited scenario facts. Final eligibility still depends on additional facts, documents, and analysis outside the current review scope.",
        immediate_action:
          "Do not rely on this result yet. Resolve the missing facts and supporting documents before any treaty conclusion.",
        article_number: "10",
        article_title: "Dividends",
        source_reference: "Article 10(2)(b)",
        source_language: "en",
        source_excerpt: "Treaty excerpt.",
        rate: "5% / 10%",
        extraction_confidence: 0.98,
        auto_conclusion_allowed: false,
        key_missing_facts: [],
        review_checklist: [],
        conditions: ["Applies when the reduced-rate branch is not established."],
        notes: [],
        human_review_required: true,
        review_priority: "high",
        review_reason:
          "Multiple treaty rate branches were found in this article, and the current scenario does not provide enough facts to choose one automatically.",
      },
      handoff_package: {
        machine_handoff: {
          schema_version: "slice1.v1",
          record_kind: "supported",
          review_state_code: "needs_human_intervention",
          recommended_route: "manual_review",
          applicable_treaty: "中国-荷兰税收协定",
          payment_direction: "CN -> NL",
          income_type: "dividends",
          article_number: "10",
          article_title: "Dividends",
          rate_display: "5% / 10%",
          auto_conclusion_allowed: false,
          human_review_required: true,
          data_source_used: "stable",
          source_reference: "Article 10(2)(b)",
          review_priority: "high",
          blocking_facts: [],
          next_actions: [],
          user_declared_facts: [],
          bo_precheck: {
            status: "insufficient_facts",
            reason_code: "beneficial_owner_unknown",
            reason_summary: "The guided BO fact is still unknown.",
            facts_considered: [
              {
                fact_key: "beneficial_owner_confirmed",
                value: "unknown",
              },
            ],
            review_note: "Confirm BO evidence before relying on treaty benefits.",
          },
          guided_conflict: {
            status: "conflict_detected",
            reason_code: "supplemental_text_conflicts_with_structured_facts",
            reason_summary:
              "Supplemental scenario text conflicts with the structured guided facts, so the system preserved the structured facts and escalated for manual review.",
            structured_facts_win: true,
            conflicting_claims: [
              "scenario_text claims the reduced dividend branch can be used, but the structured facts do not support that branch",
            ],
          },
        },
        human_review_brief: {
          brief_title: "Treaty Pre-Review Brief",
          headline: "Current scenario needs manual review.",
          disposition: "Escalate this scenario for manual review.",
          summary_lines: [],
          facts_to_verify: [],
          handoff_note: "This is a bounded pre-review output, not a final tax opinion.",
        },
      },
    }),
  }) as typeof fetch;

  render(<App />);

  expect(screen.getByRole("button", { name: /legacy free-text/i })).toBeInTheDocument();

  await user.selectOptions(screen.getByLabelText(/payer jurisdiction/i), "CN");
  await user.selectOptions(screen.getByLabelText(/payee jurisdiction/i), "NL");
  await user.selectOptions(screen.getByLabelText(/income type/i), "dividends");
  await user.type(
    await screen.findByLabelText(/direct shareholding percentage/i),
    "20",
  );
  await user.type(
    screen.getByLabelText(/dividend payment date/i),
    "2026-03-01",
  );
  await user.type(
    screen.getByLabelText(/supplemental scenario text/i),
    "中国公司向荷兰公司支付股息，且已满足 25% 直接持股门槛，可以适用协定优惠。",
  );
  await user.click(screen.getByRole("button", { name: /run guided review/i }));

  expect(await screen.findByText(/guided input conflict/i)).toBeInTheDocument();
  expect(screen.getByText(/structured facts win/i)).toBeInTheDocument();
  expect(screen.getByText(/the guided bo fact is still unknown/i)).toBeInTheDocument();
});


test("renders the internal onboarding workspace when query-param mode is enabled", async () => {
  setLocationSearch("/?internal=onboarding");

  globalThis.fetch = vi
    .fn()
    .mockResolvedValueOnce({
      ok: true,
      json: async () => ({
        manifests: [
          {
            manifest_path: "D:/repo/data/onboarding/manifests/cn-kr.initial-oecd.json",
            pair_id: "cn-kr",
            mode: "initial_onboarding",
            jurisdictions: ["CN", "KR"],
            target_articles: ["10", "11", "12"],
            baseline_enabled: true,
            source_build_manifest_path:
              "D:/repo/data/source_documents/manifests/cn-kr-main-treaty.build.json",
            source_build_available: true,
          },
        ],
      }),
    })
    .mockResolvedValueOnce({
      ok: true,
      json: async () => ({
        manifest: {
          manifest_path: "D:/repo/data/onboarding/manifests/cn-kr.initial-oecd.json",
          pair_id: "cn-kr",
          mode: "initial_onboarding",
          jurisdictions: ["CN", "KR"],
          target_articles: ["10", "11", "12"],
          baseline_enabled: true,
          source_build_manifest_path:
            "D:/repo/data/source_documents/manifests/cn-kr-main-treaty.build.json",
          source_build_available: true,
          source_documents: ["D:/repo/data/source_documents/cn-kr-main-treaty.json"],
          promotion_target_dataset: "D:/repo/data/treaties/cn-kr.v3.json",
          baseline_reference:
            "D:/repo/data/onboarding/baselines/oecd-model-2017.articles10-12.reference.json",
        },
        source_build: {
          available: true,
          manifest_path: "D:/repo/data/source_documents/manifests/cn-kr-main-treaty.build.json",
          report: { article_count: 3 },
          status: "ok",
        },
        compile: {
          status: "ok",
          report: { rule_count: 4 },
          delta_report: { delta_item_count: 4, high_materiality_count: 2 },
          delta_analysis: [
            {
              article_number: "10",
              delta_type: "rate_changed",
              summary: "Dividend fallback rate differs from the OECD baseline.",
            },
          ],
        },
        review: {
          status: "ready_for_approval",
          report: { status: "ready_for_approval" },
          diff: {
            source_changed_path_count: 1,
            dataset_changed_path_count: 1,
            source_changed_paths: ["$.parsed_articles[0]"],
            dataset_changed_paths: ["$.articles[0]"],
          },
        },
        approval: { status: null, record: null },
        promotion: { status: null, record: null },
        timing: {
          status: "active_review_session",
          review_session_active: true,
          durations: {
            review_seconds: 245,
            end_to_end_seconds: 1280,
          },
        },
        reviewed_source: {
          path: "D:/repo/data/onboarding/workdirs/cn-kr-initial-oecd/reviewed.source.json",
          content: "{\"pair\":\"cn-kr\"}",
        },
      }),
    }) as typeof fetch;

  render(<App />);

  expect(await screen.findByText(/internal onboarding workspace/i)).toBeInTheDocument();
  expect(screen.getByLabelText(/onboarding manifest/i)).toBeInTheDocument();
  expect(screen.getByText(/compiled delta summary/i)).toBeInTheDocument();
  expect(screen.getByText(/timing summary/i)).toBeInTheDocument();
  expect(screen.getByText(/active_review_session/i)).toBeInTheDocument();
  expect(screen.getByText(/245/)).toBeInTheDocument();
  expect(screen.getByText(/review diff summary/i)).toBeInTheDocument();
  expect(screen.getByLabelText(/reviewed\.source\.json editor/i)).toHaveValue(
    "{\"pair\":\"cn-kr\"}",
  );
  expect(screen.getByRole("button", { name: /start review session/i })).toBeInTheDocument();
  expect(screen.getByRole("button", { name: /run source build/i })).toBeInTheDocument();
  expect(screen.getByRole("button", { name: /run compile/i })).toBeInTheDocument();
  expect(screen.getByRole("button", { name: /run review/i })).toBeInTheDocument();
  expect(screen.getByRole("button", { name: /^approve$/i })).toBeInTheDocument();
  expect(screen.getByRole("button", { name: /promote/i })).toBeInTheDocument();
});


test("internal onboarding workspace submits edited review JSON and approval payloads", async () => {
  const user = userEvent.setup();
  setLocationSearch("/?internal=onboarding");

  globalThis.fetch = vi
    .fn()
    .mockResolvedValueOnce({
      ok: true,
      json: async () => ({
        manifests: [
          {
            manifest_path: "D:/repo/data/onboarding/manifests/cn-kr.initial-oecd.json",
            pair_id: "cn-kr",
            mode: "initial_onboarding",
            jurisdictions: ["CN", "KR"],
            target_articles: ["10", "11", "12"],
            baseline_enabled: true,
            source_build_manifest_path:
              "D:/repo/data/source_documents/manifests/cn-kr-main-treaty.build.json",
            source_build_available: true,
          },
        ],
      }),
    })
    .mockResolvedValueOnce({
      ok: true,
      json: async () => ({
        manifest: {
          manifest_path: "D:/repo/data/onboarding/manifests/cn-kr.initial-oecd.json",
          pair_id: "cn-kr",
          mode: "initial_onboarding",
          jurisdictions: ["CN", "KR"],
          target_articles: ["10", "11", "12"],
          baseline_enabled: true,
          source_build_manifest_path:
            "D:/repo/data/source_documents/manifests/cn-kr-main-treaty.build.json",
          source_build_available: true,
          source_documents: ["D:/repo/data/source_documents/cn-kr-main-treaty.json"],
          promotion_target_dataset: "D:/repo/data/treaties/cn-kr.v3.json",
          baseline_reference:
            "D:/repo/data/onboarding/baselines/oecd-model-2017.articles10-12.reference.json",
        },
        source_build: { available: true, manifest_path: "D:/repo/x", report: null, status: null },
        compile: { status: null, report: null, delta_report: null, delta_analysis: [] },
        review: { status: null, report: null, diff: null },
        approval: { status: null, record: null },
        promotion: { status: null, record: null },
        timing: {
          status: "not_started",
          review_session_active: false,
          durations: { review_seconds: null, end_to_end_seconds: null },
        },
        reviewed_source: {
          path: "D:/repo/data/onboarding/workdirs/cn-kr-initial-oecd/reviewed.source.json",
          content: "{\"initial\":true}",
        },
      }),
    })
    .mockResolvedValueOnce({
      ok: true,
      json: async () => ({
        manifest: {
          manifest_path: "D:/repo/data/onboarding/manifests/cn-kr.initial-oecd.json",
          pair_id: "cn-kr",
          mode: "initial_onboarding",
          jurisdictions: ["CN", "KR"],
          target_articles: ["10", "11", "12"],
          baseline_enabled: true,
          source_build_manifest_path:
            "D:/repo/data/source_documents/manifests/cn-kr-main-treaty.build.json",
          source_build_available: true,
          source_documents: ["D:/repo/data/source_documents/cn-kr-main-treaty.json"],
          promotion_target_dataset: "D:/repo/data/treaties/cn-kr.v3.json",
          baseline_reference:
            "D:/repo/data/onboarding/baselines/oecd-model-2017.articles10-12.reference.json",
        },
        source_build: { available: true, manifest_path: "D:/repo/x", report: null, status: null },
        compile: { status: null, report: null, delta_report: null, delta_analysis: [] },
        review: { status: null, report: null, diff: null },
        approval: { status: null, record: null },
        promotion: { status: null, record: null },
        timing: {
          status: "active_review_session",
          review_session_active: true,
          durations: { review_seconds: null, end_to_end_seconds: null },
        },
        reviewed_source: {
          path: "D:/repo/data/onboarding/workdirs/cn-kr-initial-oecd/reviewed.source.json",
          content: "{\"initial\":true}",
        },
      }),
    })
    .mockResolvedValueOnce({
      ok: true,
      json: async () => ({
        manifest: {
          manifest_path: "D:/repo/data/onboarding/manifests/cn-kr.initial-oecd.json",
          pair_id: "cn-kr",
          mode: "initial_onboarding",
          jurisdictions: ["CN", "KR"],
          target_articles: ["10", "11", "12"],
          baseline_enabled: true,
          source_build_manifest_path:
            "D:/repo/data/source_documents/manifests/cn-kr-main-treaty.build.json",
          source_build_available: true,
          source_documents: ["D:/repo/data/source_documents/cn-kr-main-treaty.json"],
          promotion_target_dataset: "D:/repo/data/treaties/cn-kr.v3.json",
          baseline_reference:
            "D:/repo/data/onboarding/baselines/oecd-model-2017.articles10-12.reference.json",
        },
        source_build: { available: true, manifest_path: "D:/repo/x", report: null, status: null },
        compile: { status: "ok", report: { rule_count: 4 }, delta_report: null, delta_analysis: [] },
        review: { status: "ready_for_approval", report: { status: "ready_for_approval" }, diff: null },
        approval: { status: null, record: null },
        promotion: { status: null, record: null },
        timing: {
          status: "active_review_session",
          review_session_active: true,
          durations: { review_seconds: 245, end_to_end_seconds: null },
        },
        reviewed_source: {
          path: "D:/repo/data/onboarding/workdirs/cn-kr-initial-oecd/reviewed.source.json",
          content: "{\"edited\":true}",
        },
      }),
    })
    .mockResolvedValueOnce({
      ok: true,
      json: async () => ({
        manifest: {
          manifest_path: "D:/repo/data/onboarding/manifests/cn-kr.initial-oecd.json",
          pair_id: "cn-kr",
          mode: "initial_onboarding",
          jurisdictions: ["CN", "KR"],
          target_articles: ["10", "11", "12"],
          baseline_enabled: true,
          source_build_manifest_path:
            "D:/repo/data/source_documents/manifests/cn-kr-main-treaty.build.json",
          source_build_available: true,
          source_documents: ["D:/repo/data/source_documents/cn-kr-main-treaty.json"],
          promotion_target_dataset: "D:/repo/data/treaties/cn-kr.v3.json",
          baseline_reference:
            "D:/repo/data/onboarding/baselines/oecd-model-2017.articles10-12.reference.json",
        },
        source_build: { available: true, manifest_path: "D:/repo/x", report: null, status: null },
        compile: { status: "ok", report: { rule_count: 4 }, delta_report: null, delta_analysis: [] },
        review: { status: "ready_for_approval", report: { status: "ready_for_approval" }, diff: null },
        approval: { status: "approved", record: { reviewer_name: "Codex Reviewer" } },
        promotion: { status: null, record: null },
        timing: {
          status: "approved",
          review_session_active: false,
          durations: { review_seconds: 245, end_to_end_seconds: null },
        },
        reviewed_source: {
          path: "D:/repo/data/onboarding/workdirs/cn-kr-initial-oecd/reviewed.source.json",
          content: "{\"edited\":true}",
        },
      }),
    }) as typeof fetch;

  render(<App />);

  await user.click(await screen.findByRole("button", { name: /start review session/i }));

  await waitFor(() => {
    expect(globalThis.fetch).toHaveBeenNthCalledWith(
      3,
      "/api/internal/onboarding/start-review",
      expect.objectContaining({
        body: JSON.stringify({
          manifest: "D:/repo/data/onboarding/manifests/cn-kr.initial-oecd.json",
          reviewer_name: "Codex Reviewer",
          note: "Approved after reviewer workspace check.",
        }),
      }),
    );
  });

  const editor = await screen.findByLabelText(/reviewed\.source\.json editor/i);
  await user.clear(editor);
  await user.paste("{\"edited\":true}");
  await user.click(screen.getByRole("button", { name: /run review/i }));

  await waitFor(() => {
    expect(globalThis.fetch).toHaveBeenNthCalledWith(
      4,
      "/api/internal/onboarding/review",
      expect.objectContaining({
        body: JSON.stringify({
          manifest: "D:/repo/data/onboarding/manifests/cn-kr.initial-oecd.json",
          reviewed_source_json: "{\"edited\":true}",
        }),
      }),
    );
  });

  await user.click(screen.getByRole("button", { name: /^approve$/i }));

  await waitFor(() => {
    expect(globalThis.fetch).toHaveBeenNthCalledWith(
      5,
      "/api/internal/onboarding/approve",
      expect.objectContaining({
        body: JSON.stringify({
          manifest: "D:/repo/data/onboarding/manifests/cn-kr.initial-oecd.json",
          reviewer_name: "Codex Reviewer",
          note: "Approved after reviewer workspace check.",
        }),
      }),
    );
  });
});

