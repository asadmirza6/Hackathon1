"""Unit tests for PostgresService in User Story 3 - Query Logging and Analytics."""
import asyncio
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, MagicMock, patch
import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.chat_query import ChatQuery
from app.services.postgres_service import PostgresService, retry_on_connection_error


@pytest.mark.asyncio
async def test_save_query_success(mock_postgres_session):
    """Test successful query saving to database."""
    postgres_service = PostgresService(mock_postgres_session)

    # Test data
    question = "What is ZMP in bipedal walking?"
    response_text = "Zero Moment Point (ZMP) is the point..."
    session_id = "test-session-123"
    source_chapters = [{"chapter": 3, "lesson": 2, "section": "Walking Pattern Generation"}]
    confidence_score = 0.92
    selected_context = "Zero Moment Point is..."
    query_duration_ms = 1500.0
    retrieval_duration_ms = 100.0
    generation_duration_ms = 1400.0

    # Mock the chat query object that will be returned
    mock_chat_query = MagicMock(spec=ChatQuery)
    mock_chat_query.id = 1
    mock_chat_query.question = question
    mock_chat_query.response_text = response_text
    mock_chat_query.session_id = session_id
    mock_chat_query.source_chapters = source_chapters
    mock_chat_query.confidence_score = confidence_score
    mock_chat_query.selected_context = selected_context
    mock_chat_query.timestamp = datetime.utcnow()
    mock_chat_query.query_duration_ms = query_duration_ms
    mock_chat_query.retrieval_duration_ms = retrieval_duration_ms
    mock_chat_query.generation_duration_ms = generation_duration_ms

    # Mock session operations
    mock_postgres_session.add = MagicMock()
    mock_postgres_session.commit = AsyncMock()
    mock_postgres_session.refresh = AsyncMock(side_effect=lambda obj: setattr(obj, 'id', 1))

    # Call the method
    result = await postgres_service.save_query(
        question=question,
        response_text=response_text,
        session_id=session_id,
        source_chapters=source_chapters,
        confidence_score=confidence_score,
        selected_context=selected_context,
        query_duration_ms=query_duration_ms,
        retrieval_duration_ms=retrieval_duration_ms,
        generation_duration_ms=generation_duration_ms,
    )

    # Assertions
    assert mock_postgres_session.add.called
    assert mock_postgres_session.commit.called
    assert mock_postgres_session.refresh.called
    assert result is not None


@pytest.mark.asyncio
async def test_get_query_logs_success(mock_postgres_session):
    """Test successful retrieval of query logs with pagination."""
    postgres_service = PostgresService(mock_postgres_session)

    # Mock data
    mock_query1 = MagicMock(spec=ChatQuery)
    mock_query1.id = 1
    mock_query1.question = "Test question 1"
    mock_query1.response_text = "Test response 1"
    mock_query1.session_id = "session-1"
    mock_query1.confidence_score = 0.85
    mock_query1.timestamp = datetime.utcnow()
    mock_query1.source_chapters = [{"chapter": 1, "lesson": 1, "section": "Intro"}]
    mock_query1.query_duration_ms = 1200.0

    mock_query2 = MagicMock(spec=ChatQuery)
    mock_query2.id = 2
    mock_query2.question = "Test question 2"
    mock_query2.response_text = "Test response 2"
    mock_query2.session_id = "session-2"
    mock_query2.confidence_score = 0.92
    mock_query2.timestamp = datetime.utcnow()
    mock_query2.source_chapters = [{"chapter": 2, "lesson": 1, "section": "Advanced"}]
    mock_query2.query_duration_ms = 1500.0

    mock_queries = [mock_query1, mock_query2]

    # Mock session execution
    mock_execute_result = MagicMock()
    mock_execute_result.fetchall.return_value = mock_queries
    mock_execute_result_2 = MagicMock()
    mock_execute_result_2.scalars.return_value.all.return_value = mock_queries

    with patch.object(mock_postgres_session, 'execute') as mock_execute:
        mock_execute.side_effect = [mock_execute_result, mock_execute_result_2]

        # Call the method
        queries, total = await postgres_service.get_query_logs(
            session_id=None,
            limit=100,
            offset=0,
            days_back=None
        )

        # Assertions
        assert len(queries) == 2
        assert total == 2
        assert queries[0].question == "Test question 1"


