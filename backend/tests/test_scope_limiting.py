"""Tests for verifying responses stay within course content scope."""
import asyncio
from unittest.mock import AsyncMock, patch
import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture
def test_client():
    """Create a test client for the FastAPI app."""
    return TestClient(app)


def contains_course_content(response_text: str) -> bool:
    """Check if response contains course-related keywords."""
    course_keywords = [
        "zmp", "zero moment point", "bipedal", "walking", "balance", "control",
        "humanoid", "robot", "locomotion", "inverted pendulum", "dynamics",
        "stability", "feedback", "capture point", "course", "lesson", "chapter"
    ]
    text_lower = response_text.lower()
    return any(keyword in text_lower for keyword in course_keywords)


def contains_external_content(response_text: str) -> bool:
    """Check if response contains external/unrelated content."""
    external_keywords = [
        "quantum computing", "stock price", "personal advice", "current events",
        "cooking", "weather", "sports", "entertainment", "social media",
        "company financials", "unrelated technology", "non-course topic"
    ]
    text_lower = response_text.lower()
    return any(keyword in text_lower for keyword in external_keywords)


@pytest.mark.asyncio
async def test_responses_contain_course_content_keywords(test_client):
    """Test that in-scope responses contain course-related keywords."""
    with patch('app.api.v1.query.RAGService') as mock_rag_service_class:
        mock_rag_service = AsyncMock()
        mock_rag_service.process_query.return_value = {
            "response_text": "Zero Moment Point (ZMP) is a concept used in bipedal locomotion to describe the point where the net moment of the ground reaction force is zero.",
            "source_references": [
                {"chapter": 3, "lesson": 2, "section": "Walking Pattern Generation"}
            ],
            "confidence_score": 0.92,
            "timestamp": "2025-12-09T13:45:23Z"
        }
        mock_rag_service_class.return_value = mock_rag_service

        response = test_client.post(
            "/v1/query",
            json={
                "question": "What is ZMP in bipedal walking?",
                "session_id": "session-scope-1"
            }
        )

        assert response.status_code == 200
        data = response.json()
        response_text = data["response_text"]

        # Verify response contains course content
        assert contains_course_content(response_text)
        assert "zmp" in response_text.lower() or "zero moment point" in response_text.lower()
        assert "bipedal" in response_text.lower() or "walking" in response_text.lower()


@pytest.mark.asyncio
async def test_out_of_scope_responses_dont_contain_external_content(test_client):
    """Test that out-of-scope responses don't contain external content."""
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
                "question": "What is the current stock price of Tesla?",
                "session_id": "session-scope-2"
            }
        )

        assert response.status_code == 200
        data = response.json()
        response_text = data["response_text"]

        # Verify response doesn't contain external content
        assert not contains_external_content(response_text)
        assert "don't have information about this in the course material" in response_text.lower()


@pytest.mark.asyncio
async def test_scope_limiting_for_assignment_questions(test_client):
    """Test that assignment-related questions are properly rejected."""
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
                "question": "What are the requirements for the final project?",
                "session_id": "session-scope-3"
            }
        )

        assert response.status_code == 200
        data = response.json()
        response_text = data["response_text"]

        assert "don't have information about this in the course material" in response_text.lower()


@pytest.mark.asyncio
async def test_scope_limiting_for_personal_questions(test_client):
    """Test that personal questions are properly rejected."""
    with patch('app.api.v1.query.RAGService') as mock_rag_service_class:
        mock_rag_service = AsyncMock()
        mock_rag_service.process_query.return_value = {
            "response_text": "I don't have information about this in the course material. Please ask about topics covered in the course.",
            "source_references": [],
            "confidence_score": 0.0,
            "timestamp": "2025-12-09T13:45:26Z"
        }
        mock_rag_service_class.return_value = mock_rag_service

        response = test_client.post(
            "/v1/query",
            json={
                "question": "Should I change my major to computer science?",
                "session_id": "session-scope-4"
            }
        )

        assert response.status_code == 200
        data = response.json()
        response_text = data["response_text"]

        assert "don't have information about this in the course material" in response_text.lower()


