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

const REFERENCE_ARCHIVES = [
  "中国居民企业向荷兰支付特许权使用费",
  "荷兰公司向中国母公司支付股息",
  "中国企业向荷兰银行支付贷款利息",
];

export default function App() {
  const [scenario, setScenario] = useState("");
  const [result, setResult] = useState<AnalyzeResponse | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState("");

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!scenario.trim()) return;

    setIsLoading(true);
    setError("");

    try {
      const response = await fetch("/api/analyze", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ scenario }),
      });

      if (!response.ok) {
        throw new Error("Request failed.");
      }

      const payload = (await response.json()) as AnalyzeResponse;
      setResult(payload);
    } catch {
      setError("The review request failed. Check that the backend service is running.");
      setResult(null);
    } finally {
      setIsLoading(false);
    }
  }

  return (
    <div className="document-body">
      <header className="memo-header">
        <div className="memo-stamp">
          <span className="stamp-seal">TTA-MVP</span>
          <span className="stamp-date">SCOPE: CN-NL</span>
        </div>
        <div className="memo-title-block">
          <h1 className="memo-title">TAX TREATY AGENT</h1>
          <p className="memo-subtitle">Treaty review workspace for bounded cross-border payment scenarios.</p>
        </div>
        <div className="memo-meta">
          <span className="meta-label">STATUS</span>
          <span className="meta-value">MVP REVIEW TOOL</span>
        </div>
      </header>

      <main className="review-main">
        <section className="submission-section">
          <form className="query-form" onSubmit={handleSubmit}>
            <div className="form-group">
              <label htmlFor="scenario-input" className="section-heading">
                I. Scenario Submission
                <span className="sr-only">Cross-border scenario</span>
              </label>
              <p className="section-desc">
                Describe the payer, payee, and income type to run a treaty-limited review.
              </p>
              
              <div className="paper-input-wrapper">
                <textarea
                  id="scenario-input"
                  name="scenario"
                  placeholder="[Enter payer, payee, and income type...]"
                  rows={4}
                  value={scenario}
                  onChange={(event) => setScenario(event.target.value)}
                  className="typewriter-input"
                />
              </div>
            </div>

            <div className="archive-reference-block">
              <span className="reference-label">Reference Cases</span>
              <ul className="archive-list">
                {REFERENCE_ARCHIVES.map((example, i) => (
                  <li key={i}>
                    <button
                      type="button"
                      className="text-link-button"
                      onClick={() => setScenario(example)}
                    >
                      [Ref. {String(i + 1).padStart(2, "0")}]: {example}
                    </button>
                  </li>
                ))}
              </ul>
            </div>

             <div className="action-row">
               <button type="submit" disabled={isLoading || !scenario.trim()} className="btn-seal">
                 {isLoading ? "Running Review..." : "Run Review"}
               </button>
             </div>
          </form>

          {error && (
            <div className="memo-alert alert-error">
              <span className="alert-marker">!</span>
              <p>{error}</p>
            </div>
          )}
        </section>

        <section className="output-section" aria-live="polite">
          <h2 className="section-heading">II. Review Record</h2>
          {result === null ? (
            <div className="empty-record">
              <p>[ NO REVIEW RECORD YET ]</p>
              <p className="empty-subtext">Submit a scenario to generate a treaty review record.</p>
            </div>
          ) : result.supported ? (
            <div className="formal-record success-record">
              <div className="record-header">
                 <h3>TREATY MATCH</h3>
                 <span className="auth-stamp stamp-green">SUPPORTED</span>
              </div>
              
              <div className="record-body">
                <div className="record-row">
                  <div className="row-label">Transaction Flow</div>
                  <div className="row-value flow-statement">
                    <div>
                      <span className="flow-term">Payer jurisdiction:</span>{" "}
                      <strong>{result.normalized_input.payer_country}</strong>
                    </div>
                    <div>
                      <span className="flow-term">Payee jurisdiction:</span>{" "}
                      <strong>{result.normalized_input.payee_country}</strong>
                    </div>
                    <div>
                      <span className="flow-term">Income type:</span>{" "}
                      <em>{result.normalized_input.transaction_type}</em>
                    </div>
                  </div>
                </div>

                <div className="record-row highlight-row">
                  <div className="row-label">Treaty Provision</div>
                  <div className="row-value extract-value">
                    Article {result.result.article_number} · {result.result.article_title}
                  </div>
                </div>

                <div className="record-row highlight-row">
                  <div className="row-label">Treaty Rate Ceiling</div>
                  <div className="row-value rate-value">
                    {result.result.rate}
                  </div>
                </div>

                <div className="record-row">
                  <div className="row-label">Conditions</div>
                  <div className="row-value">
                    <ul className="formal-list">
                      {result.result.conditions.map((condition, idx) => (
                        <li key={idx}>{condition}</li>
                      ))}
                    </ul>
                  </div>
                </div>

                <div className="record-row">
                  <div className="row-label">Notes</div>
                  <div className="row-value">
                    <ul className="formal-list">
                      {result.result.notes.map((note, idx) => (
                        <li key={idx}>{note}</li>
                      ))}
                    </ul>
                  </div>
                </div>

                <div className={`record-row warning-row ${result.result.human_review_required ? 'review-flagged' : ''}`}>
                  <div className="row-label">Review Guidance</div>
                  <div className="row-value flag-content">
                    <p className="flag-status">
                      {result.result.human_review_required ? "[ REVIEW ] Human review recommended" : "[ CLEAR ] Human review not required"}
                    </p>
                    <p className="flag-reason">{result.result.review_reason}</p>
                  </div>
                </div>
              </div>
            </div>
          ) : (
            <div className="formal-record error-record">
               <div className="record-header border-red">
                 <h3>REVIEW UNAVAILABLE</h3>
                 <span className="auth-stamp stamp-red">UNSUPPORTED</span>
              </div>
              
              <div className="record-body">
                <div className="record-row">
                  <div className="row-label text-red">Reason</div>
                  <div className="row-value courier-text">
                    {result.reason}
                  </div>
                </div>
                <div className="record-row">
                  <div className="row-label">Detail</div>
                  <div className="row-value">
                    <p>{result.message}</p>
                  </div>
                </div>
              </div>
            </div>
          )}
        </section>
      </main>
    </div>
  );
}
