"""Unit tests for validation functions."""
import pytest
from app.utils.validators import validate_query_input, validate_query_length, validate_session_id, validate_timestamp


def test_validate_query_length_valid():
    """Test valid query length."""
    # Valid length (within bounds)
    question = "What is ZMP in bipedal walking?"  # Length: 34
    result = validate_query_length(question, min_length=5, max_length=2000)
    assert result is True


def test_validate_query_length_too_short():
    """Test query that is too short."""
    with pytest.raises(ValueError, match="Question must be at least 5 characters long"):
        validate_query_length("Hi", min_length=5, max_length=2000)


def test_validate_query_length_too_long():
    """Test query that is too long."""
    long_question = "a" * 2001  # 2001 characters
    with pytest.raises(ValueError, match="Question must be no more than 2000 characters long"):
        validate_query_length(long_question, min_length=5, max_length=2000)


def test_validate_query_length_boundary_min():
    """Test query at minimum length boundary."""
    question = "a" * 5  # Exactly 5 characters
    result = validate_query_length(question, min_length=5, max_length=2000)
    assert result is True


def test_validate_query_length_boundary_max():
    """Test query at maximum length boundary."""
    question = "a" * 2000  # Exactly 2000 characters
    result = validate_query_length(question, min_length=5, max_length=2000)
    assert result is True


def test_validate_session_id_valid():
    """Test valid session ID."""
    session_id = "user-session-123"
    result = validate_session_id(session_id)
    assert result is True


def test_validate_session_id_invalid():
    """Test invalid session ID."""
    invalid_session_id = "invalid session id!"
    with pytest.raises(ValueError, match="Invalid session ID format"):
        validate_session_id(invalid_session_id)


def test_validate_session_id_empty():
    """Test empty session ID."""
    with pytest.raises(ValueError, match="Session ID cannot be empty"):
        validate_session_id("")


def test_validate_session_id_none():
    """Test None session ID."""
    with pytest.raises(ValueError, match="Session ID cannot be empty"):
        validate_session_id(None)


def test_validate_timestamp_valid():
    """Test valid timestamp."""
    timestamp = "2023-12-01T10:30:00Z"
    result = validate_timestamp(timestamp)
    assert result is True


def test_validate_timestamp_invalid():
    """Test invalid timestamp."""
    invalid_timestamp = "not-a-timestamp"
    with pytest.raises(ValueError, match="Invalid timestamp format"):
        validate_timestamp(invalid_timestamp)


def test_validate_timestamp_empty():
    """Test empty timestamp."""
    with pytest.raises(ValueError, match="Timestamp cannot be empty"):
        validate_timestamp("")


def test_validate_timestamp_none():
    """Test None timestamp."""
    with pytest.raises(ValueError, match="Timestamp cannot be empty"):
        validate_timestamp(None)


def test_validate_query_input_valid():
    """Test valid query input."""
    question = "What is ZMP?"
    session_id = "session-123"
    result = validate_query_input(question, session_id)
    assert result is True


def test_validate_query_input_invalid_question():
    """Test query input with invalid question."""
    with pytest.raises(ValueError, match="Question must be at least 5 characters long"):
        validate_query_input("Hi", "session-123")


def test_validate_query_input_invalid_session():
    """Test query input with invalid session ID."""
    with pytest.raises(ValueError, match="Invalid session ID format"):
        validate_query_input("What is ZMP?", "invalid session id!")


def test_validate_query_input_with_selected_context():
    """Test query input with selected context."""
    question = "What is ZMP?"
    session_id = "session-123"
    selected_context = "Zero Moment Point is..."
    result = validate_query_input(question, session_id, selected_context)
    assert result is True


def test_validate_query_input_selected_context_too_long():
    """Test query input with selected context that is too long."""
    question = "What is ZMP?"
    session_id = "session-123"
    selected_context = "a" * 5001  # Too long
    with pytest.raises(ValueError, match="Selected context must be no more than 5000 characters long"):
        validate_query_input(question, session_id, selected_context)


def test_validate_query_input_selected_context_valid_length():
    """Test query input with selected context at max valid length."""
    question = "What is ZMP?"
    session_id = "session-123"
    selected_context = "a" * 5000  # Exactly max length
    result = validate_query_input(question, session_id, selected_context)
    assert result is True


def test_validate_query_input_selected_context_none():
    """Test query input with None selected context."""
    question = "What is ZMP?"
    session_id = "session-123"
    result = validate_query_input(question, session_id, selected_context=None)
    assert result is True


def test_validate_query_input_selected_context_empty():
    """Test query input with empty selected context."""
    question = "What is ZMP?"
    session_id = "session-123"
    result = validate_query_input(question, session_id, selected_context="")
    assert result is True


def test_validate_query_input_none_values():
    """Test query input with None values."""
    with pytest.raises(ValueError, match="Question cannot be empty"):
        validate_query_input(None, "session-123")

    with pytest.raises(ValueError, match="Session ID cannot be empty"):
        validate_query_input("What is ZMP?", None)


def test_validate_query_length_empty():
    """Test empty query length validation."""
    with pytest.raises(ValueError, match="Question cannot be empty"):
        validate_query_length("", min_length=5, max_length=2000)


def test_validate_query_length_none():
    """Test None query length validation."""
    with pytest.raises(ValueError, match="Question cannot be empty"):
        validate_query_length(None, min_length=5, max_length=2000)