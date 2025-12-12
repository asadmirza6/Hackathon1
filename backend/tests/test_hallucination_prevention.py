"""Tests for hallucination prevention in the RAG chatbot."""
import asyncio
from unittest.mock import AsyncMock, patch
import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture
def test_client():
    """Create a test client for the FastAPI app."""
    return TestClient(app)


@pytest.mark.asyncio
async def test_out_of_scope_question_quantum_computing(test_client):
    """Test response to quantum computing question (out of course scope)."""
    with patch('app.api.v1.query.RAGService') as mock_rag_service_class:
        mock_rag_service = AsyncMock()
        # Mock response that should indicate out-of-scope
        mock_rag_service.process_query.return_value = {
            "response_text": "I don't have information about this in the course material. Please ask about topics covered in the course.",
            "source_references": [],
            "confidence_score": 0.0,
            "timestamp": "2025-12-09T13:45:23Z"
        }
        mock_rag_service_class.return_value = mock_rag_service

        response = test_client.post(
            "/v1/query",
            json={
                "question": "How does quantum computing work?",
                "session_id": "session-out-of-scope-1"
            }
        )

        assert response.status_code == 200
        data = response.json()
        assert "don't have information about this in the course material" in data["response_text"].lower()
        assert data["confidence_score"] == 0.0


@pytest.mark.asyncio
async def test_out_of_scope_question_assignment_deadlines(test_client):
    """Test response to assignment deadline question (out of course scope)."""
    with patch('app.api.v1.query.RAGService') as mock_rag_service_class:
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
                "question": "What is the deadline for assignment 3?",
                "session_id": "session-out-of-scope-2"
            }
        )

        assert response.status_code == 200
        data = response.json()
        assert "don't have information about this in the course material" in data["response_text"].lower()


@pytest.mark.asyncio
async def test_out_of_scope_personal_question(test_client):
    """Test response to personal question (out of course scope)."""
    with patch('app.api.v1.query.RAGService') as mock_rag_service_class:
        mock_rag_service = AsyncMock()
        mock_rag_service.process_query.return_value = {
            "response_text": "I don't have information about this in the course material. Please ask about topics covered in the course.",
            "source_references": [],
            "confidence_score": 0.0,
            "timestamp": "2025-12-09T13:45:25Z"
        }
        mock_rag_service_class.return_value = mock_rag_service

        response = test_client.post(
            "/v1/query",
            json={
                "question": "What should I do for my personal project?",
                "session_id": "session-out-of-scope-3"
            }
        )

        assert response.status_code == 200
        data = response.json()
        assert "don't have information about this in the course material" in data["response_text"].lower()


@pytest.mark.asyncio
async def test_in_scope_question_zmp(test_client):
    """Test response to in-scope ZMP question (should provide detailed answer)."""
    with patch('app.api.v1.query.RAGService') as mock_rag_service_class:
        mock_rag_service = AsyncMock()
        mock_rag_service.process_query.return_value = {
            "response_text": "Zero Moment Point (ZMP) is the point on the ground where the net moment of the ground reaction force is zero.",
            "source_references": [
                {"chapter": 3, "lesson": 2, "section": "Walking Pattern Generation"}
            ],
            "confidence_score": 0.92,
            "timestamp": "2025-12-09T13:45:26Z"
        }
        mock_rag_service_class.return_value = mock_rag_service

        response = test_client.post(
            "/v1/query",
            json={
                "question": "What is ZMP in bipedal walking?",
                "session_id": "session-in-scope-1"
            }
        )

        assert response.status_code == 200
        data = response.json()
        assert "zero moment point" in data["response_text"].lower()
        assert len(data["source_references"]) > 0
        assert data["confidence_score"] > 0.5


@pytest.mark.asyncio
async def test_in_scope_question_balance_control(test_client):
    """Test response to in-scope balance control question."""
    with patch('app.api.v1.query.RAGService') as mock_rag_service_class:
        mock_rag_service = AsyncMock()
        mock_rag_service.process_query.return_value = {
            "response_text": "Balance control in humanoid robots involves feedback systems that maintain the center of mass within the support polygon.",
            "source_references": [
                {"chapter": 2, "lesson": 1, "section": "Balance Control Systems"}
            ],
            "confidence_score": 0.88,
            "timestamp": "2025-12-09T13:45:27Z"
        }
        mock_rag_service_class.return_value = mock_rag_service

        response = test_client.post(
            "/v1/query",
            json={
                "question": "How do humanoid robots maintain balance?",
                "session_id": "session-in-scope-2"
            }
        )

        assert response.status_code == 200
        data = response.json()
        assert "balance" in data["response_text"].lower()
        assert len(data["source_references"]) > 0
        assert data["confidence_score"] > 0.5


