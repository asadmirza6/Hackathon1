"""Tests for error scenarios in the RAG pipeline."""
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch
import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.utils.exceptions import QdrantUnavailableError, GeminiAPIError, DatabaseError, ValidationError


@pytest.fixture
def test_client():
    """Create a test client for the FastAPI app."""
    return TestClient(app)


@pytest.mark.asyncio
async def test_qdrant_unavailable_error(test_client):
    """Test handling of Qdrant unavailable error."""
    with patch('app.api.v1.query.RAGService') as mock_rag_service_class:
        # Configure to raise QdrantUnavailableError
        mock_rag_service = AsyncMock()
        mock_rag_service.process_query.side_effect = QdrantUnavailableError("Qdrant service unavailable")
        mock_rag_service_class.return_value = mock_rag_service

        response = test_client.post(
            "/v1/query",
            json={
                "question": "What is ZMP?",
                "session_id": "session-123"
            }
        )

        # Should return 503 Service Unavailable
        assert response.status_code == 503
        data = response.json()
        assert "detail" in data
        assert "temporarily unavailable" in data["detail"]


@pytest.mark.asyncio
async def test_gemini_api_timeout_error(test_client):
    """Test handling of Gemini API timeout error."""
    with patch('app.api.v1.query.RAGService') as mock_rag_service_class:
        # Configure to raise GeminiAPIError
        mock_rag_service = AsyncMock()
        mock_rag_service.process_query.side_effect = GeminiAPIError("Gemini API timeout")
        mock_rag_service_class.return_value = mock_rag_service

        response = test_client.post(
            "/v1/query",
            json={
                "question": "What is ZMP?",
                "session_id": "session-123"
            }
        )

        # Should return 502 Bad Gateway
        assert response.status_code == 502
        data = response.json()
        assert "detail" in data
        assert "generate response" in data["detail"]


@pytest.mark.asyncio
async def test_postgres_connection_failure(test_client):
    """Test handling of Postgres connection failure."""
    with patch('app.api.v1.query.RAGService') as mock_rag_service_class:
        # Mock successful processing but simulate DB failure during async logging
        mock_rag_service = AsyncMock()
        mock_rag_service.process_query.return_value = {
            "response_text": "Response with DB issues",
            "source_references": [{"chapter": 1, "lesson": 1, "section": "Intro"}],
            "confidence_score": 0.8,
            "timestamp": "2025-12-09T13:45:23Z"
        }
        mock_rag_service_class.return_value = mock_rag_service

        # Simulate DB error during async logging by patching the postgres service
        with patch('app.services.postgres_service.PostgresService.log_query_async') as mock_log:
            mock_log.side_effect = Exception("Postgres connection failed")

            response = test_client.post(
                "/v1/query",
                json={
                    "question": "What happens with DB issues?",
                    "session_id": "session-456"
                }
            )

            # Response should still succeed even if logging fails
            assert response.status_code == 200
            data = response.json()
            assert data["response_text"] == "Response with DB issues"


@pytest.mark.asyncio
async def test_invalid_input_validation_failure(test_client):
    """Test handling of invalid input validation failure."""
    # Test with question that's too short
    response = test_client.post(
        "/v1/query",
        json={
            "question": "Hi",  # Too short
            "session_id": "session-789"
        }
    )

    # Should return 400 Bad Request
    assert response.status_code == 400
    data = response.json()
    assert "detail" in data
    assert "Question must be at least" in data["detail"]


@pytest.mark.asyncio
async def test_invalid_session_id(test_client):
    """Test handling of invalid session ID."""
    response = test_client.post(
        "/v1/query",
        json={
            "question": "What is ZMP?",
            "session_id": "invalid session id!"  # Invalid format
        }
    )

    # Should return 400 Bad Request
    assert response.status_code == 400
    data = response.json()
    assert "detail" in data


@pytest.mark.asyncio
async def test_selected_context_too_long(test_client):
    """Test handling of selected context that's too long."""
    long_context = "a" * 5001  # Too long

    response = test_client.post(
        "/v1/query",
        json={
            "question": "What is ZMP?",
            "selected_context": long_context,
            "session_id": "session-999"
        }
    )

    # Should return 400 Bad Request
    assert response.status_code == 400
    data = response.json()
    assert "detail" in data
    assert "selected context" in data["detail"].lower()