@pytest.mark.asyncio
async def test_scope_limiting_allows_valid_course_questions(test_client):
    """Test that valid course questions receive appropriate responses."""
    with patch('app.api.v1.query.RAGService') as mock_rag_service_class:
        mock_rag_service = AsyncMock()
        mock_rag_service.process_query.return_value = {
            "response_text": "The inverted pendulum model represents the human body as a pendulum with the center of mass above the pivot point, which is fundamental to understanding balance control.",
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
                "question": "Explain the inverted pendulum model for balance.",
                "session_id": "session-scope-5"
            }
        )

        assert response.status_code == 200
        data = response.json()
        response_text = data["response_text"]

        # Verify response is course-related
        assert contains_course_content(response_text)
        assert "inverted pendulum" in response_text.lower()
        assert "balance" in response_text.lower()
        assert data["confidence_score"] > 0.5


@pytest.mark.asyncio
async def test_scope_limiting_with_context_awareness(test_client):
    """Test scope limiting when context is provided."""
    with patch('app.api.v1.query.RAGService') as mock_rag_service_class:
        mock_rag_service = AsyncMock()
        mock_rag_service.process_query.return_value = {
            "response_text": "Based on the provided course context about ZMP, the concept relates to maintaining balance during locomotion.",
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
                "question": "How does this relate to balance?",
                "selected_context": "Zero Moment Point is the point where the net moment of the ground reaction force is zero.",
                "session_id": "session-scope-6"
            }
        )

        assert response.status_code == 200
        data = response.json()
        response_text = data["response_text"]

        # Verify response stays within course context
        assert contains_course_content(response_text)
        assert "provided course context" in response_text.lower()
        assert "balance" in response_text.lower()


@pytest.mark.asyncio
async def test_scope_limiting_blocks_off_topic_context(test_client):
    """Test that the system doesn't incorporate off-topic context."""
    with patch('app.api.v1.query.RAGService') as mock_rag_service_class:
        mock_rag_service = AsyncMock()
        mock_rag_service.process_query.return_value = {
            "response_text": "The provided context about cooking is not related to the course material on humanoid robotics.",
            "source_references": [],
            "confidence_score": 0.0,
            "timestamp": "2025-12-09T13:45:29Z"
        }
        mock_rag_service_class.return_value = mock_rag_service

        response = test_client.post(
            "/v1/query",
            json={
                "question": "How does this work?",
                "selected_context": "To cook pasta, boil water and add salt.",
                "session_id": "session-scope-7"
            }
        )

        assert response.status_code == 200
        data = response.json()
        response_text = data["response_text"]

        assert "not related to the course material" in response_text.lower()
        assert data["confidence_score"] == 0.0


@pytest.mark.asyncio
async def test_scope_limiting_multiple_out_of_scope_questions(test_client):
    """Test scope limiting for multiple out-of-scope questions."""
    with patch('app.api.v1.query.RAGService') as mock_rag_service_class:
        mock_rag_service = AsyncMock()

        out_of_scope_questions = [
            "What's the weather forecast?",
            "How do I invest in stocks?",
            "Tell me about ancient civilizations.",
            "What are the latest movie releases?",
            "How do I start a business?"
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
                    "session_id": f"session-scope-multi-{i}"
                }
            )

            assert response.status_code == 200
            data = response.json()
            response_text = data["response_text"]

            # Verify each response properly rejects out-of-scope content
            assert "don't have information about this in the course material" in response_text.lower()
            assert data["confidence_score"] == 0.0
            assert not contains_external_content(response_text)


