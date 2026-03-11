import json

import pytest

from app import llm_input_parser


class FakeHTTPResponse:
    def __init__(self, payload: dict):
        self._payload = json.dumps(payload).encode("utf-8")

    def read(self) -> bytes:
        return self._payload

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False


def test_load_config_from_env_returns_none_without_api_key(monkeypatch):
    monkeypatch.delenv("DEEPSEEK_API_KEY", raising=False)
    monkeypatch.setattr(llm_input_parser, "DOTENV_PATH", None)
    monkeypatch.setenv("PYTEST_CURRENT_TEST", "backend/tests/test_llm_input_parser.py::test")

    assert llm_input_parser.load_config_from_env() is None


def test_load_config_from_env_stays_off_under_pytest_without_explicit_opt_in(monkeypatch):
    monkeypatch.setenv("PYTEST_CURRENT_TEST", "backend/tests/test_llm_input_parser.py::test")
    monkeypatch.delenv("TAX_TREATY_AGENT_ALLOW_LIVE_LLM_IN_TESTS", raising=False)

    config = llm_input_parser.load_config_from_env()

    assert config is None


def test_load_config_from_env_can_read_local_dotenv_file(tmp_path, monkeypatch):
    dotenv_path = tmp_path / ".env"
    dotenv_path.write_text(
        'DEEPSEEK_API_KEY="test-dotenv-key"\n'
        'DEEPSEEK_BASE_URL="https://api.deepseek.com"\n'
        'DEEPSEEK_MODEL="deepseek-chat"\n'
        "DEEPSEEK_TIMEOUT_SECONDS=9\n",
        encoding="utf-8",
    )
    monkeypatch.delenv("DEEPSEEK_API_KEY", raising=False)
    monkeypatch.delenv("DEEPSEEK_BASE_URL", raising=False)
    monkeypatch.delenv("DEEPSEEK_MODEL", raising=False)
    monkeypatch.delenv("DEEPSEEK_TIMEOUT_SECONDS", raising=False)
    monkeypatch.setenv("PYTEST_CURRENT_TEST", "backend/tests/test_llm_input_parser.py::test")
    monkeypatch.setenv("TAX_TREATY_AGENT_ALLOW_LIVE_LLM_IN_TESTS", "1")
    monkeypatch.setattr(llm_input_parser, "DOTENV_PATH", dotenv_path)

    config = llm_input_parser.load_config_from_env()

    assert config == llm_input_parser.LLMInputParserConfig(
        api_key="test-dotenv-key",
        base_url="https://api.deepseek.com",
        model="deepseek-chat",
        timeout_seconds=9,
    )


def test_parse_scenario_to_json_reads_deepseek_compatible_response(monkeypatch):
    config = llm_input_parser.LLMInputParserConfig(
        api_key="test-key",
        base_url="https://example.com",
        model="deepseek-chat",
        timeout_seconds=5,
    )
    monkeypatch.setattr(
        llm_input_parser.request,
        "urlopen",
        lambda req, timeout: FakeHTTPResponse(
            {
                "choices": [
                    {
                        "message": {
                            "content": json.dumps(
                                {
                                    "payer_country": "CN",
                                    "payee_country": "NL",
                                    "transaction_type": "royalties",
                                    "matched_transaction_label": "软件授权",
                                    "needs_clarification": False,
                                }
                            )
                        }
                    }
                ]
            }
        ),
    )

    payload = llm_input_parser.parse_scenario_to_json(
        "我是北京的独立开发者，把软件授权给阿姆斯特丹的公司",
        config=config,
    )

    assert payload == {
        "payer_country": "CN",
        "payee_country": "NL",
        "transaction_type": "royalties",
        "matched_transaction_label": "软件授权",
        "needs_clarification": False,
    }


def test_parse_scenario_to_json_raises_on_invalid_response_shape(monkeypatch):
    config = llm_input_parser.LLMInputParserConfig(
        api_key="test-key",
        base_url="https://example.com",
        model="deepseek-chat",
        timeout_seconds=5,
    )
    monkeypatch.setattr(
        llm_input_parser.request,
        "urlopen",
        lambda req, timeout: FakeHTTPResponse({"choices": []}),
    )

    with pytest.raises(llm_input_parser.LLMInputParserError):
        llm_input_parser.parse_scenario_to_json(
            "中国居民企业向荷兰支付特许权使用费",
            config=config,
        )


def test_parse_scenario_to_json_accepts_fenced_json_content(monkeypatch):
    config = llm_input_parser.LLMInputParserConfig(
        api_key="test-key",
        base_url="https://example.com",
        model="deepseek-chat",
        timeout_seconds=5,
    )
    monkeypatch.setattr(
        llm_input_parser.request,
        "urlopen",
        lambda req, timeout: FakeHTTPResponse(
            {
                "choices": [
                    {
                        "message": {
                            "content": """```json
{"payer_country":"China","payee_country":"Netherlands","transaction_type":"royalties","matched_transaction_label":"software license","needs_clarification":false}
```"""
                        }
                    }
                ]
            }
        ),
    )

    payload = llm_input_parser.parse_scenario_to_json(
        "I am a Beijing developer licensing software to an Amsterdam company",
        config=config,
    )

    assert payload == {
        "payer_country": "China",
        "payee_country": "Netherlands",
        "transaction_type": "royalties",
        "matched_transaction_label": "software license",
        "needs_clarification": False,
    }


def test_build_request_payload_explains_payment_direction_and_includes_example():
    payload = llm_input_parser.build_request_payload(
        "我是北京的独立开发者，把软件授权给阿姆斯特丹的公司",
        "deepseek-chat",
    )

    system_prompt = payload["messages"][0]["content"]

    assert "payer_country means the country the payment is paid from" in system_prompt
    assert "payee_country means the country the payment is paid to" in system_prompt
    assert (
        "I am a Beijing developer licensing software to an Amsterdam company"
        in system_prompt
    )
    assert '"payer_country":"CN"' in system_prompt
    assert '"payee_country":"NL"' in system_prompt
    assert (
        "If the input is not a tax or cross-border payment scenario, return null countries, transaction_type unknown, and needs_clarification true."
        in system_prompt
    )


def test_parse_scenario_to_json_extracts_json_from_mixed_content(monkeypatch):
    config = llm_input_parser.LLMInputParserConfig(
        api_key="test-key",
        base_url="https://example.com",
        model="deepseek-chat",
        timeout_seconds=5,
    )
    monkeypatch.setattr(
        llm_input_parser.request,
        "urlopen",
        lambda req, timeout: FakeHTTPResponse(
            {
                "choices": [
                    {
                        "message": {
                            "content": (
                                "Here is the extracted routing JSON:\n"
                                '{"payer_country":"CN","payee_country":"NL","transaction_type":"royalties","matched_transaction_label":"software license","needs_clarification":false}\n'
                                "Use the JSON only."
                            )
                        }
                    }
                ]
            }
        ),
    )

    payload = llm_input_parser.parse_scenario_to_json(
        "I am a Beijing developer licensing software to an Amsterdam company",
        config=config,
    )

    assert payload == {
        "payer_country": "CN",
        "payee_country": "NL",
        "transaction_type": "royalties",
        "matched_transaction_label": "software license",
        "needs_clarification": False,
    }
