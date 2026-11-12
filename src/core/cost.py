"""Cost calculation utilities driven by config/models.yaml."""

from src.core.settings import ModelConfig, ModelsRegistry


def calculate_cost(
    input_tokens: int,
    output_tokens: int,
    model_config: ModelConfig,
) -> float:
    """Compute request cost in USD from token counts and a model's price table entry.

    Args:
        input_tokens: Number of prompt/input tokens consumed.
        output_tokens: Number of completion/output tokens generated.
        model_config: Pricing configuration for the model used.

    Returns:
        Total cost in USD, rounded to 8 decimal places.
    """
    if input_tokens < 0 or output_tokens < 0:
        raise ValueError("Token counts must be non-negative.")

    input_cost = (input_tokens / 1000.0) * model_config.input_price_per_1k
    output_cost = (output_tokens / 1000.0) * model_config.output_price_per_1k
    return round(input_cost + output_cost, 8)


def calculate_cost_for_model_key(
    input_tokens: int,
    output_tokens: int,
    model_key: str,
    registry: ModelsRegistry,
) -> float:
    """Look up a model by key in ModelsRegistry and calculate its USD cost."""
    if model_key not in registry.models:
        raise KeyError(f"Unknown model key '{model_key}' in models registry.")
    return calculate_cost(input_tokens, output_tokens, registry.models[model_key])

