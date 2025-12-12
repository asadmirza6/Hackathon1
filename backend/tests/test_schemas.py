"""Unit tests for Pydantic request/response schemas."""
import pytest
from datetime import datetime
from pydantic import ValidationError

from app.models.schemas import (
    ChatQueryRequest,
    ChatResponseSchema,
    SourceReference,
    HealthCheckResponse,
    QueryLogEntry,
    PaginatedLogsResponse,
    AnalyticsResponse,
    PerformanceMetrics,
    TopQuestion,
    TopQuestionsResponse,
    ContentCoverageResponse,
)


def test_chat_query_request_valid():
    """Test valid ChatQueryRequest."""
    request = ChatQueryRequest(
        question="What is ZMP in bipedal walking?",
        session_id="session-123",
        selected_context="Zero Moment Point is..."
    )

    assert request.question == "What is ZMP in bipedal walking?"
    assert request.session_id == "session-123"
    assert request.selected_context == "Zero Moment Point is..."


def test_chat_query_request_required_fields():
    """Test ChatQueryRequest with required fields only."""
    request = ChatQueryRequest(
        question="What is ZMP?",
        session_id="session-123"
    )

    assert request.question == "What is ZMP?"
    assert request.session_id == "session-123"
    assert request.selected_context is None


def test_chat_query_request_missing_question():
    """Test ChatQueryRequest with missing question."""
    with pytest.raises(ValidationError):
        ChatQueryRequest(session_id="session-123")


def test_chat_query_request_missing_session_id():
    """Test ChatQueryRequest with missing session_id."""
    with pytest.raises(ValidationError):
        ChatQueryRequest(question="What is ZMP?")


def test_chat_query_request_empty_question():
    """Test ChatQueryRequest with empty question."""
    with pytest.raises(ValidationError):
        ChatQueryRequest(question="", session_id="session-123")


def test_chat_query_request_empty_session_id():
    """Test ChatQueryRequest with empty session_id."""
    with pytest.raises(ValidationError):
        ChatQueryRequest(question="What is ZMP?", session_id="")


def test_chat_query_request_selected_context_too_long():
    """Test ChatQueryRequest with selected_context that's too long."""
    long_context = "a" * 5001  # Too long

    with pytest.raises(ValidationError):
        ChatQueryRequest(
            question="What is ZMP?",
            session_id="session-123",
            selected_context=long_context
        )


def test_chat_query_request_valid_selected_context_length():
    """Test ChatQueryRequest with valid selected_context length."""
    valid_context = "a" * 5000  # Exactly max length

    request = ChatQueryRequest(
        question="What is ZMP?",
        session_id="session-123",
        selected_context=valid_context
    )

    assert request.selected_context == valid_context


def test_chat_response_schema_valid():
    """Test valid ChatResponseSchema."""
    response = ChatResponseSchema(
        response_text="Zero Moment Point (ZMP) is...",
        source_references=[
            {"chapter": 3, "lesson": 2, "section": "Walking Pattern Generation"}
        ],
        confidence_score=0.92,
        timestamp=datetime.utcnow().isoformat()
    )

    assert response.response_text == "Zero Moment Point (ZMP) is..."
    assert len(response.source_references) == 1
    assert response.confidence_score == 0.92


def test_chat_response_schema_missing_fields():
    """Test ChatResponseSchema with required fields only."""
    response = ChatResponseSchema(
        response_text="Response text",
        source_references=[],
        confidence_score=0.5
    )

    assert response.response_text == "Response text"
    assert response.source_references == []
    assert response.confidence_score == 0.5
    assert response.timestamp is None


def test_chat_response_schema_invalid_confidence():
    """Test ChatResponseSchema with invalid confidence score."""
    with pytest.raises(ValidationError):
        ChatResponseSchema(
            response_text="Response text",
            source_references=[],
            confidence_score=1.5  # Too high
        )

    with pytest.raises(ValidationError):
        ChatResponseSchema(
            response_text="Response text",
            source_references=[],
            confidence_score=-0.5  # Too low
        )


def test_source_reference_valid():
    """Test valid SourceReference."""
    source = SourceReference(
        chapter=3,
        lesson=2,
        section="Walking Pattern Generation"
    )

    assert source.chapter == 3
    assert source.lesson == 2
    assert source.section == "Walking Pattern Generation"


def test_source_reference_invalid_chapter():
    """Test SourceReference with invalid chapter."""
    with pytest.raises(ValidationError):
        SourceReference(
            chapter="invalid",  # Should be int
            lesson=2,
            section="Section"
        )


def test_source_reference_missing_field():
    """Test SourceReference with missing required field."""
    with pytest.raises(ValidationError):
        SourceReference(
            chapter=3,
            lesson=2
            # Missing section
        )


