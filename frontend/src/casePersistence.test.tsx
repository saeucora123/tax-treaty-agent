import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";

import App from "./App";


function setLocationSearch(search: string) {
  window.history.pushState({}, "", search);
}


afterEach(() => {
  setLocationSearch("/");
});

async function openParserValidationPanel(user: ReturnType<typeof userEvent.setup>) {
  if (!screen.queryByLabelText(/cross-border scenario/i)) {
    await user.click(screen.getByRole("button", { name: /open parser validation/i }));
  }
}


function buildGuidedRoyaltiesResponse() {
  return {
    schema_version: "slice3.v1",
    input_mode_used: "guided",
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
    normalized_input: {
      payer_country: "CN",
      payee_country: "NL",
      transaction_type: "royalties",
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
      source_trace: {
        treaty_full_name: "China-Netherlands Tax Treaty",
        version_note: "2013 agreement reflected in the official English treaty text used for the stable runtime dataset.",
        source_document_title: "China-Netherlands treaty text",
        language_version: "en",
        official_source_ids: ["sat-cn-nl-2013-en-pdf"],
        protocol_note: null,
        working_paper_ref: "docs/superpowers/research/stage-6-evidence/example.md",
      },
      mli_context: {
        covered_tax_agreement: true,
        ppt_applies: true,
        summary: "MLI / PPT reviewer signal.",
        human_review_note: "Confirm PPT during manual review.",
        official_source_ids: ["sat-cn-nl-mli-en-pdf"],
      },
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
        schema_version: "slice3.v1",
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
        source_excerpt: "Treaty excerpt.",
        treaty_version:
          "2013 agreement reflected in the official English treaty text used for the stable runtime dataset.",
        mli_summary: "MLI / PPT reviewer signal.",
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
        summary_lines: ["Article 12 royalties is the current treaty lane."],
        facts_to_verify: ["Confirm beneficial ownership before relying on the treaty position."],
        handoff_note: "This is a bounded pre-review output, not a final tax opinion.",
      },
      authority_memo: {
        status: "available",
        reviewer_note: "Reviewer-facing authority support only.",
        topics: [
          {
            topic: "treaty_basis",
            summary: "Runtime basis is anchored to the official treaty text sources.",
            citations: [
              {
                source_id: "sat-cn-nl-2013-en-pdf",
                title: "China-Netherlands treaty English text",
                source_type: "treaty_text",
                official_url: "https://example.com/treaty.pdf",
                note: "Primary treaty basis for the current runtime lane.",
              },
            ],
            gap: null,
          },
        ],
        coverage_gaps: [
          {
            topic: "beneficial_owner",
            reason_code: "DATA_MISSING",
            note: "No mapped authority source is configured for this topic yet.",
          },
          {
            topic: "domestic_law",
            reason_code: "DATA_MISSING",
            note: "No mapped authority source is configured for this topic yet.",
          },
        ],
      },
    },
  } as const;
}


test("shows Save Case for guided results and saves a case with generated links", async () => {
  const user = userEvent.setup();
  const analyzePayload = buildGuidedRoyaltiesResponse();

  globalThis.fetch = vi
    .fn()
    .mockResolvedValueOnce({
      ok: true,
      json: async () => analyzePayload,
    })
    .mockResolvedValueOnce({
      ok: true,
      json: async () => ({
        case_id: "case_demo123",
        saved_at: "2026-03-21T12:00:00Z",
        creator_token: "creator-token",
        reviewer_token: "reviewer-token",
        analyze_response_snapshot: analyzePayload,
      }),
    }) as typeof fetch;

  render(<App />);

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
  await user.type(
    screen.getByLabelText(/supplemental scenario text/i),
    "中国居民企业向荷兰公司支付特许权使用费",
  );
  await user.click(screen.getByRole("button", { name: /run guided review/i }));

  expect(await screen.findByRole("button", { name: /save case/i })).toBeInTheDocument();

  await user.click(screen.getByRole("button", { name: /save case/i }));

  expect(await screen.findByText(/case_demo123/i)).toBeInTheDocument();
  expect(screen.getByText(/reviewer package is the default share surface/i)).toBeInTheDocument();
  expect(screen.getByRole("link", { name: /open reviewer view/i })).toHaveAttribute(
    "href",
    expect.stringContaining("?case=case_demo123&token=reviewer-token"),
  );
  expect((screen.getByLabelText(/reviewer case link url/i) as HTMLInputElement).value).toContain(
    "?case=case_demo123&token=reviewer-token",
  );
  expect((screen.getByLabelText(/reviewer workpaper link url/i) as HTMLInputElement).value).toContain(
    "/api/cases/case_demo123/workpaper?token=reviewer-token",
  );
  expect(screen.getByRole("link", { name: /open creator workpaper/i })).toHaveAttribute(
    "href",
    expect.stringContaining("/api/cases/case_demo123/workpaper?token=creator-token"),
  );
  expect((screen.getByLabelText(/creator case link url/i) as HTMLInputElement).value).toContain(
    "?case=case_demo123&token=creator-token",
  );
  expect(screen.getByRole("link", { name: /open reviewer workpaper/i })).toHaveAttribute(
    "href",
    expect.stringContaining("/api/cases/case_demo123/workpaper?token=reviewer-token"),
  );
  expect(globalThis.fetch).toHaveBeenNthCalledWith(
    2,
    "/api/cases",
    expect.objectContaining({
      method: "POST",
      headers: { "Content-Type": "application/json" },
    }),
  );
});


