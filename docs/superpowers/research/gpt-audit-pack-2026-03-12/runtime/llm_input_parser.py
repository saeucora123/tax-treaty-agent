from __future__ import annotations

import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from urllib import error, request


DEFAULT_BASE_URL = "https://api.deepseek.com"
DEFAULT_MODEL = "deepseek-chat"
DEFAULT_TIMEOUT_SECONDS = 20
DOTENV_PATH = Path(__file__).resolve().parents[2] / ".env"
ALLOW_LIVE_LLM_IN_TESTS_ENV = "TAX_TREATY_AGENT_ALLOW_LIVE_LLM_IN_TESTS"


@dataclass(frozen=True)
class LLMInputParserConfig:
    api_key: str
    base_url: str = DEFAULT_BASE_URL
    model: str = DEFAULT_MODEL
    timeout_seconds: int = DEFAULT_TIMEOUT_SECONDS


class LLMInputParserError(RuntimeError):
    pass


def load_config_from_env() -> LLMInputParserConfig | None:
    if os.getenv("PYTEST_CURRENT_TEST") and not is_truthy_env(ALLOW_LIVE_LLM_IN_TESTS_ENV):
        return None

    env_values = load_local_dotenv_values()

    api_key = read_env_value("DEEPSEEK_API_KEY", env_values).strip()
    if not api_key:
        return None

    base_url = read_env_value("DEEPSEEK_BASE_URL", env_values, DEFAULT_BASE_URL).strip() or DEFAULT_BASE_URL
    model = read_env_value("DEEPSEEK_MODEL", env_values, DEFAULT_MODEL).strip() or DEFAULT_MODEL
    timeout_raw = read_env_value(
        "DEEPSEEK_TIMEOUT_SECONDS",
        env_values,
        str(DEFAULT_TIMEOUT_SECONDS),
    ).strip()
    try:
        timeout_seconds = int(timeout_raw)
    except ValueError:
        timeout_seconds = DEFAULT_TIMEOUT_SECONDS

    return LLMInputParserConfig(
        api_key=api_key,
        base_url=base_url.rstrip("/"),
        model=model,
        timeout_seconds=timeout_seconds,
    )


def load_local_dotenv_values() -> dict[str, str]:
    if DOTENV_PATH is None or not DOTENV_PATH.exists():
        return {}

    values: dict[str, str] = {}
    for raw_line in DOTENV_PATH.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, raw_value = line.split("=", 1)
        values[key.strip()] = raw_value.strip().strip("'").strip('"')
    return values


def read_env_value(name: str, dotenv_values: dict[str, str], default: str = "") -> str:
    runtime_value = os.getenv(name)
    if runtime_value is not None:
        return runtime_value
    return dotenv_values.get(name, default)


def is_truthy_env(name: str) -> bool:
    value = os.getenv(name, "")
    return value.strip().lower() in {"1", "true", "yes", "on"}


def parse_scenario_to_json(scenario: str, config: LLMInputParserConfig | None = None) -> dict[str, Any] | None:
    resolved_config = config or load_config_from_env()
    if resolved_config is None:
        return None

    payload = build_request_payload(scenario, resolved_config.model)
    body = json.dumps(payload).encode("utf-8")
    http_request = request.Request(
        url=f"{resolved_config.base_url}/chat/completions",
        data=body,
        headers={
            "Authorization": f"Bearer {resolved_config.api_key}",
            "Content-Type": "application/json",
        },
        method="POST",
    )

    try:
        with request.urlopen(http_request, timeout=resolved_config.timeout_seconds) as response:
            response_payload = json.loads(response.read().decode("utf-8"))
    except (error.URLError, TimeoutError, json.JSONDecodeError) as exc:
        raise LLMInputParserError(str(exc)) from exc

    try:
        content = response_payload["choices"][0]["message"]["content"]
        return json.loads(extract_json_content(content))
    except (KeyError, IndexError, TypeError, json.JSONDecodeError) as exc:
        raise LLMInputParserError("Failed to parse structured JSON from LLM response.") from exc


def build_request_payload(scenario: str, model: str) -> dict[str, Any]:
    system_prompt = (
        "You extract structured fields for a bounded tax treaty review tool. "
        "Return only JSON with keys: payer_country, payee_country, transaction_type, "
        "matched_transaction_label, needs_clarification. "
        "payer_country means the country the payment is paid from. "
        "payee_country means the country the payment is paid to. "
        "Use ISO country codes like CN, NL, US when possible. "
        "Use transaction_type only from: dividends, interest, royalties, unknown. "
        "If a required core fact is unclear, set needs_clarification to true. "
        "If the input is not a tax or cross-border payment scenario, return null countries, "
        "transaction_type unknown, and needs_clarification true. "
        "Example: "
        'Input: "I am a Beijing developer licensing software to an Amsterdam company" '
        'Output: {"payer_country":"CN","payee_country":"NL","transaction_type":"royalties","matched_transaction_label":"software license","needs_clarification":false}. '
        "Do not reverse payer and payee."
    )

    return {
        "model": model,
        "temperature": 0,
        "response_format": {"type": "json_object"},
        "messages": [
            {
                "role": "system",
                "content": system_prompt,
            },
            {
                "role": "user",
                "content": scenario,
            },
        ],
    }


def strip_json_fences(content: str) -> str:
    normalized = content.strip()
    if not normalized.startswith("```"):
        return normalized

    lines = normalized.splitlines()
    if not lines:
        return normalized

    if lines[0].startswith("```"):
        lines = lines[1:]
    if lines and lines[-1].strip() == "```":
        lines = lines[:-1]

    return "\n".join(lines).strip()


def extract_json_content(content: str) -> str:
    normalized = strip_json_fences(content)
    if normalized.startswith("{") and normalized.endswith("}"):
        return normalized

    start = normalized.find("{")
    end = normalized.rfind("}")
    if start != -1 and end != -1 and end > start:
        return normalized[start : end + 1]

    return normalized
