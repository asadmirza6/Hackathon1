"""Integration tests for POST /v1/query endpoint."""
import pytest
from httpx import AsyncClient
from unittest.mock import AsyncMock, patch, MagicMock

from main import app
from app.models.schemas import ChatQueryRequest, ChatResponseSchema


@pytest.fixture
async def client():
    """Create test client."""
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac


class TestQueryEndpoint:
    """Tests for POST /v1/query endpoint."""

    @pytest.mark.asyncio
    async def test_query_success_happy_path(self, client):
        """Test successful query with all components working."""
        with patch(
            "app.api.v1.query.QdrantService"
        ) as mock_qdrant_class, patch(
            "app.api.v1.query.GeminiService"
        ) as mock_gemini_class, patch(
            "app.api.v1.query.PostgresService"
        ) as mock_postgres_class:

            # Setup mocks
            mock_qdrant = AsyncMock()
            mock_qdrant.search_similar_chunks.return_value = [
                {
                    "id": 1,
                    "text": "ZMP is the point where total moment is zero.",
                    "similarity_score": 0.92,
                    "chapter": 3,
                    "lesson": 2,
                    "section": "Walking Pattern",
                }
            ]
            mock_qdrant_class.return_value = mock_qdrant

            mock_gemini = AsyncMock()
            mock_gemini.generate_embedding.return_value = [0.1] * 768
            mock_gemini.generate_response_for_query.return_value = (
                "ZMP (Zero Moment Point) is the point where the total moment is zero."
            )
            mock_gemini_class.return_value = mock_gemini

            mock_postgres = AsyncMock()
            mock_postgres.save_query.return_value = MagicMock(id=1)
            mock_postgres_class.return_value = mock_postgres

            request_body = {
                "question": "What is ZMP in bipedal walking?",
                "session_id": "test-session-12345",
                "selected_context": None,
            }

            response = await client.post("/v1/query", json=request_body)

            assert response.status_code == 200
            data = response.json()
            assert "response_text" in data
            assert "source_references" in data
            assert "confidence_score" in data
            assert "timestamp" in data
            assert data["confidence_score"] > 0.3

    @pytest.mark.asyncio
    async def test_query_validation_error_short_question(self, client):
        """Test validation error for question too short."""
        request_body = {
            "question": "Hi",  # Too short
            "session_id": "test-session-12345",
        }

        response = await client.post("/v1/query", json=request_body)

        assert response.status_code == 400
        assert "error" in response.json() or "detail" in response.json()

    @pytest.mark.asyncio
    async def test_query_validation_error_long_question(self, client):
        """Test validation error for question too long."""
        request_body = {
            "question": "x" * 2001,  # Too long
            "session_id": "test-session-12345",
        }

        response = await client.post("/v1/query", json=request_body)

        assert response.status_code == 400

    @pytest.mark.asyncio
    async def test_query_validation_error_invalid_session(self, client):
        """Test validation error for invalid session ID."""
        request_body = {
            "question": "What is control systems?",
            "session_id": "123",  # Too short
        }

        response = await client.post("/v1/query", json=request_body)

        assert response.status_code == 400

    @pytest.mark.asyncio
    async def test_query_qdrant_unavailable(self, client):
        """Test graceful error when Qdrant is unavailable."""
        with patch(
            "app.api.v1.query.QdrantService"
        ) as mock_qdrant_class, patch(
            "app.api.v1.query.GeminiService"
        ) as mock_gemini_class:

            # Qdrant unavailable
            mock_qdrant = AsyncMock()
            mock_qdrant.search_similar_chunks.side_effect = Exception(
                "Connection refused"
            )
            mock_qdrant_class.return_value = mock_qdrant

            mock_gemini = AsyncMock()
            mock_gemini.generate_embedding.return_value = [0.1] * 768
            mock_gemini_class.return_value = mock_gemini

            request_body = {
                "question": "What is a PID controller?",
                "session_id": "test-session-12345",
            }

            response = await client.post("/v1/query", json=request_body)

            # Should handle gracefully
            assert response.status_code in [500, 503]

    @pytest.mark.asyncio
    async def test_query_gemini_error(self, client):
        """Test graceful error when Gemini API fails."""
        with patch(
            "app.api.v1.query.QdrantService"
        ) as mock_qdrant_class, patch(
            "app.api.v1.query.GeminiService"
        ) as mock_gemini_class:

            mock_qdrant = AsyncMock()
            mock_qdrant.search_similar_chunks.return_value = [
                {
                    "text": "Content",
                    "similarity_score": 0.9,
                    "chapter": 1,
                    "lesson": 1,
                    "section": "Intro",
                }
            ]
            mock_qdrant_class.return_value = mock_qdrant

            mock_gemini = AsyncMock()
            mock_gemini.generate_embedding.return_value = [0.1] * 768
            mock_gemini.generate_response_for_query.side_effect = Exception(
                "API quota exceeded"
            )
            mock_gemini_class.return_value = mock_gemini

            request_body = {
                "question": "What is acceleration?",
                "session_id": "test-session-12345",
            }

            response = await client.post("/v1/query", json=request_body)

            assert response.status_code in [500, 502]

    @pytest.mark.asyncio
    async def test_query_with_selected_context(self, client):
        """Test query with selected text context."""
        with patch(
            "app.api.v1.query.QdrantService"
        ) as mock_qdrant_class, patch(
            "app.api.v1.query.GeminiService"
        ) as mock_gemini_class, patch(
            "app.api.v1.query.PostgresService"
        ) as mock_postgres_class:

            mock_qdrant = AsyncMock()
            mock_qdrant.search_similar_chunks.return_value = [
                {
                    "text": "Motion planning involves trajectory generation.",
                    "similarity_score": 0.88,
                    "chapter": 3,
                    "lesson": 1,
                    "section": "Locomotion",
                }
            ]
            mock_qdrant_class.return_value = mock_qdrant

            mock_gemini = AsyncMock()
            mock_gemini.generate_embedding.return_value = [0.1] * 768
            mock_gemini.generate_response_for_query.return_value = (
                "Motion planning is the process..."
            )
            mock_gemini_class.return_value = mock_gemini

            mock_postgres = AsyncMock()
            mock_postgres.save_query.return_value = MagicMock(id=1)
            mock_postgres_class.return_value = mock_postgres

            request_body = {
                "question": "How does this relate to bipedal motion?",
                "session_id": "test-session-12345",
                "selected_context": "Selected text about motion planning",
            }

            response = await client.post("/v1/query", json=request_body)

            assert response.status_code == 200
            data = response.json()
            assert len(data["source_references"]) > 0

    @pytest.mark.asyncio
    async def test_query_response_schema_validation(self, client):
        """Test response conforms to ChatResponseSchema."""
        with patch(
            "app.api.v1.query.QdrantService"
        ) as mock_qdrant_class, patch(
            "app.api.v1.query.GeminiService"
        ) as mock_gemini_class, patch(
            "app.api.v1.query.PostgresService"
        ) as mock_postgres_class:

            mock_qdrant = AsyncMock()
            mock_qdrant.search_similar_chunks.return_value = [
                {
                    "text": "Test content",
                    "similarity_score": 0.85,
                    "chapter": 1,
                    "lesson": 1,
                    "section": "Test",
                }
            ]
            mock_qdrant_class.return_value = mock_qdrant

            mock_gemini = AsyncMock()
            mock_gemini.generate_embedding.return_value = [0.1] * 768
            mock_gemini.generate_response_for_query.return_value = "Test response"
            mock_gemini_class.return_value = mock_gemini

            mock_postgres = AsyncMock()
            mock_postgres.save_query.return_value = MagicMock(id=1)
            mock_postgres_class.return_value = mock_postgres

            request_body = {
                "question": "Test question please?",
                "session_id": "test-session-12345",
            }

            response = await client.post("/v1/query", json=request_body)

            assert response.status_code == 200
            data = response.json()

            # Validate all required fields
            assert isinstance(data["response_text"], str)
            assert isinstance(data["source_references"], list)
            assert isinstance(data["confidence_score"], (int, float))
            assert 0 <= data["confidence_score"] <= 1
            assert isinstance(data["timestamp"], str)


