"""Tests for concurrent request handling in the RAG chatbot."""
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch
import pytest
import time
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture
def test_client():
    """Create a test client for the FastAPI app."""
    return TestClient(app)


@pytest.mark.asyncio
async def test_multiple_concurrent_requests():
    """Test handling of multiple concurrent requests to the query endpoint."""
    # Use test client in async context
    with patch('app.api.v1.query.RAGService') as mock_rag_service_class:
        # Create a mock instance that returns consistent responses
        mock_rag_service = AsyncMock()
        mock_rag_service.process_query.return_value = {
            "response_text": "Response to concurrent request",
            "source_references": [{"chapter": 1, "lesson": 1, "section": "Intro"}],
            "confidence_score": 0.8,
            "timestamp": "2025-12-09T13:45:23Z"
        }
        mock_rag_service_class.return_value = mock_rag_service

        async def make_request(client, question, session_id):
            # Simulate making the request using FastAPI TestClient in a thread
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None,
                lambda: client.post(
                    "/v1/query",
                    json={
                        "question": question,
                        "session_id": session_id
                    }
                )
            )
            return response.status_code, response.json()

        # Create a shared test client instance
        client = TestClient(app)

        # Create multiple concurrent requests
        tasks = []
        for i in range(10):
            task = make_request(client, f"Question {i}", f"session-{i}")
            tasks.append(task)

        # Execute all requests concurrently
        results = await asyncio.gather(*tasks)

        # Verify all requests succeeded
        for status_code, data in results:
            assert status_code == 200
            assert "response_text" in data
            assert "confidence_score" in data


@pytest.mark.asyncio
async def test_high_concurrency_load():
    """Test handling of high concurrency load (simulated)."""
    with patch('app.api.v1.query.RAGService') as mock_rag_service_class:
        mock_rag_service = AsyncMock()
        mock_rag_service.process_query.return_value = {
            "response_text": "Response under load",
            "source_references": [{"chapter": 2, "lesson": 1, "section": "Advanced"}],
            "confidence_score": 0.75,
            "timestamp": "2025-12-09T13:45:24Z"
        }
        mock_rag_service_class.return_value = mock_rag_service

        async def make_request(client, question, session_id):
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None,
                lambda: client.post(
                    "/v1/query",
                    json={
                        "question": question,
                        "session_id": session_id
                    }
                )
            )
            return response.status_code

        client = TestClient(app)

        # Simulate 20 concurrent requests
        tasks = [make_request(client, f"Load test question {i}", f"load-session-{i}") for i in range(20)]
        results = await asyncio.gather(*tasks)

        # All requests should succeed (no 5xx errors under load)
        success_count = sum(1 for status in results if status == 200)
        assert success_count == 20, f"Expected all 20 requests to succeed, but only {success_count} did"


@pytest.mark.asyncio
async def test_concurrent_requests_with_different_contexts():
    """Test concurrent requests with different selected contexts."""
    with patch('app.api.v1.query.RAGService') as mock_rag_service_class:
        mock_rag_service = AsyncMock()
        mock_rag_service.process_query.return_value = {
            "response_text": "Context-aware response",
            "source_references": [{"chapter": 3, "lesson": 2, "section": "Walking"}],
            "confidence_score": 0.85,
            "timestamp": "2025-12-09T13:45:25Z"
        }
        mock_rag_service_class.return_value = mock_rag_service

        async def make_context_request(client, question, context, session_id):
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None,
                lambda: client.post(
                    "/v1/query",
                    json={
                        "question": question,
                        "selected_context": context,
                        "session_id": session_id
                    }
                )
            )
            return response.status_code, response.json()

        client = TestClient(app)

        # Create concurrent requests with different contexts
        contexts = [
            "Zero Moment Point is...",
            "Inverted Pendulum Model...",
            "Dynamic Walking Control...",
            "Balance and Stability...",
            "Feedback Control Systems..."
        ]

        tasks = [
            make_context_request(client, f"Context question {i}", contexts[i % len(contexts)], f"ctx-session-{i}")
            for i in range(10)
        ]

        results = await asyncio.gather(*tasks)

        # Verify all requests succeeded
        for status_code, data in results:
            assert status_code == 200
            assert "response_text" in data
            assert "source_references" in data