def test_health_check_response_valid():
    """Test valid HealthCheckResponse."""
    health = HealthCheckResponse(
        status="healthy",
        timestamp=datetime.utcnow().isoformat(),
        services={
            "qdrant": "healthy",
            "gemini": "healthy",
            "postgres": "healthy"
        }
    )

    assert health.status == "healthy"
    assert "qdrant" in health.services


def test_query_log_entry_valid():
    """Test valid QueryLogEntry."""
    log_entry = QueryLogEntry(
        id=1,
        question="Test question?",
        response_text="Test response",
        session_id="session-123",
        confidence_score=0.85,
        timestamp=datetime.utcnow().isoformat(),
        source_chapters=[{"chapter": 1, "lesson": 1, "section": "Intro"}],
        query_duration_ms=1200.0
    )

    assert log_entry.id == 1
    assert log_entry.question == "Test question?"
    assert log_entry.confidence_score == 0.85


def test_paginated_logs_response_valid():
    """Test valid PaginatedLogsResponse."""
    paginated = PaginatedLogsResponse(
        items=[
            QueryLogEntry(
                id=1,
                question="Test?",
                response_text="Response",
                session_id="session-123",
                confidence_score=0.8
            )
        ],
        total=1,
        limit=10,
        offset=0
    )

    assert len(paginated.items) == 1
    assert paginated.total == 1
    assert paginated.limit == 10
    assert paginated.offset == 0


def test_analytics_response_valid():
    """Test valid AnalyticsResponse."""
    analytics = AnalyticsResponse(
        query_count=10,
        avg_confidence=0.85,
        avg_response_time_ms=1400.0,
        unique_sessions=5,
        period_days=7
    )

    assert analytics.query_count == 10
    assert analytics.avg_confidence == 0.85
    assert analytics.avg_response_time_ms == 1400.0


def test_performance_metrics_valid():
    """Test valid PerformanceMetrics."""
    metrics = PerformanceMetrics(
        query_count=15,
        period_days=7,
        avg_confidence=0.87,
        min_confidence=0.75,
        max_confidence=0.95,
        avg_response_time_ms=1350.0,
        p95_response_time_ms=2100.0,
        avg_retrieval_time_ms=120.0,
        avg_generation_time_ms=1230.0,
        unique_sessions=8
    )

    assert metrics.query_count == 15
    assert metrics.avg_confidence == 0.87
    assert metrics.p95_response_time_ms == 2100.0


def test_top_question_valid():
    """Test valid TopQuestion."""
    top_q = TopQuestion(
        question="What is ZMP?",
        count=5,
        avg_confidence=0.88
    )

    assert top_q.question == "What is ZMP?"
    assert top_q.count == 5
    assert top_q.avg_confidence == 0.88


def test_top_questions_response_valid():
    """Test valid TopQuestionsResponse."""
    response = TopQuestionsResponse(
        items=[
            TopQuestion(question="What is ZMP?", count=5, avg_confidence=0.88)
        ],
        period_days=7
    )

    assert len(response.items) == 1
    assert response.items[0].question == "What is ZMP?"
    assert response.period_days == 7


def test_content_coverage_response_valid():
    """Test valid ContentCoverageResponse."""
    coverage = ContentCoverageResponse(
        coverage={"chapter_1": {"lesson_1": 10}},
        total_queries=23,
        chapters_queried=1
    )

    assert "chapter_1" in coverage.coverage
    assert coverage.total_queries == 23
    assert coverage.chapters_queried == 1


def test_chat_query_request_question_length_validation():
    """Test ChatQueryRequest question length validation."""
    short_question = "Hi"  # Too short

    with pytest.raises(ValidationError):
        ChatQueryRequest(
            question=short_question,
            session_id="session-123"
        )


def test_chat_response_schema_confidence_range():
    """Test ChatResponseSchema confidence score range."""
    # Test lower bound
    response = ChatResponseSchema(
        response_text="Response",
        source_references=[],
        confidence_score=0.0
    )
    assert response.confidence_score == 0.0

    # Test upper bound
    response = ChatResponseSchema(
        response_text="Response",
        source_references=[],
        confidence_score=1.0
    )
    assert response.confidence_score == 1.0


def test_query_log_entry_optional_fields():
    """Test QueryLogEntry with optional fields."""
    log_entry = QueryLogEntry(
        id=1,
        question="Test?",
        response_text="Response",
        session_id="session-123",
        confidence_score=0.8
        # Other fields are optional
    )

    assert log_entry.id == 1
    assert log_entry.timestamp is None
    assert log_entry.source_chapters is None
    assert log_entry.query_duration_ms is None


def test_paginated_logs_response_required_fields():
    """Test PaginatedLogsResponse with required fields only."""
    paginated = PaginatedLogsResponse(
        items=[],
        total=0,
        limit=10,
        offset=0
    )

    assert paginated.items == []
    assert paginated.total == 0
    assert paginated.limit == 10
    assert paginated.offset == 0