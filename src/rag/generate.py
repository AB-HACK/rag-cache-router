"""Answer generation with citations using LiteLLM."""

from src.core.types import SourceDocument


async def generate_answer(
    query: str,
    sources: list[SourceDocument],
    model_name: str,
) -> dict[str, object]:
    """Generate a grounded answer from retrieved chunks via LiteLLM.

    Args:
        query: User question (treated as untrusted input).
        sources: Retrieved document chunks (treated as untrusted context).
        model_name: LiteLLM model identifier.

    Returns:
        Dictionary containing answer text, input_tokens, and output_tokens.
    """
    # TODO (Task 0.4): Call litellm.acompletion with system prompt separated from context.
    raise NotImplementedError("Generation will be implemented in Task 0.4.")

