"""Document chunking utilities for corpus ingestion."""


def chunk_text(text: str, chunk_size: int, chunk_overlap: int) -> list[str]:
    """Split a document string into overlapping chunks.

    Args:
        text: Raw document text.
        chunk_size: Maximum size of each chunk.
        chunk_overlap: Overlap size between consecutive chunks.

    Returns:
        List of text chunks.
    """
    # TODO (Task 0.3): Implement deterministic chunking with overlap.
    raise NotImplementedError("Chunking will be implemented in Task 0.3.")