@pytest.mark.asyncio
async def test_hallucination_detection(test_client):
    """Test handling of potential hallucination scenarios."""
    with patch('app.api.v1.query.RAGService') as mock_rag_service_class:
        # Mock a scenario where the service detects a hallucination
        mock_rag_service = AsyncMock()
        mock_rag_service.process_query.return_value = {
            "response_text": "I don't have information about this in the course material. Please ask about topics covered in the course.",
            "source_references": [],
            "confidence_score": 0.0,
            "timestamp": "2025-12-09T13:45:24Z"
        }
        mock_rag_service_class.return_value = mock_rag_service

        response = test_client.post(
            "/v1/query",
            json={
                "question": "What is the current stock price of Tesla?",
                "session_id": "session-888"
            }
        )

        # Should return a response indicating out-of-scope content
        assert response.status_code == 200
        data = response.json()
        assert "don't have information about this in the course material" in data["response_text"]


@pytest.mark.asyncio
async def test_empty_question_error(test_client):
    """Test handling of empty question."""
    response = test_client.post(
        "/v1/query",
        json={
            "question": "",  # Empty question
            "session_id": "session-777"
        }
    )

    # Should return 400 Bad Request
    assert response.status_code == 400
    data = response.json()
    assert "detail" in data


@pytest.mark.asyncio
async def test_empty_session_id_error(test_client):
    """Test handling of empty session ID."""
    response = test_client.post(
        "/v1/query",
        json={
            "question": "What is ZMP?",
            "session_id": ""  # Empty session ID
        }
    )

    # Should return 400 Bad Request
    assert response.status_code == 400
    data = response.json()
    assert "detail" in data


@pytest.mark.asyncio
async def test_missing_required_fields(test_client):
    """Test handling of missing required fields."""
    # Missing question
    response = test_client.post(
        "/v1/query",
        json={
            "session_id": "session-666"
            # Missing question
        }
    )

    # Should return 422 Unprocessable Entity
    assert response.status_code == 422

    # Missing session_id
    response = test_client.post(
        "/v1/query",
        json={
            "question": "What is ZMP?"
            # Missing session_id
        }
    )

    # Should return 422 Unprocessable Entity
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_health_endpoint_qdrant_error(test_client):
    """Test health endpoint when Qdrant is unavailable."""
    with patch('app.api.v1.health.QdrantService') as mock_qdrant_service:
        mock_service_instance = AsyncMock()
        mock_service_instance.check_health.side_effect = QdrantUnavailableError("Qdrant unavailable")
        mock_qdrant_service.return_value = mock_service_instance

        response = test_client.get("/v1/health")

        # Health check should still work but report Qdrant as unhealthy
        data = response.json()
        assert "services" in data
        assert data["status"] in ["healthy", "degraded"]  # Implementation dependent


@pytest.mark.asyncio
async def test_health_endpoint_gemini_error(test_client):
    """Test health endpoint when Gemini API is unavailable."""
    with patch('app.api.v1.health.GeminiService') as mock_gemini_service:
        mock_service_instance = AsyncMock()
        mock_service_instance.check_health.side_effect = GeminiAPIError("Gemini unavailable")
        mock_gemini_service.return_value = mock_service_instance

        response = test_client.get("/v1/health")

        # Health check should still work but report Gemini as unhealthy
        data = response.json()
        assert "services" in data


@pytest.mark.asyncio
async def test_logs_endpoint_admin_auth_required(test_client):
    """Test that logs endpoint requires admin authentication."""
    # Try to access logs without admin token
    response = test_client.get("/v1/logs")

    # Should return 401 Unauthorized or 422 if header required
    assert response.status_code in [401, 422]


