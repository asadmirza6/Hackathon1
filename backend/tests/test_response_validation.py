"""Tests to verify all responses conform to expected schemas and formats."""
import json
from datetime import datetime
from unittest.mock import AsyncMock, patch
import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.models.schemas import ChatResponseSchema, HealthCheckResponse, PaginatedLogsResponse


@pytest.fixture
def test_client():
    """Create a test client for the FastAPI app."""
    return TestClient(app)


def test_chat_response_schema_structure():
    """Test that ChatResponseSchema has the correct structure."""
    response_data = {
        "response_text": "Zero Moment Point (ZMP) is a concept...",
        "source_references": [
            {"chapter": 3, "lesson": 2, "section": "Walking Pattern Generation"}
        ],
        "confidence_score": 0.92,
        "timestamp": "2025-12-09T13:45:23Z"
    }

    schema = ChatResponseSchema(**response_data)

    assert schema.response_text == response_data["response_text"]
    assert len(schema.source_references) == 1
    assert schema.confidence_score == 0.92
    assert schema.timestamp == "2025-12-09T13:45:23Z"

    # Test with optional timestamp as None
    response_data_no_timestamp = {
        "response_text": "Response text",
        "source_references": [],
        "confidence_score": 0.8
    }

    schema_no_timestamp = ChatResponseSchema(**response_data_no_timestamp)
    assert schema_no_timestamp.timestamp is None


def test_source_reference_schema():
    """Test that SourceReference has the correct structure."""
    from app.models.schemas import SourceReference

    source_data = {
        "chapter": 3,
        "lesson": 2,
        "section": "Walking Pattern Generation"
    }

    source = SourceReference(**source_data)

    assert source.chapter == 3
    assert source.lesson == 2
    assert source.section == "Walking Pattern Generation"


def test_health_check_response_schema():
    """Test that HealthCheckResponse has the correct structure."""
    health_data = {
        "status": "healthy",
        "timestamp": "2025-12-09T13:45:23Z",
        "services": {
            "qdrant": "healthy",
            "gemini": "healthy",
            "postgres": "degraded"
        }
    }

    health = HealthCheckResponse(**health_data)

    assert health.status == "healthy"
    assert "qdrant" in health.services
    assert health.services["qdrant"] == "healthy"


def test_paginated_logs_response_schema():
    """Test that PaginatedLogsResponse has the correct structure."""
    from app.models.schemas import QueryLogEntry

    log_entry = QueryLogEntry(
        id=1,
        question="Test question?",
        response_text="Test response",
        session_id="session-123",
        confidence_score=0.8
    )

    paginated_data = {
        "items": [log_entry],
        "total": 1,
        "limit": 10,
        "offset": 0
    }

    paginated = PaginatedLogsResponse(**paginated_data)

    assert len(paginated.items) == 1
    assert paginated.total == 1
    assert paginated.limit == 10
    assert paginated.offset == 0


@pytest.mark.asyncio
async def test_query_endpoint_response_conforms_to_schema(test_client):
    """Test that query endpoint responses conform to ChatResponseSchema."""
    with patch('app.api.v1.query.RAGService') as mock_rag_service_class:
        mock_rag_service = AsyncMock()
        expected_response = {
            "response_text": "Zero Moment Point (ZMP) is a concept used in bipedal locomotion...",
            "source_references": [
                {"chapter": 3, "lesson": 2, "section": "Walking Pattern Generation"}
            ],
            "confidence_score": 0.92,
            "timestamp": "2025-12-09T13:45:23Z"
        }
        mock_rag_service.process_query.return_value = expected_response
        mock_rag_service_class.return_value = mock_rag_service

        response = test_client.post(
            "/v1/query",
            json={
                "question": "What is ZMP in bipedal walking?",
                "session_id": "session-123"
            }
        )

        assert response.status_code == 200
        data = response.json()

        # Validate required fields exist
        assert "response_text" in data
        assert "source_references" in data
        assert "confidence_score" in data

        # Validate field types
        assert isinstance(data["response_text"], str)
        assert isinstance(data["source_references"], list)
        assert isinstance(data["confidence_score"], float)

        # Validate confidence score range
        assert 0.0 <= data["confidence_score"] <= 1.0

        # Validate source reference structure
        if data["source_references"]:
            source = data["source_references"][0]
            assert "chapter" in source
            assert "lesson" in source
            assert "section" in source
            assert isinstance(source["chapter"], int)
            assert isinstance(source["lesson"], int)
            assert isinstance(source["section"], str)


