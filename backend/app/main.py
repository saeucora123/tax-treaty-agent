from typing import Literal

from fastapi import FastAPI
from pydantic import BaseModel

from app.service import analyze_scenario


app = FastAPI(title="Tax Treaty Agent API")


class FactInputs(BaseModel):
    direct_holding_confirmed: Literal["yes", "no", "unknown"] | None = None
    direct_holding_threshold_met: Literal["yes", "no", "unknown"] | None = None
    pe_effectively_connected: Literal["yes", "no", "unknown"] | None = None
    beneficial_owner_confirmed: Literal["yes", "no", "unknown"] | None = None


class AnalyzeRequest(BaseModel):
    scenario: str
    data_source: Literal["stable", "llm_generated"] = "stable"
    fact_inputs: FactInputs | None = None


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/analyze")
def analyze(request: AnalyzeRequest) -> dict:
    return analyze_scenario(
        request.scenario,
        data_source=request.data_source,
        fact_inputs=request.fact_inputs.model_dump(exclude_none=True)
        if request.fact_inputs is not None
        else None,
    )
