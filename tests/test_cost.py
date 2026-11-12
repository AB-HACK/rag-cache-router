"""Tests for cost calculation against the model price table."""

import pytest

from src.core.cost import calculate_cost, calculate_cost_for_model_key
from src.core.settings import ModelConfig, ModelsRegistry


def test_calculate_cost_known_tokens() -> None:
    """Cost equals (input/1000 * input_price) + (output/1000 * output_price)."""
    model = ModelConfig(
        provider_model="gpt-4o-mini",
        input_price_per_1k=0.00015,
        output_price_per_1k=0.00060,
    )
    cost = calculate_cost(input_tokens=2000, output_tokens=500, model_config=model)
    # (2 * 0.00015) + (0.5 * 0.00060) = 0.00030 + 0.00030 = 0.00060
    assert cost == pytest.approx(0.0006)


def test_calculate_cost_for_model_key() -> None:
    """Cost lookup by model key resolves from ModelsRegistry."""
    registry = ModelsRegistry(
        models={
            "large": ModelConfig(
                provider_model="gpt-4o",
                input_price_per_1k=0.0025,
                output_price_per_1k=0.01,
            )
        }
    )
    cost = calculate_cost_for_model_key(
        input_tokens=1000,
        output_tokens=1000,
        model_key="large",
        registry=registry,
    )
    assert cost == pytest.approx(0.0125)


def test_calculate_cost_negative_tokens_raises() -> None:
    """Negative token counts raise ValueError."""
    model = ModelConfig(
        provider_model="gpt-4o-mini",
        input_price_per_1k=0.00015,
        output_price_per_1k=0.00060,
    )
    with pytest.raises(ValueError, match="non-negative"):
        calculate_cost(input_tokens=-1, output_tokens=100, model_config=model)

