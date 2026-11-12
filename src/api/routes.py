"""API route handlers (thin layer: validate input, call services, return response)."""

from fastapi import APIRouter, Depends, HTTPException

from src.api.dependencies import get_app_settings
from src.api.schemas import AskRequest, AskResponse, HealthResponse
from src.core.settings import AppSettings

router = APIRouter()


@router.get("/health", response_model=HealthResponse, tags=["system"])
async def health_check(settings: AppSettings = Depends(get_app_settings)) -> HealthResponse:
    """Liveness check returning service status and active corpus version."""
    return HealthResponse(
        status="ok",
        app_env=settings.app_env,
        corpus_version=settings.corpus.corpus_version,
    )


@router.post("/ask", response_model=AskResponse, tags=["rag"])
async def ask(payload: AskRequest) -> AskResponse:
    """Answer a question via the RAG pipeline (to be wired in Task 0.5)."""
    # TODO (Task 0.5): Call RAG service, log request, and return AskResponse.
    raise HTTPException(
        status_code=501,
        detail="POST /ask is not implemented yet (scheduled for Task 0.5).",
    )

