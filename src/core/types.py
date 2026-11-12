"""Shared domain types and data structures used across the RAG pipeline."""

from typing import Literal

from pydantic import BaseModel, Field

RouteType = Literal["simple", "complex", "cache"]


class SourceDocument(BaseModel):
    """A retrieved document chunk returned as a citation."""

    doc_id: str
    title: str | None = None
    score: float
    snippet: str


class AskResult(BaseModel):
    """Internal result object returned by the RAG / cache / router pipeline."""

    answer: str
    sources: list[SourceDocument] = Field(default_factory=list)
    route: RouteType
    cache_hit: bool = False
    cache_score: float | None = None
    router_signals: dict[str, object] = Field(default_factory=dict)
    model_used: str
    escalated: bool = False
    input_tokens: int = 0
    output_tokens: int = 0
    cost_usd: float = 0.0
    latency_ms: int = 0
    corpus_version: int = 1

