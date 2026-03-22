import { FormEvent, useEffect, useState } from "react";
import {
  type AnalyzeResponse,
  type BOPrecheck,
  type ChangeSummary,
  type ConfirmedScope,
  type FactCompletionStatus,
  type GuidedFactValue,
  type GuidedConflict,
  type HandoffPackage,
  type InputInterpretation,
  type InputMode,
  type MLIContext,
  type SourceTrace,
  type NextAction,
  type ReviewState,
  type UserDeclaredFacts,
  GUIDED_FACT_CONFIG,
} from "./generated/contract";

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
const REFERENCE_GUIDED_PRESETS = {
  中国居民企业向荷兰支付特许权使用费: {
    payer_country: "CN",
    payee_country: "NL",
    income_type: "royalties" as GuidedIncomeType,
  },
  中国居民企业向新加坡公司支付特许权使用费: {
    payer_country: "CN",
    payee_country: "SG",
    income_type: "royalties" as GuidedIncomeType,
  },
  中国居民企业向美国支付特许权使用费: {
    payer_country: "CN",
    payee_country: "US",
    income_type: "royalties" as GuidedIncomeType,
  },
  向荷兰公司支付股息: {
    payer_country: "",
    payee_country: "NL",
    income_type: "dividends" as GuidedIncomeType,
  },
} satisfies Record<
  (typeof REFERENCE_ARCHIVES)[number]["scenario"],
  {
    payer_country: string;
    payee_country: string;
    income_type: GuidedIncomeType;
  }
>;
const FIELD_LABELS: Record<string, string> = {
  payer_country: "Payer country",
  payee_country: "Payee country",
  transaction_type: "Income type",
};
const GUIDED_FACT_PROMPTS = Object.entries(GUIDED_FACT_CONFIG).reduce<
  Record<string, Record<string, string>>
>((accumulator, [incomeType, fields]) => {
  accumulator[incomeType] = fields.reduce<Record<string, string>>((fieldAccumulator, field) => {
    fieldAccumulator[field.fact_key] = field.prompt;
    return fieldAccumulator;
  }, {});
  return accumulator;
}, {});
type GuidedIncomeType = keyof typeof GUIDED_FACT_CONFIG;

type AnalyzeRequestPayload = {
  input_mode?: InputMode;
  scenario?: string;
  guided_input?: {
    payer_country: string;
    payee_country: string;
    income_type: string;
    facts: Record<string, string>;
    scenario_text?: string;
  };
};

type CaseCreateResponse = {
  case_id: string;
  saved_at: string;
  creator_token: string;
  reviewer_token: string;
  analyze_response_snapshot: AnalyzeResponse;
};

type SavedCaseView = {
  case_id: string;
  saved_at: string;
  schema_version: string;
  input_mode_used: InputMode;
  view_role: "creator" | "reviewer";
  reviewer_share_ready: boolean;
  request_snapshot: AnalyzeRequestPayload;
  response_snapshot: AnalyzeResponse;
};

type SavedCaseLinks = {
  case_id: string;
  saved_at: string;
  creator_link: string;
  reviewer_link: string;
  creator_workpaper_link: string;
  reviewer_workpaper_link: string;
};

type SavedMachineHandoff = HandoffPackage["machine_handoff"];
type SavedAuthorityMemo = NonNullable<HandoffPackage["authority_memo"]>;
type ReviewerRiskSummary = {
  items: string[];
  escalated: boolean;
  recommendedRoute: string;
  reviewPriority: string;
};

function buildGuidedFactState(incomeType: GuidedIncomeType): Record<string, GuidedFactValue> {
  const nextFacts: Record<string, GuidedFactValue> = {};
  for (const fact of GUIDED_FACT_CONFIG[incomeType]) {
    nextFacts[fact.fact_key] = fact.input_type === "text" ? "" : "unknown";
  }
  return nextFacts;
}

function getCaseAccessParams() {
  const params = new URLSearchParams(window.location.search);
  const caseId = params.get("case");
  const token = params.get("token");
  if (!caseId || !token) {
    return null;
  }
  return { caseId, token };
}

function buildCaseLink(caseId: string, token: string) {
  const url = new URL(window.location.href);
  url.search = "";
  url.hash = "";
  url.searchParams.set("case", caseId);
  url.searchParams.set("token", token);
  return url.toString();
}

function buildWorkpaperLink(caseId: string, token: string) {
  return `/api/cases/${encodeURIComponent(caseId)}/workpaper?token=${encodeURIComponent(token)}`;
}

function getGuidedFactPrompt(incomeType: string | undefined, factKey: string) {
  return GUIDED_FACT_PROMPTS[incomeType ?? ""]?.[factKey] ?? factKey;
}

function applyReferencePreset(
  scenario: (typeof REFERENCE_ARCHIVES)[number]["scenario"],
  setGuidedPayerCountry: (value: string) => void,
  setGuidedPayeeCountry: (value: string) => void,
  setGuidedIncomeType: (value: GuidedIncomeType) => void,
  setGuidedFacts: (value: Record<string, GuidedFactValue>) => void,
  setGuidedScenarioText: (value: string) => void,
  setShowLegacyParserValidation: (value: boolean) => void,
  setSubmissionMode: (value: InputMode) => void,
  setScenario: (value: string) => void,
) {
  const preset = REFERENCE_GUIDED_PRESETS[scenario];
  setGuidedPayerCountry(preset.payer_country);
  setGuidedPayeeCountry(preset.payee_country);
  setGuidedIncomeType(preset.income_type);
  setGuidedFacts(buildGuidedFactState(preset.income_type));
  setGuidedScenarioText(scenario);
  setShowLegacyParserValidation(false);
  setSubmissionMode("guided");
  setScenario("");
}

