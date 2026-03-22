from __future__ import annotations

import hashlib
import hmac
import html
import json
import secrets
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from app.guided_facts import GUIDED_FACT_SCHEMA


REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_CASE_DB_PATH = REPO_ROOT / "data" / "runtime" / "cases.sqlite3"
CASE_NOT_FOUND_DETAIL = "Case not found."
GUIDED_FACT_PROMPTS = {
    income_type: {
        str(field.get("fact_key")): str(field.get("prompt"))
        for field in fields
        if field.get("fact_key") and field.get("prompt")
    }
    for income_type, fields in GUIDED_FACT_SCHEMA.items()
}


def get_case_db_path() -> Path:
    configured = Path(
        __import__("os").environ.get(
            "TAX_TREATY_AGENT_CASE_DB_PATH",
            str(DEFAULT_CASE_DB_PATH),
        )
    )
    configured.parent.mkdir(parents=True, exist_ok=True)
    return configured


def _connect() -> sqlite3.Connection:
    connection = sqlite3.connect(get_case_db_path())
    connection.row_factory = sqlite3.Row
    _ensure_schema(connection)
    return connection


def _ensure_schema(connection: sqlite3.Connection) -> None:
    connection.execute(
        """
        CREATE TABLE IF NOT EXISTS cases (
            case_id TEXT PRIMARY KEY,
            created_at TEXT NOT NULL,
            schema_version TEXT NOT NULL,
            input_mode_used TEXT NOT NULL,
            request_snapshot_json TEXT NOT NULL,
            response_snapshot_json TEXT NOT NULL,
            review_state_code TEXT NOT NULL,
            record_kind TEXT NOT NULL,
            creator_token_hash TEXT NOT NULL,
            reviewer_token_hash TEXT NOT NULL
        )
        """
    )
    connection.commit()


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _hash_token(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def _generate_case_id() -> str:
    return f"case_{secrets.token_hex(8)}"


def _generate_access_token() -> str:
    return secrets.token_urlsafe(24)


def _extract_review_state_code(response_snapshot: dict[str, Any]) -> str:
    review_state = response_snapshot.get("review_state")
    if isinstance(review_state, dict):
        state_code = review_state.get("state_code")
        if isinstance(state_code, str) and state_code:
            return state_code
    return "unknown"


def _extract_record_kind(response_snapshot: dict[str, Any]) -> str:
    handoff = response_snapshot.get("handoff_package")
    if isinstance(handoff, dict):
        machine_handoff = handoff.get("machine_handoff")
        if isinstance(machine_handoff, dict):
            record_kind = machine_handoff.get("record_kind")
            if isinstance(record_kind, str) and record_kind:
                return record_kind
    if response_snapshot.get("supported") is True:
        return "supported"
    if response_snapshot.get("reason") == "incomplete_scenario":
        return "incomplete"
    return "unsupported"


def create_case_snapshot(
    request_snapshot: dict[str, Any],
    response_snapshot: dict[str, Any],
) -> dict[str, Any]:
    created_at = _utc_now_iso()
    creator_token = _generate_access_token()
    reviewer_token = _generate_access_token()
    case_id = _generate_case_id()
    schema_version = str(response_snapshot.get("schema_version") or "unknown")
    input_mode_used = str(response_snapshot.get("input_mode_used") or request_snapshot.get("input_mode") or "unknown")
    review_state_code = _extract_review_state_code(response_snapshot)
    record_kind = _extract_record_kind(response_snapshot)

    with _connect() as connection:
        connection.execute(
            """
            INSERT INTO cases (
                case_id,
                created_at,
                schema_version,
                input_mode_used,
                request_snapshot_json,
                response_snapshot_json,
                review_state_code,
                record_kind,
                creator_token_hash,
                reviewer_token_hash
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                case_id,
                created_at,
                schema_version,
                input_mode_used,
                json.dumps(request_snapshot, ensure_ascii=False),
                json.dumps(response_snapshot, ensure_ascii=False),
                review_state_code,
                record_kind,
                _hash_token(creator_token),
                _hash_token(reviewer_token),
            ),
        )
        connection.commit()

    return {
        "case_id": case_id,
        "saved_at": created_at,
        "creator_token": creator_token,
        "reviewer_token": reviewer_token,
        "analyze_response_snapshot": response_snapshot,
    }


def _resolve_case_row(case_id: str, token: str) -> tuple[sqlite3.Row, str] | None:
    token_hash = _hash_token(token)
    with _connect() as connection:
        row = connection.execute(
            "SELECT * FROM cases WHERE case_id = ?",
            (case_id,),
        ).fetchone()

    if row is None:
        return None
    if hmac.compare_digest(row["creator_token_hash"], token_hash):
        return row, "creator"
    if hmac.compare_digest(row["reviewer_token_hash"], token_hash):
        return row, "reviewer"
    return None


def load_case_view(case_id: str, token: str) -> dict[str, Any] | None:
    resolved = _resolve_case_row(case_id, token)
    if resolved is None:
        return None
    row, view_role = resolved
    request_snapshot = json.loads(row["request_snapshot_json"])
    response_snapshot = json.loads(row["response_snapshot_json"])
    return {
        "case_id": row["case_id"],
        "saved_at": row["created_at"],
        "schema_version": row["schema_version"],
        "input_mode_used": row["input_mode_used"],
        "view_role": view_role,
        "reviewer_share_ready": view_role == "creator",
        "request_snapshot": request_snapshot,
        "response_snapshot": response_snapshot,
    }


def _render_list(items: list[str]) -> str:
    if not items:
        return "<p>None.</p>"
    return "<ul>" + "".join(f"<li>{html.escape(item)}</li>" for item in items) + "</ul>"


def _render_pretty_json(payload: dict[str, Any]) -> str:
    return f"<pre>{html.escape(json.dumps(payload, ensure_ascii=False, indent=2))}</pre>"


def _render_detail_rows(rows: list[tuple[str, str]]) -> str:
    filtered_rows = [(label, value) for label, value in rows if value]
    if not filtered_rows:
        return "<p>None.</p>"
    return (
        '<dl class="detail-grid">'
        + "".join(
            "<div class=\"detail-row\">"
            + f"<dt>{html.escape(label)}</dt>"
            + f"<dd>{html.escape(value)}</dd>"
            + "</div>"
            for label, value in filtered_rows
        )
        + "</dl>"
    )


def _get_guided_fact_prompt(income_type: str | None, fact_key: str) -> str:
    return GUIDED_FACT_PROMPTS.get(income_type or "", {}).get(fact_key, fact_key)


def _format_fact_value(value: Any) -> str:
    if value is None:
        return "Not provided"
    if isinstance(value, str) and value == "":
        return "Not provided"
    return str(value)


def _render_saved_fact_snapshot(request_snapshot: dict[str, Any]) -> str:
    guided_input = request_snapshot.get("guided_input")
    if not isinstance(guided_input, dict):
        return "<p>Structured guided snapshot unavailable.</p>"

    income_type = str(guided_input.get("income_type") or "")
    summary_rows = [
        ("Payer jurisdiction", str(guided_input.get("payer_country") or "")),
        ("Payee jurisdiction", str(guided_input.get("payee_country") or "")),
        ("Income type", income_type),
        ("Scenario text", str(guided_input.get("scenario_text") or "")),
    ]
    facts = guided_input.get("facts")
    fact_lines: list[str] = []
    if isinstance(facts, dict):
        fact_lines = [
            f"{_get_guided_fact_prompt(income_type, str(fact_key))}: {_format_fact_value(fact_value)}"
            for fact_key, fact_value in facts.items()
        ]

    return "\n".join(
        [
            _render_detail_rows(summary_rows),
            "<h3>Saved Facts</h3>",
            _render_list(fact_lines),
        ]
    )


def _render_case_summary(
    response_snapshot: dict[str, Any],
    human_review_brief: dict[str, Any],
    machine_handoff: dict[str, Any],
) -> str:
    if response_snapshot.get("supported") is True:
        result = response_snapshot.get("result") or {}
        summary_rows = [
            ("Preliminary view", str(result.get("summary") or "Saved supported result.")),
            ("Immediate action", str(result.get("immediate_action") or "")),
            ("Review guidance", str(result.get("review_reason") or "")),
            ("Reviewer disposition", str(human_review_brief.get("disposition") or "")),
            ("Recommended route", str(machine_handoff.get("recommended_route") or "")),
            ("Rate display", str(machine_handoff.get("rate_display") or result.get("rate") or "")),
        ]
        return _render_detail_rows(summary_rows)

    summary_rows = [
        ("Unavailable detail", str(response_snapshot.get("message") or "Saved unsupported result.")),
        ("Immediate action", str(response_snapshot.get("immediate_action") or "")),
        ("Reason code", str(response_snapshot.get("reason") or "unsupported")),
        ("Reviewer disposition", str(human_review_brief.get("disposition") or "")),
        ("Recommended route", str(machine_handoff.get("recommended_route") or "")),
    ]
    return _render_detail_rows(summary_rows)


def _render_workflow_handoff_detail(
    human_review_brief: dict[str, Any],
    machine_handoff: dict[str, Any],
) -> str:
    workflow_rows = [
        ("Brief title", str(human_review_brief.get("brief_title") or "")),
        ("Headline", str(human_review_brief.get("headline") or "")),
        ("Disposition", str(human_review_brief.get("disposition") or "")),
        ("Record kind", str(machine_handoff.get("record_kind") or "")),
        ("Recommended route", str(machine_handoff.get("recommended_route") or "")),
        (
            "Article lane",
            f"{machine_handoff.get('article_number')} · {machine_handoff.get('article_title')}"
            if machine_handoff.get("article_number") and machine_handoff.get("article_title")
            else "",
        ),
        ("Rate display", str(machine_handoff.get("rate_display") or "")),
    ]
    summary_lines = [str(line) for line in human_review_brief.get("summary_lines") or [] if str(line)]
    facts_to_verify = [
        str(line) for line in human_review_brief.get("facts_to_verify") or [] if str(line)
    ]
    user_declared_lines = [
        f"{str(fact.get('label') or fact.get('fact_key') or 'fact')}: {_format_fact_value(fact.get('value'))}"
        for fact in machine_handoff.get("user_declared_facts") or []
        if isinstance(fact, dict)
    ]

    return "\n".join(
        [
            _render_detail_rows(workflow_rows),
            "<h3>Summary Lines</h3>",
            _render_list(summary_lines),
            "<h3>Facts To Verify</h3>",
            _render_list(facts_to_verify),
            "<h3>Unverified User-Declared Facts</h3>",
            _render_list(user_declared_lines),
        ]
    )


def _render_source_chain(response_snapshot: dict[str, Any], machine_handoff: dict[str, Any]) -> str:
    if response_snapshot.get("supported") is not True:
        fallback_rows = [
            ("Treaty version", str(machine_handoff.get("treaty_version") or "")),
            ("MLI / PPT", str(machine_handoff.get("mli_summary") or "")),
            ("Source reference", str(machine_handoff.get("source_reference") or "")),
        ]
        return _render_detail_rows(fallback_rows)

    result = response_snapshot.get("result") or {}
    source_trace = result.get("source_trace") or {}
    mli_context = result.get("mli_context") or {}
    source_rows = [
        ("Treaty text", str(source_trace.get("treaty_full_name") or "")),
        ("Version note", str(source_trace.get("version_note") or "")),
        ("Source document", str(source_trace.get("source_document_title") or "")),
        ("Language version", str(source_trace.get("language_version") or "")),
        ("Working paper", str(source_trace.get("working_paper_ref") or "")),
    ]
    source_ids = [str(source_id) for source_id in source_trace.get("official_source_ids") or []]
    mli_rows = [
        (
            "Covered tax agreement",
            "yes" if mli_context.get("covered_tax_agreement") else "no",
        )
        if mli_context
        else ("", ""),
        ("PPT applies", "yes" if mli_context.get("ppt_applies") else "no") if mli_context else ("", ""),
        ("MLI summary", str(mli_context.get("summary") or "")),
        ("Reviewer note", str(mli_context.get("human_review_note") or "")),
    ]
    mli_source_ids = [str(source_id) for source_id in mli_context.get("official_source_ids") or []]

    return "\n".join(
        [
            _render_detail_rows(source_rows),
            "<h3>Official Source IDs</h3>",
            _render_list(source_ids),
            "<h3>MLI / PPT</h3>",
            _render_detail_rows(mli_rows),
            "<h3>MLI Source IDs</h3>",
            _render_list(mli_source_ids),
        ]
    )


def _render_authority_memo(authority_memo: dict[str, Any] | None) -> str:
    if not authority_memo:
        return "<p>Authority memo unavailable.</p>"

    topic_blocks: list[str] = []
    for topic in authority_memo.get("topics", []):
        citations = topic.get("citations") or []
        citation_html = "<p>No citations recorded.</p>"
        if citations:
            citation_html = (
                "<ul>"
                + "".join(
                    "<li>"
                    + html.escape(str(citation.get("title") or citation.get("source_id") or "Untitled source"))
                    + (
                        f" · {html.escape(str(citation.get('note')))}"
                        if citation.get("note")
                        else ""
                    )
                    + (
                        f" · <a href=\"{html.escape(str(citation.get('official_url')))}\">official source</a>"
                        if citation.get("official_url")
                        else ""
                    )
                    + "</li>"
                    for citation in citations
                )
                + "</ul>"
            )
        topic_blocks.append(
            "\n".join(
                [
                    "<article class=\"topic-card\">",
                    f"<h3>{html.escape(str(topic.get('topic') or 'topic'))}</h3>",
                    f"<p>{html.escape(str(topic.get('summary') or ''))}</p>",
                    (
                        f"<p><strong>Gap:</strong> {html.escape(str(topic.get('gap')))}</p>"
                        if topic.get("gap")
                        else ""
                    ),
                    citation_html,
                    "</article>",
                ]
            )
        )

    coverage_gaps = authority_memo.get("coverage_gaps") or []
    coverage_gap_html = "<p>None.</p>"
    if coverage_gaps:
        coverage_gap_html = (
            "<ul>"
            + "".join(
                "<li>"
                + html.escape(str(gap.get("topic") or "topic"))
                + " · "
                + html.escape(str(gap.get("reason_code") or "unknown"))
                + " · "
                + html.escape(str(gap.get("note") or ""))
                + "</li>"
                for gap in coverage_gaps
            )
            + "</ul>"
        )

    return "\n".join(
        [
            f"<p><strong>Status:</strong> {html.escape(str(authority_memo.get('status') or 'unknown'))}</p>",
            f"<p>{html.escape(str(authority_memo.get('reviewer_note') or ''))}</p>",
            "".join(topic_blocks) if topic_blocks else "<p>No authority topics recorded.</p>",
            "<h3>Coverage Gaps</h3>",
            coverage_gap_html,
        ]
    )


def _combine_risk_notes(*notes: str) -> str:
    deduped: list[str] = []
    for note in notes:
        if note and note not in deduped:
            deduped.append(note)
    return " ".join(deduped)


def _build_reviewer_risk_items(
    machine_handoff: dict[str, Any],
    authority_memo: dict[str, Any] | None,
) -> list[str]:
    items: list[str] = []
    bo_precheck = machine_handoff.get("bo_precheck")
    if isinstance(bo_precheck, dict):
        note = _combine_risk_notes(
            str(bo_precheck.get("reason_summary") or ""),
            str(bo_precheck.get("review_note") or ""),
        )
        if note:
            items.append(f"BO precheck ({bo_precheck.get('status') or 'unknown'}): {note}")

    guided_conflict = machine_handoff.get("guided_conflict")
    if isinstance(guided_conflict, dict):
        reason_summary = str(guided_conflict.get("reason_summary") or guided_conflict.get("reason_code") or "")
        if reason_summary:
            items.append(f"Guided input conflict: {reason_summary}")

    coverage_gaps = authority_memo.get("coverage_gaps") if isinstance(authority_memo, dict) else []
    if isinstance(coverage_gaps, list) and coverage_gaps:
        formatted_gaps = [
            f"{str(gap.get('topic') or 'topic')} ({str(gap.get('reason_code') or 'unknown')})"
            for gap in coverage_gaps
            if isinstance(gap, dict)
        ]
        if formatted_gaps:
            items.append(f"Authority memo gaps: {'; '.join(formatted_gaps)}")

    recommended_route = str(machine_handoff.get("recommended_route") or "")
    if recommended_route and recommended_route != "standard_review":
        items.append(f"Machine handoff route remains {recommended_route}.")

    if machine_handoff.get("review_priority") == "high":
        items.append("Machine handoff keeps this case at high review priority.")
    if machine_handoff.get("mli_ppt_review_required") is True:
        items.append("MLI / PPT review is still required.")
    if machine_handoff.get("short_holding_period_review_required") is True:
        items.append("Short holding period review is still required.")
    if machine_handoff.get("payment_date_unconfirmed") is True:
        items.append("Payment date remains unconfirmed in the saved snapshot.")

    if machine_handoff.get("calculated_threshold_met") is False:
        items.append("Saved facts do not support the reduced-rate threshold.")
    elif (
        machine_handoff.get("calculated_threshold_met") is None
        and machine_handoff.get("determining_condition_priority") is not None
    ):
        items.append("Saved facts still do not let the tool confirm the reduced-rate threshold.")

    return items


def _render_reviewer_risk_summary(
    machine_handoff: dict[str, Any],
    authority_memo: dict[str, Any] | None,
) -> str:
    risk_items = _build_reviewer_risk_items(machine_handoff, authority_memo)
    escalated = (
        machine_handoff.get("recommended_route") == "manual_review"
        or machine_handoff.get("review_priority") == "high"
        or isinstance(machine_handoff.get("guided_conflict"), dict)
    )
    heading = (
        "Escalated reviewer-risk signals remain in this immutable saved snapshot."
        if escalated
        else "Compact reviewer-risk cues from this immutable saved snapshot."
    )
    summary_rows = [
        ("Recommended route", str(machine_handoff.get("recommended_route") or "not_recorded")),
        ("Review priority", str(machine_handoff.get("review_priority") or "not_recorded")),
    ]
    risk_block = (
        _render_list(risk_items)
        if risk_items
        else "<p>No additional elevated reviewer-risk signals were recorded beyond the standard review path.</p>"
    )
    return "\n".join(
        [
            f"<p><strong>{html.escape(heading)}</strong></p>",
            _render_detail_rows(summary_rows),
            risk_block,
        ]
    )


def build_workpaper_html(case_view: dict[str, Any]) -> str:
    response_snapshot = case_view["response_snapshot"]
    request_snapshot = case_view["request_snapshot"]
    handoff_package = response_snapshot.get("handoff_package") or {}
    human_review_brief = handoff_package.get("human_review_brief") or {}
    machine_handoff = handoff_package.get("machine_handoff") or {}
    authority_memo = handoff_package.get("authority_memo")
    review_state = response_snapshot.get("review_state") or {}
    confirmed_scope = response_snapshot.get("confirmed_scope") or {}
    boundary_note = (
        (response_snapshot.get("result") or {}).get("boundary_note")
        or human_review_brief.get("handoff_note")
        or "This output is a bounded pre-review workpaper, not a final tax opinion."
    )
    next_actions = response_snapshot.get("next_actions") or []
    view_role_note = (
        "Creator read-only package for the internal case owner."
        if case_view.get("view_role") == "creator"
        else "Reviewer read-only package for downstream review and printable export."
    )

    confirmed_scope_lines = [
        f"Treaty: {confirmed_scope.get('applicable_treaty')}" if confirmed_scope.get("applicable_treaty") else "",
        f"Article: {confirmed_scope.get('applicable_article')}" if confirmed_scope.get("applicable_article") else "",
        f"Direction: {confirmed_scope.get('payment_direction')}" if confirmed_scope.get("payment_direction") else "",
        f"Income type: {confirmed_scope.get('income_type')}" if confirmed_scope.get("income_type") else "",
        f"Review state: {review_state.get('state_code')}" if review_state.get("state_code") else "",
    ]
    confirmed_scope_lines = [line for line in confirmed_scope_lines if line]

    next_action_lines = [
        f"[{action.get('priority', 'medium')}] {action.get('action', '')} — {action.get('reason', '')}"
        for action in next_actions
        if isinstance(action, dict)
    ]

    return f"""<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="utf-8" />
    <title>{html.escape(case_view['case_id'])} workpaper</title>
    <style>
      body {{
        font-family: "Times New Roman", Georgia, serif;
        color: #1b1712;
        margin: 32px;
        line-height: 1.45;
        background: #f9f6ef;
      }}
      header, footer {{
        border-bottom: 1px solid #b6aa96;
        padding-bottom: 12px;
        margin-bottom: 24px;
      }}
      footer {{
        border-top: 1px solid #b6aa96;
        border-bottom: none;
        padding-top: 12px;
        margin-top: 24px;
      }}
      h1, h2, h3 {{
        margin-bottom: 8px;
      }}
      section {{
        margin-bottom: 24px;
        page-break-inside: avoid;
      }}
      .notice-card {{
        border: 1px solid #d8cdb8;
        background: #fffdfa;
        padding: 12px;
      }}
      .detail-grid {{
        display: grid;
        grid-template-columns: minmax(180px, 220px) 1fr;
        gap: 8px 16px;
        margin: 0;
      }}
      .detail-row {{
        display: contents;
      }}
      dt {{
        font-weight: 700;
      }}
      dd {{
        margin: 0;
      }}
      .eyebrow {{
        letter-spacing: 0.08em;
        font-size: 12px;
        text-transform: uppercase;
      }}
      .topic-card {{
        border: 1px solid #d8cdb8;
        padding: 12px;
        margin-bottom: 12px;
        background: #fffdfa;
      }}
      pre {{
        white-space: pre-wrap;
        word-break: break-word;
        background: #fffdfa;
        border: 1px solid #d8cdb8;
        padding: 12px;
      }}
    </style>
  </head>
  <body>
    <header>
      <div class="eyebrow">Tax Treaty Agent Pre-Review Workpaper</div>
      <h1>READ-ONLY WORKPAPER</h1>
      <p><strong>Case ID:</strong> {html.escape(case_view['case_id'])}</p>
      <p><strong>Saved at:</strong> {html.escape(case_view['saved_at'])}</p>
      <p><strong>Schema version:</strong> {html.escape(case_view['schema_version'])}</p>
      <p><strong>View role:</strong> {html.escape(case_view['view_role'])}</p>
      <div class="notice-card">{html.escape(view_role_note)}</div>
    </header>

    <section>
      <h2>Case Summary</h2>
      {_render_case_summary(response_snapshot, human_review_brief, machine_handoff)}
    </section>

    <section>
      <h2>Reviewer Risk Summary</h2>
      {_render_reviewer_risk_summary(machine_handoff, authority_memo)}
    </section>

    <section>
      <h2>Saved Facts / Scenario Snapshot</h2>
      {_render_saved_fact_snapshot(request_snapshot)}
    </section>

    <section>
      <h2>Source Chain</h2>
      {_render_source_chain(response_snapshot, machine_handoff)}
    </section>

    <section>
      <h2>Input Snapshot</h2>
      {_render_pretty_json(request_snapshot)}
    </section>

    <section>
      <h2>Confirmed Scope / Review State</h2>
      {_render_list(confirmed_scope_lines)}
    </section>

    <section>
      <h2>Workflow Handoff</h2>
      {_render_workflow_handoff_detail(human_review_brief, machine_handoff)}
    </section>

    <section>
      <h2>Authority Memo</h2>
      {_render_authority_memo(authority_memo)}
    </section>

    <section>
      <h2>Next Actions</h2>
      {_render_list(next_action_lines)}
    </section>

    <section>
      <h2>Boundary / Not Final Opinion</h2>
      <p>{html.escape(str(boundary_note))}</p>
    </section>

    <footer>
      <p><strong>Timestamp:</strong> {html.escape(case_view['saved_at'])}</p>
      <p><strong>Version:</strong> {html.escape(case_view['schema_version'])}</p>
      <p><strong>Watermark:</strong> Tax Treaty Agent Pre-Review Workpaper</p>
    </footer>
  </body>
</html>"""