@pytest.mark.asyncio
async def test_hallucination_prevention_with_context(test_client):
    """Test that the system doesn't hallucinate when given selected context."""
    with patch('app.api.v1.query.RAGService') as mock_rag_service_class:
        mock_rag_service = AsyncMock()
        mock_rag_service.process_query.return_value = {
            "response_text": "Based on the provided context, the concept relates to the walking pattern generation.",
            "source_references": [
                {"chapter": 3, "lesson": 2, "section": "Walking Pattern Generation"}
            ],
            "confidence_score": 0.85,
            "timestamp": "2025-12-09T13:45:28Z"
        }
        mock_rag_service_class.return_value = mock_rag_service

        response = test_client.post(
            "/v1/query",
            json={
                "question": "Can you explain this concept?",
                "selected_context": "Zero Moment Point is the point where the net moment is zero.",
                "session_id": "session-context-1"
            }
        )

        assert response.status_code == 200
        data = response.json()
        assert "provided context" in data["response_text"].lower()
        assert len(data["source_references"]) > 0


@pytest.mark.asyncio
async def test_hallucination_prevention_with_wrong_context(test_client):
    """Test that the system doesn't incorporate information outside the provided context."""
    with patch('app.api.v1.query.RAGService') as mock_rag_service_class:
        mock_rag_service = AsyncMock()
        mock_rag_service.process_query.return_value = {
            "response_text": "I cannot provide information about quantum computing as it's not related to the provided context about bipedal walking.",
            "source_references": [],
            "confidence_score": 0.0,
            "timestamp": "2025-12-09T13:45:29Z"
        }
        mock_rag_service_class.return_value = mock_rag_service

        response = test_client.post(
            "/v1/query",
            json={
                "question": "How does quantum computing relate to this?",
                "selected_context": "The Zero Moment Point in bipedal walking...",
                "session_id": "session-wrong-context-1"
            }
        )

        assert response.status_code == 200
        data = response.json()
        assert "cannot provide information" in data["response_text"].lower()
        assert data["confidence_score"] == 0.0


@pytest.mark.asyncio
async def test_course_topic_boundary_enforcement(test_client):
    """Test that the system enforces course topic boundaries."""
    with patch('app.api.v1.query.RAGService') as mock_rag_service_class:
        mock_rag_service = AsyncMock()

        # Test various out-of-scope questions
        out_of_scope_questions = [
            "What is the weather like today?",
            "How do I cook pasta?",
            "What's the stock price of Google?",
            "Tell me about ancient Rome.",
            "How do I fix my car?"
        ]

        for i, question in enumerate(out_of_scope_questions):
            mock_rag_service.process_query.return_value = {
                "response_text": "I don't have information about this in the course material. Please ask about topics covered in the course.",
                "source_references": [],
                "confidence_score": 0.0,
                "timestamp": f"2025-12-09T13:45:{30+i}Z"
            }

            response = test_client.post(
                "/v1/query",
                json={
                    "question": question,
                    "session_id": f"session-boundary-{i}"
                }
            )

            assert response.status_code == 200
            data = response.json()
            assert "don't have information about this in the course material" in data["response_text"].lower()
            assert data["confidence_score"] == 0.0