function formatSavedCaseRole(viewRole: SavedCaseView["view_role"]) {
  return viewRole === "creator" ? "Creator read-only package" : "Reviewer read-only package";
}

function getSavedCaseAccessNote(viewRole: SavedCaseView["view_role"]) {
  if (viewRole === "creator") {
    return "This creator link stays read-only and is meant for the internal case owner.";
  }
  return "This reviewer link is a read-only package for downstream review and printable export.";
}

function combineRiskNotes(primary?: string | null, secondary?: string | null) {
  const notes = [primary, secondary].filter(
    (item, index, items): item is string => Boolean(item) && items.indexOf(item) === index,
  );
  return notes.join(" ");
}

function formatAuthorityCoverageGap(
  gap: SavedAuthorityMemo["coverage_gaps"][number],
) {
  return `${gap.topic} (${gap.reason_code})`;
}

function buildReviewerRiskItems(
  machineHandoff?: SavedMachineHandoff,
  authorityMemo?: SavedAuthorityMemo,
) {
  const items: string[] = [];
  const boPrecheck = machineHandoff?.bo_precheck;

  if (boPrecheck) {
    const note = combineRiskNotes(boPrecheck.reason_summary, boPrecheck.review_note);
    if (note) {
      items.push(`BO precheck (${boPrecheck.status}): ${note}`);
    }
  }

  if (machineHandoff?.guided_conflict) {
    items.push(`Guided input conflict: ${machineHandoff.guided_conflict.reason_summary}`);
  }

  if (authorityMemo?.coverage_gaps.length) {
    items.push(
      `Authority memo gaps: ${authorityMemo.coverage_gaps.map(formatAuthorityCoverageGap).join("; ")}`,
    );
  }

  if (machineHandoff?.recommended_route && machineHandoff.recommended_route !== "standard_review") {
    items.push(`Machine handoff route remains ${machineHandoff.recommended_route}.`);
  }
  if (machineHandoff?.review_priority === "high") {
    items.push("Machine handoff keeps this case at high review priority.");
  }
  if (machineHandoff?.mli_ppt_review_required) {
    items.push("MLI / PPT review is still required.");
  }
  if (machineHandoff?.short_holding_period_review_required) {
    items.push("Short holding period review is still required.");
  }
  if (machineHandoff?.payment_date_unconfirmed) {
    items.push("Payment date remains unconfirmed in the saved snapshot.");
  }
  if (machineHandoff?.calculated_threshold_met === false) {
    items.push("Saved facts do not support the reduced-rate threshold.");
  } else if (
    machineHandoff?.calculated_threshold_met === null &&
    machineHandoff?.determining_condition_priority !== undefined
  ) {
    items.push("Saved facts still do not let the tool confirm the reduced-rate threshold.");
  }

  return items;
}

function buildReviewerRiskSummary(result: AnalyzeResponse): ReviewerRiskSummary {
  const machineHandoff = result.handoff_package?.machine_handoff;
  const authorityMemo = result.handoff_package?.authority_memo;
  const items = buildReviewerRiskItems(machineHandoff, authorityMemo);
  const escalated =
    machineHandoff?.recommended_route === "manual_review" ||
    machineHandoff?.review_priority === "high" ||
    Boolean(machineHandoff?.guided_conflict);

  return {
    items,
    escalated,
    recommendedRoute: machineHandoff?.recommended_route ?? "not_recorded",
    reviewPriority: machineHandoff?.review_priority ?? "not_recorded",
  };
}

type OnboardingManifestSummary = {
  manifest_path: string;
  pair_id: string;
  mode: "shadow_rebuild" | "initial_onboarding";
  jurisdictions: string[];
  target_articles: string[];
  baseline_enabled: boolean;
  source_build_manifest_path: string;
  source_build_available: boolean;
};

type OnboardingWorkspace = {
  manifest: OnboardingManifestSummary & {
    source_documents: string[];
    promotion_target_dataset: string;
    baseline_reference: string | null;
  };
  source_bundle_summary?: {
    document_count: number;
    compile_target_count: number;
    compile_target_roles: string[];
    roles?: string[];
  };
  authority_coverage?: {
    configured_topic_count: number;
    mapped_topic_count?: number;
    gap_topics: string[];
  };
  protocol_override_count?: number;
  source_build: {
    available: boolean;
    manifest_path: string;
    report: Record<string, unknown> | null;
    status: string | null;
  };
  compile: {
    status: string | null;
    report: Record<string, unknown> | null;
    delta_report: Record<string, unknown> | null;
    delta_analysis: Array<Record<string, unknown>>;
  };
  review: {
    status: string | null;
    report: Record<string, unknown> | null;
    diff: Record<string, unknown> | null;
  };
  approval: {
    status: string | null;
    record: Record<string, unknown> | null;
  };
  promotion: {
    status: string | null;
    record: Record<string, unknown> | null;
  };
  timing: {
    status: string | null;
    review_session_active: boolean;
    durations: {
      review_seconds: number | null;
      end_to_end_seconds: number | null;
    };
    record?: Record<string, unknown> | null;
  };
  reviewed_source: {
    path: string;
    content: string | null;
  };
};

async function readApiJson<T>(url: string, init?: RequestInit): Promise<T> {
  const response = await fetch(url, init);
  const payload = await response.json().catch(() => null);
  if (!response.ok) {
    const detail =
      payload && typeof payload === "object" && "detail" in payload
        ? String((payload as { detail?: unknown }).detail ?? "Request failed.")
        : "Request failed.";
    throw new Error(detail);
  }
  return payload as T;
}

function isInternalOnboardingMode() {
  return new URLSearchParams(window.location.search).get("internal") === "onboarding";
}

