from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse

from app.cases import CASE_NOT_FOUND_DETAIL, build_workpaper_html, create_case_snapshot, load_case_view
from app.contracts import (
    AnalyzeRequest,
    InternalAnalyzeRequest,
    InternalOnboardingApproveRequest,
    InternalOnboardingManifestRequest,
    InternalOnboardingReviewRequest,
    InternalOnboardingStartReviewRequest,
)
from app.guided_facts import build_guided_fact_contract
from app.service import analyze_scenario
from app.source_ingest import SourceBuildError
from app.treaty_onboarding import (
    ManifestValidationError,
    PromotionGateError,
    ReviewGateError,
    TreatyOnboardingError,
    build_workspace,
    list_onboarding_manifests,
    run_approve,
    run_compile,
    run_promote,
    run_review,
    run_source_build_for_manifest,
    save_reviewed_source_json,
    start_review_session,
)


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


@app.post("/cases")
def create_case(request: AnalyzeRequest) -> dict[str, object]:
    if request.guided_input is None or request.input_mode == "free_text":
        raise HTTPException(
            status_code=400,
            detail="Case persistence currently supports guided input only.",
        )

    request_snapshot = request.model_dump(exclude_none=True)
    response_snapshot = analyze_scenario(
        request.scenario,
        input_mode="guided",
        guided_input=request.guided_input.model_dump(exclude_none=True),
    )
    return create_case_snapshot(request_snapshot, response_snapshot)


@app.get("/cases/{case_id}")
def get_case(case_id: str, token: str) -> dict[str, object]:
    case_view = load_case_view(case_id, token)
    if case_view is None:
        raise HTTPException(status_code=404, detail=CASE_NOT_FOUND_DETAIL)
    return case_view


@app.get("/cases/{case_id}/workpaper", response_class=HTMLResponse)
def get_case_workpaper(case_id: str, token: str) -> HTMLResponse:
    case_view = load_case_view(case_id, token)
    if case_view is None:
        raise HTTPException(status_code=404, detail=CASE_NOT_FOUND_DETAIL)
    return HTMLResponse(
        content=build_workpaper_html(case_view),
        headers={"Content-Disposition": f'inline; filename="{case_id}-workpaper.html"'},
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


def _raise_internal_onboarding_error(error: Exception) -> None:
    raise HTTPException(status_code=400, detail=str(error)) from error


@app.get("/internal/onboarding/manifests")
def list_internal_onboarding_manifests() -> dict[str, object]:
    return {"manifests": list_onboarding_manifests()}


@app.get("/internal/onboarding/workspace")
def get_internal_onboarding_workspace(manifest: str) -> dict[str, object]:
    try:
        return build_workspace(manifest)
    except (TreatyOnboardingError, ManifestValidationError) as error:
        _raise_internal_onboarding_error(error)


@app.post("/internal/onboarding/source-build")
def run_internal_onboarding_source_build(
    request: InternalOnboardingManifestRequest,
) -> dict[str, object]:
    try:
        run_source_build_for_manifest(request.manifest)
        return build_workspace(request.manifest)
    except (TreatyOnboardingError, ManifestValidationError, SourceBuildError) as error:
        _raise_internal_onboarding_error(error)


@app.post("/internal/onboarding/compile")
def run_internal_onboarding_compile(
    request: InternalOnboardingManifestRequest,
) -> dict[str, object]:
    try:
        run_compile(request.manifest)
        return build_workspace(request.manifest)
    except (TreatyOnboardingError, ManifestValidationError) as error:
        _raise_internal_onboarding_error(error)


@app.post("/internal/onboarding/review")
def run_internal_onboarding_review(
    request: InternalOnboardingReviewRequest,
) -> dict[str, object]:
    try:
        if request.reviewed_source_json is not None:
            save_reviewed_source_json(request.manifest, request.reviewed_source_json)
        run_review(request.manifest)
        return build_workspace(request.manifest)
    except (TreatyOnboardingError, ManifestValidationError, ReviewGateError) as error:
        _raise_internal_onboarding_error(error)


@app.post("/internal/onboarding/start-review")
def run_internal_onboarding_start_review(
    request: InternalOnboardingStartReviewRequest,
) -> dict[str, object]:
    try:
        start_review_session(
            request.manifest,
            reviewer_name=request.reviewer_name,
            note=request.note,
        )
        return build_workspace(request.manifest)
    except (TreatyOnboardingError, ManifestValidationError, ReviewGateError) as error:
        _raise_internal_onboarding_error(error)


@app.post("/internal/onboarding/approve")
def run_internal_onboarding_approve(
    request: InternalOnboardingApproveRequest,
) -> dict[str, object]:
    try:
        run_approve(
            request.manifest,
            reviewer_name=request.reviewer_name,
            note=request.note,
        )
        return build_workspace(request.manifest)
    except (TreatyOnboardingError, ManifestValidationError, ReviewGateError) as error:
        _raise_internal_onboarding_error(error)


@app.post("/internal/onboarding/promote")
def run_internal_onboarding_promote(
    request: InternalOnboardingManifestRequest,
) -> dict[str, object]:
    try:
        run_promote(request.manifest)
        return build_workspace(request.manifest)
    except (TreatyOnboardingError, ManifestValidationError, ReviewGateError, PromotionGateError) as error:
        _raise_internal_onboarding_error(error)
