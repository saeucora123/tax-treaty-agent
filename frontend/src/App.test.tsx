import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";

import App from "./App";


test("shows structured treaty analysis after submitting a supported scenario", async () => {
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
        article_number: "12",
        article_title: "Royalties",
        rate: "10%",
        conditions: ["Treaty applicability depends on the facts of the payment."],
        notes: ["Beneficial ownership and factual details may affect the final conclusion."],
        human_review_required: true,
        review_reason: "Final eligibility depends on facts beyond v1 scope.",
      },
    }),
  }) as typeof fetch;

  render(<App />);

  await user.type(
    screen.getByLabelText(/cross-border scenario/i),
    "中国居民企业向荷兰支付特许权使用费",
  );
  await user.click(screen.getByRole("button", { name: /run review/i }));

  expect(await screen.findByText("Article 12 · Royalties")).toBeInTheDocument();
  expect(screen.getByText("10%")).toBeInTheDocument();
  expect(screen.getByText(/human review recommended/i)).toBeInTheDocument();
});