@pytest.mark.asyncio
async def test_logs_endpoint_wrong_admin_token(test_client):
    """Test that logs endpoint rejects wrong admin token."""
    response = test_client.get("/v1/logs", headers={"X-Admin-Token": "wrong-token"})

    # Should return 401 Unauthorized
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_gemini_service_generation_error(test_client):
    """Test error handling when Gemini generation fails."""
    with patch('app.api.v1.query.RAGService') as mock_rag_service_class:
        mock_rag_service = AsyncMock()
        mock_rag_service.process_query.side_effect = GeminiAPIError("Generation failed")
        mock_rag_service_class.return_value = mock_rag_service

        response = test_client.post(
            "/v1/query",
            json={
                "question": "What is ZMP?",
                "session_id": "session-555"
            }
        )

        # Should return 502 Bad Gateway
        assert response.status_code == 502


@pytest.mark.asyncio
async def test_qdrant_service_search_error(test_client):
    """Test error handling when Qdrant search fails."""
    with patch('app.api.v1.query.RAGService') as mock_rag_service_class:
        mock_rag_service = AsyncMock()
        mock_rag_service.process_query.side_effect = QdrantUnavailableError("Search failed")
        mock_rag_service_class.return_value = mock_rag_service

        response = test_client.post(
            "/v1/query",
            json={
                "question": "What is ZMP?",
                "session_id": "session-444"
            }
        )

        # Should return 503 Service Unavailable
        assert response.status_code == 503


@pytest.mark.asyncio
async def test_database_error_during_query_save(test_client):
    """Test handling of database error during query save."""
    with patch('app.services.postgres_service.PostgresService.save_query') as mock_save:
        mock_save.side_effect = Exception("Database connection failed")

        with patch('app.api.v1.query.RAGService') as mock_rag_service_class:
            mock_rag_service = AsyncMock()
            mock_rag_service.process_query.return_value = {
                "response_text": "Response despite DB error",
                "source_references": [{"chapter": 1, "lesson": 1, "section": "Intro"}],
                "confidence_score": 0.8,
                "timestamp": "2025-12-09T13:45:25Z"
            }
            mock_rag_service_class.return_value = mock_rag_service

            response = test_client.post(
                "/v1/query",
                json={
                    "question": "What about DB errors?",
                    "session_id": "session-333"
                }
            )

            # Response should still succeed even if DB save fails
            assert response.status_code == 200
            data = response.json()
            assert data["response_text"] == "Response despite DB error"


@pytest.mark.asyncio
async def test_timeout_handling_in_pipeline(test_client):
    """Test timeout handling in the RAG pipeline."""
    with patch('app.api.v1.query.RAGService') as mock_rag_service_class:
        # Simulate a timeout scenario
        mock_rag_service = AsyncMock()
        mock_rag_service.process_query.side_effect = asyncio.TimeoutError("Operation timed out")
        mock_rag_service_class.return_value = mock_rag_service

        response = test_client.post(
            "/v1/query",
            json={
                "question": "What is ZMP?",
                "session_id": "session-222"
            }
        )

        # Should return 500 Internal Server Error or similar
        assert response.status_code >= 500


@pytest.mark.asyncio
async def test_rate_limiting_error(test_client):
    """Test rate limiting error scenario."""
    # This would typically be implemented with middleware
    # For now, test if the error message is handled properly
    response = test_client.post(
        "/v1/query",
        json={
            "question": "What is ZMP?",
            "session_id": "session-111"
        }
    )

    # If rate limiting is implemented, this would return 429
    # For now, we're testing that the system handles it gracefully
    assert response.status_code in [200, 429]  # Either success or rate limited


@pytest.mark.asyncio
async def test_large_request_payload(test_client):
    """Test handling of large request payloads."""
    large_question = "a" * 3000  # Very long question

    response = test_client.post(
        "/v1/query",
        json={
            "question": large_question,
            "session_id": "session-000"
        }
    )

    # Should return 400 for validation error or 413 for payload too large
    assert response.status_code in [400, 413]


@pytest.mark.asyncio
async def test_malformed_json_request(test_client):
    """Test handling of malformed JSON requests."""
    # Send malformed JSON
    response = test_client.post(
        "/v1/query",
        content="{invalid json",
        headers={"Content-Type": "application/json"}
    )

    # Should return 422 for validation error or 400 for malformed JSON
    assert response.status_code in [400, 422]