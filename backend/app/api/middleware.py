"""API middleware for cross-cutting concerns."""
import logging
import time
import uuid
from typing import Callable

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger(__name__)


class RequestIDMiddleware(BaseHTTPMiddleware):
    """Middleware that adds a correlation ID to each request and provides comprehensive tracing."""

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Add correlation ID to request and response with comprehensive tracing.

        Args:
            request: Incoming request
            call_next: Next middleware/handler

        Returns:
            Response with correlation ID

        """
        # Generate or get correlation ID
        correlation_id = request.headers.get(
            "X-Correlation-ID", str(uuid.uuid4())
        )
        request.state.correlation_id = correlation_id

        # Add start time for timing
        start_time = time.time()

        # Add tracing information to request state
        request.state.start_time = start_time
        request.state.method = request.method
        request.state.path = request.url.path
        request.state.client_host = request.client.host if request.client else 'unknown'

        # Process request
        response = await call_next(request)

        # Calculate duration
        duration = time.time() - start_time

        # Add correlation ID to response headers
        response.headers["X-Correlation-ID"] = correlation_id

        # Add timing information to response headers
        response.headers["X-Response-Time"] = f"{duration:.3f}s"

        # Add tracing information to response for debugging (in development)
        if hasattr(request.state, 'trace_info'):
            response.headers["X-Trace-Info"] = str(request.state.trace_info)

        return response


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Middleware that logs all requests and responses with comprehensive tracing."""

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Log request and response details with comprehensive tracing.

        Args:
            request: Incoming request
            call_next: Next middleware/handler

        Returns:
            Response

        """
        # Get correlation ID if available
        correlation_id = getattr(request.state, 'correlation_id', str(uuid.uuid4()))

        # Get additional tracing info
        client_host = getattr(request.state, 'client_host', request.client.host if request.client else 'unknown')
        method = getattr(request.state, 'method', request.method)
        path = getattr(request.state, 'path', request.url.path)

        # Log request with tracing info
        logger.info(
            f"📥 {method} {path} [CID: {correlation_id}] - "
            f"Client: {client_host}",
            extra={
                "correlation_id": correlation_id,
                "method": method,
                "path": path,
                "client_host": client_host,
                "timestamp": time.time()
            }
        )

        # Process request
        response = await call_next(request)

        # Calculate duration if available
        start_time = getattr(request.state, 'start_time', None)
        duration = None
        if start_time:
            duration = time.time() - start_time

        # Log response with tracing info
        logger.info(
            f"📤 {method} {path} [CID: {correlation_id}] - Status: {response.status_code}"
            + (f" - Duration: {duration:.3f}s" if duration else ""),
            extra={
                "correlation_id": correlation_id,
                "method": method,
                "path": path,
                "status_code": response.status_code,
                "duration": duration,
                "timestamp": time.time()
            }
        )

        return response


class CORSMiddlewareConfig:
    """CORS middleware configuration."""

    @staticmethod
    def get_cors_config() -> dict:
        """Get CORS configuration.

        Returns:
            CORS config dict

        """
        return {
            "allow_origins": [
                "http://localhost:3000",
                "http://localhost:8000",
                "https://physical-ai.io",
                "*",  # For development, restrict in production
            ],
            "allow_credentials": True,
            "allow_methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            "allow_headers": ["*"],
            "expose_headers": ["X-Correlation-ID"],
        }
