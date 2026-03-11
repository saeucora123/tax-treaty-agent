import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";

import App from "./App";


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
        source_reference: "Article 12(1)",
        source_language: "en",
        source_excerpt:
          "Royalty treatment is governed by Article 12(1), subject to treaty conditions and factual qualification.",
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
  expect(screen.getByText(/how we read this input/i)).toBeInTheDocument();
  expect(screen.getByText(/parsed by llm input parser/i)).toBeInTheDocument();
  expect(screen.getByText(/software license/i)).toBeInTheDocument();
  expect(await screen.findByText("Article 12 · Royalties")).toBeInTheDocument();
  expect(screen.getByText("Article 12(1)")).toBeInTheDocument();
  expect(
    screen.getByText(
      "Royalty treatment is governed by Article 12(1), subject to treaty conditions and factual qualification.",
    ),
  ).toBeInTheDocument();
  expect(screen.getByText("10%")).toBeInTheDocument();
  expect(screen.getByText(/english source/i)).toBeInTheDocument();
  expect(screen.getByText(/98% extraction confidence/i)).toBeInTheDocument();
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
});


test("shows a stronger review warning for medium-confidence treaty extraction", async () => {
  const user = userEvent.setup();

  globalThis.fetch = vi.fn().mockResolvedValue({
    ok: true,
    json: async () => ({
      supported: true,
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
  expect(
    screen.getByText(/escalate this case for priority manual review before using the treaty result/i),
  ).toBeInTheDocument();
  expect(await screen.findByText(/\[ priority review \]/i)).toBeInTheDocument();
  expect(screen.getByText(/88% extraction confidence/i)).toBeInTheDocument();
  expect(screen.getByText(/prioritize manual verification/i)).toBeInTheDocument();
});


test("holds automatic treaty conclusion when source confidence is very low", async () => {
  const user = userEvent.setup();

  globalThis.fetch = vi.fn().mockResolvedValue({
    ok: true,
    json: async () => ({
      supported: true,
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
  expect(
    screen.getByText(/do not rely on this result yet\. resolve the missing facts and supporting documents/i),
  ).toBeInTheDocument();
  expect(await screen.findByText(/provisional review only/i)).toBeInTheDocument();
  expect(screen.getByText(/\[ hold \] confidence too low for automatic conclusion/i)).toBeInTheDocument();
  expect(screen.getByText(/72% extraction confidence/i)).toBeInTheDocument();
  expect(screen.getByText(/automatic treaty conclusion/i)).toBeInTheDocument();
});


test("shows missing-input guidance for unsupported or incomplete scenarios", async () => {
  const user = userEvent.setup();

  globalThis.fetch = vi.fn().mockResolvedValue({
    ok: true,
    json: async () => ({
      supported: false,
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

  expect(await screen.findByText(/review unavailable/i)).toBeInTheDocument();
  expect(screen.getByText(/immediate action/i)).toBeInTheDocument();
  expect(
    screen.getByText(/add the missing scenario facts before running the treaty review again/i),
  ).toBeInTheDocument();
  expect(screen.getByText(/how to fix this input/i)).toBeInTheDocument();
  expect(screen.getByText(/payer country/i)).toBeInTheDocument();
  expect(screen.getByText(/try a sentence like/i)).toBeInTheDocument();
  expect(screen.getByText("荷兰公司向中国公司支付利息")).toBeInTheDocument();
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