@pytest.mark.asyncio
async def test_query_endpoint_response_with_selected_context(test_client):
    """Test that query endpoint responses with selected context conform to schema."""
    with patch('app.api.v1.query.RAGService') as mock_rag_service_class:
        mock_rag_service = AsyncMock()
        expected_response = {
            "response_text": "Based on the selected passage, ZMP refers to...",
            "source_references": [
                {"chapter": 3, "lesson": 2, "section": "Walking Pattern Generation", "from_selected_context": True}
            ],
            "confidence_score": 0.88,
            "timestamp": "2025-12-09T13:45:24Z"
        }
        mock_rag_service.process_query.return_value = expected_response
        mock_rag_service_class.return_value = mock_rag_service

        response = test_client.post(
            "/v1/query",
            json={
                "question": "Can you explain this concept?",
                "selected_context": "Zero Moment Point is the point where the net moment of the ground reaction force is zero.",
                "session_id": "session-456"
            }
        )

        assert response.status_code == 200
        data = response.json()

        # Validate response structure
        assert "response_text" in data
        assert "source_references" in data
        assert "confidence_score" in data

        # Validate confidence score is in range
        assert 0.0 <= data["confidence_score"] <= 1.0


@pytest.mark.asyncio
async def test_health_endpoint_response_conforms_to_schema(test_client):
    """Test that health endpoint responses conform to HealthCheckResponse schema."""
    response = test_client.get("/v1/health")

    assert response.status_code == 200
    data = response.json()

    # Validate required fields exist
    assert "status" in data
    assert "timestamp" in data
    assert "services" in data

    # Validate field types
    assert isinstance(data["status"], str)
    assert isinstance(data["timestamp"], str)
    assert isinstance(data["services"], dict)

    # Validate timestamp format (should be ISO 8601)
    try:
        datetime.fromisoformat(data["timestamp"].replace("Z", "+00:00"))
    except ValueError:
        pytest.fail("timestamp is not in valid ISO 8601 format")


@pytest.mark.asyncio
async def test_logs_endpoint_response_conforms_to_schema(test_client):
    """Test that logs endpoint responses conform to PaginatedLogsResponse schema."""
    with patch('os.getenv', return_value=None):  # Bypass admin token for testing
        with patch('app.api.v1.logs.PostgresService') as mock_postgres_service_class:
            # Mock empty results
            mock_service_instance = AsyncMock()
            mock_service_instance.get_query_logs.return_value = ([], 0)
            mock_postgres_service_class.return_value = mock_service_instance

            response = test_client.get("/v1/logs", headers={"X-Admin-Token": "test"})

            assert response.status_code == 200
            data = response.json()

            # Validate required fields exist
            assert "items" in data
            assert "total" in data
            assert "limit" in data
            assert "offset" in data

            # Validate field types
            assert isinstance(data["items"], list)
            assert isinstance(data["total"], int)
            assert isinstance(data["limit"], int)
            assert isinstance(data["offset"], int)