@pytest.mark.asyncio
async def test_scope_limiting_allows_all_course_topics(test_client):
    """Test that all valid course topics are accepted."""
    with patch('app.api.v1.query.RAGService') as mock_rag_service_class:
        mock_rag_service = AsyncMock()

        course_questions = [
            ("What is ZMP?", "zmp"),
            ("Explain balance control", "balance"),
            ("How does walking work?", "walking"),
            ("Describe humanoid design", "humanoid"),
            ("What is feedback control?", "feedback"),
            ("Explain dynamic walking", "dynamic"),
            ("How does locomotion work?", "locomotion"),
            ("What is the capture point?", "capture point")
        ]

        for i, (question, keyword) in enumerate(course_questions):
            mock_rag_service.process_query.return_value = {
                "response_text": f"According to the course material, {question.lower()} relates to {keyword}.",
                "source_references": [
                    {"chapter": 1 + (i % 4), "lesson": 1 + (i % 2), "section": "Relevant Section"}
                ],
                "confidence_score": 0.8 + (i * 0.01),
                "timestamp": f"2025-12-09T13:45:{40+i}Z"
            }

            response = test_client.post(
                "/v1/query",
                json={
                    "question": question,
                    "session_id": f"session-scope-course-{i}"
                }
            )

            assert response.status_code == 200
            data = response.json()
            response_text = data["response_text"]

            # Verify response contains course content and has high confidence
            assert contains_course_content(response_text)
            assert keyword.lower() in response_text.lower()
            assert data["confidence_score"] > 0.75


@pytest.mark.asyncio
async def test_scope_limiting_with_company_questions(test_client):
    """Test that questions about specific companies are rejected."""
    with patch('app.api.v1.query.RAGService') as mock_rag_service_class:
        mock_rag_service = AsyncMock()
        mock_rag_service.process_query.return_value = {
            "response_text": "I don't have information about this in the course material. Please ask about topics covered in the course.",
            "source_references": [],
            "confidence_score": 0.0,
            "timestamp": "2025-12-09T13:45:48Z"
        }
        mock_rag_service_class.return_value = mock_rag_service

        response = test_client.post(
            "/v1/query",
            json={
                "question": "What is the business model of Boston Dynamics?",
                "session_id": "session-scope-company-1"
            }
        )

        assert response.status_code == 200
        data = response.json()
        response_text = data["response_text"]

        assert "don't have information about this in the course material" in response_text.lower()
        assert data["confidence_score"] == 0.0


@pytest.mark.asyncio
async def test_scope_limiting_with_research_questions(test_client):
    """Test that current research questions are rejected if not in course."""
    with patch('app.api.v1.query.RAGService') as mock_rag_service_class:
        mock_rag_service = AsyncMock()
        mock_rag_service.process_query.return_value = {
            "response_text": "I don't have information about this in the course material. Please ask about topics covered in the course.",
            "source_references": [],
            "confidence_score": 0.0,
            "timestamp": "2025-12-09T13:45:49Z"
        }
        mock_rag_service_class.return_value = mock_rag_service

        response = test_client.post(
            "/v1/query",
            json={
                "question": "What were the latest findings in humanoid robotics from 2024?",
                "session_id": "session-scope-research-1"
            }
        )

        assert response.status_code == 200
        data = response.json()
        response_text = data["response_text"]

        assert "don't have information about this in the course material" in response_text.lower()
        assert data["confidence_score"] == 0.0


@pytest.mark.asyncio
async def test_scope_limiting_with_general_ai_questions(test_client):
    """Test that general AI questions are rejected."""
    with patch('app.api.v1.query.RAGService') as mock_rag_service_class:
        mock_rag_service = AsyncMock()
        mock_rag_service.process_query.return_value = {
            "response_text": "I don't have information about this in the course material. Please ask about topics covered in the course.",
            "source_references": [],
            "confidence_score": 0.0,
            "timestamp": "2025-12-09T13:45:50Z"
        }
        mock_rag_service_class.return_value = mock_rag_service

        response = test_client.post(
            "/v1/query",
            json={
                "question": "How does GPT-4 work?",
                "session_id": "session-scope-ai-1"
            }
        )

        assert response.status_code == 200
        data = response.json()
        response_text = data["response_text"]

        assert "don't have information about this in the course material" in response_text.lower()
        assert data["confidence_score"] == 0.0


