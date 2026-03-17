from fastapi import FastAPI

from app.contracts import AnalyzeRequest, InternalAnalyzeRequest
from app.guided_facts import build_guided_fact_contract
from app.service import analyze_scenario


app = FastAPI(title="Tax Treaty Agent API")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/analyze")
def analyze(request: AnalyzeRequest) -> dict:
    return analyze_scenario(
        request.scenario,
        input_mode=request.input_mode,
        guided_input=request.guided_input.model_dump(exclude_none=True)
        if request.guided_input is not None
        else None,
    )


@app.post("/internal/analyze")
def internal_analyze(request: InternalAnalyzeRequest) -> dict:
    return analyze_scenario(
        request.scenario,
        data_source=request.data_source,
        input_mode=request.input_mode,
        guided_input=request.guided_input.model_dump(exclude_none=True)
        if request.guided_input is not None
        else None,
    )


@app.get("/guided-facts")
def guided_facts() -> dict[str, object]:
    return build_guided_fact_contract()
