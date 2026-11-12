"""Versioned semantic cache backed by the vector store (Phase 1A)."""

from src.core.types import AskResult


class SemanticCache:
    """Lookup and store normalized query embeddings with corpus_version and TTL."""

    async def lookup(
        self,
        query_vector: list[float],
        corpus_version: int,
        tenant_id: str | None = None,
    ) -> AskResult | None:
        """Return a cached AskResult if similarity >= threshold, version matches, and not expired."""
        # TODO (Phase 1A - Task 1A.1 / 1A.2): Implement vector lookup with metadata filters.
        return None

    async def store(
        self,
        query_vector: list[float],
        query_text: str,
        result: AskResult,
        corpus_version: int,
        tenant_id: str | None = None,
    ) -> None:
        """Persist a cacheable answer in the semantic cache collection."""
        # TODO (Phase 1A - Task 1A.1 / 1A.2): Never cache errors, empty, or "I don't know".
        return None

