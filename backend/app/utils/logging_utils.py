"""Logging utilities for request/response tracking and timing."""
import logging
import time
from functools import wraps
from typing import Callable, Any
from contextlib import contextmanager

logger = logging.getLogger(__name__)


@contextmanager
def log_operation(operation_name: str, **context):
    """Context manager for logging operations with timing.

    Args:
        operation_name: Name of the operation
        **context: Additional context to include in logs

    Usage:
        with log_operation("vector_search", query_id="123", chunks=5):
            # Do operation
            pass

    """
    start_time = time.time()
    logger.info(f"⏱️  Starting {operation_name}", extra={"operation": operation_name, **context})

    try:
        yield
        duration = time.time() - start_time
        logger.info(
            f"✅ Completed {operation_name} ({duration*1000:.1f}ms)",
            extra={"operation": operation_name, "duration_ms": duration * 1000, **context},
        )
    except Exception as e:
        duration = time.time() - start_time
        logger.error(
            f"❌ Failed {operation_name} ({duration*1000:.1f}ms): {e}",
            extra={"operation": operation_name, "duration_ms": duration * 1000, "error": str(e), **context},
            exc_info=True,
        )
        raise


def measure_latency(operation_name: str) -> Callable:
    """Decorator to measure and log operation latency.

    Args:
        operation_name: Name of the operation

    Usage:
        @measure_latency("gemini_api_call")
        async def generate_response(...):
            pass

    """

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def async_wrapper(*args, **kwargs) -> Any:
            start_time = time.time()
            try:
                logger.debug(f"⏱️  Starting {operation_name}")
                result = await func(*args, **kwargs)
                duration = time.time() - start_time
                logger.info(
                    f"✅ {operation_name} completed ({duration*1000:.1f}ms)"
                )
                return result
            except Exception as e:
                duration = time.time() - start_time
                logger.error(
                    f"❌ {operation_name} failed ({duration*1000:.1f}ms): {e}"
                )
                raise

        @wraps(func)
        def sync_wrapper(*args, **kwargs) -> Any:
            start_time = time.time()
            try:
                logger.debug(f"⏱️  Starting {operation_name}")
                result = func(*args, **kwargs)
                duration = time.time() - start_time
                logger.info(
                    f"✅ {operation_name} completed ({duration*1000:.1f}ms)"
                )
                return result
            except Exception as e:
                duration = time.time() - start_time
                logger.error(
                    f"❌ {operation_name} failed ({duration*1000:.1f}ms): {e}"
                )
                raise

        # Return async or sync wrapper based on function type
        if hasattr(func, "__await__"):
            return async_wrapper
        return sync_wrapper

    return decorator


def log_request_details(request_id: str, query: str, session_id: str) -> dict:
    """Log request details and return context for subsequent logs.

    Args:
        request_id: Unique request ID
        query: User query
        session_id: Session ID

    Returns:
        Context dict for logging

    """
    context = {
        "request_id": request_id,
        "session_id": session_id,
        "query_length": len(query),
    }
    logger.info(
        f"📥 Request {request_id} from session {session_id} (query: {len(query)} chars)",
        extra=context,
    )
    return context


def log_response_details(
    request_id: str,
    response_length: int,
    confidence_score: float,
    duration_ms: float,
) -> None:
    """Log response details.

    Args:
        request_id: Unique request ID
        response_length: Length of response text
        confidence_score: Confidence score (0-1)
        duration_ms: Total duration in milliseconds

    """
    context = {
        "request_id": request_id,
        "response_length": response_length,
        "confidence_score": confidence_score,
        "duration_ms": duration_ms,
    }
    logger.info(
        f"📤 Response {request_id} ({response_length} chars, confidence: {confidence_score:.2f}, "
        f"time: {duration_ms:.1f}ms)",
        extra=context,
    )


def log_error_context(
    request_id: str,
    error_type: str,
    error_message: str,
    duration_ms: float,
) -> None:
    """Log error context for debugging.

    Args:
        request_id: Unique request ID
        error_type: Type of error
        error_message: Error message
        duration_ms: Duration before error

    """
    context = {
        "request_id": request_id,
        "error_type": error_type,
        "duration_ms": duration_ms,
    }
    logger.error(
        f"🔴 Error in {request_id}: {error_type} - {error_message} ({duration_ms:.1f}ms)",
        extra=context,
        exc_info=True,
    )
