"""Validation functions for chat queries and user input."""
import re
from datetime import datetime
from typing import Optional

from app.core.constants import (
    MIN_QUERY_LENGTH,
    MAX_QUERY_LENGTH,
    SESSION_ID_PATTERN,
    MAX_CONTEXT_LENGTH,
)


class ValidationError(Exception):
    """Custom exception for validation errors."""

    pass


def validate_query_length(query: str) -> None:
    """Validate query length is within acceptable bounds.

    Args:
        query: User question text

    Raises:
        ValidationError: If query length is invalid

    """
    length = len(query.strip())
    if length < MIN_QUERY_LENGTH:
        raise ValidationError(
            f"Query too short. Minimum length is {MIN_QUERY_LENGTH} characters."
        )
    if length > MAX_QUERY_LENGTH:
        raise ValidationError(
            f"Query too long. Maximum length is {MAX_QUERY_LENGTH} characters."
        )


def validate_session_id(session_id: str) -> None:
    """Validate session ID format.

    Args:
        session_id: Session identifier

    Raises:
        ValidationError: If session ID format is invalid

    """
    if not re.match(SESSION_ID_PATTERN, session_id):
        raise ValidationError(
            f"Invalid session ID format. Must match pattern: {SESSION_ID_PATTERN}"
        )


def validate_timestamp(timestamp: str) -> datetime:
    """Validate and parse ISO-8601 timestamp.

    Args:
        timestamp: ISO-8601 formatted timestamp string

    Returns:
        Parsed datetime object

    Raises:
        ValidationError: If timestamp format is invalid

    """
    try:
        return datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
    except (ValueError, AttributeError) as e:
        raise ValidationError(f"Invalid timestamp format: {e}")


def validate_selected_context(context: Optional[str]) -> None:
    """Validate selected context length.

    Args:
        context: Optional selected text from lesson

    Raises:
        ValidationError: If context is too long

    """
    if context and len(context) > MAX_CONTEXT_LENGTH:
        raise ValidationError(
            f"Selected context too long. Maximum length is {MAX_CONTEXT_LENGTH} characters."
        )


def validate_query_input(
    question: str, session_id: str, selected_context: Optional[str] = None
) -> None:
    """Validate complete query input.

    Args:
        question: User question
        session_id: Session identifier
        selected_context: Optional selected text context

    Raises:
        ValidationError: If any validation fails

    """
    validate_query_length(question)
    validate_session_id(session_id)
    validate_selected_context(selected_context)
