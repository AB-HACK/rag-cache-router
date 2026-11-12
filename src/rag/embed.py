"""Shared embedding model wrapper (used by corpus, queries, and semantic cache)."""

import re


def normalize_query(query: str) -> str:
    """Normalize a query string before embedding (lowercase, strip punctuation/whitespace).

    Args:
        query: Raw user query string.

    Returns:
        Normalized query string.
    """
    cleaned = re.sub(r"[^\w\s]", " ", query.lower())
    return " ".join(cleaned.split())


class Embedder:
    """Wrapper around sentence-transformers for encoding text into vectors."""

    def __init__(self, model_name: str) -> None:
        """Initialize embedder configuration (model loaded lazily or at startup)."""
        self.model_name = model_name

    async def embed_text(self, text: str) -> list[float]:
        """Encode a single text string into an embedding vector without blocking the event loop."""
        # TODO (Task 0.3): Run sentence-transformers encode in a thread pool.
        raise NotImplementedError("Embedding will be implemented in Task 0.3.")