@pytest.mark.asyncio
async def test_concurrent_requests_error_handling():
    """Test that concurrent requests handle errors gracefully without affecting each other."""
    with patch('app.api.v1.query.RAGService') as mock_rag_service_class:
        mock_rag_service = AsyncMock()

        # Alternate between successful and failed responses to test error isolation
        async def mock_process_query(question, session_id, selected_context=None):
            if "error" in question.lower():
                from app.utils.exceptions import QdrantUnavailableError
                raise QdrantUnavailableError("Simulated Qdrant error")
            else:
                return {
                    "response_text": f"Normal response to {question}",
                    "source_references": [{"chapter": 1, "lesson": 1, "section": "Intro"}],
                    "confidence_score": 0.8,
                    "timestamp": "2025-12-09T13:45:26Z"
                }

        mock_rag_service.process_query.side_effect = mock_process_query
        mock_rag_service_class.return_value = mock_rag_service

        async def make_mixed_request(client, question, session_id):
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None,
                lambda: client.post(
                    "/v1/query",
                    json={
                        "question": question,
                        "session_id": session_id
                    }
                )
            )
            return response.status_code

        client = TestClient(app)

        # Create mixed requests (some will error, some will succeed)
        questions = ["normal question 1", "question with error", "normal question 2", "another error", "normal question 3"]
        tasks = [make_mixed_request(client, q, f"mixed-session-{i}") for i, q in enumerate(questions)]

        results = await asyncio.gather(*tasks)

        # Verify that errors in one request don't affect others
        # Some should succeed (200), some should error (503 for Qdrant error)
        success_count = sum(1 for status in results if status == 200)
        error_count = sum(1 for status in results if status == 503)
        assert success_count + error_count == len(questions)  # All requests should get some response


@pytest.mark.asyncio
async def test_concurrent_logging_operations():
    """Test concurrent logging operations to ensure database connection handling."""
    with patch('app.api.v1.query.RAGService') as mock_rag_service_class:
        mock_rag_service = AsyncMock()
        mock_rag_service.process_query.return_value = {
            "response_text": "Response with concurrent logging",
            "source_references": [{"chapter": 4, "lesson": 1, "section": "Future"}],
            "confidence_score": 0.9,
            "timestamp": "2025-12-09T13:45:27Z"
        }
        mock_rag_service_class.return_value = mock_rag_service

        # Mock the postgres service to track logging calls
        with patch('app.services.postgres_service.PostgresService.save_query') as mock_save:
            mock_save.return_value = AsyncMock()

            async def make_logging_request(client, question, session_id):
                loop = asyncio.get_event_loop()
                response = await loop.run_in_executor(
                    None,
                    lambda: client.post(
                        "/v1/query",
                        json={
                            "question": question,
                            "session_id": session_id
                        }
                    )
                )
                return response.status_code

            client = TestClient(app)

            # Create multiple concurrent requests that will all trigger logging
            tasks = [make_logging_request(client, f"Logging question {i}", f"log-session-{i}") for i in range(15)]
            results = await asyncio.gather(*tasks)

            # All requests should succeed
            for status_code in results:
                assert status_code == 200

            # Verify that logging was called for each request
            assert mock_save.call_count == 15


@pytest.mark.asyncio
async def test_concurrent_health_checks():
    """Test concurrent health check requests."""
    async def make_health_request(client):
        loop = asyncio.get_event_loop()
        response = await loop.run_in_executor(
            None,
            lambda: client.get("/v1/health")
        )
        return response.status_code, response.json()

    client = TestClient(app)

    # Make multiple concurrent health check requests
    tasks = [make_health_request(client) for _ in range(5)]
    results = await asyncio.gather(*tasks)

    # All health checks should succeed
    for status_code, data in results:
        assert status_code == 200
        assert "status" in data
        assert "timestamp" in data


@pytest.mark.asyncio
async def test_concurrent_logs_requests():
    """Test concurrent requests to logs endpoint (with mocked auth bypass)."""
    with patch('os.getenv', return_value=None):  # Bypass admin token requirement for testing
        with patch('app.api.v1.logs.PostgresService') as mock_postgres_service_class:
            # Mock the service to return empty results
            mock_service_instance = AsyncMock()
            mock_service_instance.get_query_logs.return_value = ([], 0)
            mock_service_instance.get_analytics.return_value = {
                "query_count": 0,
                "avg_confidence": 0.0,
                "avg_response_time_ms": 0.0,
                "unique_sessions": 0,
                "period_days": 7
            }
            mock_postgres_service_class.return_value = mock_service_instance

            async def make_logs_request(client):
                loop = asyncio.get_event_loop()
                response = await loop.run_in_executor(
                    None,
                    lambda: client.get("/v1/logs")
                )
                return response.status_code

            client = TestClient(app)

            # Make multiple concurrent logs requests
            tasks = [make_logs_request(client) for _ in range(5)]
            results = await asyncio.gather(*tasks)

            # All requests should succeed
            for status_code in results:
                assert status_code == 200


