from __future__ import annotations

import json

from app.constants import SCHEMA_VERSION


GUIDED_FACT_SCHEMA: dict[str, list[dict[str, object]]] = {
    "dividends": [
        {
            "fact_key": "direct_holding_percentage",
            "prompt": "What is the recipient's direct shareholding percentage in the paying company as of the payment date?",
            "input_type": "text",
            "allowed_values_format": 'numeric string or "unknown"',
            "deprecated": False,
        },
        {
            "fact_key": "payment_date",
            "prompt": "What is the dividend payment date (or declared payment date)?",
            "input_type": "text",
            "allowed_values_format": 'ISO 8601 date string or "unknown"',
            "deprecated": False,
        },
        {
            "fact_key": "holding_period_months",
            "prompt": "How many months has the recipient continuously held the shares as of the payment date?",
            "input_type": "text",
            "allowed_values_format": 'non-negative integer string or "unknown"',
            "deprecated": False,
        },
        {
            "fact_key": "beneficial_owner_confirmed",
            "prompt": "Has beneficial-owner status been separately confirmed outside this tool?",
            "input_type": "single_select",
            "options": ["yes", "no", "unknown"],
            "allowed_values_format": '"yes", "no", or "unknown"',
            "deprecated": False,
        },
        {
            "fact_key": "pe_effectively_connected",
            "prompt": "Is the dividend effectively connected with a permanent establishment or fixed base of the Dutch recipient in China?",
            "input_type": "single_select",
            "options": ["yes", "no", "unknown"],
            "allowed_values_format": '"yes", "no", or "unknown"',
            "deprecated": False,
        },
        {
            "fact_key": "holding_structure_is_direct",
            "prompt": "Is the holding structure confirmed to be direct with no intermediate holding entity between the recipient and the paying company?",
            "input_type": "single_select",
            "options": ["yes", "no", "unknown"],
            "allowed_values_format": '"yes", "no", or "unknown"',
            "deprecated": False,
        },
        {
            "fact_key": "mli_ppt_risk_flag",
            "prompt": "Has a principal purpose test (PPT) risk assessment been performed for this dividend payment under the MLI?",
            "input_type": "single_select",
            "options": ["yes", "no", "unknown"],
            "allowed_values_format": '"yes", "no", or "unknown"',
            "deprecated": False,
        },
    ],
    "interest": [
        {
            "fact_key": "interest_character_confirmed",
            "prompt": "Is the payment legally characterized as interest under the financing arrangement?",
            "input_type": "single_select",
            "options": ["yes", "no", "unknown"],
            "allowed_values_format": '"yes", "no", or "unknown"',
            "deprecated": False,
        },
        {
            "fact_key": "beneficial_owner_status",
            "prompt": "Has the recipient's beneficial-owner status for the interest income been separately confirmed?",
            "input_type": "single_select",
            "options": ["yes", "no", "unknown"],
            "allowed_values_format": '"yes", "no", or "unknown"',
            "deprecated": False,
        },
        {
            "fact_key": "lending_documents_consistent",
            "prompt": "Do the loan agreement, interest calculation, and payment records support the current interest characterization?",
            "input_type": "single_select",
            "options": ["yes", "no", "unknown"],
            "allowed_values_format": '"yes", "no", or "unknown"',
            "deprecated": False,
        },
    ],
    "royalties": [
        {
            "fact_key": "royalty_character_confirmed",
            "prompt": "Is the payment actually for the use of, or the right to use, qualifying intellectual property?",
            "input_type": "single_select",
            "options": ["yes", "no", "unknown"],
            "allowed_values_format": '"yes", "no", or "unknown"',
            "deprecated": False,
        },
        {
            "fact_key": "beneficial_owner_status",
            "prompt": "Has the recipient's beneficial-owner status for the royalty income been separately confirmed?",
            "input_type": "single_select",
            "options": ["yes", "no", "unknown"],
            "allowed_values_format": '"yes", "no", or "unknown"',
            "deprecated": False,
        },
        {
            "fact_key": "contract_payment_flow_consistent",
            "prompt": "Do the contract, invoice, and payment flow support the current royalty characterization?",
            "input_type": "single_select",
            "options": ["yes", "no", "unknown"],
            "allowed_values_format": '"yes", "no", or "unknown"',
            "deprecated": False,
        },
    ],
}

GUIDED_FACT_CONFIG = {
    income_type: [field["fact_key"] for field in fields]
    for income_type, fields in GUIDED_FACT_SCHEMA.items()
}
BACKEND_GUIDED_FACT_CONFIG = {
    "dividends": [
        "direct_holding_percentage",
        "payment_date",
        "holding_period_months",
        "direct_holding_confirmed",
        "direct_holding_threshold_met",
        "beneficial_owner_confirmed",
        "pe_effectively_connected",
        "holding_structure_is_direct",
        "mli_ppt_risk_flag",
    ],
    "interest": list(GUIDED_FACT_CONFIG["interest"]),
    "royalties": list(GUIDED_FACT_CONFIG["royalties"]),
}
DIVIDEND_FACT_KEYS = tuple(BACKEND_GUIDED_FACT_CONFIG["dividends"])
DIVIDEND_RAW_FACT_KEYS = (
    "direct_holding_percentage",
    "payment_date",
    "holding_period_months",
)
DIVIDEND_DEPRECATED_BRIDGE_FACT_KEYS = (
    "direct_holding_confirmed",
    "direct_holding_threshold_met",
)
DIVIDEND_SELECT_FACT_KEYS = (
    "beneficial_owner_confirmed",
    "pe_effectively_connected",
    "holding_structure_is_direct",
    "mli_ppt_risk_flag",
    *DIVIDEND_DEPRECATED_BRIDGE_FACT_KEYS,
)


