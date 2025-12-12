"""RAG (Retrieval-Augmented Generation) service orchestrator."""
import logging
from typing import List, Dict, Any, Optional
import time
import hashlib
from datetime import datetime

from app.services.qdrant_service import QdrantService
from app.services.gemini_service import GeminiService
from app.services.postgres_service import PostgresService
from app.utils.validators import validate_query_input
from app.core.constants import (
    RAG_CONSTRAINT_PROMPT,
    MIN_CONFIDENCE_SCORE,
    MAX_RETRIEVED_CHUNKS,
)
from app.core.metrics import (
    metrics_collector,
    QUERY_DURATION_HISTOGRAM,
    RETRIEVAL_DURATION_HISTOGRAM,
    GENERATION_DURATION_HISTOGRAM,
    QUERY_TOTAL_COUNTER,
    QUERY_ERROR_COUNTER,
    measure_duration,
    count_calls,
    record_error
)

logger = logging.getLogger(__name__)


class RAGService:
    """Orchestrates the RAG pipeline: Retrieval → Augmentation → Generation."""

    def __init__(
        self,
        qdrant_service: QdrantService,
        gemini_service: GeminiService,
        postgres_service: PostgresService,
    ):
        """Initialize RAG service with dependencies.

        Args:
            qdrant_service: Vector database service
            gemini_service: LLM service
            postgres_service: Database service

        """
        self.qdrant = qdrant_service
        self.gemini = gemini_service
        self.postgres = postgres_service

    @measure_duration(QUERY_DURATION_HISTOGRAM)
    @count_calls(QUERY_TOTAL_COUNTER)
    @record_error(QUERY_ERROR_COUNTER)
    async def process_query(
        self,
        question: str,
        session_id: str,
        selected_context: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Process a user query through the full RAG pipeline.

        Supports User Story 1 (basic RAG) and User Story 2 (context-aware).

        Pipeline stages:
        1. Input Validation
        2. Vector Retrieval
        3. RAG Augmentation (with optional selected_context for US2)
        4. Generation
        5. Source Attribution
        6. Async Logging

        Args:
            question: User question
            session_id: Session ID
            selected_context: Optional selected text (User Story 2)

        Returns:
            Response dict with text, sources, confidence, timestamp

        """
        start_time = time.time()

        # Stage 1: Validation
        logger.info("📝 Stage 1: Input Validation")
        validate_query_input(question, session_id, selected_context)

        # Stage 2: Vector Retrieval
        logger.info("📝 Stage 2: Vector Retrieval")
        retrieval_start = time.time()
        query_embedding = await self.gemini.generate_embedding(question)
        retrieved_chunks = await self.qdrant.search_similar_chunks(
            embedding=query_embedding, limit=MAX_RETRIEVED_CHUNKS
        )
        retrieval_duration = time.time() - retrieval_start

        # Record retrieval metrics
        metrics_collector.observe_histogram(
            RETRIEVAL_DURATION_HISTOGRAM,
            retrieval_duration,
            {"operation": "vector_search", "session_id": session_id}
        )

        if not retrieved_chunks:
            logger.warning("⚠️  No relevant chunks found")
            return {
                "response_text": "I couldn't find relevant information about your question in the course materials.",
                "source_references": [],
                "confidence_score": 0.0,
                "timestamp": None,
            }

        # Stage 3: RAG Augmentation
        logger.info("📝 Stage 3: RAG Augmentation")
        augmented_prompt = self._build_augmented_prompt(
            question, retrieved_chunks, selected_context
        )

        # Stage 4: Generation
        logger.info("📝 Stage 4: LLM Generation")
        generation_start = time.time()
        response_text = await self.gemini.generate_response_for_query(
            question, augmented_prompt
        )
        generation_duration = time.time() - generation_start

        # Record generation metrics
        metrics_collector.observe_histogram(
            GENERATION_DURATION_HISTOGRAM,
            generation_duration,
            {"operation": "llm_generation", "session_id": session_id}
        )

        # Stage 5: Source Attribution & Scoring
        logger.info("📝 Stage 5: Source Attribution")
        source_references = self._extract_source_references(retrieved_chunks)
        confidence_score = self._calculate_confidence_score(
            retrieved_chunks, response_text
        )

        total_duration = time.time() - start_time
        logger.info(f"✅ Query processed in {total_duration:.2f}s")

        # Generate a unique query ID for tracking
        query_id = hashlib.md5(f"{question}_{session_id}_{time.time()}".encode()).hexdigest()[:12]

        # Stage 6: Async logging (fire and forget)
        logger.info("📝 Stage 6: Async Logging")

        # Add structured logging for centralized log analysis (T066)
        logger.info(
            "🎯 Query completed",
            extra={
                "query_id": query_id,
                "user_session": session_id,
                "timestamp": datetime.utcnow().isoformat(),
                "duration_ms": total_duration * 1000,
                "confidence": confidence_score,
                "question_length": len(question),
                "response_length": len(response_text),
                "retrieval_duration_ms": retrieval_duration * 1000,
                "generation_duration_ms": generation_duration * 1000,
                "retrieved_chunks_count": len(retrieved_chunks),
                "selected_context_provided": selected_context is not None,
            }
        )

        # Log context tracking info (T056)
        if selected_context:
            # Hash the selected context for privacy (never log raw text)
            context_hash = hashlib.sha256(selected_context.encode()).hexdigest()[:8]
            logger.info(
                f"🔍 Context-aware query detected: context_hash={context_hash}, "
                f"context_len={len(selected_context)}"
            )

        # Log retrieval details (matched chunks with similarity scores)
        logger.info(
            f"📊 Retrieval details: {len(retrieved_chunks)} chunks retrieved, "
            f"avg_similarity={sum(c.get('similarity_score', 0) for c in retrieved_chunks) / len(retrieved_chunks):.2f}"
        )
        for idx, chunk in enumerate(retrieved_chunks, 1):
            logger.debug(
                f"  Chunk {idx}: chapter={chunk.get('chapter')}, "
                f"lesson={chunk.get('lesson')}, "
                f"similarity={chunk.get('similarity_score', 0):.2f}"
            )

        # Record overall query metrics
        metrics_collector.set_gauge(
            "rag_active_queries",
            0,  # This would be incremented before and decremented after if tracking active queries
            {"session_id": session_id}
        )

        # In production, this would be a background task
        await self.postgres.save_query(
            question=question,
            response_text=response_text,
            session_id=session_id,
            source_chapters=source_references,
            confidence_score=confidence_score,
            selected_context=selected_context,
            query_duration_ms=total_duration * 1000,
            retrieval_duration_ms=retrieval_duration * 1000,
            generation_duration_ms=generation_duration * 1000,
        )

        return {
            "response_text": response_text,
            "source_references": source_references,
            "confidence_score": confidence_score,
            "timestamp": None,  # Will be set by API endpoint
        }

    def _build_augmented_prompt(
        self,
        question: str,
        chunks: List[Dict[str, Any]],
        selected_context: Optional[str] = None,
    ) -> str:
        """Build augmented prompt with RAG context.

        Args:
            question: User question
            chunks: Retrieved content chunks
            selected_context: Optional selected text

        Returns:
            Complete augmented prompt

        """
        context_text = "\n\n".join([chunk["text"] for chunk in chunks])

        if selected_context:
            # Mark selected context prominently for context-aware answers (US2)
            context_text = f"""🔍 SELECTED PASSAGE (user-highlighted text):
{selected_context}

📚 ADDITIONAL COURSE MATERIAL:
{context_text}"""

        prompt = f"""{RAG_CONSTRAINT_PROMPT}

Course Material Context:
{context_text}

User Question: {question}

Answer:"""
        return prompt

    def _extract_source_references(
        self, chunks: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Extract source references from chunks.

        Args:
            chunks: Retrieved chunks with metadata

        Returns:
            List of source references

        """
        sources = []
        for chunk in chunks:
            source = {
                "chapter": chunk.get("chapter"),
                "lesson": chunk.get("lesson"),
                "section": chunk.get("section"),
            }
            sources.append(source)
        return sources

    def _calculate_confidence_score(
        self,
        chunks: List[Dict[str, Any]],
        response: str,
    ) -> float:
        """Calculate confidence score for response.

        Args:
            chunks: Retrieved chunks with similarity scores
            response: Generated response

        Returns:
            Confidence score (0-1)

        """
        if not chunks:
            return 0.0

        # Average similarity of retrieved chunks
        avg_similarity = sum(c.get("similarity_score", 0) for c in chunks) / len(
            chunks
        )

        # Adjust for response length (longer responses are more confident)
        response_factor = min(len(response) / 200, 1.0)

        # Combined confidence
        confidence = (avg_similarity * 0.7) + (response_factor * 0.3)
        confidence = max(MIN_CONFIDENCE_SCORE, min(confidence, 1.0))

        logger.info(f"📊 Confidence score: {confidence:.2f}")
        return confidence

    async def validate_input(self, question: str, session_id: str) -> None:
        """Validate query input.

        Args:
            question: User question
            session_id: Session ID

        Raises:
            ValidationError: If validation fails

        """
        validate_query_input(question, session_id)
