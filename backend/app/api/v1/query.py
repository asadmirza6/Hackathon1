"""POST /v1/query endpoint for submitting chatbot queries."""
import logging
import time
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.schemas import ChatQueryRequest, ChatResponseSchema
from app.services.rag_service import RAGService
from app.services.qdrant_service import QdrantService
from app.services.gemini_service import GeminiService
from app.services.postgres_service import PostgresService
from app.models.database import get_session
from app.utils.exceptions import (
    QdrantUnavailableError,
    GeminiAPIError,
    DatabaseError,
    ValidationError,
)
from app.core.constants import TARGET_P95_LATENCY_MS

logger = logging.getLogger(__name__)
router = APIRouter()

# Service instances (in production, use dependency injection)
qdrant_service: QdrantService | None = None
gemini_service: GeminiService | None = None


async def init_services() -> None:
    """Initialize external services."""
    global qdrant_service, gemini_service
    if qdrant_service is None:
        qdrant_service = QdrantService()
        await qdrant_service.init()
    if gemini_service is None:
        gemini_service = GeminiService()
        await gemini_service.init()


@router.post("/query", response_model=ChatResponseSchema)
async def query_chatbot(
    request: Request,
    query_request: ChatQueryRequest,
    session: AsyncSession = Depends(get_session),
) -> ChatResponseSchema:
    """Submit a question to the RAG chatbot.

    Processes the query through the RAG pipeline:
    1. Input validation
    2. Vector retrieval from Qdrant
    3. RAG augmentation with scope constraints
    4. LLM generation via Gemini
    5. Source attribution
    6. Async logging to Postgres

    Args:
        request: FastAPI request
        query_request: ChatQueryRequest with question, context, session_id
        session: Database session

    Returns:
        ChatResponseSchema with response text, sources, confidence, timestamp

    Raises:
        HTTPException: For validation errors or service unavailability

    """
    start_time = time.time()
    correlation_id = getattr(request.state, "correlation_id", "unknown")

    try:
        logger.info(
            f"📝 Query received: {query_request.question[:50]}... "
            f"(session: {query_request.session_id}, correlation: {correlation_id})"
        )

        # Initialize services if needed
        await init_services()

        # Create service instances for this request
        postgres_service = PostgresService(session)
        rag_service = RAGService(qdrant_service, gemini_service, postgres_service)

        # Stage 1: Input Validation
        try:
            from app.utils.validators import validate_query_input

            validate_query_input(
                query_request.question,
                query_request.session_id,
                query_request.selected_context,
            )
            logger.info("✅ Input validation passed")
        except ValidationError as e:
            logger.warning(f"❌ Validation error: {e}")
            raise HTTPException(status_code=400, detail=str(e))

        # Stage 2-5: Full RAG pipeline
        try:
            rag_result = await rag_service.process_query(
                question=query_request.question,
                session_id=query_request.session_id,
                selected_context=query_request.selected_context,
            )
        except QdrantUnavailableError as e:
            logger.error(f"🔴 Qdrant unavailable: {e}")
            raise HTTPException(status_code=503, detail=str(e))
        except GeminiAPIError as e:
            logger.error(f"🔴 Gemini API error: {e}")
            raise HTTPException(status_code=502, detail=str(e))
        except DatabaseError as e:
            logger.error(f"🔴 Database error: {e}")
            # Don't block response for database errors
            logger.warning("⚠️  Continuing despite database error")

        # Calculate performance metrics
        duration_ms = (time.time() - start_time) * 1000
        logger.info(f"⏱️  Total pipeline duration: {duration_ms:.1f}ms")

        # Warn if exceeding performance target
        if duration_ms > TARGET_P95_LATENCY_MS:
            logger.warning(
                f"⚠️  P95 latency target exceeded: {duration_ms:.1f}ms > {TARGET_P95_LATENCY_MS}ms"
            )

        # Build response
        response = ChatResponseSchema(
            response_text=rag_result["response_text"],
            source_references=rag_result["source_references"],
            confidence_score=rag_result["confidence_score"],
            timestamp=datetime.utcnow().isoformat(),
        )

        logger.info(
            f"✅ Query processed successfully ({duration_ms:.1f}ms, "
            f"confidence: {response.confidence_score:.2f})"
        )

        return response

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"🔴 Unexpected error: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="An unexpected error occurred. Please try again.",
        )
