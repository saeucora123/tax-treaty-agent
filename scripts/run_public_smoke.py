from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


DEFAULT_API_BASE = "http://127.0.0.1:8000"


@dataclass(frozen=True)
class SmokeCase:
    name: str
    path: str
    payload: dict[str, Any]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run the public-facing smoke proof against a live Tax Treaty Agent backend."
    )
    parser.add_argument(
        "--api-base",
        default=DEFAULT_API_BASE,
        help="Base URL for the backend API. Default: http://127.0.0.1:8000",
    )
    parser.add_argument(
        "--timeout",
        type=float,
        default=10.0,
        help="Request timeout in seconds. Default: 10",
    )
    return parser.parse_args()


def post_json(url: str, payload: dict[str, Any], timeout: float) -> dict[str, Any]:
    body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    request = Request(
        url,
        data=body,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urlopen(request, timeout=timeout) as response:
        return json.loads(response.read().decode("utf-8"))


def run_guided_supported_check(api_base: str, timeout: float) -> tuple[bool, str]:
    payload = {
        "input_mode": "guided",
        "guided_input": {
            "payer_country": "CN",
            "payee_country": "NL",
            "income_type": "dividends",
            "facts": {
                "direct_holding_percentage": "27",
                "payment_date": "2026-03-01",
                "holding_period_months": "18",
                "beneficial_owner_confirmed": "yes",
                "pe_effectively_connected": "no",
                "holding_structure_is_direct": "yes",
                "mli_ppt_risk_flag": "no",
            },
        },
    }
    response = post_json(f"{api_base}/analyze", payload, timeout)
    ok = (
        response.get("supported") is True
        and response.get("result", {}).get("article_number") == "10"
        and response.get("result", {}).get("rate") == "5%"
        and response.get("handoff_package", {})
        .get("machine_handoff", {})
        .get("recommended_route")
        == "standard_review"
    )
    detail = (
        f"observed supported={response.get('supported')}, "
        f"article={response.get('result', {}).get('article_number')}, "
        f"rate={response.get('result', {}).get('rate')}, "
        f"route={response.get('handoff_package', {}).get('machine_handoff', {}).get('recommended_route')}"
    )
    return ok, detail


def run_out_of_scope_check(api_base: str, timeout: float) -> tuple[bool, str]:
    payload = {"scenario": "中国居民企业向美国支付特许权使用费"}
    response = post_json(f"{api_base}/analyze", payload, timeout)
    ok = (
        response.get("supported") is False
        and response.get("reason") == "unsupported_country_pair"
    )
    detail = (
        f"observed supported={response.get('supported')}, "
        f"reason={response.get('reason')}"
    )
    return ok, detail


def main() -> int:
    args = parse_args()
    checks = [
        ("Guided CN->NL dividends narrows to 5%", run_guided_supported_check),
        ("Out-of-scope case is refused cleanly", run_out_of_scope_check),
    ]

    print("Tax Treaty Agent Public Smoke")
    print(f"API base: {args.api_base}")
    print("")

    passed = 0
    for label, check in checks:
        try:
            ok, detail = check(args.api_base, args.timeout)
        except (HTTPError, URLError, TimeoutError, OSError) as error:
            ok = False
            detail = f"request failed: {error}"

        status = "PASS" if ok else "FAIL"
        print(f"[{status}] {label}")
        print(f"       {detail}")
        if ok:
            passed += 1

    total = len(checks)
    print("")
    print(f"Summary: {passed}/{total} checks passed")
    return 0 if passed == total else 1


if __name__ == "__main__":
    raise SystemExit(main())
