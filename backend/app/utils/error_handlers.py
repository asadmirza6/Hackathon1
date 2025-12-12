"""Global error handlers for FastAPI exceptions."""
import logging
from typing import Callable

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse

from app.utils.exceptions import (
    ChatbotException,
    QdrantUnavailableError,
    GeminiAPIError,
    DatabaseError,
    ValidationError,
    RateLimitError,
)
from app.models.schemas import ErrorResponse

logger = logging.getLogger(__name__)


def register_exception_handlers(app: FastAPI) -> None:
    """Register all exception handlers with FastAPI app.

    Args:
        app: FastAPI application instance

    """

    @app.exception_handler(QdrantUnavailableError)
    async def qdrant_exception_handler(
        request: Request, exc: QdrantUnavailableError
    ) -> JSONResponse:
        """Handle Qdrant errors."""
        correlation_id = getattr(request.state, "correlation_id", "unknown")
        path = getattr(request.state, "path", request.url.path)
        method = getattr(request.state, "method", request.method)

        logger.error(
            f"🔴 Qdrant error: {exc.message}",
            extra={
                "correlation_id": correlation_id,
                "path": path,
                "method": method,
                "error_type": "QdrantUnavailableError",
                "timestamp": __import__('time').time()
            }
        )
        return JSONResponse(
            status_code=exc.status_code,
            content=ErrorResponse(
                error="QdrantUnavailableError",
                message=exc.message,
                status_code=exc.status_code,
                correlation_id=correlation_id,
            ).model_dump(),
        )

    @app.exception_handler(GeminiAPIError)
    async def gemini_exception_handler(
        request: Request, exc: GeminiAPIError
    ) -> JSONResponse:
        """Handle Gemini API errors."""
        correlation_id = getattr(request.state, "correlation_id", "unknown")
        path = getattr(request.state, "path", request.url.path)
        method = getattr(request.state, "method", request.method)

        logger.error(
            f"🔴 Gemini error: {exc.message}",
            extra={
                "correlation_id": correlation_id,
                "path": path,
                "method": method,
                "error_type": "GeminiAPIError",
                "timestamp": __import__('time').time()
            }
        )
        return JSONResponse(
            status_code=exc.status_code,
            content=ErrorResponse(
                error="GeminiAPIError",
                message=exc.message,
                status_code=exc.status_code,
                correlation_id=correlation_id,
            ).model_dump(),
        )

    @app.exception_handler(DatabaseError)
    async def database_exception_handler(
        request: Request, exc: DatabaseError
    ) -> JSONResponse:
        """Handle database errors."""
        correlation_id = getattr(request.state, "correlation_id", "unknown")
        path = getattr(request.state, "path", request.url.path)
        method = getattr(request.state, "method", request.method)

        logger.error(
            f"🔴 Database error: {exc.message}",
            extra={
                "correlation_id": correlation_id,
                "path": path,
                "method": method,
                "error_type": "DatabaseError",
                "timestamp": __import__('time').time()
            }
        )
        return JSONResponse(
            status_code=exc.status_code,
            content=ErrorResponse(
                error="DatabaseError",
                message="An error occurred. Please try again.",
                status_code=exc.status_code,
                correlation_id=correlation_id,
            ).model_dump(),
        )

    @app.exception_handler(ValidationError)
    async def validation_exception_handler(
        request: Request, exc: ValidationError
    ) -> JSONResponse:
        """Handle validation errors."""
        correlation_id = getattr(request.state, "correlation_id", "unknown")
        path = getattr(request.state, "path", request.url.path)
        method = getattr(request.state, "method", request.method)

        logger.warning(
            f"⚠️  Validation error: {exc.message}",
            extra={
                "correlation_id": correlation_id,
                "path": path,
                "method": method,
                "error_type": "ValidationError",
                "timestamp": __import__('time').time()
            }
        )
        return JSONResponse(
            status_code=exc.status_code,
            content=ErrorResponse(
                error="ValidationError",
                message=exc.message,
                status_code=exc.status_code,
                correlation_id=correlation_id,
            ).model_dump(),
        )

    @app.exception_handler(RateLimitError)
    async def rate_limit_exception_handler(
        request: Request, exc: RateLimitError
    ) -> JSONResponse:
        """Handle rate limit errors."""
        correlation_id = getattr(request.state, "correlation_id", "unknown")
        path = getattr(request.state, "path", request.url.path)
        method = getattr(request.state, "method", request.method)

        logger.warning(
            f"⚠️  Rate limit exceeded",
            extra={
                "correlation_id": correlation_id,
                "path": path,
                "method": method,
                "error_type": "RateLimitError",
                "timestamp": __import__('time').time()
            }
        )
        response = JSONResponse(
            status_code=exc.status_code,
            content=ErrorResponse(
                error="RateLimitError",
                message=exc.message,
                status_code=exc.status_code,
                correlation_id=correlation_id,
            ).model_dump(),
        )
        if exc.retry_after:
            response.headers["Retry-After"] = str(exc.retry_after)
        return response

    @app.exception_handler(ChatbotException)
    async def chatbot_exception_handler(
        request: Request, exc: ChatbotException
    ) -> JSONResponse:
        """Handle generic chatbot exceptions."""
        correlation_id = getattr(request.state, "correlation_id", "unknown")
        path = getattr(request.state, "path", request.url.path)
        method = getattr(request.state, "method", request.method)

        logger.error(
            f"🔴 Chatbot error: {exc.message}",
            extra={
                "correlation_id": correlation_id,
                "path": path,
                "method": method,
                "error_type": exc.__class__.__name__,
                "timestamp": __import__('time').time()
            }
        )
        return JSONResponse(
            status_code=exc.status_code,
            content=ErrorResponse(
                error=exc.__class__.__name__,
                message=exc.message,
                status_code=exc.status_code,
                correlation_id=correlation_id,
            ).model_dump(),
        )

    @app.exception_handler(Exception)
    async def general_exception_handler(
        request: Request, exc: Exception
    ) -> JSONResponse:
        """Handle unexpected exceptions."""
        correlation_id = getattr(request.state, "correlation_id", "unknown")
        path = getattr(request.state, "path", request.url.path)
        method = getattr(request.state, "method", request.method)

        logger.error(
            f"🔴 Unexpected error: {str(exc)}",
            extra={
                "correlation_id": correlation_id,
                "path": path,
                "method": method,
                "error_type": "InternalServerError",
                "timestamp": __import__('time').time()
            },
            exc_info=True
        )
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=ErrorResponse(
                error="InternalServerError",
                message="An unexpected error occurred. Please try again.",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                correlation_id=correlation_id,
            ).model_dump(),
        )
