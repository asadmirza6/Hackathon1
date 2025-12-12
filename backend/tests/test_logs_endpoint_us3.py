"""Integration tests for logs endpoint in User Story 3 - Query Logging and Analytics."""
import asyncio
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, MagicMock, patch
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.main import app
from app.models.chat_query import ChatQuery
from app.services.postgres_service import PostgresService


@pytest.fixture
def test_client():
    """Create a test client for the FastAPI app."""
    return TestClient(app)


@pytest.mark.asyncio
async def test_get_logs_pagination(test_client, mock_postgres_session):
    """Test GET /v1/logs endpoint with pagination."""
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

    # Mock the postgres service
    with patch('app.api.v1.logs.PostgresService') as mock_service_class:
        mock_service_instance = AsyncMock()
        mock_service_instance.get_query_logs.return_value = (mock_queries, 2)
        mock_service_class.return_value = mock_service_instance

        # Make request to the endpoint
        response = test_client.get("/v1/logs", headers={"X-Admin-Token": "test-token"})

        # Assertions
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert "total" in data
        assert len(data["items"]) == 2
        assert data["total"] == 2


@pytest.mark.asyncio
async def test_get_logs_with_filters(test_client, mock_postgres_session):
    """Test GET /v1/logs endpoint with filters."""
    # Mock data
    mock_query = MagicMock(spec=ChatQuery)
    mock_query.id = 1
    mock_query.question = "Filtered question"
    mock_query.response_text = "Filtered response"
    mock_query.session_id = "filtered-session"
    mock_query.confidence_score = 0.88
    mock_query.timestamp = datetime.utcnow()
    mock_query.source_chapters = [{"chapter": 1, "lesson": 1, "section": "Intro"}]
    mock_query.query_duration_ms = 1300.0

    mock_queries = [mock_query]

    # Mock the postgres service
    with patch('app.api.v1.logs.PostgresService') as mock_service_class:
        mock_service_instance = AsyncMock()
        mock_service_instance.get_query_logs.return_value = (mock_queries, 1)
        mock_service_class.return_value = mock_service_instance

        # Make request with filters
        response = test_client.get(
            "/v1/logs",
            params={"session_id": "filtered-session", "limit": 10, "offset": 0},
            headers={"X-Admin-Token": "test-token"}
        )

        # Assertions
        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) == 1
        assert data["items"][0]["session_id"] == "filtered-session"


@pytest.mark.asyncio
async def test_get_analytics(test_client, mock_postgres_session):
    """Test GET /v1/logs/aggregate endpoint."""
    # Mock analytics data
    mock_analytics = {
        "query_count": 10,
        "avg_confidence": 0.85,
        "avg_response_time_ms": 1400.0,
        "unique_sessions": 5,
        "period_days": 7
    }

    # Mock the postgres service
    with patch('app.api.v1.logs.PostgresService') as mock_service_class:
        mock_service_instance = AsyncMock()
        mock_service_instance.get_analytics.return_value = mock_analytics
        mock_service_class.return_value = mock_service_instance

        # Make request to the analytics endpoint
        response = test_client.get("/v1/logs/aggregate", headers={"X-Admin-Token": "test-token"})

        # Assertions
        assert response.status_code == 200
        data = response.json()
        assert "query_count" in data
        assert "avg_confidence" in data
        assert data["query_count"] == 10


@pytest.mark.asyncio
async def test_get_performance_metrics(test_client, mock_postgres_session):
    """Test GET /v1/logs/metrics endpoint."""
    # Mock metrics data
    mock_metrics = {
        "query_count": 15,
        "period_days": 7,
        "avg_confidence": 0.87,
        "min_confidence": 0.75,
        "max_confidence": 0.95,
        "avg_response_time_ms": 1350.0,
        "p95_response_time_ms": 2100.0,
        "avg_retrieval_time_ms": 120.0,
        "avg_generation_time_ms": 1230.0,
        "unique_sessions": 8
    }

    # Mock the analytics service
    with patch('app.api.v1.logs.AnalyticsService') as mock_service_class:
        mock_service_instance = AsyncMock()
        mock_service_instance.get_performance_metrics.return_value = mock_metrics
        mock_service_class.return_value = mock_service_instance

        # Make request to the metrics endpoint
        response = test_client.get("/v1/logs/metrics", headers={"X-Admin-Token": "test-token"})

        # Assertions
        assert response.status_code == 200
        data = response.json()
        assert "query_count" in data
        assert "avg_response_time_ms" in data
        assert data["query_count"] == 15


