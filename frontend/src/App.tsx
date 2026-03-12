import { FormEvent, useState } from "react";

type ReviewState = {
  state_code:
    | "pre_review_complete"
    | "can_be_completed"
    | "partial_review"
    | "needs_human_intervention"
    | "out_of_scope";
  state_label_zh: string;
  state_summary: string;
};

type NextAction = {
  priority: "high" | "medium" | "low";
  action: string;
  reason: string;
};

type ConfirmedScope = {
  applicable_treaty: string;
  applicable_article: string;
  payment_direction: string;
  income_type: string;
};

type FactCompletionQuestion = {
  fact_key: string;
  prompt: string;
  input_type: "single_select";
  options: Array<"yes" | "no" | "unknown">;
};

type FactCompletion = {
  flow_type: "bounded_form";
  session_type: "pseudo_multiturn";
  user_declaration_note: string;
  facts: FactCompletionQuestion[];
};

type UserDeclaredFacts = {
  declaration_label: string;
  facts: Array<{
    fact_key: string;
    value: "yes" | "no" | "unknown";
    label: string;
  }>;
};

type FactCompletionStatus = {
  status_code:
    | "awaiting_user_facts"
    | "completed_narrowed"
    | "terminated_unknown_facts"
    | "terminated_pe_exclusion"
    | "terminated_beneficial_owner_unconfirmed"
    | "terminated_conflicting_user_facts";
  status_label_zh: string;
  status_summary: string;
};

type ChangeSummary = {
  summary_label: string;
  state_change: string;
  rate_change: string;
  trigger_facts: string[];
};

type SourceTrace = {
  treaty_full_name: string;
  version_note: string;
  source_document_title: string;
  language_version: string;
  official_source_ids: string[];
  protocol_note: string | null;
  working_paper_ref: string | null;
};

type MLIContext = {
  covered_tax_agreement: boolean;
  ppt_applies: boolean;
  summary: string;
  human_review_note: string;
  official_source_ids: string[];
};

type MachineHandoff = {
  schema_version: "stage5.v1";
  record_kind: "supported" | "unsupported" | "incomplete";
  review_state_code: ReviewState["state_code"];
  recommended_route:
    | "standard_review"
    | "complete_facts_then_rerun"
    | "manual_review"
    | "out_of_scope_rewrite";
  applicable_treaty: string | null;
  payment_direction: string | null;
  income_type: string | null;
  article_number: string | null;
  article_title: string | null;
  rate_display: string | null;
  auto_conclusion_allowed: boolean;
  human_review_required: boolean;
  data_source_used: "stable" | "llm_generated";
  source_reference: string | null;
  source_excerpt?: string | null;
  treaty_version?: string | null;
  mli_summary?: string | null;
  review_priority: "none" | "normal" | "high";
  blocking_facts: string[];
  next_actions: NextAction[];
  user_declared_facts: Array<{
    fact_key: string;
    value: "yes" | "no" | "unknown";
    label: string;
  }>;
};

type HumanReviewBrief = {
  brief_title: string;
  headline: string;
  disposition: string;
  summary_lines: string[];
  facts_to_verify: string[];
  handoff_note: string;
};

type HandoffPackage = {
  machine_handoff: MachineHandoff;
  human_review_brief: HumanReviewBrief;
};

