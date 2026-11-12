"""Escalation checks for weak small-model responses (Phase 1B)."""

from src.core.types import AskResult


def needs_escalation(result: AskResult, min_retrieval_score: float) -> bool:
    """Return True if a small-model result looks weak and should be retried on the large model.

    Args:
        result: Result returned by the small model.
        min_retrieval_score: Minimum acceptable top retrieval score.

    Returns:
        True if escalation is needed, False otherwise.
    """
    # TODO (Phase 1B - Task 1B.4): Check retrieval scores, missing citations, or refusal phrases.
    return False

