"""Unit tests for RAG service User Story 1 logic."""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from app.services.rag_service import RAGService
from app.services.qdrant_service import QdrantService
from app.services.gemini_service import GeminiService
from app.services.postgres_service import PostgresService


@pytest.fixture
def mock_services():
    """Create mock service instances."""
    qdrant = AsyncMock(spec=QdrantService)
    gemini = AsyncMock(spec=GeminiService)
    postgres = AsyncMock(spec=PostgresService)
    return qdrant, gemini, postgres


@pytest.fixture
def rag_service(mock_services):
    """Create RAG service with mock dependencies."""
    qdrant, gemini, postgres = mock_services
    return RAGService(qdrant, gemini, postgres)


class TestRAGServiceValidation:
    """Tests for input validation."""

    @pytest.mark.asyncio
    async def test_validate_input_valid_query(self, rag_service):
        """Test validation passes for valid input."""
        # Should not raise
        await rag_service.validate_input(
            question="What is ZMP?",
            session_id="session-123",
        )

    @pytest.mark.asyncio
    async def test_validate_input_question_too_short(self, rag_service):
        """Test validation fails for question too short."""
        from app.utils.validators import ValidationError

        with pytest.raises(ValidationError):
            await rag_service.validate_input(
                question="Hi",
                session_id="session-123",
            )

    @pytest.mark.asyncio
    async def test_validate_input_question_too_long(self, rag_service):
        """Test validation fails for question too long."""
        from app.utils.validators import ValidationError

        with pytest.raises(ValidationError):
            await rag_service.validate_input(
                question="x" * 2001,
                session_id="session-123",
            )

    @pytest.mark.asyncio
    async def test_validate_input_invalid_session_id(self, rag_service):
        """Test validation fails for invalid session ID."""
        from app.utils.validators import ValidationError

        with pytest.raises(ValidationError):
            await rag_service.validate_input(
                question="What is ZMP?",
                session_id="123",  # Too short
            )


class TestRAGServiceAugmentation:
    """Tests for RAG prompt augmentation."""

    def test_build_augmented_prompt_basic(self, rag_service):
        """Test augmented prompt building with basic chunks."""
        chunks = [
            {
                "text": "ZMP is the point where the total moment is zero.",
                "chapter": 3,
                "lesson": 2,
                "section": "Walking",
            },
        ]

        prompt = rag_service._build_augmented_prompt(
            question="What is ZMP?",
            chunks=chunks,
            selected_context=None,
        )

        assert "ZMP is the point" in prompt
        assert "What is ZMP?" in prompt
        assert "ONLY use information from the course materials" in prompt

    def test_build_augmented_prompt_with_context(self, rag_service):
        """Test augmented prompt includes selected context."""
        chunks = [
            {
                "text": "ZMP is important for balance.",
                "chapter": 3,
                "lesson": 2,
                "section": "Walking",
            },
        ]

        prompt = rag_service._build_augmented_prompt(
            question="Why is ZMP important?",
            chunks=chunks,
            selected_context="Selected passage about ZMP",
        )

        assert "Selected passage about ZMP" in prompt
        assert "ZMP is important" in prompt

    def test_build_augmented_prompt_multiple_chunks(self, rag_service):
        """Test augmented prompt combines multiple chunks."""
        chunks = [
            {"text": "Chunk 1 text", "chapter": 1, "lesson": 1, "section": "Sec1"},
            {"text": "Chunk 2 text", "chapter": 2, "lesson": 1, "section": "Sec2"},
            {"text": "Chunk 3 text", "chapter": 3, "lesson": 1, "section": "Sec3"},
        ]

        prompt = rag_service._build_augmented_prompt(
            question="Combined question?",
            chunks=chunks,
            selected_context=None,
        )

        assert "Chunk 1 text" in prompt
        assert "Chunk 2 text" in prompt
        assert "Chunk 3 text" in prompt


class TestRAGServiceSourceAttribution:
    """Tests for source reference extraction."""

    def test_extract_source_references_single(self, rag_service):
        """Test extracting single source reference."""
        chunks = [
            {
                "text": "Content",
                "chapter": 3,
                "lesson": 2,
                "section": "Walking Pattern",
            },
        ]

        sources = rag_service._extract_source_references(chunks)

        assert len(sources) == 1
        assert sources[0]["chapter"] == 3
        assert sources[0]["lesson"] == 2
        assert sources[0]["section"] == "Walking Pattern"

    def test_extract_source_references_multiple(self, rag_service):
        """Test extracting multiple source references."""
        chunks = [
            {
                "text": "Content 1",
                "chapter": 1,
                "lesson": 1,
                "section": "Basics",
            },
            {
                "text": "Content 2",
                "chapter": 2,
                "lesson": 2,
                "section": "Control",
            },
        ]

        sources = rag_service._extract_source_references(chunks)

        assert len(sources) == 2
        assert sources[0]["chapter"] == 1
        assert sources[1]["chapter"] == 2

    def test_extract_source_references_empty(self, rag_service):
        """Test extracting sources from empty chunks."""
        sources = rag_service._extract_source_references([])
        assert sources == []