@pytest.mark.asyncio
async def test_get_query_logs_with_filters(mock_postgres_session):
    """Test query log retrieval with filters."""
    postgres_service = PostgresService(mock_postgres_session)

    # Mock data
    mock_query = MagicMock(spec=ChatQuery)
    mock_query.id = 1
    mock_query.question = "Filtered question"
    mock_query.response_text = "Filtered response"
    mock_query.session_id = "filtered-session"
    mock_query.confidence_score = 0.88
    mock_query.timestamp = datetime.utcnow() - timedelta(days=1)
    mock_query.source_chapters = [{"chapter": 1, "lesson": 1, "section": "Intro"}]
    mock_query.query_duration_ms = 1300.0

    mock_queries = [mock_query]

    # Mock session execution
    mock_execute_result = MagicMock()
    mock_execute_result.fetchall.return_value = mock_queries
    mock_execute_result_2 = MagicMock()
    mock_execute_result_2.scalars.return_value.all.return_value = mock_queries

    with patch.object(mock_postgres_session, 'execute') as mock_execute:
        mock_execute.side_effect = [mock_execute_result, mock_execute_result_2]

        # Call the method with filters
        queries, total = await postgres_service.get_query_logs(
            session_id="filtered-session",
            limit=50,
            offset=0,
            days_back=7
        )

        # Assertions
        assert len(queries) == 1
        assert total == 1
        assert queries[0].session_id == "filtered-session"


@pytest.mark.asyncio
async def test_get_analytics_success(mock_postgres_session):
    """Test successful retrieval of analytics."""
    postgres_service = PostgresService(mock_postgres_session)

    # Mock data
    mock_query1 = MagicMock(spec=ChatQuery)
    mock_query1.confidence_score = 0.85
    mock_query1.query_duration_ms = 1200.0
    mock_query1.session_id = "session-1"
    mock_query1.timestamp = datetime.utcnow()

    mock_query2 = MagicMock(spec=ChatQuery)
    mock_query2.confidence_score = 0.92
    mock_query2.query_duration_ms = 1500.0
    mock_query2.session_id = "session-2"
    mock_query2.timestamp = datetime.utcnow()

    mock_queries = [mock_query1, mock_query2]

    # Mock session execution
    mock_execute_result = MagicMock()
    mock_execute_result.scalars.return_value.all.return_value = mock_queries

    with patch.object(mock_postgres_session, 'execute') as mock_execute:
        mock_execute.return_value = mock_execute_result

        # Call the method
        analytics = await postgres_service.get_analytics(days_back=7)

        # Assertions
        assert analytics["query_count"] == 2
        assert analytics["avg_confidence"] == 0.885  # (0.85 + 0.92) / 2
        assert analytics["unique_sessions"] == 2


@pytest.mark.asyncio
async def test_log_query_async_success(mock_postgres_session):
    """Test successful async logging of query."""
    postgres_service = PostgresService(mock_postgres_session)

    # Test data
    question = "Async test question"
    response_text = "Async test response"
    session_id = "async-session-123"
    confidence_score = 0.88

    # Mock session operations
    mock_postgres_session.add = MagicMock()
    mock_postgres_session.commit = AsyncMock()

    # Call the method
    await postgres_service.log_query_async(
        question=question,
        response_text=response_text,
        session_id=session_id,
        confidence_score=confidence_score
    )

    # Assertions
    assert mock_postgres_session.add.called
    assert mock_postgres_session.commit.called


@pytest.mark.asyncio
async def test_retry_decorator_success():
    """Test the retry decorator functionality."""
    attempt_count = 0

    @retry_on_connection_error(max_retries=2, initial_delay=0.01, backoff_factor=1)
    async def test_function():
        nonlocal attempt_count
        attempt_count += 1

        if attempt_count < 2:
            from sqlalchemy.exc import SQLAlchemyError
            raise SQLAlchemyError("Connection failed")

        return "success"

    # This should succeed on the second attempt
    result = await test_function()
    assert result == "success"
    assert attempt_count == 2


@pytest.mark.asyncio
async def test_retry_decorator_max_attempts():
    """Test the retry decorator reaches max attempts."""
    attempt_count = 0

    @retry_on_connection_error(max_retries=2, initial_delay=0.001, backoff_factor=1)
    async def test_function():
        nonlocal attempt_count
        attempt_count += 1
        from sqlalchemy.exc import SQLAlchemyError
        raise SQLAlchemyError("Always fails")

    # This should fail after max retries
    with pytest.raises(Exception):
        await test_function()

    assert attempt_count == 3  # Original attempt + 2 retries


def test_postgres_service_initialization(mock_postgres_session):
    """Test PostgresService initialization."""
    postgres_service = PostgresService(mock_postgres_session)

    assert postgres_service.session == mock_postgres_session


@pytest.mark.asyncio
async def test_close_session(mock_postgres_session):
    """Test closing the database session."""
    postgres_service = PostgresService(mock_postgres_session)

    # Mock the close method
    mock_postgres_session.close = AsyncMock()

    # Call the method
    await postgres_service.close()

    # Assertions
    assert mock_postgres_session.close.called