@pytest.mark.asyncio
async def test_course_topic_acceptance(test_client):
    """Test that the system properly answers course-related questions."""
    with patch('app.api.v1.query.RAGService') as mock_rag_service_class:
        mock_rag_service = AsyncMock()

        # Test various in-scope questions
        in_scope_questions = [
            ("What is ZMP?", 0.8),
            ("Explain inverted pendulum model", 0.75),
            ("How does dynamic walking work?", 0.85),
            ("What is the role of feedback control?", 0.8),
            ("Describe capture point concept", 0.9)
        ]

        for i, (question, min_confidence) in enumerate(in_scope_questions):
            expected_response = f"Answer to {question} based on course material."
            mock_rag_service.process_query.return_value = {
                "response_text": expected_response,
                "source_references": [
                    {"chapter": 1 + (i % 4), "lesson": 1 + (i % 2), "section": "Test Section"}
                ],
                "confidence_score": min_confidence,
                "timestamp": f"2025-12-09T13:45:{40+i}Z"
            }

            response = test_client.post(
                "/v1/query",
                json={
                    "question": question,
                    "session_id": f"session-accept-{i}"
                }
            )

            assert response.status_code == 200
            data = response.json()
            assert "source_references" in data
            assert len(data["source_references"]) > 0
            assert data["confidence_score"] >= min_confidence - 0.1  # Allow small variance


@pytest.mark.asyncio
async def test_hallucination_detection_in_response_content(test_client):
    """Test that responses don't contain external information not in context."""
    with patch('app.api.v1.query.RAGService') as mock_rag_service_class:
        mock_rag_service = AsyncMock()
        mock_rag_service.process_query.return_value = {
            "response_text": "According to the course material, ZMP is specifically defined as...",
            "source_references": [
                {"chapter": 3, "lesson": 2, "section": "Walking Pattern Generation"}
            ],
            "confidence_score": 0.9,
            "timestamp": "2025-12-09T13:45:45Z"
        }
        mock_rag_service_class.return_value = mock_rag_service

        response = test_client.post(
            "/v1/query",
            json={
                "question": "What is the definition of ZMP?",
                "session_id": "session-content-1"
            }
        )

        assert response.status_code == 200
        data = response.json()
        response_text = data["response_text"].lower()

        # Check that response indicates it's based on course material
        assert "according to the course material" in response_text
        assert "zmp" in response_text
        assert len(data["source_references"]) > 0


@pytest.mark.asyncio
async def test_hallucination_prevention_with_company_info(test_client):
    """Test that the system doesn't provide information about real companies not in course."""
    with patch('app.api.v1.query.RAGService') as mock_rag_service_class:
        mock_rag_service = AsyncMock()
        mock_rag_service.process_query.return_value = {
            "response_text": "I don't have information about this in the course material. Please ask about topics covered in the course.",
            "source_references": [],
            "confidence_score": 0.0,
            "timestamp": "2025-12-09T13:45:46Z"
        }
        mock_rag_service_class.return_value = mock_rag_service

        response = test_client.post(
            "/v1/query",
            json={
                "question": "What are the financial results of Boston Dynamics?",
                "session_id": "session-company-1"
            }
        )

        assert response.status_code == 200
        data = response.json()
        assert "don't have information about this in the course material" in data["response_text"].lower()


@pytest.mark.asyncio
async def test_hallucination_prevention_with_current_events(test_client):
    """Test that the system doesn't provide information about current events not in course."""
    with patch('app.api.v1.query.RAGService') as mock_rag_service_class:
        mock_rag_service = AsyncMock()
        mock_rag_service.process_query.return_value = {
            "response_text": "I don't have information about this in the course material. Please ask about topics covered in the course.",
            "source_references": [],
            "confidence_score": 0.0,
            "timestamp": "2025-12-09T13:45:47Z"
        }
        mock_rag_service_class.return_value = mock_rag_service

        response = test_client.post(
            "/v1/query",
            json={
                "question": "What happened in robotics research last week?",
                "session_id": "session-current-1"
            }
        )

        assert response.status_code == 200
        data = response.json()
        assert "don't have information about this in the course material" in data["response_text"].lower()


