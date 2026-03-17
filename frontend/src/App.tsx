import { FormEvent, useState } from "react";

type InputMode = "guided" | "free_text";
type GuidedFactValue = string;
type GuidedSelectFactValue = "yes" | "no" | "unknown";

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
  input_type: "single_select" | "text";
  options?: Array<GuidedSelectFactValue>;
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
    value: string;
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
  schema_version: string;
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
    value: GuidedFactValue;
    label: string;
  }>;
  bo_precheck?: BOPrecheck;
  guided_conflict?: GuidedConflict;
  determining_condition_priority?: number | null;
  mli_ppt_review_required?: boolean;
  short_holding_period_review_required?: boolean;
  payment_date_unconfirmed?: boolean;
  calculated_threshold_met?: boolean | null;
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

type BOPrecheck = {
  status: "not_run" | "insufficient_facts" | "flagged_for_review" | "no_initial_flag";
  reason_code: string;
  reason_summary: string;
  facts_considered: Array<{
    fact_key: string;
    value: string;
  }>;
  review_note: string;
};

type GuidedConflict = {
  status: "conflict_detected";
  reason_code: string;
  reason_summary: string;
  structured_facts_win: boolean;
  conflicting_claims: string[];
};

type AnalyzeResponse =
  | {
      schema_version?: string;
      input_mode_used?: InputMode;
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
      schema_version?: string;
      input_mode_used?: InputMode;
      supported: true;
      review_state?: ReviewState;
      next_actions?: NextAction[];
      confirmed_scope?: ConfirmedScope;
      input_interpretation?: InputInterpretation;
      fact_completion_status?: FactCompletionStatus | null;
      change_summary?: ChangeSummary | null;
      fact_completion?: FactCompletion | null;
      user_declared_facts?: UserDeclaredFacts | null;
      bo_precheck?: BOPrecheck;
      guided_conflict?: GuidedConflict;
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
const GUIDED_FACT_CONFIG: Record<
  string,
  Array<{
    fact_key: string;
    prompt: string;
    input_type: "single_select" | "text";
  }>
> = {
  dividends: [
    {
      fact_key: "direct_holding_percentage",
      prompt: "What is the recipient's direct shareholding percentage in the paying company as of the payment date?",
      input_type: "text",
    },
    {
      fact_key: "payment_date",
      prompt: "What is the dividend payment date (or declared payment date)?",
      input_type: "text",
    },
    {
      fact_key: "holding_period_months",
      prompt: "How many months has the recipient continuously held the shares as of the payment date?",
      input_type: "text",
    },
    {
      fact_key: "beneficial_owner_confirmed",
      prompt: "Has beneficial-owner status been separately confirmed outside this tool?",
      input_type: "single_select",
    },
    {
      fact_key: "pe_effectively_connected",
      prompt:
        "Is the dividend effectively connected with a permanent establishment or fixed base of the Dutch recipient in China?",
      input_type: "single_select",
    },
    {
      fact_key: "holding_structure_is_direct",
      prompt:
        "Is the holding structure confirmed to be direct with no intermediate holding entity between the recipient and the paying company?",
      input_type: "single_select",
    },
    {
      fact_key: "mli_ppt_risk_flag",
      prompt:
        "Has a principal purpose test (PPT) risk assessment been performed for this dividend payment under the MLI?",
      input_type: "single_select",
    },
  ],
  interest: [
    {
      fact_key: "interest_character_confirmed",
      prompt: "Is the payment legally characterized as interest under the financing arrangement?",
      input_type: "single_select",
    },
    {
      fact_key: "beneficial_owner_status",
      prompt: "Has the recipient's beneficial-owner status for the interest income been separately confirmed?",
      input_type: "single_select",
    },
    {
      fact_key: "lending_documents_consistent",
      prompt:
        "Do the loan agreement, interest calculation, and payment records support the current interest characterization?",
      input_type: "single_select",
    },
  ],
  royalties: [
    {
      fact_key: "royalty_character_confirmed",
      prompt:
        "Is the payment actually for the use of, or the right to use, qualifying intellectual property?",
      input_type: "single_select",
    },
    {
      fact_key: "beneficial_owner_status",
      prompt: "Has the recipient's beneficial-owner status for the royalty income been separately confirmed?",
      input_type: "single_select",
    },
    {
      fact_key: "contract_payment_flow_consistent",
      prompt:
        "Do the contract, invoice, and payment flow support the current royalty characterization?",
      input_type: "single_select",
    },
  ],
};

export default function App() {
  const [submissionMode, setSubmissionMode] = useState<InputMode>("guided");
  const [guidedPayerCountry, setGuidedPayerCountry] = useState("CN");
  const [guidedPayeeCountry, setGuidedPayeeCountry] = useState("NL");
  const [guidedIncomeType, setGuidedIncomeType] = useState("dividends");
  const [guidedScenarioText, setGuidedScenarioText] = useState("");
  const [guidedFacts, setGuidedFacts] = useState<Record<string, GuidedFactValue>>({
    direct_holding_percentage: "",
    payment_date: "",
    holding_period_months: "",
    beneficial_owner_confirmed: "unknown",
    pe_effectively_connected: "unknown",
    holding_structure_is_direct: "unknown",
    mli_ppt_risk_flag: "unknown",
  });
  const [scenario, setScenario] = useState("");
  const [result, setResult] = useState<AnalyzeResponse | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState("");
  const [factSelections, setFactSelections] = useState<Record<string, string>>({});

  async function submitReview(
    factInputs?: Record<string, string>,
    modeOverride?: InputMode,
    guidedOverride?: {
      payer_country: string;
      payee_country: string;
      income_type: string;
      facts: Record<string, string>;
      scenario_text?: string;
    },
  ) {
    setIsLoading(true);
    setError("");

    try {
      const resolvedMode = modeOverride ?? submissionMode;
      const body =
        resolvedMode === "guided"
          ? {
              input_mode: "guided",
              guided_input:
                guidedOverride ?? {
                  payer_country: guidedPayerCountry,
                  payee_country: guidedPayeeCountry,
                  income_type: guidedIncomeType,
                  facts: guidedFacts,
                  ...(guidedScenarioText.trim()
                    ? { scenario_text: guidedScenarioText.trim() }
                    : {}),
                },
            }
          : { scenario };
      const response = await fetch("/api/analyze", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(body),
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
    if (submissionMode === "free_text" && !scenario.trim()) return;
    await submitReview(undefined, submissionMode);
  }

  async function handleFactCompletionSubmit() {
    if (!scenario.trim() || !result || !result.supported) return;
    await submitReview(undefined, "guided", {
      payer_country: result.normalized_input.payer_country,
      payee_country: result.normalized_input.payee_country,
      income_type: result.normalized_input.transaction_type,
      facts: factSelections,
      scenario_text: scenario.trim(),
    });
  }

  function buildInitialFactSelections(payload: AnalyzeResponse) {
    if (!payload.supported || !payload.fact_completion) {
      return {};
    }
    const nextSelections: Record<string, string> = {};
    for (const fact of payload.fact_completion.facts) {
      nextSelections[fact.fact_key] = fact.input_type === "text" ? "" : "unknown";
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

  function getGuidedFactsForIncomeType(incomeType: string) {
    return GUIDED_FACT_CONFIG[incomeType] ?? [];
  }

  function handleGuidedIncomeTypeChange(nextIncomeType: string) {
    setGuidedIncomeType(nextIncomeType);
    const nextFacts: Record<string, GuidedFactValue> = {};
    for (const fact of getGuidedFactsForIncomeType(nextIncomeType)) {
      nextFacts[fact.fact_key] = fact.input_type === "text" ? "" : "unknown";
    }
    setGuidedFacts(nextFacts);
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

  function formatFactValue(value: string) {
    if (value === "yes") return "yes";
    if (value === "no") return "no";
    if (value === "unknown") return "unknown";
    return value;
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

  function renderBOPrecheck(boPrecheck?: BOPrecheck) {
    if (!boPrecheck) {
      return null;
    }

    return (
      <div className="record-row highlight-row">
        <div className="row-label">BO Precheck</div>
        <div className="row-value">
          <p><strong>{boPrecheck.status}</strong></p>
          <p>{boPrecheck.reason_summary}</p>
          <ul className="formal-list">
            <li>Reason code: {boPrecheck.reason_code}</li>
            {boPrecheck.facts_considered.map((fact) => (
              <li key={fact.fact_key}>
                {fact.fact_key}: {fact.value}
              </li>
            ))}
            <li>{boPrecheck.review_note}</li>
          </ul>
        </div>
      </div>
    );
  }

  function renderGuidedConflict(guidedConflict?: GuidedConflict) {
    if (!guidedConflict) {
      return null;
    }

    return (
      <div className="record-row warning-row review-flagged">
        <div className="row-label">Guided Input Conflict</div>
        <div className="row-value">
          <p><strong>{guidedConflict.status}</strong></p>
          <p>{guidedConflict.reason_summary}</p>
          <ul className="formal-list">
            <li>Reason code: {guidedConflict.reason_code}</li>
            <li>Structured facts win: {guidedConflict.structured_facts_win ? "yes" : "no"}</li>
            {guidedConflict.conflicting_claims.map((claim, idx) => (
              <li key={idx}>{claim}</li>
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
                  {fact.input_type === "text" ? (
                    <input
                      id={`fact-${fact.fact_key}`}
                      type="text"
                      value={factSelections[fact.fact_key] ?? ""}
                      onChange={(event) =>
                        setFactSelections((current) => ({
                          ...current,
                          [fact.fact_key]: event.target.value,
                        }))
                      }
                    />
                  ) : (
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
                      {fact.options?.map((option) => (
                        <option key={option} value={option}>
                          {option}
                        </option>
                      ))}
                    </select>
                  )}
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
            {machineHandoff.determining_condition_priority !== undefined && (
              <li>
                Determining condition priority: {machineHandoff.determining_condition_priority ?? "n/a"}
              </li>
            )}
            {machineHandoff.mli_ppt_review_required !== undefined && (
              <li>
                MLI PPT review required: {machineHandoff.mli_ppt_review_required ? "yes" : "no"}
              </li>
            )}
            {machineHandoff.short_holding_period_review_required !== undefined && (
              <li>
                Short holding period review required: {machineHandoff.short_holding_period_review_required ? "yes" : "no"}
              </li>
            )}
            {machineHandoff.payment_date_unconfirmed !== undefined && (
              <li>
                Payment date unconfirmed: {machineHandoff.payment_date_unconfirmed ? "yes" : "no"}
              </li>
            )}
            {machineHandoff.calculated_threshold_met !== undefined && (
              <li>
                Calculated threshold met: {machineHandoff.calculated_threshold_met === null ? "n/a" : machineHandoff.calculated_threshold_met ? "yes" : "no"}
              </li>
            )}
            {machineHandoff.treaty_version && (
              <li>Treaty version: {machineHandoff.treaty_version}</li>
            )}
            {machineHandoff.mli_summary && (
              <li>MLI / PPT: {machineHandoff.mli_summary}</li>
            )}
            {machineHandoff.bo_precheck && (
              <li>BO precheck: {machineHandoff.bo_precheck.status}</li>
            )}
            {machineHandoff.guided_conflict && (
              <li>Guided conflict: {machineHandoff.guided_conflict.reason_code}</li>
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
              <span className="section-heading">I. Scenario Submission</span>
              <p className="section-desc">
                Guided input is the primary path. Legacy free-text remains available for demo and parser validation.
              </p>
              <div className="action-row">
                <button
                  type="button"
                  className="btn-seal"
                  onClick={() => setSubmissionMode("guided")}
                >
                  Guided Workspace
                </button>
                <button
                  type="button"
                  className="btn-seal"
                  onClick={() => setSubmissionMode("free_text")}
                >
                  Legacy Free-Text
                </button>
              </div>
            </div>

            {submissionMode === "guided" && (
              <div className="form-group">
                <div className="record-row">
                  <div className="row-label">
                    <label htmlFor="guided-payer">Payer jurisdiction</label>
                  </div>
                  <div className="row-value">
                    <select
                      id="guided-payer"
                      value={guidedPayerCountry}
                      onChange={(event) => setGuidedPayerCountry(event.target.value)}
                    >
                      <option value="CN">CN</option>
                      <option value="NL">NL</option>
                      <option value="SG">SG</option>
                      <option value="US">US</option>
                    </select>
                  </div>
                </div>
                <div className="record-row">
                  <div className="row-label">
                    <label htmlFor="guided-payee">Payee jurisdiction</label>
                  </div>
                  <div className="row-value">
                    <select
                      id="guided-payee"
                      value={guidedPayeeCountry}
                      onChange={(event) => setGuidedPayeeCountry(event.target.value)}
                    >
                      <option value="NL">NL</option>
                      <option value="CN">CN</option>
                      <option value="SG">SG</option>
                      <option value="US">US</option>
                    </select>
                  </div>
                </div>
                <div className="record-row">
                  <div className="row-label">
                    <label htmlFor="guided-income-type">Income type</label>
                  </div>
                  <div className="row-value">
                    <select
                      id="guided-income-type"
                      value={guidedIncomeType}
                      onChange={(event) => handleGuidedIncomeTypeChange(event.target.value)}
                    >
                      <option value="dividends">dividends</option>
                      <option value="interest">interest</option>
                      <option value="royalties">royalties</option>
                    </select>
                  </div>
                </div>

                {getGuidedFactsForIncomeType(guidedIncomeType).map((fact) => (
                  <div className="record-row" key={fact.fact_key}>
                    <div className="row-label">
                      <label htmlFor={`guided-fact-${fact.fact_key}`}>{fact.prompt}</label>
                    </div>
                    <div className="row-value">
                      {fact.input_type === "text" ? (
                        <input
                          id={`guided-fact-${fact.fact_key}`}
                          type="text"
                          value={guidedFacts[fact.fact_key] ?? ""}
                          onChange={(event) =>
                            setGuidedFacts((current) => ({
                              ...current,
                              [fact.fact_key]: event.target.value,
                            }))
                          }
                        />
                      ) : (
                        <select
                          id={`guided-fact-${fact.fact_key}`}
                          value={guidedFacts[fact.fact_key] ?? "unknown"}
                          onChange={(event) =>
                            setGuidedFacts((current) => ({
                              ...current,
                              [fact.fact_key]: event.target.value,
                            }))
                          }
                        >
                          <option value="yes">yes</option>
                          <option value="no">no</option>
                          <option value="unknown">unknown</option>
                        </select>
                      )}
                    </div>
                  </div>
                ))}

                <div className="record-row">
                  <div className="row-label">
                    <label htmlFor="guided-scenario-text">Supplemental scenario text</label>
                  </div>
                  <div className="row-value">
                    <textarea
                      id="guided-scenario-text"
                      rows={3}
                      value={guidedScenarioText}
                      onChange={(event) => setGuidedScenarioText(event.target.value)}
                      className="typewriter-input"
                    />
                  </div>
                </div>

                <div className="action-row">
                  <button
                    type="button"
                    disabled={isLoading}
                    className="btn-seal"
                    onClick={() => {
                      setSubmissionMode("guided");
                      void submitReview(undefined, "guided");
                    }}
                  >
                    {isLoading && submissionMode === "guided" ? "Running Review..." : "Run Guided Review"}
                  </button>
                </div>
              </div>
            )}

            <div className="form-group">
              {submissionMode !== "free_text" && (
                <p className="section-desc">Legacy free-text stays available as a secondary compatibility lane.</p>
              )}
              <label htmlFor="scenario-input" className="section-heading">
                Legacy Free-Text
                <span className="sr-only">Cross-border scenario</span>
              </label>
              <p className="section-desc">
                Use the older parser-oriented lane for demo and validation only.
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

              <div className="action-row">
                <button
                  type="button"
                  disabled={isLoading || !scenario.trim()}
                  className="btn-seal"
                  onClick={() => {
                    setSubmissionMode("free_text");
                    void submitReview(undefined, "free_text");
                  }}
                >
                  {isLoading && submissionMode === "free_text" ? "Running Review..." : "Run Review"}
                </button>
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
                      onClick={() => {
                        setSubmissionMode("free_text");
                        setScenario(example.scenario);
                      }}
                    >
                      <span className="example-state-tag">[{example.state}]</span>{" "}
                      [Ref. {String(i + 1).padStart(2, "0")}]: {example.scenario}
                    </button>
                    <p className="example-hint">{example.hint}</p>
                  </li>
                ))}
              </ul>
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

                {renderGuidedConflict(result.guided_conflict)}
                {renderBOPrecheck(result.bo_precheck)}
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
