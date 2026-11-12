"""FastAPI application factory with startup lifecycle, middleware, and error handling."""

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse

from src.api.routes import router
from src.api.schemas import ErrorResponse
from src.core.settings import get_settings
from src.logging.logger import RequestLogger


class AppError(Exception):
    """Domain exception carrying an HTTP status code and machine-readable error code."""

    def __init__(self, detail: str, code: str, status_code: int = 500) -> None:
        super().__init__(detail)
        self.detail = detail
        self.code = code
        self.status_code = status_code


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """Initialize shared clients (logger, vector store, embedder) once at startup."""
    settings = get_settings()
    request_logger = RequestLogger(settings.sqlite_db_path)
    await request_logger.init_db()
    app.state.request_logger = request_logger
    # TODO (Task 0.3 / 0.4): Initialize shared Qdrant client and Embedder here.
    try:
        yield
    finally:
        await request_logger.close()


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    settings = get_settings()

    app = FastAPI(
        title="RAG Semantic Cache & Cost-Aware Router",
        version="0.1.0",
        lifespan=lifespan,
    )

    app.add_middleware(GZipMiddleware, minimum_size=1000)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.allowed_origins if settings.app_env != "development" else ["*"],
        allow_credentials=False,
        allow_methods=["GET", "POST"],
        allow_headers=["*"],
    )

    @app.exception_handler(AppError)
    async def app_error_handler(_request: Request, exc: AppError) -> JSONResponse:
        body = ErrorResponse(detail=exc.detail, code=exc.code)
        return JSONResponse(status_code=exc.status_code, content=body.model_dump())

    @app.exception_handler(HTTPException)
    async def http_exception_handler(_request: Request, exc: HTTPException) -> JSONResponse:
        body = ErrorResponse(detail=str(exc.detail), code=f"HTTP_{exc.status_code}")
        return JSONResponse(status_code=exc.status_code, content=body.model_dump())

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(
        _request: Request, exc: RequestValidationError
    ) -> JSONResponse:
        body = ErrorResponse(detail=str(exc.errors()), code="VALIDATION_ERROR")
        return JSONResponse(status_code=422, content=body.model_dump())

    app.include_router(router)
    return app


app = create_app()

