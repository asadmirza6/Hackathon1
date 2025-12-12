"""Postgres database service for storing and retrieving chat queries."""
import asyncio
import logging
import functools
import time
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc, and_
from sqlalchemy.exc import SQLAlchemyError

from app.models.chat_query import ChatQuery
from app.utils.exceptions import DatabaseError

logger = logging.getLogger(__name__)


def retry_on_connection_error(max_retries=3, initial_delay=0.1, backoff_factor=2):
    """Decorator to retry function calls on SQLAlchemy connection errors with exponential backoff.

    Args:
        max_retries: Maximum number of retry attempts (default: 3)
        initial_delay: Initial delay in seconds (default: 0.1)
        backoff_factor: Multiplier for delay after each retry (default: 2)
    """
    def decorator(func):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            last_exception = None
            delay = initial_delay

            for attempt in range(max_retries + 1):
                try:
                    return await func(*args, **kwargs)
                except SQLAlchemyError as e:
                    last_exception = e
                    if attempt == max_retries:  # Last attempt
                        logger.error(f"❌ Failed after {max_retries} retries: {e}")
                        raise e

                    logger.warning(f"⚠️ Attempt {attempt + 1} failed: {e}. Retrying in {delay}s...")
                    await asyncio.sleep(delay)
                    delay *= backoff_factor  # Exponential backoff

            # This should never be reached, but included for completeness
            raise last_exception
        return wrapper
    return decorator