@pytest.mark.asyncio
async def test_get_top_questions(test_client, mock_postgres_session):
    """Test GET /v1/logs/top-questions endpoint."""
    # Mock top questions data
    mock_top_questions = [
        {
            "question": "What is ZMP?",
            "count": 5,
            "avg_confidence": 0.88
        },
        {
            "question": "How does walking work?",
            "count": 3,
            "avg_confidence": 0.82
        }
    ]

    # Mock the analytics service
    with patch('app.api.v1.logs.AnalyticsService') as mock_service_class:
        mock_service_instance = AsyncMock()
        mock_service_instance.get_top_questions.return_value = mock_top_questions
        mock_service_class.return_value = mock_service_instance

        # Make request to the top questions endpoint
        response = test_client.get("/v1/logs/top-questions", headers={"X-Admin-Token": "test-token"})

        # Assertions
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert len(data["items"]) == 2
        assert data["items"][0]["question"] == "What is ZMP?"


@pytest.mark.asyncio
async def test_get_content_coverage(test_client, mock_postgres_session):
    """Test GET /v1/logs/coverage endpoint."""
    # Mock coverage data
    mock_coverage = {
        "coverage": {
            "chapter_1": {"lesson_1": 10, "lesson_2": 5},
            "chapter_2": {"lesson_1": 8}
        },
        "total_queries": 23,
        "chapters_queried": 2
    }

    # Mock the analytics service
    with patch('app.api.v1.logs.AnalyticsService') as mock_service_class:
        mock_service_instance = AsyncMock()
        mock_service_instance.get_content_coverage.return_value = mock_coverage
        mock_service_class.return_value = mock_service_instance

        # Make request to the content coverage endpoint
        response = test_client.get("/v1/logs/coverage", headers={"X-Admin-Token": "test-token"})

        # Assertions
        assert response.status_code == 200
        data = response.json()
        assert "coverage" in data
        assert "total_queries" in data
        assert data["total_queries"] == 23


@pytest.mark.asyncio
async def test_logs_endpoint_unauthorized(test_client):
    """Test that logs endpoints require admin token."""
    # Make request without admin token
    response = test_client.get("/v1/logs")

    # Should return 401 Unauthorized or 422 if header is required
    assert response.status_code in [401, 422]


@pytest.mark.asyncio
async def test_logs_endpoint_wrong_token(test_client):
    """Test that logs endpoints reject wrong admin token."""
    # Make request with wrong admin token
    response = test_client.get("/v1/logs", headers={"X-Admin-Token": "wrong-token"})

    # Should return 401 Unauthorized
    assert response.status_code == 401
    assert "Unauthorized" in response.json()["detail"]


@pytest.mark.asyncio
async def test_logs_endpoint_valid_token(test_client, mock_postgres_session):
    """Test that logs endpoints work with valid admin token."""
    # Mock empty results
    mock_queries = []

    # Mock the postgres service
    with patch('app.api.v1.logs.PostgresService') as mock_service_class:
        mock_service_instance = AsyncMock()
        mock_service_instance.get_query_logs.return_value = (mock_queries, 0)
        mock_service_class.return_value = mock_service_instance

        # Make request with valid admin token (using environment variable bypass)
        with patch('os.getenv', return_value=None):  # Simulate no ADMIN_TOKEN set for dev mode
            response = test_client.get("/v1/logs")

        # Should return 200 OK in dev mode when ADMIN_TOKEN not set
        assert response.status_code == 200


@pytest.mark.asyncio
async def test_aggregate_endpoint_with_params(test_client, mock_postgres_session):
    """Test GET /v1/logs/aggregate endpoint with parameters."""
    # Mock analytics data
    mock_analytics = {
        "query_count": 5,
        "avg_confidence": 0.82,
        "avg_response_time_ms": 1200.0,
        "unique_sessions": 3,
        "period_days": 3
    }

    # Mock the postgres service
    with patch('app.api.v1.logs.PostgresService') as mock_service_class:
        mock_service_instance = AsyncMock()
        mock_service_instance.get_analytics.return_value = mock_analytics
        mock_service_class.return_value = mock_service_instance

        # Make request with days_back parameter
        response = test_client.get("/v1/logs/aggregate?days_back=3", headers={"X-Admin-Token": "test-token"})

        # Assertions
        assert response.status_code == 200
        data = response.json()
        assert data["period_days"] == 3
        assert data["query_count"] == 5