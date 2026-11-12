"""Vector store retrieval against the corpus collection."""

from src.core.types import SourceDocument


async def retrieve_chunks(
    query_vector: list[float],
    collection_name: str,
    top_k: int,
) -> list[SourceDocument]:
    """Search the vector store for the top-k most relevant document chunks.

    Args:
        query_vector: Embedded query vector.
        collection_name: Target Qdrant collection name.
        top_k: Number of chunks to retrieve.

    Returns:
        Ordered list of SourceDocument citations.
    """
    # TODO (Task 0.4): Query Qdrant asynchronously using shared client.
    raise NotImplementedError("Retrieval will be implemented in Task 0.4.")