function formatWorkspaceStatus(status?: string | null) {
  return status ?? "not_run";
}

function formatTimingSeconds(seconds?: number | null) {
  if (seconds === null || seconds === undefined) {
    return "not_measured";
  }
  return `${seconds}s`;
}

function InternalOnboardingWorkspace() {
  const [manifests, setManifests] = useState<OnboardingManifestSummary[]>([]);
  const [selectedManifest, setSelectedManifest] = useState("");
  const [workspace, setWorkspace] = useState<OnboardingWorkspace | null>(null);
  const [reviewedSourceJson, setReviewedSourceJson] = useState("");
  const [reviewerName, setReviewerName] = useState("Codex Reviewer");
  const [approvalNote, setApprovalNote] = useState("Approved after reviewer workspace check.");
  const [error, setError] = useState("");
  const [isLoading, setIsLoading] = useState(false);

  useEffect(() => {
    void loadManifests();
  }, []);

  async function loadManifests() {
    setIsLoading(true);
    setError("");
    try {
      const payload = await readApiJson<{ manifests: OnboardingManifestSummary[] }>(
        "/api/internal/onboarding/manifests",
      );
      setManifests(payload.manifests);
      const nextManifest = selectedManifest || payload.manifests[0]?.manifest_path;
      if (nextManifest) {
        await loadWorkspace(nextManifest);
      }
    } catch (nextError) {
      setError(nextError instanceof Error ? nextError.message : "Failed to load onboarding manifests.");
    } finally {
      setIsLoading(false);
    }
  }

  async function loadWorkspace(manifestPath: string) {
    const payload = await readApiJson<OnboardingWorkspace>(
      `/api/internal/onboarding/workspace?manifest=${encodeURIComponent(manifestPath)}`,
    );
    setSelectedManifest(manifestPath);
    setWorkspace(payload);
    setReviewedSourceJson(payload.reviewed_source.content ?? "");
  }

  async function runWorkspaceAction(
    endpoint: string,
    body: Record<string, unknown>,
  ) {
    setIsLoading(true);
    setError("");
    try {
      const payload = await readApiJson<OnboardingWorkspace>(endpoint, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(body),
      });
      setWorkspace(payload);
      setReviewedSourceJson(payload.reviewed_source.content ?? "");
    } catch (nextError) {
      setError(nextError instanceof Error ? nextError.message : "Internal onboarding action failed.");
    } finally {
      setIsLoading(false);
    }
  }

  return (
    <div className="app-shell">
      <main className="workspace-layout">
        <section className="input-section">
          <div className="section-heading">Internal Onboarding Workspace</div>
          <p className="section-desc">
            Internal-only reviewer surface for source build, compile, review, approval, and promotion.
          </p>

          <div className="record-row">
            <div className="row-label">
              <label htmlFor="onboarding-manifest">Onboarding manifest</label>
            </div>
            <div className="row-value">
              <select
                id="onboarding-manifest"
                value={selectedManifest}
                onChange={(event) => {
                  void loadWorkspace(event.target.value);
                }}
              >
                {manifests.map((manifest) => (
                  <option key={manifest.manifest_path} value={manifest.manifest_path}>
                    {manifest.pair_id} · {manifest.mode}
                  </option>
                ))}
              </select>
            </div>
          </div>

          {workspace && (
            <>
              <div className="record-row">
                <div className="row-label">Manifest summary</div>
                <div className="row-value">
                  <ul className="formal-list">
                    <li>Pair: {workspace.manifest.pair_id}</li>
                    <li>Mode: {workspace.manifest.mode}</li>
                    <li>Jurisdictions: {workspace.manifest.jurisdictions.join(" -> ")}</li>
                    <li>Target articles: {workspace.manifest.target_articles.join(", ")}</li>
                    <li>Baseline enabled: {workspace.manifest.baseline_enabled ? "yes" : "no"}</li>
                    <li>Source build available: {workspace.manifest.source_build_available ? "yes" : "no"}</li>
                    <li>Promotion target: {workspace.manifest.promotion_target_dataset}</li>
                  </ul>
                </div>
              </div>

              <div className="record-row">
                <div className="row-label">Source bundle summary</div>
                <div className="row-value">
                  <ul className="formal-list">
                    <li>Documents: {workspace.source_bundle_summary?.document_count ?? 0}</li>
                    <li>Compile targets: {workspace.source_bundle_summary?.compile_target_count ?? 0}</li>
                    <li>
                      Compile target roles:{" "}
                      {workspace.source_bundle_summary?.compile_target_roles?.join(", ") || "none"}
                    </li>
                    <li>Protocol overrides: {workspace.protocol_override_count ?? 0}</li>
                  </ul>
                </div>
              </div>

              <div className="record-row">
                <div className="row-label">Authority coverage</div>
                <div className="row-value">
                  <ul className="formal-list">
                    <li>Configured topics: {workspace.authority_coverage?.configured_topic_count ?? 0}</li>
                    <li>Mapped topics: {workspace.authority_coverage?.mapped_topic_count ?? 0}</li>
                    <li>
                      Gap topics:{" "}
                      {(workspace.authority_coverage?.gap_topics.length ?? 0) > 0
                        ? workspace.authority_coverage?.gap_topics?.join(", ")
                        : "none"}
                    </li>
                  </ul>
                </div>
              </div>

              <div className="record-row highlight-row">
                <div className="row-label">Pipeline status</div>
                <div className="row-value">
                  <ul className="formal-list">
                    <li>Source build: {formatWorkspaceStatus(workspace.source_build.status)}</li>
                    <li>Compile: {formatWorkspaceStatus(workspace.compile.status)}</li>
                    <li>Review: {formatWorkspaceStatus(workspace.review.status)}</li>
                    <li>Approval: {formatWorkspaceStatus(workspace.approval.status)}</li>
                    <li>Promotion: {formatWorkspaceStatus(workspace.promotion.status)}</li>
                  </ul>
                </div>
              </div>

              {workspace.compile.delta_report && (
                <div className="record-row">
                  <div className="row-label">Compiled delta summary</div>
                  <div className="row-value">
                    <ul className="formal-list">
                      <li>
                        Delta items: {String(workspace.compile.delta_report["delta_item_count"] ?? 0)}
                      </li>
                      <li>
                        High materiality: {String(workspace.compile.delta_report["high_materiality_count"] ?? 0)}
                      </li>
                    </ul>
                    {workspace.compile.delta_analysis.length > 0 && (
                      <ul className="formal-list">
                        {workspace.compile.delta_analysis.map((item, index) => (
                          <li key={`${item["article_number"] ?? "delta"}-${index}`}>
                            {String(item["article_number"] ?? "n/a")} · {String(item["delta_type"] ?? "n/a")} ·{" "}
                            {String(item["summary"] ?? "")}
                          </li>
                        ))}
                      </ul>
                    )}
                  </div>
                </div>
              )}

              <div className="record-row">
                <div className="row-label">Timing summary</div>
                <div className="row-value">
                  <ul className="formal-list">
                    <li>Status: {workspace.timing.status ?? "not_started"}</li>
                    <li>Review session active: {workspace.timing.review_session_active ? "yes" : "no"}</li>
                    <li>Reviewer elapsed: {formatTimingSeconds(workspace.timing.durations.review_seconds)}</li>
                    <li>End-to-end elapsed: {formatTimingSeconds(workspace.timing.durations.end_to_end_seconds)}</li>
                  </ul>
                </div>
              </div>

              {workspace.review.diff && (
                <div className="record-row">
                  <div className="row-label">Review diff summary</div>
                  <div className="row-value">
                    <ul className="formal-list">
                      <li>
                        Source changed paths:{" "}
                        {String(workspace.review.diff["source_changed_path_count"] ?? 0)}
                      </li>
                      <li>
                        Dataset changed paths:{" "}
                        {String(workspace.review.diff["dataset_changed_path_count"] ?? 0)}
                      </li>
                    </ul>
                    <ul className="formal-list">
                      {[
                        ...((workspace.review.diff["source_changed_paths"] as string[] | undefined) ?? []),
                        ...((workspace.review.diff["dataset_changed_paths"] as string[] | undefined) ?? []),
                      ].map((path, index) => (
                        <li key={`${path}-${index}`}>{path}</li>
                      ))}
                    </ul>
                  </div>
                </div>
              )}

              <div className="record-row">
                <div className="row-label">
                  <label htmlFor="reviewed-source-json">reviewed.source.json editor</label>
                </div>
                <div className="row-value">
                  <textarea
                    id="reviewed-source-json"
                    rows={18}
                    value={reviewedSourceJson}
                    onChange={(event) => setReviewedSourceJson(event.target.value)}
                    className="typewriter-input"
                  />
                </div>
              </div>

              <div className="record-row">
                <div className="row-label">
                  <label htmlFor="reviewer-name">Reviewer name</label>
                </div>
                <div className="row-value">
                  <input
                    id="reviewer-name"
                    type="text"
                    value={reviewerName}
                    onChange={(event) => setReviewerName(event.target.value)}
                  />
                </div>
              </div>

              <div className="record-row">
                <div className="row-label">
                  <label htmlFor="approval-note">Approval note</label>
                </div>
                <div className="row-value">
                  <textarea
                    id="approval-note"
                    rows={3}
                    value={approvalNote}
                    onChange={(event) => setApprovalNote(event.target.value)}
                    className="typewriter-input"
                  />
                </div>
              </div>

              <div className="action-row">
                <button
                  type="button"
                  className="btn-seal"
                  disabled={isLoading || !selectedManifest}
                  onClick={() =>
                    void runWorkspaceAction("/api/internal/onboarding/start-review", {
                      manifest: selectedManifest,
                      reviewer_name: reviewerName,
                      note: approvalNote,
                    })
                  }
                >
                  Start Review Session
                </button>
                <button
                  type="button"
                  className="btn-seal"
                  disabled={isLoading || !selectedManifest || !workspace.manifest.source_build_available}
                  onClick={() =>
                    void runWorkspaceAction("/api/internal/onboarding/source-build", {
                      manifest: selectedManifest,
                    })
                  }
                >
                  Run Source Build
                </button>
                <button
                  type="button"
                  className="btn-seal"
                  disabled={isLoading || !selectedManifest}
                  onClick={() =>
                    void runWorkspaceAction("/api/internal/onboarding/compile", {
                      manifest: selectedManifest,
                    })
                  }
                >
                  Run Compile
                </button>
                <button
                  type="button"
                  className="btn-seal"
                  disabled={isLoading || !selectedManifest}
                  onClick={() =>
                    void runWorkspaceAction("/api/internal/onboarding/review", {
                      manifest: selectedManifest,
                      reviewed_source_json: reviewedSourceJson,
                    })
                  }
                >
                  Run Review
                </button>
                <button
                  type="button"
                  className="btn-seal"
                  disabled={isLoading || !selectedManifest}
                  onClick={() =>
                    void runWorkspaceAction("/api/internal/onboarding/approve", {
                      manifest: selectedManifest,
                      reviewer_name: reviewerName,
                      note: approvalNote,
                    })
                  }
                >
                  Approve
                </button>
                <button
                  type="button"
                  className="btn-seal"
                  disabled={isLoading || !selectedManifest}
                  onClick={() =>
                    void runWorkspaceAction("/api/internal/onboarding/promote", {
                      manifest: selectedManifest,
                    })
                  }
                >
                  Promote
                </button>
              </div>
            </>
          )}

          {error && (
            <div className="memo-alert alert-error">
              <span className="alert-marker">!</span>
              <p>{error}</p>
            </div>
          )}
        </section>
      </main>
    </div>
  );
}