class TestRAGServiceConfidenceScoring:
    """Tests for confidence score calculation."""

    def test_calculate_confidence_score_high(self, rag_service):
        """Test high confidence with good similarity scores."""
        chunks = [
            {"similarity_score": 0.95},
            {"similarity_score": 0.92},
            {"similarity_score": 0.88},
        ]
        response = "x" * 300  # Longer response

        score = rag_service._calculate_confidence_score(chunks, response)

        assert 0.8 < score <= 1.0
        assert score > 0.3  # Above minimum

    def test_calculate_confidence_score_low(self, rag_service):
        """Test low confidence with poor similarity scores."""
        chunks = [
            {"similarity_score": 0.45},
            {"similarity_score": 0.42},
            {"similarity_score": 0.40},
        ]
        response = "Short"

        score = rag_service._calculate_confidence_score(chunks, response)

        assert 0.3 <= score <= 0.6

    def test_calculate_confidence_score_no_chunks(self, rag_service):
        """Test confidence score with no chunks."""
        score = rag_service._calculate_confidence_score([], "Some response")
        assert score == 0.3  # Minimum score

    def test_calculate_confidence_score_range(self, rag_service):
        """Test confidence score stays within valid range."""
        chunks = [{"similarity_score": 0.50}]
        response = "Response text"

        score = rag_service._calculate_confidence_score(chunks, response)

        assert 0.0 <= score <= 1.0


class TestRAGServicePipeline:
    """Tests for full RAG pipeline."""

    @pytest.mark.asyncio
    async def test_process_query_full_pipeline(self, rag_service, mock_services):
        """Test complete query processing pipeline."""
        qdrant_svc, gemini_svc, postgres_svc = mock_services

        # Setup mock returns
        gemini_svc.generate_embedding.return_value = [0.1] * 768
        qdrant_svc.search_similar_chunks.return_value = [
            {
                "id": 1,
                "text": "ZMP is the point where torque equals zero.",
                "similarity_score": 0.92,
                "chapter": 3,
                "lesson": 2,
                "section": "Walking",
            },
        ]
        gemini_svc.generate_response_for_query.return_value = (
            "ZMP (Zero Moment Point) is the point where..."
        )
        postgres_svc.save_query.return_value = MagicMock(id=1)

        result = await rag_service.process_query(
            question="What is ZMP?",
            session_id="test-session-123",
            selected_context=None,
        )

        # Verify pipeline results
        assert "response_text" in result
        assert "source_references" in result
        assert "confidence_score" in result
        assert result["confidence_score"] > 0.3

    @pytest.mark.asyncio
    async def test_process_query_with_context(self, rag_service, mock_services):
        """Test query processing with selected context."""
        qdrant_svc, gemini_svc, postgres_svc = mock_services

        gemini_svc.generate_embedding.return_value = [0.1] * 768
        qdrant_svc.search_similar_chunks.return_value = [
            {
                "text": "Context content",
                "similarity_score": 0.88,
                "chapter": 2,
                "lesson": 1,
                "section": "Control",
            },
        ]
        gemini_svc.generate_response_for_query.return_value = "Answer from context"
        postgres_svc.save_query.return_value = MagicMock(id=1)

        result = await rag_service.process_query(
            question="Follow-up question?",
            session_id="test-session-123",
            selected_context="Selected text from lesson",
        )

        assert result["response_text"] == "Answer from context"
        assert len(result["source_references"]) > 0

    @pytest.mark.asyncio
    async def test_process_query_no_results(self, rag_service, mock_services):
        """Test graceful handling when no chunks found."""
        qdrant_svc, gemini_svc, postgres_svc = mock_services

        gemini_svc.generate_embedding.return_value = [0.1] * 768
        qdrant_svc.search_similar_chunks.return_value = []  # No results

        result = await rag_service.process_query(
            question="Unrelated question?",
            session_id="test-session-123",
            selected_context=None,
        )

        assert "couldn't find relevant information" in result["response_text"].lower()
        assert result["confidence_score"] == 0.0