class PostgresService:
    """Service for Postgres database operations."""

    def __init__(self, session: AsyncSession):
        """Initialize PostgresService.

        Args:
            session: SQLAlchemy async session

        """
        self.session = session

    @retry_on_connection_error(max_retries=3, initial_delay=0.1, backoff_factor=2)
    async def save_query(
        self,
        question: str,
        response_text: str,
        session_id: str,
        source_chapters: Optional[List[Dict[str, Any]]] = None,
        confidence_score: float = 0.0,
        selected_context: Optional[str] = None,
        query_duration_ms: Optional[float] = None,
        retrieval_duration_ms: Optional[float] = None,
        generation_duration_ms: Optional[float] = None,
    ) -> ChatQuery:
        """Save a chat query and response to database.

        Args:
            question: User question
            response_text: Generated response
            session_id: User session ID
            source_chapters: List of source references
            confidence_score: Response confidence (0-1)
            selected_context: Optional selected text context
            query_duration_ms: Total pipeline duration
            retrieval_duration_ms: Vector search duration
            generation_duration_ms: LLM generation duration

        Returns:
            Saved ChatQuery object

        Raises:
            DatabaseError: If save fails

        """
        try:
            chat_query = ChatQuery(
                question=question,
                response_text=response_text,
                session_id=session_id,
                source_chapters=source_chapters,
                confidence_score=confidence_score,
                selected_context=selected_context,
                timestamp=datetime.utcnow(),
                query_duration_ms=query_duration_ms,
                retrieval_duration_ms=retrieval_duration_ms,
                generation_duration_ms=generation_duration_ms,
            )
            self.session.add(chat_query)
            await self.session.commit()
            await self.session.refresh(chat_query)
            logger.info(f"✅ Saved query {chat_query.id} for session {session_id}")
            return chat_query
        except SQLAlchemyError as e:
            await self.session.rollback()
            logger.error(f"❌ Failed to save query: {e}")
            raise DatabaseError(f"Failed to save query: {str(e)}")

    async def get_query_logs(
        self,
        session_id: Optional[str] = None,
        limit: int = 100,
        offset: int = 0,
        days_back: Optional[int] = None,
    ) -> tuple[List[ChatQuery], int]:
        """Retrieve query logs with optional filters.

        Args:
            session_id: Filter by session ID
            limit: Max records to return
            offset: Pagination offset
            days_back: Only queries from last N days

        Returns:
            Tuple of (query list, total count)

        Raises:
            DatabaseError: If retrieval fails

        """
        try:
            filters = []

            if session_id:
                filters.append(ChatQuery.session_id == session_id)

            if days_back:
                cutoff = datetime.utcnow() - timedelta(days=days_back)
                filters.append(ChatQuery.timestamp >= cutoff)

            # Count total
            count_stmt = select(ChatQuery)
            if filters:
                count_stmt = count_stmt.where(and_(*filters))
            count_result = await self.session.execute(count_stmt)
            total = len(count_result.fetchall())

            # Get paginated results
            stmt = select(ChatQuery).order_by(desc(ChatQuery.timestamp))
            if filters:
                stmt = stmt.where(and_(*filters))
            stmt = stmt.limit(limit).offset(offset)

            result = await self.session.execute(stmt)
            queries = result.scalars().all()
            logger.info(f"📊 Retrieved {len(queries)} logs (total: {total})")
            return queries, total

        except SQLAlchemyError as e:
            logger.error(f"❌ Failed to retrieve logs: {e}")
            raise DatabaseError(f"Failed to retrieve logs: {str(e)}")

    async def get_analytics(
        self, days_back: int = 7
    ) -> Dict[str, Any]:
        """Get analytics for queries in the last N days.

        Args:
            days_back: Number of days to analyze

        Returns:
            Analytics dictionary

        """
        try:
            cutoff = datetime.utcnow() - timedelta(days=days_back)
            stmt = select(ChatQuery).where(ChatQuery.timestamp >= cutoff)
            result = await self.session.execute(stmt)
            queries = result.scalars().all()

            if not queries:
                return {
                    "query_count": 0,
                    "avg_confidence": 0,
                    "avg_response_time_ms": 0,
                    "unique_sessions": 0,
                }

            # Calculate metrics
            confidences = [q.confidence_score for q in queries if q.confidence_score]
            durations = [q.query_duration_ms for q in queries if q.query_duration_ms]
            sessions = set(q.session_id for q in queries)

            return {
                "query_count": len(queries),
                "avg_confidence": sum(confidences) / len(confidences)
                if confidences
                else 0,
                "avg_response_time_ms": sum(durations) / len(durations)
                if durations
                else 0,
                "unique_sessions": len(sessions),
                "period_days": days_back,
            }

        except SQLAlchemyError as e:
            logger.error(f"❌ Failed to get analytics: {e}")
            return {}

    async def close(self) -> None:
        """Close database session."""
        await self.session.close()

    async def log_query_async(
        self,
        question: str,
        response_text: str,
        session_id: str,
        source_chapters: Optional[List[Dict[str, Any]]] = None,
        confidence_score: float = 0.0,
        selected_context: Optional[str] = None,
        query_duration_ms: Optional[float] = None,
        retrieval_duration_ms: Optional[float] = None,
        generation_duration_ms: Optional[float] = None,
    ) -> None:
        """Log query asynchronously in the background without blocking response.

        Args:
            question: User question
            response_text: Generated response
            session_id: User session ID
            source_chapters: List of source references
            confidence_score: Response confidence (0-1)
            selected_context: Optional selected text context
            query_duration_ms: Total pipeline duration
            retrieval_duration_ms: Vector search duration
            generation_duration_ms: LLM generation duration
        """
        try:
            chat_query = ChatQuery(
                question=question,
                response_text=response_text,
                session_id=session_id,
                source_chapters=source_chapters,
                confidence_score=confidence_score,
                selected_context=selected_context,
                timestamp=datetime.utcnow(),
                query_duration_ms=query_duration_ms,
                retrieval_duration_ms=retrieval_duration_ms,
                generation_duration_ms=generation_duration_ms,
            )
            self.session.add(chat_query)
            await self.session.commit()
            logger.info(f"✅ Async logged query for session {session_id}")
        except SQLAlchemyError as e:
            # Don't raise exception as this is async background task
            logger.error(f"❌ Failed to async log query: {e}")
