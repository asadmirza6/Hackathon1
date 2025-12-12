"""Custom exceptions for the RAG Chatbot Backend."""
from typing import Optional

from fastapi import HTTPException, status


class ChatbotException(Exception):
    """Base exception for chatbot errors."""

    def __init__(self, message: str, status_code: int = 500):
        """Initialize exception.

        Args:
            message: Error message
            status_code: HTTP status code

        """
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)


class QdrantUnavailableError(ChatbotException):
    """Raised when Qdrant vector database is unavailable."""

    def __init__(self, message: str = "Vector search temporarily unavailable"):
        """Initialize QdrantUnavailableError."""
        super().__init__(message, status.HTTP_503_SERVICE_UNAVAILABLE)

    def to_http_exception(self) -> HTTPException:
        """Convert to FastAPI HTTPException."""
        return HTTPException(
            status_code=self.status_code,
            detail=self.message,
        )


class GeminiAPIError(ChatbotException):
    """Raised when Gemini API call fails."""

    def __init__(self, message: str = "Unable to generate response"):
        """Initialize GeminiAPIError."""
        super().__init__(message, status.HTTP_502_BAD_GATEWAY)

    def to_http_exception(self) -> HTTPException:
        """Convert to FastAPI HTTPException."""
        return HTTPException(
            status_code=self.status_code,
            detail=self.message,
        )


class DatabaseError(ChatbotException):
    """Raised when database operation fails."""

    def __init__(self, message: str = "Database error occurred"):
        """Initialize DatabaseError."""
        super().__init__(message, status.HTTP_500_INTERNAL_SERVER_ERROR)

    def to_http_exception(self) -> HTTPException:
        """Convert to FastAPI HTTPException."""
        return HTTPException(
            status_code=self.status_code,
            detail=self.message,
        )


class ValidationError(ChatbotException):
    """Raised when input validation fails."""

    def __init__(self, message: str = "Invalid input"):
        """Initialize ValidationError."""
        super().__init__(message, status.HTTP_400_BAD_REQUEST)

    def to_http_exception(self) -> HTTPException:
        """Convert to FastAPI HTTPException."""
        return HTTPException(
            status_code=self.status_code,
            detail=self.message,
        )


class RateLimitError(ChatbotException):
    """Raised when rate limit is exceeded."""

    def __init__(
        self,
        message: str = "Rate limit exceeded",
        retry_after: Optional[int] = None,
    ):
        """Initialize RateLimitError.

        Args:
            message: Error message
            retry_after: Seconds to retry after

        """
        super().__init__(message, status.HTTP_429_TOO_MANY_REQUESTS)
        self.retry_after = retry_after

    def to_http_exception(self) -> HTTPException:
        """Convert to FastAPI HTTPException."""
        headers = {}
        if self.retry_after:
            headers["Retry-After"] = str(self.retry_after)

        return HTTPException(
            status_code=self.status_code,
            detail=self.message,
            headers=headers,
        )


def exception_to_http_response(exc: ChatbotException) -> dict:
    """Convert ChatbotException to HTTP response dict."""
    return {
        "error": exc.__class__.__name__,
        "message": exc.message,
        "status_code": exc.status_code,
    }