@pytest.mark.asyncio
async def test_response_timestamp_format_validation(test_client):
    """Test that response timestamps are in valid ISO-8601 format."""
    with patch('app.api.v1.query.RAGService') as mock_rag_service_class:
        mock_rag_service = AsyncMock()
        expected_response = {
            "response_text": "Response with timestamp",
            "source_references": [{"chapter": 1, "lesson": 1, "section": "Intro"}],
            "confidence_score": 0.8,
            "timestamp": "2025-12-09T13:45:23Z"  # ISO 8601 format
        }
        mock_rag_service.process_query.return_value = expected_response
        mock_rag_service_class.return_value = mock_rag_service

        response = test_client.post(
            "/v1/query",
            json={
                "question": "Timestamp format test?",
                "session_id": "session-789"
            }
        )

        assert response.status_code == 200
        data = response.json()

        # Validate timestamp format if present
        if "timestamp" in data and data["timestamp"]:
            try:
                # Handle both 'Z' suffix and standard ISO format
                timestamp_str = data["timestamp"]
                if timestamp_str.endswith('Z'):
                    timestamp_str = timestamp_str[:-1] + '+00:00'
                datetime.fromisoformat(timestamp_str)
            except ValueError:
                pytest.fail(f"Timestamp '{data['timestamp']}' is not in valid ISO 8601 format")


@pytest.mark.asyncio
async def test_response_confidence_score_validation(test_client):
    """Test that confidence scores are within valid range (0.0 to 1.0)."""
    test_cases = [
        0.0,   # Minimum
        0.5,   # Middle
        1.0,   # Maximum
        0.85,  # Typical value
    ]

    for confidence in test_cases:
        with patch('app.api.v1.query.RAGService') as mock_rag_service_class:
            mock_rag_service = AsyncMock()
            expected_response = {
                "response_text": f"Response with confidence {confidence}",
                "source_references": [{"chapter": 1, "lesson": 1, "section": "Intro"}],
                "confidence_score": confidence,
                "timestamp": "2025-12-09T13:45:25Z"
            }
            mock_rag_service.process_query.return_value = expected_response
            mock_rag_service_class.return_value = mock_rag_service

            response = test_client.post(
                "/v1/query",
                json={
                    "question": f"Confidence test {confidence}?",
                    "session_id": f"session-{confidence}"
                }
            )

            assert response.status_code == 200
            data = response.json()

            # Validate confidence score is within range
            assert 0.0 <= data["confidence_score"] <= 1.0
            assert data["confidence_score"] == confidence


@pytest.mark.asyncio
async def test_response_source_references_structure(test_client):
    """Test that source references have the correct structure."""
    with patch('app.api.v1.query.RAGService') as mock_rag_service_class:
        mock_rag_service = AsyncMock()
        expected_response = {
            "response_text": "Response with sources",
            "source_references": [
                {"chapter": 1, "lesson": 1, "section": "Introduction"},
                {"chapter": 2, "lesson": 1, "section": "Advanced Concepts"},
                {"chapter": 3, "lesson": 2, "section": "Applications"}
            ],
            "confidence_score": 0.85,
            "timestamp": "2025-12-09T13:45:26Z"
        }
        mock_rag_service.process_query.return_value = expected_response
        mock_rag_service_class.return_value = mock_rag_service

        response = test_client.post(
            "/v1/query",
            json={
                "question": "Source reference structure test?",
                "session_id": "session-sources"
            }
        )

        assert response.status_code == 200
        data = response.json()

        # Validate all source references have required fields
        for source in data["source_references"]:
            assert "chapter" in source
            assert "lesson" in source
            assert "section" in source
            assert isinstance(source["chapter"], int)
            assert isinstance(source["lesson"], int)
            assert isinstance(source["section"], str)


@pytest.mark.asyncio
async def test_error_response_structure(test_client):
    """Test that error responses have the expected structure."""
    # Test with invalid input (too short question)
    response = test_client.post(
        "/v1/query",
        json={
            "question": "Hi",  # Too short
            "session_id": "session-error"
        }
    )

    # Should return 400 with detail field
    assert response.status_code == 400
    data = response.json()

    # Error responses should have a 'detail' field
    assert "detail" in data
    assert isinstance(data["detail"], str)


