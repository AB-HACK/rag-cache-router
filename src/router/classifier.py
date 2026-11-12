"""Rule-based query complexity classifier (Phase 1B)."""

from typing import Literal


def classify_query(query: str) -> tuple[Literal["simple", "complex"], dict[str, object]]:
    """Classify a query as 'simple' or 'complex' and return the fired signals.

    Args:
        query: User question string.

    Returns:
        Tuple of (route_label, signals_dict).
    """
    # TODO (Phase 1B - Task 1B.2): Implement rule-based signals (length, keywords, entities).
    return "complex", {"reason": "baseline_default"}

