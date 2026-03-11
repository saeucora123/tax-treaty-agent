from app import llm_smoke


def test_build_input_smoke_report_marks_llm_success():
    response = {
        "supported": True,
        "input_interpretation": {
            "parser_source": "llm",
            "payer_country": "CN",
            "payee_country": "NL",
            "transaction_type": "royalties",
            "matched_transaction_label": "software license",
        },
        "normalized_input": {
            "payer_country": "CN",
            "payee_country": "NL",
            "transaction_type": "royalties",
        },
        "result": {
            "summary": "Preliminary view: Article 12 Royalties appears relevant.",
            "immediate_action": "Proceed with standard manual review before relying on the treaty position.",
        },
    }

    report = llm_smoke.build_input_smoke_report(
        "I am a Beijing developer licensing software to an Amsterdam company",
        response,
    )

    assert report == {
        "status": "llm_used",
        "scenario": "I am a Beijing developer licensing software to an Amsterdam company",
        "supported": True,
        "parser_source": "llm",
        "input_interpretation": {
            "parser_source": "llm",
            "payer_country": "CN",
            "payee_country": "NL",
            "transaction_type": "royalties",
            "matched_transaction_label": "software license",
        },
        "normalized_input": {
            "payer_country": "CN",
            "payee_country": "NL",
            "transaction_type": "royalties",
        },
        "result_summary": "Preliminary view: Article 12 Royalties appears relevant.",
        "immediate_action": "Proceed with standard manual review before relying on the treaty position.",
    }


def test_build_input_smoke_report_marks_rules_fallback():
    response = {
        "supported": True,
        "normalized_input": {
            "payer_country": "CN",
            "payee_country": "NL",
            "transaction_type": "royalties",
        },
        "result": {
            "summary": "Preliminary view: Article 12 Royalties appears relevant.",
            "immediate_action": "Proceed with standard manual review before relying on the treaty position.",
        },
    }

    report = llm_smoke.build_input_smoke_report(
        "中国居民企业向荷兰支付特许权使用费",
        response,
    )

    assert report == {
        "status": "fallback_to_rules",
        "scenario": "中国居民企业向荷兰支付特许权使用费",
        "supported": True,
        "parser_source": "rules",
        "input_interpretation": None,
        "normalized_input": {
            "payer_country": "CN",
            "payee_country": "NL",
            "transaction_type": "royalties",
        },
        "result_summary": "Preliminary view: Article 12 Royalties appears relevant.",
        "immediate_action": "Proceed with standard manual review before relying on the treaty position.",
    }


def test_run_input_smoke_delegates_to_analyze_scenario(monkeypatch):
    monkeypatch.setattr(
        llm_smoke,
        "analyze_scenario",
        lambda scenario: {
            "supported": False,
            "input_interpretation": {
                "parser_source": "llm",
                "payer_country": "CN",
                "payee_country": None,
                "transaction_type": "royalties",
                "matched_transaction_label": "software license",
            },
            "reason": "incomplete_scenario",
            "immediate_action": "Add the missing scenario facts before running the treaty review again.",
        },
    )

    report = llm_smoke.run_input_smoke(
        "I am a Beijing developer licensing software to a European company"
    )

    assert report == {
        "status": "llm_used",
        "scenario": "I am a Beijing developer licensing software to a European company",
        "supported": False,
        "parser_source": "llm",
        "input_interpretation": {
            "parser_source": "llm",
            "payer_country": "CN",
            "payee_country": None,
            "transaction_type": "royalties",
            "matched_transaction_label": "software license",
        },
        "reason": "incomplete_scenario",
        "immediate_action": "Add the missing scenario facts before running the treaty review again.",
    }