@pytest.mark.asyncio
async def test_response_text_not_empty_validation(test_client):
    """Test that response text is not empty in successful responses."""
    with patch('app.api.v1.query.RAGService') as mock_rag_service_class:
        mock_rag_service = AsyncMock()
        expected_response = {
            "response_text": "This is a valid response text.",
            "source_references": [{"chapter": 1, "lesson": 1, "section": "Intro"}],
            "confidence_score": 0.7,
            "timestamp": "2025-12-09T13:45:27Z"
        }
        mock_rag_service.process_query.return_value = expected_response
        mock_rag_service_class.return_value = mock_rag_service

        response = test_client.post(
            "/v1/query",
            json={
                "question": "Response text validation?",
                "session_id": "session-validation"
            }
        )

        assert response.status_code == 200
        data = response.json()

        # Response text should not be empty
        assert "response_text" in data
        assert data["response_text"] != ""
        assert isinstance(data["response_text"], str)
        assert len(data["response_text"]) > 0


@pytest.mark.asyncio
async def test_response_with_no_sources(test_client):
    """Test response structure when no sources are found."""
    with patch('app.api.v1.query.RAGService') as mock_rag_service_class:
        mock_rag_service = AsyncMock()
        expected_response = {
            "response_text": "No relevant information found in course materials.",
            "source_references": [],  # Empty list when no sources
            "confidence_score": 0.0,
            "timestamp": "2025-12-09T13:45:28Z"
        }
        mock_rag_service.process_query.return_value = expected_response
        mock_rag_service_class.return_value = mock_rag_service

        response = test_client.post(
            "/v1/query",
            json={
                "question": "Question with no course matches?",
                "session_id": "session-no-sources"
            }
        )

        assert response.status_code == 200
        data = response.json()

        # Validate structure even with no sources
        assert "response_text" in data
        assert "source_references" in data
        assert "confidence_score" in data
        assert data["source_references"] == []  # Should be empty list, not None
        assert data["confidence_score"] == 0.0


@pytest.mark.asyncio
async def test_response_json_serialization(test_client):
    """Test that responses can be properly serialized to JSON."""
    with patch('app.api.v1.query.RAGService') as mock_rag_service_class:
        mock_rag_service = AsyncMock()
        expected_response = {
            "response_text": "JSON serialization test response.",
            "source_references": [{"chapter": 1, "lesson": 1, "section": "Intro"}],
            "confidence_score": 0.8,
            "timestamp": "2025-12-09T13:45:29Z"
        }
        mock_rag_service.process_query.return_value = expected_response
        mock_rag_service_class.return_value = mock_rag_service

        response = test_client.post(
            "/v1/query",
            json={
                "question": "JSON serialization test?",
                "session_id": "session-json"
            }
        )

        assert response.status_code == 200

        # Verify the response can be parsed as JSON
        try:
            data = response.json()
            json_str = json.dumps(data)
            parsed_again = json.loads(json_str)
            assert parsed_again == data
        except json.JSONDecodeError:
            pytest.fail("Response is not valid JSON")


@pytest.mark.asyncio
async def test_response_field_types_consistency(test_client):
    """Test that response fields maintain consistent types."""
    with patch('app.api.v1.query.RAGService') as mock_rag_service_class:
        mock_rag_service = AsyncMock()
        expected_response = {
            "response_text": "Consistent type test",
            "source_references": [
                {"chapter": 1, "lesson": 1, "section": "Type Test Section"}
            ],
            "confidence_score": 0.75,
            "timestamp": "2025-12-09T13:45:30Z"
        }
        mock_rag_service.process_query.return_value = expected_response
        mock_rag_service_class.return_value = mock_rag_service

        response = test_client.post(
            "/v1/query",
            json={
                "question": "Field type consistency?",
                "session_id": "session-types"
            }
        )

        assert response.status_code == 200
        data = response.json()

        # Verify field types are consistent
        assert isinstance(data["response_text"], str)
        assert isinstance(data["source_references"], list)
        assert isinstance(data["confidence_score"], float)
        if "timestamp" in data and data["timestamp"]:
            assert isinstance(data["timestamp"], str)

        # Verify source reference types
        if data["source_references"]:
            source = data["source_references"][0]
            assert isinstance(source["chapter"], int)
            assert isinstance(source["lesson"], int)
            assert isinstance(source["section"], str)