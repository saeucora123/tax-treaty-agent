def assert_machine_handoff(
    payload: dict,
    *,
    record_kind: str,
    review_state_code: str,
    recommended_route: str,
) -> dict:
    assert "handoff_package" in payload
    handoff = payload["handoff_package"]
    assert payload["schema_version"] == "slice3.v1"
    assert handoff["machine_handoff"]["schema_version"] == payload["schema_version"]
    assert handoff["machine_handoff"]["record_kind"] == record_kind
    assert handoff["machine_handoff"]["review_state_code"] == review_state_code
    assert handoff["machine_handoff"]["recommended_route"] == recommended_route
    assert handoff["human_review_brief"]["brief_title"] == "Treaty Pre-Review Brief"
    assert "not a final tax opinion" in handoff["human_review_brief"]["handoff_note"]
    return handoff


def guided_cn_nl_dividend_payload(facts: dict) -> dict:
    return {
        "input_mode": "guided",
        "guided_input": {
            "payer_country": "CN",
            "payee_country": "NL",
            "income_type": "dividends",
            "facts": facts,
        },
    }
