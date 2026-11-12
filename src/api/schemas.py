"""Pydantic request, response, and error schemas for the API."""

from pydantic import BaseModel, Field

from src.core.types import RouteType, SourceDocument


class ErrorResponse(BaseModel):
    """Consistent error response payload (AGENT.md Section 7)."""

    detail: str
    code: str


class HealthResponse(BaseModel):
    """Liveness probe response."""

    status: str = "ok"
    app_env: str
    corpus_version: int


class AskRequest(BaseModel):
    """Input payload for POST /ask."""

    query: str = Field(..., min_length=1, max_length=2000, description="User question")
    tenant_id: str | None = Field(
        default=None,
        max_length=128,
        description="Optional tenant identifier for cache isolation",
    )


class AskResponse(BaseModel):
    """Output payload for POST /ask (AGENT.md Section 7)."""

    answer: str
    sources: list[SourceDocument]
    route: RouteType
    cache_hit: bool
    model_used: str
    escalated: bool
    cost_usd: float
    latency_ms: int