def build_guided_fact_contract() -> dict[str, object]:
    return {
        "schema_version": SCHEMA_VERSION,
        "income_types": GUIDED_FACT_SCHEMA,
    }


def build_frontend_contract_source() -> str:
    guided_fact_json = json.dumps(GUIDED_FACT_SCHEMA, ensure_ascii=False, indent=2)
    return f"""/* auto-generated from backend/app/guided_facts.py */
export type InputMode = "guided" | "free_text";
export type GuidedFactValue = string;
export type GuidedSelectFactValue = "yes" | "no" | "unknown";

export type ReviewState = {{
  state_code:
    | "pre_review_complete"
    | "can_be_completed"
    | "partial_review"
    | "needs_human_intervention"
    | "out_of_scope";
  state_label_zh: string;
  state_summary: string;
}};

export type NextAction = {{
  priority: "high" | "medium" | "low";
  action: string;
  reason: string;
}};

export type ConfirmedScope = {{
  applicable_treaty: string;
  applicable_article: string;
  payment_direction: string;
  income_type: string;
}};

export type FactCompletionQuestion = {{
  fact_key: string;
  prompt: string;
  input_type: "single_select" | "text";
  options?: Array<GuidedSelectFactValue>;
}};

export type FactCompletion = {{
  flow_type: "bounded_form";
  session_type: "pseudo_multiturn";
  user_declaration_note: string;
  facts: FactCompletionQuestion[];
}};

export type UserDeclaredFacts = {{
  declaration_label: string;
  facts: Array<{{
    fact_key: string;
    value: string;
    label: string;
  }}>;
}};

export type FactCompletionStatus = {{
  status_code:
    | "awaiting_user_facts"
    | "completed_narrowed"
    | "terminated_unknown_facts"
    | "terminated_pe_exclusion"
    | "terminated_beneficial_owner_unconfirmed"
    | "terminated_conflicting_user_facts";
  status_label_zh: string;
  status_summary: string;
}};

export type ChangeSummary = {{
  summary_label: string;
  state_change: string;
  rate_change: string;
  trigger_facts: string[];
}};

export type SourceTrace = {{
  treaty_full_name: string;
  version_note: string;
  source_document_title: string;
  language_version: string;
  official_source_ids: string[];
  protocol_note: string | null;
  working_paper_ref: string | null;
}};

export type MLIContext = {{
  covered_tax_agreement: boolean;
  ppt_applies: boolean;
  summary: string;
  human_review_note: string;
  official_source_ids: string[];
}};

export type BOPrecheck = {{
  status: "not_run" | "insufficient_facts" | "flagged_for_review" | "no_initial_flag";
  reason_code: string;
  reason_summary: string;
  facts_considered: Array<{{
    fact_key: string;
    value: string;
  }}>;
  review_note: string;
}};

export type GuidedConflict = {{
  status: "conflict_detected";
  reason_code: string;
  reason_summary: string;
  structured_facts_win: boolean;
  conflicting_claims: string[];
}};

export type MachineHandoff = {{
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
  user_declared_facts: Array<{{
    fact_key: string;
    value: GuidedFactValue;
    label: string;
  }}>;
  bo_precheck?: BOPrecheck;
  guided_conflict?: GuidedConflict;
  determining_condition_priority?: number | null;
  mli_ppt_review_required?: boolean;
  short_holding_period_review_required?: boolean;
  payment_date_unconfirmed?: boolean;
  calculated_threshold_met?: boolean | null;
}};

export type HumanReviewBrief = {{
  brief_title: string;
  headline: string;
  disposition: string;
  summary_lines: string[];
  facts_to_verify: string[];
  handoff_note: string;
}};

export type AuthorityMemoCitation = {{
  source_id: string;
  title: string;
  source_type: string;
  official_url: string;
  note: string;
}};

export type AuthorityMemoTopic = {{
  topic: "treaty_basis" | "mli_ppt" | "beneficial_owner" | "domestic_law" | "working_paper";
  summary: string;
  citations: AuthorityMemoCitation[];
  gap: string | null;
}};

export type AuthorityMemoCoverageGap = {{
  topic: AuthorityMemoTopic["topic"];
  reason_code: "DATA_MISSING" | "TREATY_SILENT";
  note: string;
}};

export type AuthorityMemo = {{
  status: string;
  topics: AuthorityMemoTopic[];
  reviewer_note: string;
  coverage_gaps: AuthorityMemoCoverageGap[];
}};

export type HandoffPackage = {{
  machine_handoff: MachineHandoff;
  human_review_brief: HumanReviewBrief;
  authority_memo?: AuthorityMemo;
}};

export type InputInterpretation = {{
  parser_source: "llm";
  payer_country: string | null;
  payee_country: string | null;
  transaction_type: string;
  matched_transaction_label: string | null;
}};

export type AnalyzeResponse =
  | {{
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
    }}
  | {{
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
      normalized_input: {{
        payer_country: string;
        payee_country: string;
        transaction_type: string;
      }};
      result: {{
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
        alternative_rate_candidates?: {{
          source_reference: string;
          rate: string;
          conditions: string[];
        }}[];
      }};
    }};

export const SCHEMA_VERSION = "{SCHEMA_VERSION}";
export const GUIDED_FACT_CONFIG = {guided_fact_json} as const;
"""
