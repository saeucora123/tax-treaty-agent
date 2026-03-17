from typing import Annotated, Literal

from fastapi import FastAPI
from pydantic import BaseModel, Field

from app.service import analyze_scenario


app = FastAPI(title="Tax Treaty Agent API")


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
    data_source: Literal["stable", "llm_generated"] = "stable"
    guided_input: GuidedInput | None = None


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/analyze")
def analyze(request: AnalyzeRequest) -> dict:
    return analyze_scenario(
        request.scenario,
        data_source=request.data_source,
        input_mode=request.input_mode,
        guided_input=request.guided_input.model_dump(exclude_none=True)
        if request.guided_input is not None
        else None,
    )
