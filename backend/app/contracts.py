from __future__ import annotations

from typing import Annotated, Literal

from pydantic import BaseModel, Field


class GuidedInput(BaseModel):
    payer_country: str | None = None
    payee_country: str | None = None
    income_type: str | None = None
    facts: Annotated[
        dict[str, str],
        Field(
            default_factory=dict,
            description=(
                "This relaxation is required to support raw fact fields for CN-NL dividends "
                "(direct_holding_percentage, payment_date, holding_period_months). "
                'Interest and royalties fact values are still expected to be "yes", "no", or '
                '"unknown" — the schema does not enforce this but service-layer validation applies.'
            ),
        ),
    ]
    scenario_text: str | None = None


class AnalyzeRequest(BaseModel):
    input_mode: Literal["guided", "free_text"] | None = None
    scenario: str | None = None
    guided_input: GuidedInput | None = None


class InternalAnalyzeRequest(AnalyzeRequest):
    data_source: Literal["stable", "llm_generated"] = "stable"