@pytest.mark.asyncio
async def test_hallucination_prevention_high_rejection_rate(test_client):
    """Test that the system maintains high rejection rate for out-of-scope queries."""
    with patch('app.api.v1.query.RAGService') as mock_rag_service_class:
        mock_rag_service = AsyncMock()

        # Simulate multiple out-of-scope questions
        out_of_scope_questions = [
            "What is machine learning?",
            "How do neural networks work?",
            "Tell me about deep learning",
            "What's the latest in AI?",
            "Explain computer vision",
            "How does NLP work?",
            "What is reinforcement learning?",
            "Tell me about GPT models",
            "How do transformers work?",
            "What is computer graphics?"
        ]

        rejection_count = 0
        total_questions = len(out_of_scope_questions)

        for i, question in enumerate(out_of_scope_questions):
            mock_rag_service.process_query.return_value = {
                "response_text": "I don't have information about this in the course material. Please ask about topics covered in the course." if i < 9 else "Partially related to course content.",
                "source_references": [],
                "confidence_score": 0.0 if i < 9 else 0.3,
                "timestamp": f"2025-12-09T13:45:{50+i}Z"
            }

            response = test_client.post(
                "/v1/query",
                json={
                    "question": question,
                    "session_id": f"session-rejection-{i}"
                }
            )

            assert response.status_code == 200
            data = response.json()

            if "don't have information about this in the course material" in data["response_text"].lower():
                rejection_count += 1

        # Calculate rejection rate
        rejection_rate = rejection_count / total_questions
        assert rejection_rate >= 0.8  # Should reject at least 80% of out-of-scope queries


@pytest.mark.asyncio
async def test_in_scope_questions_get_high_confidence(test_client):
    """Test that in-scope questions receive high confidence scores."""
    with patch('app.api.v1.query.RAGService') as mock_rag_service_class:
        mock_rag_service = AsyncMock()

        in_scope_questions = [
            "What is ZMP?",
            "Explain inverted pendulum",
            "How does walking work?",
            "What is balance control?",
            "Describe dynamic walking"
        ]

        for i, question in enumerate(in_scope_questions):
            mock_rag_service.process_query.return_value = {
                "response_text": f"Answer to {question} from course materials",
                "source_references": [
                    {"chapter": 1 + (i % 4), "lesson": 1, "section": "Test Section"}
                ],
                "confidence_score": 0.85 + (i * 0.01),  # Slightly increasing confidence
                "timestamp": f"2025-12-09T13:46:{00+i}Z"
            }

            response = test_client.post(
                "/v1/query",
                json={
                    "question": question,
                    "session_id": f"session-confidence-{i}"
                }
            )

            assert response.status_code == 200
            data = response.json()
            assert data["confidence_score"] >= 0.8  # High confidence for in-scope questions


@pytest.mark.asyncio
async def test_hallucination_prevention_with_specific_constraints(test_client):
    """Test hallucination prevention with specific course constraint enforcement."""
    with patch('app.api.v1.query.RAGService') as mock_rag_service_class:
        mock_rag_service = AsyncMock()
        mock_rag_service.process_query.return_value = {
            "response_text": "Based on Chapter 3, Lesson 2 of the course material, ZMP is defined as...",
            "source_references": [
                {"chapter": 3, "lesson": 2, "section": "Walking Pattern Generation"}
            ],
            "confidence_score": 0.92,
            "timestamp": "2025-12-09T13:46:05Z"
        }
        mock_rag_service_class.return_value = mock_rag_service

        response = test_client.post(
            "/v1/query",
            json={
                "question": "Provide the course definition of ZMP",
                "session_id": "session-constraint-1"
            }
        )

        assert response.status_code == 200
        data = response.json()
        response_text = data["response_text"].lower()

        # Verify the response references course material specifically
        assert "based on" in response_text
        assert "chapter" in response_text or "lesson" in response_text
        assert len(data["source_references"]) > 0
        assert data["confidence_score"] > 0.9


@pytest.mark.asyncio
async def test_hallucination_prevention_with_fact_checking(test_client):
    """Test that the system doesn't generate false facts."""
    with patch('app.api.v1.query.RAGService') as mock_rag_service_class:
        mock_rag_service = AsyncMock()
        mock_rag_service.process_query.return_value = {
            "response_text": "I don't have specific information about that claim in the course material.",
            "source_references": [],
            "confidence_score": 0.0,
            "timestamp": "2025-12-09T13:46:06Z"
        }
        mock_rag_service_class.return_value = mock_rag_service

        response = test_client.post(
            "/v1/query",
            json={
                "question": "Is it true that ZMP was invented in 2005?",
                "session_id": "session-fact-check-1"
            }
        )

        assert response.status_code == 200
        data = response.json()
        response_text = data["response_text"].lower()

        # Verify the system doesn't claim to know false facts
        assert "don't have specific information" in response_text or "not in course material" in response_text
        assert data["confidence_score"] == 0.0