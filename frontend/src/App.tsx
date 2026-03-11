import { FormEvent, useState } from "react";


type AnalyzeResponse =
  | {
      supported: false;
      reason: string;
      message: string;
    }
  | {
      supported: true;
      normalized_input: {
        payer_country: string;
        payee_country: string;
        transaction_type: string;
      };
      result: {
        article_number: string;
        article_title: string;
        rate: string;
        conditions: string[];
        notes: string[];
        human_review_required: boolean;
        review_reason: string;
      };
    };

const exampleScenario = "中国居民企业向荷兰支付特许权使用费";

export default function App() {
  const [scenario, setScenario] = useState(exampleScenario);
  const [result, setResult] = useState<AnalyzeResponse | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState("");

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setIsLoading(true);
    setError("");

    try {
      const response = await fetch("/api/analyze", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ scenario }),
      });

      if (!response.ok) {
        throw new Error("Request failed.");
      }

      const payload = (await response.json()) as AnalyzeResponse;
      setResult(payload);
    } catch {
      setError("The analysis request failed. Please make sure the backend is running.");
      setResult(null);
    } finally {
      setIsLoading(false);
    }
  }

  return (
    <main className="app-shell">
      <section className="hero-card">
        <p className="eyebrow">Tax Treaty Agent</p>
        <h1>Translate a cross-border tax scenario into a bounded treaty analysis.</h1>
        <p className="intro">
          This MVP currently supports China-Netherlands treaty scenarios for dividends,
          interest, and royalties.
        </p>

        <form className="scenario-form" onSubmit={handleSubmit}>
          <label htmlFor="scenario-input">Cross-border scenario</label>
          <textarea
            id="scenario-input"
            name="scenario"
            rows={4}
            value={scenario}
            onChange={(event) => setScenario(event.target.value)}
          />

          <div className="form-actions">
            <button type="submit" disabled={isLoading}>
              {isLoading ? "Analyzing..." : "Analyze"}
            </button>
            <button type="button" className="ghost-button" onClick={() => setScenario(exampleScenario)}>
              Use example
            </button>
          </div>
        </form>

        {error ? <p className="error-banner">{error}</p> : null}
      </section>

      <section className="result-card" aria-live="polite">
        <h2>Structured Output</h2>

        {result === null ? (
          <p className="placeholder">
            Submit a supported treaty scenario to see article, rate, conditions, and review
            guidance.
          </p>
        ) : result.supported ? (
          <div className="result-grid">
            <div className="result-panel">
              <p className="result-kicker">Treaty Match</p>
              <h3>
                Article {result.result.article_number} · {result.result.article_title}
              </h3>
              <p className="rate-pill">{result.result.rate}</p>
              <p className="summary-line">
                {result.normalized_input.payer_country} → {result.normalized_input.payee_country} ·{" "}
                {result.normalized_input.transaction_type}
              </p>
            </div>

            <div className="result-panel">
              <p className="result-kicker">Conditions</p>
              <ul>
                {result.result.conditions.map((condition) => (
                  <li key={condition}>{condition}</li>
                ))}
              </ul>
            </div>

            <div className="result-panel">
              <p className="result-kicker">Notes</p>
              <ul>
                {result.result.notes.map((note) => (
                  <li key={note}>{note}</li>
                ))}
              </ul>
            </div>

            <div className="result-panel review-panel">
              <p className="result-kicker">Review Guidance</p>
              <p className="review-flag">
                {result.result.human_review_required
                  ? "Human review recommended"
                  : "Human review not required"}
              </p>
              <p>{result.result.review_reason}</p>
            </div>
          </div>
        ) : (
          <div className="unsupported-card">
            <p className="result-kicker">Unsupported</p>
            <h3>{result.reason}</h3>
            <p>{result.message}</p>
          </div>
        )}
      </section>
    </main>
  );
}