type AnalyzeResponse =
  | {
      supported: false;
      review_state?: ReviewState;
      next_actions?: NextAction[];
      handoff_package?: HandoffPackage;
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
      review_state?: ReviewState;
      next_actions?: NextAction[];
      confirmed_scope?: ConfirmedScope;
      input_interpretation?: InputInterpretation;
      fact_completion_status?: FactCompletionStatus | null;
      change_summary?: ChangeSummary | null;
      fact_completion?: FactCompletion | null;
      user_declared_facts?: UserDeclaredFacts | null;
      handoff_package?: HandoffPackage;
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
        source_trace?: SourceTrace;
        mli_context?: MLIContext;
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
        alternative_rate_candidates?: {
          source_reference: string;
          rate: string;
          conditions: string[];
        }[];
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
    hint: "Second pilot pair example for China-Singapore treaty review.",
    scenario: "中国居民企业向新加坡公司支付特许权使用费",
  },
  {
    state: "Unsupported",
    hint: "Shows how the tool refuses scenarios outside the current pilot treaty-pair scope.",
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
  const [factSelections, setFactSelections] = useState<Record<string, string>>({});

  async function submitReview(factInputs?: Record<string, string>) {
    setIsLoading(true);
    setError("");

    try {
      const response = await fetch("/api/analyze", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(
          factInputs
            ? { scenario, fact_inputs: factInputs }
            : { scenario },
        ),
      });

      if (!response.ok) {
        throw new Error("Request failed.");
      }

      const payload = (await response.json()) as AnalyzeResponse;
      setResult(payload);
      setFactSelections(buildInitialFactSelections(payload));
    } catch {
      setError("The review request failed. Check that the backend service is running.");
      setResult(null);
      setFactSelections({});
    } finally {
      setIsLoading(false);
    }
  }

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!scenario.trim()) return;
    await submitReview();
  }

  async function handleFactCompletionSubmit() {
    if (!scenario.trim()) return;
    await submitReview(factSelections);
  }

  function buildInitialFactSelections(payload: AnalyzeResponse) {
    if (!payload.supported || !payload.fact_completion) {
      return {};
    }
    const nextSelections: Record<string, string> = {};
    for (const fact of payload.fact_completion.facts) {
      nextSelections[fact.fact_key] = "unknown";
    }
    return nextSelections;
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
    if (!result.auto_conclusion_allowed && result.alternative_rate_candidates && result.alternative_rate_candidates.length > 0) {
      return "[ HOLD ] Multiple treaty branches require manual selection";
    }
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
    if (!result.auto_conclusion_allowed && result.alternative_rate_candidates && result.alternative_rate_candidates.length > 0) {
      return "MANUAL BRANCH REVIEW REQUIRED";
    }
    if (!result.auto_conclusion_allowed) {
      return "PROVISIONAL REVIEW ONLY";
    }
    if (result.review_priority === "high") {
      return "PRIORITY REVIEW REQUIRED";
    }
    return "TREATY MATCH";
  }

  function getSupportedRecordStamp(result: Extract<AnalyzeResponse, { supported: true }>["result"]) {
    if (result.review_priority === "high" && result.auto_conclusion_allowed) {
      return "REVIEW";
    }
    return result.auto_conclusion_allowed ? "SUPPORTED" : "HOLD";
  }

  function getRateLabel(result: Extract<AnalyzeResponse, { supported: true }>["result"]) {
    if (result.alternative_rate_candidates && result.alternative_rate_candidates.length > 0) {
      return "Possible Treaty Rates";
    }
    return result.auto_conclusion_allowed ? "Treaty Rate Ceiling" : "Indicative Treaty Rate";
  }

  function formatMissingField(field: string) {
    return FIELD_LABELS[field] ?? field;
  }

  function formatActionPriority(priority: NextAction["priority"]) {
    if (priority === "high") return "High";
    if (priority === "medium") return "Medium";
    return "Low";
  }

  function formatFactValue(value: "yes" | "no" | "unknown") {
    if (value === "yes") return "yes";
    if (value === "no") return "no";
    return "unknown";
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

  function renderReviewStateBlock(reviewState?: ReviewState) {
    if (!reviewState) {
      return null;
    }

    return (
      <div className="record-row highlight-row">
        <div className="row-label">Review State</div>
        <div className="row-value">
          <p><strong>{reviewState.state_label_zh}</strong></p>
          <p>{reviewState.state_summary}</p>
        </div>
      </div>
    );
  }

  function renderConfirmedScope(confirmedScope?: ConfirmedScope) {
    if (!confirmedScope) {
      return null;
    }

    return (
      <div className="record-row">
        <div className="row-label">Confirmed Scope</div>
        <div className="row-value">
          <ul className="formal-list">
            <li>Treaty: {confirmedScope.applicable_treaty}</li>
            <li>Article: {confirmedScope.applicable_article}</li>
            <li>Direction: {confirmedScope.payment_direction}</li>
            <li>Income type: {confirmedScope.income_type}</li>
          </ul>
        </div>
      </div>
    );
  }

  function renderSourceChain(
    sourceTrace?: SourceTrace,
    mliContext?: MLIContext,
  ) {
    if (!sourceTrace && !mliContext) {
      return null;
    }

    return (
      <div className="record-row">
        <div className="row-label">Source Chain</div>
        <div className="row-value">
          {sourceTrace && (
            <ul className="formal-list">
              <li>Treaty text: {sourceTrace.treaty_full_name}</li>
              <li>Version note: {sourceTrace.version_note}</li>
              <li>Source document: {sourceTrace.source_document_title}</li>
              <li>Language version: {sourceTrace.language_version}</li>
              <li>Official source ids: {sourceTrace.official_source_ids.join(", ")}</li>
              {sourceTrace.protocol_note && <li>Protocol context: {sourceTrace.protocol_note}</li>}
              {sourceTrace.working_paper_ref && <li>Working paper: {sourceTrace.working_paper_ref}</li>}
            </ul>
          )}
          {mliContext && (
            <>
              <p><strong>MLI / PPT</strong></p>
              <ul className="formal-list">
                <li>Covered tax agreement: {mliContext.covered_tax_agreement ? "yes" : "no"}</li>
                <li>PPT applies: {mliContext.ppt_applies ? "yes" : "no"}</li>
                <li>{mliContext.summary}</li>
                <li>{mliContext.human_review_note}</li>
                <li>MLI source ids: {mliContext.official_source_ids.join(", ")}</li>
              </ul>
            </>
          )}
        </div>
      </div>
    );
  }

  function renderNextActions(nextActions?: NextAction[]) {
    if (!nextActions || nextActions.length === 0) {
      return null;
    }

    return (
      <div className="record-row">
        <div className="row-label">Next Actions</div>
        <div className="row-value">
          <ul className="formal-list">
            {nextActions.map((item, idx) => (
              <li key={idx}>
                [{formatActionPriority(item.priority)}] {item.action} — {item.reason}
              </li>
            ))}
          </ul>
        </div>
      </div>
    );
  }

  function renderUserDeclaredFacts(userDeclaredFacts?: UserDeclaredFacts | null) {
    if (!userDeclaredFacts || userDeclaredFacts.facts.length === 0) {
      return null;
    }

    return (
      <div className="record-row">
        <div className="row-label">{userDeclaredFacts.declaration_label}</div>
        <div className="row-value">
          <ul className="formal-list">
            {userDeclaredFacts.facts.map((fact) => (
              <li key={fact.fact_key}>
                {fact.label} {"->"} {formatFactValue(fact.value)}
              </li>
            ))}
          </ul>
        </div>
      </div>
    );
  }

  function renderFactCompletionStatus(
    factCompletionStatus?: FactCompletionStatus | null,
  ) {
    if (!factCompletionStatus) {
      return null;
    }

    return (
      <div className="record-row highlight-row">
        <div className="row-label">Fact Completion Status</div>
        <div className="row-value">
          <p><strong>{factCompletionStatus.status_label_zh}</strong></p>
          <p>{factCompletionStatus.status_summary}</p>
        </div>
      </div>
    );
  }

  function renderChangeSummary(changeSummary?: ChangeSummary | null) {
    if (!changeSummary) {
      return null;
    }

    return (
      <div className="record-row">
        <div className="row-label">{changeSummary.summary_label}</div>
        <div className="row-value">
          <ul className="formal-list">
            <li>{changeSummary.state_change}</li>
            <li>{changeSummary.rate_change}</li>
            {changeSummary.trigger_facts.map((fact, idx) => (
              <li key={idx}>{fact}</li>
            ))}
          </ul>
        </div>
      </div>
    );
  }

  function renderFactCompletion(
    supportedResult: Extract<AnalyzeResponse, { supported: true }>,
  ) {
    if (!supportedResult.fact_completion) {
      return null;
    }

    return (
      <div className="record-row highlight-row">
        <div className="row-label">Complete Missing Facts</div>
        <div className="row-value">
          <p>{supportedResult.fact_completion.user_declaration_note}</p>
          <div>
            {supportedResult.fact_completion.facts.map((fact) => (
              <div key={fact.fact_key}>
                <label htmlFor={`fact-${fact.fact_key}`}>{fact.prompt}</label>
                <div>
                  <select
                    id={`fact-${fact.fact_key}`}
                    value={factSelections[fact.fact_key] ?? "unknown"}
                    onChange={(event) =>
                      setFactSelections((current) => ({
                        ...current,
                        [fact.fact_key]: event.target.value,
                      }))
                    }
                  >
                    {fact.options.map((option) => (
                      <option key={option} value={option}>
                        {option}
                      </option>
                    ))}
                  </select>
                </div>
              </div>
            ))}
          </div>
          <div className="action-row">
            <button
              type="button"
              className="btn-seal"
              onClick={() => void handleFactCompletionSubmit()}
              disabled={isLoading}
            >
              {isLoading ? "Running Review..." : "Re-run With These Facts"}
            </button>
          </div>
        </div>
      </div>
    );
  }

  function renderWorkflowHandoff(handoffPackage?: HandoffPackage) {
    if (!handoffPackage) {
      return null;
    }

    const { machine_handoff: machineHandoff, human_review_brief: humanReviewBrief } = handoffPackage;

    return (
      <div className="record-row highlight-row">
        <div className="row-label">Workflow Handoff</div>
        <div className="row-value">
          <p><strong>{humanReviewBrief.brief_title}</strong></p>
          <p>{humanReviewBrief.headline}</p>
          <p>{humanReviewBrief.disposition}</p>
          <ul className="formal-list">
            <li>Recommended route: {machineHandoff.recommended_route}</li>
            <li>Record kind: {machineHandoff.record_kind}</li>
            <li>Review state: {machineHandoff.review_state_code}</li>
            <li>Data source: {machineHandoff.data_source_used}</li>
            {machineHandoff.article_number && machineHandoff.article_title && (
              <li>
                Article lane: {machineHandoff.article_number} · {machineHandoff.article_title}
              </li>
            )}
            {machineHandoff.rate_display && (
              <li>Rate display: {machineHandoff.rate_display}</li>
            )}
            {machineHandoff.treaty_version && (
              <li>Treaty version: {machineHandoff.treaty_version}</li>
            )}
            {machineHandoff.mli_summary && (
              <li>MLI / PPT: {machineHandoff.mli_summary}</li>
            )}
          </ul>
          {humanReviewBrief.summary_lines.length > 0 && (
            <>
              <p>Summary lines:</p>
              <ul className="formal-list">
                {humanReviewBrief.summary_lines.map((line, idx) => (
                  <li key={`summary-${idx}`}>{line}</li>
                ))}
              </ul>
            </>
          )}
          {humanReviewBrief.facts_to_verify.length > 0 && (
            <>
              <p>Facts to verify:</p>
              <ul className="formal-list">
                {humanReviewBrief.facts_to_verify.map((fact, idx) => (
                  <li key={`fact-${idx}`}>{fact}</li>
                ))}
              </ul>
            </>
          )}
          {machineHandoff.user_declared_facts.length > 0 && (
            <>
              <p>Unverified user-declared facts:</p>
              <ul className="formal-list">
                {machineHandoff.user_declared_facts.map((fact) => (
                  <li key={fact.fact_key}>
                    {fact.label} {"->"} {formatFactValue(fact.value)}
                  </li>
                ))}
              </ul>
            </>
          )}
          <p>{humanReviewBrief.handoff_note}</p>
        </div>
      </div>
    );
  }

  return (
    <div className="document-body">
      <header className="memo-header">
        <div className="memo-stamp">
          <span className="stamp-seal">TTA-MVP</span>
          <span className="stamp-date">SCOPE: CN-NL / CN-SG</span>
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
                {renderReviewStateBlock(result.review_state)}
                {renderFactCompletionStatus(result.fact_completion_status)}

                <div className="record-row highlight-row">
                  <div className="row-label">Preliminary View</div>
                  <div className="row-value">
                    <p>{result.result.summary}</p>
                  </div>
                </div>

                {renderInputInterpretation(result.input_interpretation)}
                {renderConfirmedScope(result.confirmed_scope)}
                {renderSourceChain(result.result.source_trace, result.result.mli_context)}
                {renderUserDeclaredFacts(result.user_declared_facts)}
                {renderChangeSummary(result.change_summary)}

                <div className="record-row">
                  <div className="row-label">Immediate Action</div>
                  <div className="row-value">
                    <p>{result.result.immediate_action}</p>
                  </div>
                </div>

                {renderNextActions(result.next_actions)}
                {renderFactCompletion(result)}
                {renderWorkflowHandoff(result.handoff_package)}

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

                {result.result.alternative_rate_candidates &&
                  result.result.alternative_rate_candidates.length > 0 && (
                    <div className="record-row">
                      <div className="row-label">Alternative Rate Candidates</div>
                      <div className="row-value">
                        <ul className="formal-list">
                          {result.result.alternative_rate_candidates.map((candidate, idx) => (
                            <li key={idx}>
                              {candidate.rate} · {candidate.source_reference}
                              {candidate.conditions.length > 0 && (
                                <>
                                  {" "}
                                  — {candidate.conditions.join(" ")}
                                </>
                              )}
                            </li>
                          ))}
                        </ul>
                      </div>
                    </div>
                  )}

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
                {renderReviewStateBlock(result.review_state)}
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
                {renderNextActions(result.next_actions)}
                {renderWorkflowHandoff(result.handoff_package)}
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
