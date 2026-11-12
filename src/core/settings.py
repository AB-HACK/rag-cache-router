"""Configuration loader for YAML settings, model prices, and environment variables."""

import os
from functools import lru_cache
from pathlib import Path
from typing import Any

from pydantic import BaseModel, Field


class CorpusSettings(BaseModel):
    """Corpus ingestion and retrieval settings."""

    corpus_version: int = 1
    collection_name: str = "rag_corpus"
    chunk_size: int = 512
    chunk_overlap: int = 64
    top_k: int = 5


class EmbeddingSettings(BaseModel):
    """Embedding model configuration shared across corpus, queries, and cache."""

    model_name: str = "BAAI/bge-small-en-v1.5"


class CacheSettings(BaseModel):
    """Semantic cache configuration."""

    enabled: bool = False
    collection_name: str = "semantic_cache"
    similarity_threshold: float = 0.92
    ttl_seconds: int = 86400


class RouterSettings(BaseModel):
    """Cost-aware router and escalation configuration."""

    enabled: bool = False
    min_retrieval_score: float = 0.50
    max_simple_query_words: int = 15


class ModelConfig(BaseModel):
    """Model provider identifier, pricing, and generation parameters."""

    provider_model: str
    input_price_per_1k: float
    output_price_per_1k: float
    temperature: float = 0.0
    max_tokens: int = 512


class ModelsRegistry(BaseModel):
    """Registry of available models and their prices."""

    default_small_model: str = "small"
    default_large_model: str = "large"
    models: dict[str, ModelConfig] = Field(default_factory=dict)


class AppSettings(BaseModel):
    """Top-level application settings combining YAML configs and environment variables."""

    app_env: str = Field(default_factory=lambda: os.getenv("APP_ENV", "development"))
    log_level: str = Field(default_factory=lambda: os.getenv("LOG_LEVEL", "INFO"))
    qdrant_url: str = Field(default_factory=lambda: os.getenv("QDRANT_URL", "http://localhost:6333"))
    qdrant_api_key: str | None = Field(default_factory=lambda: os.getenv("QDRANT_API_KEY") or None)
    sqlite_db_path: str = Field(
        default_factory=lambda: os.getenv("SQLITE_DB_PATH", "data/logs/requests.db")
    )
    allowed_origins: list[str] = Field(
        default_factory=lambda: [
            origin.strip()
            for origin in os.getenv("ALLOWED_ORIGINS", "http://localhost:8501").split(",")
            if origin.strip()
        ]
    )

    corpus: CorpusSettings = Field(default_factory=CorpusSettings)
    embedding: EmbeddingSettings = Field(default_factory=EmbeddingSettings)
    cache: CacheSettings = Field(default_factory=CacheSettings)
    router: RouterSettings = Field(default_factory=RouterSettings)
    models_registry: ModelsRegistry = Field(default_factory=ModelsRegistry)


def _load_yaml(path: Path) -> dict[str, Any]:
    """Load a YAML file if it exists, returning an empty dict otherwise."""
    if not path.exists():
        return {}
    import yaml  # Imported lazily so unit tests without PyYAML can still use defaults

    with path.open("r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    return data if isinstance(data, dict) else {}


@lru_cache(maxsize=1)
def get_settings(config_dir: Path | None = None) -> AppSettings:
    """Load and cache application settings from config/settings.yaml and config/models.yaml."""
    base_dir = config_dir or Path("config")
    settings_data = _load_yaml(base_dir / "settings.yaml")
    models_data = _load_yaml(base_dir / "models.yaml")

    return AppSettings(
        corpus=CorpusSettings(**settings_data.get("corpus", {})),
        embedding=EmbeddingSettings(**settings_data.get("embedding", {})),
        cache=CacheSettings(**settings_data.get("cache", {})),
        router=RouterSettings(**settings_data.get("router", {})),
        models_registry=ModelsRegistry(**models_data) if models_data else ModelsRegistry(),
    )