test("does not show Save Case for legacy free-text results", async () => {
  const user = userEvent.setup();

  globalThis.fetch = vi.fn().mockResolvedValue({
    ok: true,
    json: async () => ({
      supported: true,
      input_mode_used: "free_text",
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
      next_actions: [],
      normalized_input: {
        payer_country: "CN",
        payee_country: "NL",
        transaction_type: "royalties",
      },
      result: {
        summary: "Preliminary view: Article 12 Royalties appears relevant.",
        boundary_note: "This is a first-pass treaty pre-review based on limited scenario facts.",
        immediate_action: "Proceed with standard manual review before relying on the treaty position.",
        article_number: "12",
        article_title: "Royalties",
        source_reference: "Article 12(2)",
        source_language: "en",
        source_excerpt: "Treaty excerpt.",
        source_trace: {
          treaty_full_name: "China-Netherlands Tax Treaty",
          version_note: "2013 agreement",
          source_document_title: "China-Netherlands treaty text",
          language_version: "en",
          official_source_ids: ["sat-cn-nl-2013-en-pdf"],
          protocol_note: null,
          working_paper_ref: "docs/example.md",
        },
        mli_context: {
          covered_tax_agreement: true,
          ppt_applies: true,
          summary: "MLI / PPT reviewer signal.",
          human_review_note: "Confirm PPT during manual review.",
          official_source_ids: ["sat-cn-nl-mli-en-pdf"],
        },
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
          schema_version: "slice3.v1",
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

  await openParserValidationPanel(user);
  await user.type(
    screen.getByLabelText(/cross-border scenario/i),
    "中国居民企业向荷兰支付特许权使用费",
  );
  await user.click(screen.getByRole("button", { name: /run parser review/i }));

  await screen.findByText(/preliminary view: article 12 royalties appears relevant/i);
  expect(screen.queryByRole("button", { name: /save case/i })).not.toBeInTheDocument();
});


test("loads a saved reviewer case view from query params and hides the submission form", async () => {
  setLocationSearch("/?case=case_demo123&token=reviewer-token");

  globalThis.fetch = vi.fn().mockResolvedValue({
    ok: true,
    json: async () => ({
      case_id: "case_demo123",
      saved_at: "2026-03-21T12:00:00Z",
      schema_version: "slice3.v1",
      input_mode_used: "guided",
      view_role: "reviewer",
      reviewer_share_ready: false,
      request_snapshot: {
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
          scenario_text: "中国居民企业向荷兰公司支付特许权使用费",
        },
      },
      response_snapshot: buildGuidedRoyaltiesResponse(),
    }),
  }) as typeof fetch;

  render(<App />);

  expect(await screen.findByText(/saved case/i)).toBeInTheDocument();
  expect(screen.getByText(/reviewer read-only package/i)).toBeInTheDocument();
  expect(screen.getByText(/reviewer risk summary/i)).toBeInTheDocument();
  expect(screen.getByText(/bo precheck \(no_initial_flag\):/i)).toBeInTheDocument();
  expect(screen.getByText(/beneficial_owner \(DATA_MISSING\)/i)).toBeInTheDocument();
  expect(screen.getAllByText(/facts to verify:/i).length).toBeGreaterThan(0);
  expect(
    screen.getByText(/has the recipient's beneficial-owner status for the royalty income been separately confirmed/i),
  ).toBeInTheDocument();
  expect(screen.getByText(/printable workpaper uses the same immutable saved snapshot/i)).toBeInTheDocument();
  expect(screen.getByText(/workflow handoff/i)).toBeInTheDocument();
  expect(screen.getAllByText(/authority memo/i).length).toBeGreaterThan(0);
  expect(screen.queryByLabelText(/cross-border scenario/i)).not.toBeInTheDocument();
  expect(screen.queryByRole("button", { name: /run guided review/i })).not.toBeInTheDocument();
  expect(screen.getByRole("link", { name: /open printable workpaper/i })).toHaveAttribute(
    "href",
    "/api/cases/case_demo123/workpaper?token=reviewer-token",
  );
});
