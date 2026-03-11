import { FormEvent, useState } from "react";

type AnalyzeResponse =
  | {
      supported: false;
      reason: string;
      message: string;
      immediate_action: string;
      missing_fields: string[];
      classification_note?: string;
      suggested_format: string;
      suggested_examples: string[];
      input_interpretation?: InputInterpretation;
    }
  | {
      supported: true;
      input_interpretation?: InputInterpretation;
      normalized_input: {
        payer_country: string;
        payee_country: string;
        transaction_type: string;
      };
      result: {
        summary: string;
        boundary_note: string;
        immediate_action: string;
        article_number: string;
        article_title: string;
        source_reference: string;
        source_language: string;
        source_excerpt: string;
        rate: string;
        extraction_confidence: number;
        auto_conclusion_allowed: boolean;
        key_missing_facts: string[];
        review_checklist: string[];
        conditions: string[];
        notes: string[];
        human_review_required: boolean;
        review_priority: "none" | "normal" | "high";
        review_reason: string;
      };
    };

type InputInterpretation = {
  parser_source: "llm";
  payer_country: string | null;
  payee_country: string | null;
  transaction_type: string;
  matched_transaction_label: string | null;
};

const REFERENCE_ARCHIVES = [
  {
    state: "Supported",
    hint: "Baseline supported match with standard review guidance.",
    scenario: "中国居民企业向荷兰支付特许权使用费",
  },
  {
    state: "Supported",
    hint: "Reverse-direction supported case for dividend review.",
    scenario: "荷兰公司向中国母公司支付股息",
  },
  {
    state: "Unsupported",
    hint: "Shows how the tool refuses scenarios outside the China-Netherlands treaty scope.",
    scenario: "中国居民企业向美国支付特许权使用费",
  },
  {
    state: "Incomplete",
    hint: "Shows how the tool guides the user to repair missing input.",
    scenario: "向荷兰公司支付股息",
  },
] as const;
const FIELD_LABELS: Record<string, string> = {
  payer_country: "Payer country",
  payee_country: "Payee country",
  transaction_type: "Income type",
};

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

  function formatSourceLanguage(language: string) {
    if (language === "en") return "English source";
    if (language === "zh") return "Chinese source";
    return `${language.toUpperCase()} source`;
  }

  function formatConfidence(confidence: number) {
    return `${Math.round(confidence * 100)}% extraction confidence`;
  }

  function formatReviewStatus(result: Extract<AnalyzeResponse, { supported: true }>["result"]) {
    if (!result.auto_conclusion_allowed) {
      return "[ HOLD ] Confidence too low for automatic conclusion";
    }
    if (result.review_priority === "high") {
      return "[ PRIORITY REVIEW ] Moderate-confidence source; escalate human review";
    }
    if (result.human_review_required) {
      return "[ REVIEW ] Human review recommended";
    }
    return "[ CLEAR ] Human review not required";
  }

  function getSupportedRecordTitle(result: Extract<AnalyzeResponse, { supported: true }>["result"]) {
    return result.auto_conclusion_allowed ? "TREATY MATCH" : "PROVISIONAL REVIEW ONLY";
  }

  function getSupportedRecordStamp(result: Extract<AnalyzeResponse, { supported: true }>["result"]) {
    return result.auto_conclusion_allowed ? "SUPPORTED" : "HOLD";
  }

  function getRateLabel(result: Extract<AnalyzeResponse, { supported: true }>["result"]) {
    return result.auto_conclusion_allowed ? "Treaty Rate Ceiling" : "Indicative Treaty Rate";
  }

  function formatMissingField(field: string) {
    return FIELD_LABELS[field] ?? field;
  }

  function renderInputInterpretation(inputInterpretation?: InputInterpretation) {
    if (!inputInterpretation) {
      return null;
    }

    return (
      <div className="record-row">
        <div className="row-label">How We Read This Input</div>
        <div className="row-value">
          <p>Parsed by LLM input parser</p>
          <ul className="formal-list">
            <li>
              Payer country: {inputInterpretation.payer_country ?? "Not confidently identified"}
            </li>
            <li>
              Payee country: {inputInterpretation.payee_country ?? "Not confidently identified"}
            </li>
            <li>Income type lane: {inputInterpretation.transaction_type}</li>
            {inputInterpretation.matched_transaction_label && (
              <li>Matched business wording: {inputInterpretation.matched_transaction_label}</li>
            )}
          </ul>
        </div>
      </div>
    );
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
                      onClick={() => setScenario(example.scenario)}
                    >
                      <span className="example-state-tag">[{example.state}]</span>{" "}
                      [Ref. {String(i + 1).padStart(2, "0")}]: {example.scenario}
                    </button>
                    <p className="example-hint">{example.hint}</p>
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
                <h3>{getSupportedRecordTitle(result.result)}</h3>
                <span className={`auth-stamp ${result.result.auto_conclusion_allowed ? "stamp-green" : "stamp-red"}`}>
                  {getSupportedRecordStamp(result.result)}
                </span>
              </div>

              <div className="record-body">
                <div className="record-row highlight-row">
                  <div className="row-label">Preliminary View</div>
                  <div className="row-value">
                    <p>{result.result.summary}</p>
                  </div>
                </div>

                {renderInputInterpretation(result.input_interpretation)}

                <div className="record-row">
                  <div className="row-label">Immediate Action</div>
                  <div className="row-value">
                    <p>{result.result.immediate_action}</p>
                  </div>
                </div>

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

                <div className="record-row">
                  <div className="row-label">Source Anchor</div>
                  <div className="row-value">
                    <p>{result.result.source_reference}</p>
                  </div>
                </div>

                <div className="record-row">
                  <div className="row-label">Source Quality</div>
                  <div className="row-value">
                    <p>{formatSourceLanguage(result.result.source_language)}</p>
                    <p>{formatConfidence(result.result.extraction_confidence)}</p>
                  </div>
                </div>

                <div className="record-row">
                  <div className="row-label">Treaty Excerpt</div>
                  <div className="row-value">
                    <p>{result.result.source_excerpt}</p>
                  </div>
                </div>

                <div className="record-row highlight-row">
                  <div className="row-label">{getRateLabel(result.result)}</div>
                  <div className="row-value rate-value">{result.result.rate}</div>
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
                  <div className="row-label">What This Review Means</div>
                  <div className="row-value">
                    <p>{result.result.boundary_note}</p>
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

                <div className="record-row">
                  <div className="row-label">Key Missing Facts</div>
                  <div className="row-value">
                    <ul className="formal-list">
                      {result.result.key_missing_facts.map((item, idx) => (
                        <li key={idx}>{item}</li>
                      ))}
                    </ul>
                  </div>
                </div>

                <div className="record-row">
                  <div className="row-label">Next Verification Steps</div>
                  <div className="row-value">
                    <ul className="formal-list">
                      {result.result.review_checklist.map((item, idx) => (
                        <li key={idx}>{item}</li>
                      ))}
                    </ul>
                  </div>
                </div>

                <div className={`record-row warning-row ${result.result.human_review_required ? "review-flagged" : ""}`}>
                  <div className="row-label">Review Guidance</div>
                  <div className="row-value flag-content">
                    <p className="flag-status">{formatReviewStatus(result.result)}</p>
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
                  <div className="row-value courier-text">{result.reason}</div>
                </div>
                {renderInputInterpretation(result.input_interpretation)}
                <div className="record-row">
                  <div className="row-label">Detail</div>
                  <div className="row-value">
                    <p>{result.message}</p>
                  </div>
                </div>
                <div className="record-row">
                  <div className="row-label">Immediate Action</div>
                  <div className="row-value">
                    <p>{result.immediate_action}</p>
                  </div>
                </div>
                <div className="record-row">
                  <div className="row-label">How To Fix This Input</div>
                  <div className="row-value">
                    {result.classification_note && (
                      <>
                        <p>Classification note:</p>
                        <p>{result.classification_note}</p>
                      </>
                    )}
                    {result.missing_fields.length > 0 && (
                      <>
                        <p>Missing information:</p>
                        <ul className="formal-list">
                          {result.missing_fields.map((field) => (
                            <li key={field}>{formatMissingField(field)}</li>
                          ))}
                        </ul>
                      </>
                    )}
                    <p>{result.suggested_format}</p>
                    <ul className="formal-list">
                      {result.suggested_examples.map((example, idx) => (
                        <li key={idx}>{example}</li>
                      ))}
                    </ul>
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