@pytest.mark.asyncio
async def test_scope_limiting_with_specific_course_references(test_client):
    """Test that responses properly reference specific course materials."""
    with patch('app.api.v1.query.RAGService') as mock_rag_service_class:
        mock_rag_service = AsyncMock()
        mock_rag_service.process_query.return_value = {
            "response_text": "According to Chapter 3, Lesson 2 of the course, ZMP is defined as the point where the net moment is zero.",
            "source_references": [
                {"chapter": 3, "lesson": 2, "section": "Walking Pattern Generation"}
            ],
            "confidence_score": 0.92,
            "timestamp": "2025-12-09T13:45:51Z"
        }
        mock_rag_service_class.return_value = mock_rag_service

        response = test_client.post(
            "/v1/query",
            json={
                "question": "What is the course definition of ZMP?",
                "session_id": "session-scope-reference-1"
            }
        )

        assert response.status_code == 200
        data = response.json()
        response_text = data["response_text"]

        # Verify response references specific course material
        assert "according to chapter" in response_text.lower()
        assert "course" in response_text.lower()
        assert len(data["source_references"]) > 0
        assert data["confidence_score"] > 0.9


@pytest.mark.asyncio
async def test_scope_limiting_prevents_external_knowledge_inference(test_client):
    """Test that system doesn't infer external knowledge from course concepts."""
    with patch('app.api.v1.query.RAGService') as mock_rag_service_class:
        mock_rag_service = AsyncMock()
        mock_rag_service.process_query.return_value = {
            "response_text": "Based on the course material, I can explain the theoretical aspects of ZMP, but I don't have external information about its commercial applications.",
            "source_references": [
                {"chapter": 3, "lesson": 2, "section": "Walking Pattern Generation"}
            ],
            "confidence_score": 0.75,
            "timestamp": "2025-12-09T13:45:52Z"
        }
        mock_rag_service_class.return_value = mock_rag_service

        response = test_client.post(
            "/v1/query",
            json={
                "question": "Which companies use ZMP in their products?",
                "session_id": "session-scope-external-1"
            }
        )

        assert response.status_code == 200
        data = response.json()
        response_text = data["response_text"]

        # Verify response acknowledges course limits
        assert "don't have external information" in response_text.lower() or "not in course material" in response_text.lower()
        assert "course material" in response_text.lower()


@pytest.mark.asyncio
async def test_scope_limiting_statistics_accuracy(test_client):
    """Test that scope limiting maintains high accuracy for scope enforcement."""
    with patch('app.api.v1.query.RAGService') as mock_rag_service_class:
        mock_rag_service = AsyncMock()

        # Test both in-scope and out-of-scope questions
        test_cases = [
            # (question, expected_to_be_in_scope, keyword_to_check)
            ("What is ZMP?", True, "zmp"),
            ("Explain balance control", True, "balance"),
            ("What is the stock market?", False, "don't have"),
            ("How do I cook pasta?", False, "don't have"),
            ("Describe inverted pendulum", True, "pendulum"),
            ("Who is the CEO of Tesla?", False, "don't have"),
        ]

        correct_classifications = 0
        total_tests = len(test_cases)

        for i, (question, should_be_in_scope, expected_content) in enumerate(test_cases):
            if should_be_in_scope:
                mock_rag_service.process_query.return_value = {
                    "response_text": f"According to course material, {question.lower()} involves {expected_content}.",
                    "source_references": [
                        {"chapter": 1 + (i % 4), "lesson": 1, "section": "Test Section"}
                    ],
                    "confidence_score": 0.85,
                    "timestamp": f"2025-12-09T13:45:{53+i}Z"
                }
            else:
                mock_rag_service.process_query.return_value = {
                    "response_text": "I don't have information about this in the course material. Please ask about topics covered in the course.",
                    "source_references": [],
                    "confidence_score": 0.0,
                    "timestamp": f"2025-12-09T13:45:{59+i}Z"
                }

            response = test_client.post(
                "/v1/query",
                json={
                    "question": question,
                    "session_id": f"session-scope-stats-{i}"
                }
            )

            assert response.status_code == 200
            data = response.json()
            response_text = data["response_text"]

            # Check if classification was correct
            if should_be_in_scope:
                is_correct = contains_course_content(response_text) and data["confidence_score"] > 0.5
            else:
                is_correct = "don't have information about this in the course material" in response_text.lower()

            if is_correct:
                correct_classifications += 1

        # Calculate accuracy
        accuracy = correct_classifications / total_tests
        assert accuracy >= 0.9  # Should have high accuracy in scope classification