from fastapi import FastAPI
from pydantic import BaseModel
from typing import Literal

from app.service import analyze_scenario


app = FastAPI(title="Tax Treaty Agent API")


class AnalyzeRequest(BaseModel):
    scenario: str
    data_source: Literal["stable", "llm_generated"] = "stable"


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/analyze")
def analyze(request: AnalyzeRequest) -> dict:
    return analyze_scenario(request.scenario, data_source=request.data_source)