export default function App() {
  if (isInternalOnboardingMode()) {
    return <InternalOnboardingWorkspace />;
  }

  const caseAccessParams = getCaseAccessParams();
  const caseIdParam = caseAccessParams?.caseId ?? "";
  const caseTokenParam = caseAccessParams?.token ?? "";
  const isSavedCaseMode = caseIdParam !== "" && caseTokenParam !== "";
  const [submissionMode, setSubmissionMode] = useState<InputMode>("guided");
  const [guidedPayerCountry, setGuidedPayerCountry] = useState("CN");
  const [guidedPayeeCountry, setGuidedPayeeCountry] = useState("NL");
  const [guidedIncomeType, setGuidedIncomeType] = useState<GuidedIncomeType>("dividends");
  const [guidedScenarioText, setGuidedScenarioText] = useState("");
  const [guidedFacts, setGuidedFacts] = useState<Record<string, GuidedFactValue>>(
    buildGuidedFactState("dividends"),
  );
  const [scenario, setScenario] = useState("");
  const [showLegacyParserValidation, setShowLegacyParserValidation] = useState(false);
  const [result, setResult] = useState<AnalyzeResponse | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState("");
  const [factSelections, setFactSelections] = useState<Record<string, string>>({});
  const [lastRequestPayload, setLastRequestPayload] = useState<AnalyzeRequestPayload | null>(null);
  const [savedCaseLinks, setSavedCaseLinks] = useState<SavedCaseLinks | null>(null);
  const [isSavingCase, setIsSavingCase] = useState(false);
  const [savedCaseView, setSavedCaseView] = useState<SavedCaseView | null>(null);
  const [isSavedCaseLoading, setIsSavedCaseLoading] = useState(isSavedCaseMode);

  useEffect(() => {
    if (!isSavedCaseMode) {
      setSavedCaseView(null);
      setIsSavedCaseLoading(false);
      return;
    }

    let isDisposed = false;
    setIsSavedCaseLoading(true);
    setError("");

    void readApiJson<SavedCaseView>(
      `/api/cases/${encodeURIComponent(caseIdParam)}?token=${encodeURIComponent(caseTokenParam)}`,
    )
      .then((payload) => {
        if (isDisposed) {
          return;
        }
        setSavedCaseView(payload);
      })
      .catch(() => {
        if (isDisposed) {
          return;
        }
        setSavedCaseView(null);
        setError("Saved case unavailable. Check that the link is still valid and the backend is running.");
      })
      .finally(() => {
        if (!isDisposed) {
          setIsSavedCaseLoading(false);
        }
      });

    return () => {
      isDisposed = true;
    };
  }, [caseIdParam, caseTokenParam, isSavedCaseMode]);

  async function submitReview(
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
    setSavedCaseLinks(null);

    try {
      const resolvedMode = modeOverride ?? submissionMode;
      const body: AnalyzeRequestPayload =
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
      setLastRequestPayload(body);
      const payload = await readApiJson<AnalyzeResponse>("/api/analyze", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(body),
      });
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
    await submitReview(submissionMode);
  }

  async function handleFactCompletionSubmit() {
    if (!result || !result.supported) return;

    const priorScenarioText =
      lastRequestPayload?.guided_input?.scenario_text?.trim() || lastRequestPayload?.scenario?.trim();

    await submitReview("guided", {
      payer_country: result.normalized_input.payer_country,
      payee_country: result.normalized_input.payee_country,
      income_type: result.normalized_input.transaction_type,
      facts: factSelections,
      ...(priorScenarioText ? { scenario_text: priorScenarioText } : {}),
    });
  }

  async function handleSaveCase() {
    if (!lastRequestPayload?.guided_input) {
      return;
    }

    setIsSavingCase(true);
    setError("");

    try {
      const payload = await readApiJson<CaseCreateResponse>("/api/cases", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(lastRequestPayload),
      });

      setResult(payload.analyze_response_snapshot);
      setSavedCaseLinks({
        case_id: payload.case_id,
        saved_at: payload.saved_at,
        creator_link: buildCaseLink(payload.case_id, payload.creator_token),
        reviewer_link: buildCaseLink(payload.case_id, payload.reviewer_token),
        creator_workpaper_link: buildWorkpaperLink(payload.case_id, payload.creator_token),
        reviewer_workpaper_link: buildWorkpaperLink(payload.case_id, payload.reviewer_token),
      });
    } catch {
      setError("Case save failed. Check that the backend service is running.");
    } finally {
      setIsSavingCase(false);
    }
  }

  function canSaveCurrentCase() {
    return (
      result !== null &&
      result.input_mode_used === "guided" &&
      Boolean(result.handoff_package) &&
      Boolean(lastRequestPayload?.guided_input)
    );
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

  function getGuidedFactsForIncomeType(incomeType: GuidedIncomeType) {
    return GUIDED_FACT_CONFIG[incomeType];
  }

  function handleGuidedIncomeTypeChange(nextIncomeType: GuidedIncomeType) {
    setGuidedIncomeType(nextIncomeType);
    setGuidedFacts(buildGuidedFactState(nextIncomeType));
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

    const {
      machine_handoff: machineHandoff,
      human_review_brief: humanReviewBrief,
      authority_memo: authorityMemo,
    } = handoffPackage;

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
          {authorityMemo && (
            <details>
              <summary>
                Authority Memo · status: {authorityMemo.status} · coverage gaps:{" "}
                {authorityMemo.coverage_gaps.length}
              </summary>
              <p>{authorityMemo.reviewer_note}</p>
              <ul className="formal-list">
                {authorityMemo.topics.map((topic) => (
                  <li key={topic.topic}>
                    <strong>{topic.topic}</strong>
                    {topic.summary ? ` · ${topic.summary}` : ""}
                    {topic.gap ? ` · Gap: ${topic.gap}` : ""}
                    {topic.citations.length > 0 && (
                      <ul className="formal-list">
                        {topic.citations.map((citation) => (
                          <li key={`${topic.topic}-${citation.source_id}`}>
                            {citation.title} ({citation.source_id})
                            {citation.note ? ` · ${citation.note}` : ""}
                          </li>
                        ))}
                      </ul>
                    )}
                  </li>
                ))}
              </ul>
            </details>
          )}
        </div>
      </div>
    );
  }

  function renderSavedCaseLinks() {
    if (!savedCaseLinks) {
      return null;
    }

    function renderSavedCaseLinkField(label: string, url: string) {
      return (
        <label className="saved-share-field">
          <span className="saved-share-field-label">{label}</span>
          <input
            className="saved-share-field-input"
            type="text"
            aria-label={`${label} URL`}
            value={url}
            readOnly
            spellCheck={false}
            onClick={(event) => event.currentTarget.select()}
            onFocus={(event) => event.currentTarget.select()}
          />
        </label>
      );
    }

    function renderSavedCaseSharePackage(options: {
      title: string;
      note: string;
      caseLinkLabel: string;
      caseLink: string;
      workpaperLinkLabel: string;
      workpaperLink: string;
      caseActionLabel: string;
      workpaperActionLabel: string;
      primary?: boolean;
    }) {
      const packageClassName = options.primary
        ? "saved-share-package saved-share-package-primary"
        : "saved-share-package";

      return (
        <div className={packageClassName}>
          <p className="saved-share-title">
            <strong>{options.title}</strong>
          </p>
          <p className="saved-share-note">{options.note}</p>
          <div className="action-row saved-share-actions">
            <a className="btn-seal" href={options.caseLink} target="_blank" rel="noreferrer">
              {options.caseActionLabel}
            </a>
            <a className="btn-seal" href={options.workpaperLink} target="_blank" rel="noreferrer">
              {options.workpaperActionLabel}
            </a>
          </div>
          <div className="saved-share-fields">
            {renderSavedCaseLinkField(options.caseLinkLabel, options.caseLink)}
            {renderSavedCaseLinkField(options.workpaperLinkLabel, options.workpaperLink)}
          </div>
        </div>
      );
    }

    return (
      <div className="record-row highlight-row">
        <div className="row-label">Saved Case</div>
        <div className="row-value">
          <p><strong>{savedCaseLinks.case_id}</strong></p>
          <p>Saved at: {savedCaseLinks.saved_at}</p>
          <p>Immutable snapshot saved.</p>
          <p>
            <strong>Reviewer package is the default share surface.</strong> Open the reviewer
            read-only case or reviewer workpaper below, and click either URL field to select the
            full link for manual copy.
          </p>
          <div className="saved-share-grid">
            {renderSavedCaseSharePackage({
              title: "Reviewer Package",
              note: "Use these links for downstream review and printable handoff.",
              caseLinkLabel: "Reviewer case link",
              caseLink: savedCaseLinks.reviewer_link,
              workpaperLinkLabel: "Reviewer workpaper link",
              workpaperLink: savedCaseLinks.reviewer_workpaper_link,
              caseActionLabel: "Open Reviewer View",
              workpaperActionLabel: "Open Reviewer Workpaper",
              primary: true,
            })}
            {renderSavedCaseSharePackage({
              title: "Creator-Only Backup",
              note: "Keep these internal for the case owner; they stay read-only but are not the default review share path.",
              caseLinkLabel: "Creator case link",
              caseLink: savedCaseLinks.creator_link,
              workpaperLinkLabel: "Creator workpaper link",
              workpaperLink: savedCaseLinks.creator_workpaper_link,
              caseActionLabel: "Open Creator View",
              workpaperActionLabel: "Open Creator Workpaper",
            })}
          </div>
        </div>
      </div>
    );
  }

  function renderSavedCasePackageSummary(savedCase: SavedCaseView) {
    const savedResult = savedCase.response_snapshot;
    const humanReviewBrief = savedResult.handoff_package?.human_review_brief;
    const machineHandoff = savedResult.handoff_package?.machine_handoff;
    const authorityMemo = savedResult.handoff_package?.authority_memo;
    const summaryText = savedResult.supported ? savedResult.result.summary : savedResult.message;
    const immediateAction = savedResult.supported
      ? savedResult.result.immediate_action
      : savedResult.immediate_action;

    return (
      <div className="record-row highlight-row">
        <div className="row-label">Saved Case Summary</div>
        <div className="row-value">
          <p><strong>{formatSavedCaseRole(savedCase.view_role)}</strong></p>
          <p>{getSavedCaseAccessNote(savedCase.view_role)}</p>
          <p>{summaryText}</p>
          <ul className="formal-list">
            <li>Immediate action: {immediateAction}</li>
            {humanReviewBrief?.headline && <li>Reviewer headline: {humanReviewBrief.headline}</li>}
            {humanReviewBrief?.disposition && <li>Reviewer disposition: {humanReviewBrief.disposition}</li>}
            {machineHandoff?.recommended_route && (
              <li>Recommended route: {machineHandoff.recommended_route}</li>
            )}
            {machineHandoff?.record_kind && <li>Record kind: {machineHandoff.record_kind}</li>}
            {authorityMemo && (
              <li>
                Authority memo: {authorityMemo.status} · coverage gaps: {authorityMemo.coverage_gaps.length}
              </li>
            )}
            <li>Printable workpaper uses the same immutable saved snapshot.</li>
          </ul>
          {humanReviewBrief?.summary_lines.length ? (
            <>
              <p>Reviewer summary lines:</p>
              <ul className="formal-list">
                {humanReviewBrief.summary_lines.map((line, idx) => (
                  <li key={`saved-summary-${idx}`}>{line}</li>
                ))}
              </ul>
            </>
          ) : null}
          {humanReviewBrief?.facts_to_verify.length ? (
            <>
              <p>Facts to verify:</p>
              <ul className="formal-list">
                {humanReviewBrief.facts_to_verify.map((fact, idx) => (
                  <li key={`saved-verify-${idx}`}>{fact}</li>
                ))}
              </ul>
            </>
          ) : null}
        </div>
      </div>
    );
  }

  function renderSavedCaseReviewerRiskSummary(savedCase: SavedCaseView) {
    const summary = buildReviewerRiskSummary(savedCase.response_snapshot);

    return (
      <div className={`record-row ${summary.escalated ? "warning-row review-flagged" : "highlight-row"}`}>
        <div className="row-label">Reviewer Risk Summary</div>
        <div className="row-value">
          <p>
            <strong>
              {summary.escalated
                ? "Escalated reviewer-risk signals remain in this immutable saved snapshot."
                : "Compact reviewer-risk cues from this immutable saved snapshot."}
            </strong>
          </p>
          <p>
            Recommended route: {summary.recommendedRoute} · Review priority: {summary.reviewPriority}
          </p>
          <ul className="formal-list">
            {summary.items.length > 0 ? (
              summary.items.map((item, idx) => <li key={`saved-risk-${idx}`}>{item}</li>)
            ) : (
              <li>No additional elevated reviewer-risk signals are recorded beyond the standard review path.</li>
            )}
          </ul>
        </div>
      </div>
    );
  }

  function renderSavedCaseInputSnapshot(savedCase: SavedCaseView) {
    const guidedInput = savedCase.request_snapshot.guided_input;
    if (!guidedInput) {
      return null;
    }

    return (
      <div className="record-row">
        <div className="row-label">Saved Facts / Scenario Snapshot</div>
        <div className="row-value">
          <ul className="formal-list">
            <li>Payer jurisdiction: {guidedInput.payer_country}</li>
            <li>Payee jurisdiction: {guidedInput.payee_country}</li>
            <li>Income type: {guidedInput.income_type}</li>
            {guidedInput.scenario_text && <li>Scenario text: {guidedInput.scenario_text}</li>}
          </ul>
          {Object.keys(guidedInput.facts).length > 0 ? (
            <ul className="formal-list">
              {Object.entries(guidedInput.facts).map(([factKey, factValue]) => (
                <li key={factKey}>
                  {getGuidedFactPrompt(guidedInput.income_type, factKey)}: {formatFactValue(factValue)}
                </li>
              ))}
            </ul>
          ) : (
            <p>No structured facts were saved with this case snapshot.</p>
          )}
        </div>
      </div>
    );
  }

  function renderSavedCaseView() {
    if (isSavedCaseLoading) {
      return (
        <div className="document-body">
          <header className="memo-header">
            <div className="memo-stamp">
              <span className="stamp-seal">TTA-MVP</span>
              <span className="stamp-date">READ-ONLY CASE</span>
            </div>
            <div className="memo-title-block">
              <h1 className="memo-title">TAX TREATY AGENT</h1>
              <p className="memo-subtitle">Loading saved case...</p>
            </div>
            <div className="memo-meta">
              <span className="meta-label">STATUS</span>
              <span className="meta-value">LOADING</span>
            </div>
          </header>
        </div>
      );
    }

    if (!savedCaseView) {
      return (
        <div className="document-body">
          <header className="memo-header">
            <div className="memo-stamp">
              <span className="stamp-seal">TTA-MVP</span>
              <span className="stamp-date">READ-ONLY CASE</span>
            </div>
            <div className="memo-title-block">
              <h1 className="memo-title">TAX TREATY AGENT</h1>
              <p className="memo-subtitle">Saved case unavailable.</p>
            </div>
            <div className="memo-meta">
              <span className="meta-label">STATUS</span>
              <span className="meta-value">UNAVAILABLE</span>
            </div>
          </header>
          {error && (
            <main className="review-main">
              <section className="output-section">
                <div className="memo-alert alert-error">
                  <span className="alert-marker">!</span>
                  <p>{error}</p>
                </div>
              </section>
            </main>
          )}
        </div>
      );
    }

    const savedResult = savedCaseView.response_snapshot;
    const workpaperLink = buildWorkpaperLink(savedCaseView.case_id, caseTokenParam);
    const savedCaseStatusLabel =
      savedCaseView.view_role === "creator" ? "CREATOR PACKAGE" : "REVIEWER PACKAGE";
    const savedCaseSubtitle =
      savedCaseView.view_role === "creator"
        ? "Read-only creator package with printable workpaper access."
        : "Read-only reviewer package with printable workpaper access.";

    return (
      <div className="document-body">
        <header className="memo-header">
          <div className="memo-stamp">
            <span className="stamp-seal">TTA-MVP</span>
            <span className="stamp-date">READ-ONLY CASE</span>
          </div>
          <div className="memo-title-block">
            <h1 className="memo-title">TAX TREATY AGENT</h1>
            <p className="memo-subtitle">{savedCaseSubtitle}</p>
          </div>
          <div className="memo-meta">
            <span className="meta-label">STATUS</span>
            <span className="meta-value">{savedCaseStatusLabel}</span>
          </div>
        </header>

        <main className="review-main">
          <section className="output-section" aria-live="polite">
            <h2 className="section-heading">Saved Case</h2>

            <div className="formal-record success-record">
              <div className="record-body">
                <div className="record-row highlight-row">
                  <div className="row-label">Case Header</div>
                  <div className="row-value">
                    <ul className="formal-list">
                      <li>Case ID: {savedCaseView.case_id}</li>
                      <li>Saved at: {savedCaseView.saved_at}</li>
                      <li>Schema version: {savedCaseView.schema_version}</li>
                      <li>Input mode: {savedCaseView.input_mode_used}</li>
                      <li>View role: {savedCaseView.view_role}</li>
                      <li>Reviewer share ready: {savedCaseView.reviewer_share_ready ? "yes" : "no"}</li>
                    </ul>
                    <div className="action-row">
                      <a className="btn-seal" href={workpaperLink} target="_blank" rel="noreferrer">
                        Open Printable Workpaper
                      </a>
                    </div>
                  </div>
                </div>

                {renderSavedCasePackageSummary(savedCaseView)}
                {renderSavedCaseReviewerRiskSummary(savedCaseView)}
                {renderSavedCaseInputSnapshot(savedCaseView)}
                {renderReviewStateBlock(savedResult.review_state)}
                {savedResult.supported && renderFactCompletionStatus(savedResult.fact_completion_status)}
                {savedResult.supported && renderConfirmedScope(savedResult.confirmed_scope)}
                {renderInputInterpretation(savedResult.input_interpretation)}
                {savedResult.supported && renderBOPrecheck(savedResult.bo_precheck)}
                {savedResult.supported &&
                  renderSourceChain(savedResult.result.source_trace, savedResult.result.mli_context)}
                {savedResult.supported && renderUserDeclaredFacts(savedResult.user_declared_facts)}
                {savedResult.supported && renderChangeSummary(savedResult.change_summary)}
                {renderNextActions(savedResult.next_actions)}
                {renderWorkflowHandoff(savedResult.handoff_package)}

                <div className="record-row">
                  <div className="row-label">Boundary Note</div>
                  <div className="row-value">
                    <p>
                      {savedResult.supported
                        ? savedResult.result.boundary_note
                        : savedResult.handoff_package?.human_review_brief.handoff_note ??
                          "This output is a bounded pre-review record, not a final tax opinion."}
                    </p>
                  </div>
                </div>
              </div>
            </div>

            {error && (
              <div className="memo-alert alert-error">
                <span className="alert-marker">!</span>
                <p>{error}</p>
              </div>
            )}
          </section>
        </main>
      </div>
    );
  }

  if (isSavedCaseMode) {
    return renderSavedCaseView();
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
                Guided input is the public submission path. The older parser lane stays tucked behind
                an internal validation panel for compatibility checks only.
              </p>
            </div>

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
                    <option value="">-- Select --</option>
                    <option value="CN">CN</option>
                    <option value="KR">KR</option>
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
                    <option value="">-- Select --</option>
                    <option value="NL">NL</option>
                    <option value="CN">CN</option>
                    <option value="KR">KR</option>
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
                    onChange={(event) =>
                      handleGuidedIncomeTypeChange(event.target.value as GuidedIncomeType)
                    }
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
                    void submitReview("guided");
                  }}
                >
                  {isLoading && submissionMode === "guided" ? "Running Review..." : "Run Guided Review"}
                </button>
              </div>
            </div>

            <div className="form-group">
              <p className="section-desc">
                Need the older parser lane for compatibility or demo checks? Open the internal parser
                validation panel.
              </p>
              <div className="action-row">
                <button
                  type="button"
                  className="text-link-button"
                  onClick={() => {
                    setShowLegacyParserValidation((current) => !current);
                    setSubmissionMode("free_text");
                  }}
                >
                  {showLegacyParserValidation ? "Hide Parser Validation" : "Open Parser Validation"}
                </button>
              </div>
            </div>

            {showLegacyParserValidation && (
              <div className="form-group">
                <label htmlFor="scenario-input" className="section-heading">
                  Parser Validation Input
                  <span className="sr-only">Cross-border scenario</span>
                </label>
                <p className="section-desc">
                  Use the older parser-oriented lane for internal validation only.
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
                      void submitReview("free_text");
                    }}
                  >
                    {isLoading && submissionMode === "free_text"
                      ? "Running Parser Review..."
                      : "Run Parser Review"}
                  </button>
                </div>
              </div>
            )}

            <div className="archive-reference-block">
              <span className="reference-label">Reference Cases</span>
              <ul className="archive-list">
                {REFERENCE_ARCHIVES.map((example, i) => (
                  <li key={i}>
                    <button
                      type="button"
                      className="text-link-button"
                      onClick={() => {
                        applyReferencePreset(
                          example.scenario,
                          setGuidedPayerCountry,
                          setGuidedPayeeCountry,
                          setGuidedIncomeType,
                          setGuidedFacts,
                          setGuidedScenarioText,
                          setShowLegacyParserValidation,
                          setSubmissionMode,
                          setScenario,
                        );
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
          {canSaveCurrentCase() && (
            <div className="action-row">
              <button
                type="button"
                className="btn-seal"
                onClick={() => void handleSaveCase()}
                disabled={isSavingCase}
              >
                {isSavingCase ? "Saving Case..." : "Save Case"}
              </button>
            </div>
          )}
          {renderSavedCaseLinks()}
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