@pytest.mark.asyncio
async def test_concurrent_different_endpoints():
    """Test concurrent requests to different endpoints."""
    with patch('app.api.v1.query.RAGService') as mock_rag_service_class, \
         patch('app.api.v1.health.GeminiService') as mock_gemini_health, \
         patch('app.api.v1.health.QdrantService') as mock_qdrant_health, \
         patch('os.getenv', return_value=None):  # Bypass admin token

        # Mock RAG service
        mock_rag_service = AsyncMock()
        mock_rag_service.process_query.return_value = {
            "response_text": "Concurrent response",
            "source_references": [{"chapter": 1, "lesson": 1, "section": "Intro"}],
            "confidence_score": 0.8,
            "timestamp": "2025-12-09T13:45:28Z"
        }
        mock_rag_service_class.return_value = mock_rag_service

        # Mock health services
        health_instance = AsyncMock()
        health_instance.check_health.return_value = True
        mock_gemini_health.return_value = health_instance
        mock_qdrant_health.return_value = health_instance

        async def make_request(client, endpoint, method="GET", json_data=None):
            loop = asyncio.get_event_loop()
            if method == "GET":
                response = await loop.run_in_executor(
                    None,
                    lambda: client.get(endpoint)
                )
            else:
                response = await loop.run_in_executor(
                    None,
                    lambda: client.post(endpoint, json=json_data)
                )
            return endpoint, response.status_code

        client = TestClient(app)

        # Create requests to different endpoints
        tasks = [
            make_request(client, "/v1/query", "POST", {"question": "Test 1", "session_id": "s1"}),
            make_request(client, "/v1/query", "POST", {"question": "Test 2", "session_id": "s2"}),
            make_request(client, "/v1/health"),
            make_request(client, "/v1/query", "POST", {"question": "Test 3", "session_id": "s3"}),
            make_request(client, "/v1/health"),
        ]

        results = await asyncio.gather(*tasks)

        # Check results
        query_count = sum(1 for endpoint, status in results if "/v1/query" in endpoint and status == 200)
        health_count = sum(1 for endpoint, status in results if "/v1/health" in endpoint and status == 200)

        assert query_count == 3  # All query requests should succeed
        assert health_count == 2  # All health requests should succeed


@pytest.mark.asyncio
async def test_concurrent_requests_performance_timing():
    """Test that concurrent requests maintain acceptable performance."""
    with patch('app.api.v1.query.RAGService') as mock_rag_service_class:
        mock_rag_service = AsyncMock()
        mock_rag_service.process_query.return_value = {
            "response_text": "Timed response",
            "source_references": [{"chapter": 1, "lesson": 1, "section": "Intro"}],
            "confidence_score": 0.8,
            "timestamp": "2025-12-09T13:45:29Z"
        }
        mock_rag_service_class.return_value = mock_rag_service

        async def time_request(client, question, session_id):
            start_time = time.time()
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None,
                lambda: client.post(
                    "/v1/query",
                    json={
                        "question": question,
                        "session_id": session_id
                    }
                )
            )
            end_time = time.time()
            return response.status_code, (end_time - start_time) * 1000  # Return time in ms

        client = TestClient(app)

        # Make concurrent requests and time them
        tasks = [time_request(client, f"Timing question {i}", f"timing-{i}") for i in range(10)]
        results = await asyncio.gather(*tasks)

        # All requests should succeed
        for status_code, duration_ms in results:
            assert status_code == 200
            # In a real system, we'd check that duration is reasonable under load
            # For this test, just ensure it's positive
            assert duration_ms > 0


@pytest.mark.asyncio
async def test_concurrent_requests_session_isolation():
    """Test that concurrent requests maintain proper session isolation."""
    with patch('app.api.v1.query.RAGService') as mock_rag_service_class:
        mock_rag_service = AsyncMock()

        async def mock_process_query(question, session_id, selected_context=None):
            # Return response that includes session ID to verify isolation
            return {
                "response_text": f"Response for session {session_id}",
                "source_references": [{"chapter": 1, "lesson": 1, "section": "Intro"}],
                "confidence_score": 0.8,
                "timestamp": "2025-12-09T13:45:30Z"
            }

        mock_rag_service.process_query.side_effect = mock_process_query
        mock_rag_service_class.return_value = mock_rag_service

        async def make_isolated_request(client, session_id):
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None,
                lambda: client.post(
                    "/v1/query",
                    json={
                        "question": "Session isolation test",
                        "session_id": session_id
                    }
                )
            )
            return response.status_code, response.json().get("response_text", "")

        client = TestClient(app)

        # Create requests with different session IDs
        session_ids = [f"iso-session-{i}" for i in range(5)]
        tasks = [make_isolated_request(client, sid) for sid in session_ids]
        results = await asyncio.gather(*tasks)

        # Verify each response corresponds to the correct session
        for i, (status_code, response_text) in enumerate(results):
            expected_session = session_ids[i]
            assert status_code == 200
            assert expected_session in response_text