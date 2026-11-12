"""FastAPI dependency injection providers."""

from fastapi import Request

from src.core.settings import AppSettings, get_settings
from src.logging.logger import RequestLogger


def get_app_settings() -> AppSettings:
    """Return cached application settings."""
    return get_settings()


def get_request_logger(request: Request) -> RequestLogger:
    """Return the shared RequestLogger created at app startup."""
    return request.app.state.request_logger