class TestHealthEndpoint:
    """Tests for GET /v1/health endpoint."""

    @pytest.mark.asyncio
    async def test_health_check_success(self, client):
        """Test health check returns status."""
        with patch(
            "app.api.v1.health.check_qdrant_health"
        ) as mock_qdrant, patch(
            "app.api.v1.health.check_gemini_health"
        ) as mock_gemini, patch(
            "app.api.v1.health.check_postgres_health"
        ) as mock_postgres:

            mock_qdrant.return_value = (True, "Connected")
            mock_gemini.return_value = (True, "Connected")
            mock_postgres.return_value = (True, "Configured")

            response = await client.get("/v1/health")

            assert response.status_code == 200
            data = response.json()
            assert "status" in data
            assert "services" in data
            assert "timestamp" in data
            assert data["status"] in ["healthy", "degraded", "unhealthy"]


class TestLogsEndpoint:
    """Tests for GET /v1/logs endpoint."""

    @pytest.mark.asyncio
    async def test_logs_retrieval(self, client):
        """Test retrieving query logs."""
        with patch(
            "app.api.v1.logs.PostgresService"
        ) as mock_postgres_class:

            mock_postgres = AsyncMock()
            from app.models.chat_query import ChatQuery
            from datetime import datetime

            mock_query = MagicMock(spec=ChatQuery)
            mock_query.id = 1
            mock_query.question = "What is ZMP?"
            mock_query.response_text = "ZMP is..."
            mock_query.session_id = "session-123"
            mock_query.confidence_score = 0.92
            mock_query.timestamp = datetime.utcnow()
            mock_query.source_chapters = []

            mock_postgres.get_query_logs.return_value = ([mock_query], 1)
            mock_postgres_class.return_value = mock_postgres

            response = await client.get("/v1/logs?limit=10&offset=0")

            assert response.status_code == 200
            data = response.json()
            assert "items" in data
            assert "total" in data
            assert "limit" in data
            assert "offset" in data
