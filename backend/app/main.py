from fastapi import FastAPI
from pydantic import BaseModel

from app.service import analyze_scenario


app = FastAPI(title="Tax Treaty Agent API")


class AnalyzeRequest(BaseModel):
    scenario: str


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/analyze")
def analyze(request: AnalyzeRequest) -> dict:
    return analyze_scenario(request.scenario)

