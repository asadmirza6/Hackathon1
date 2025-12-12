"""Analytics service for query insights and course improvement."""
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc
from sqlalchemy.exc import SQLAlchemyError

from app.models.chat_query import ChatQuery

logger = logging.getLogger(__name__)


class AnalyticsService:
    """Service for analyzing query patterns and chatbot performance."""

    def __init__(self, session: AsyncSession):
        """Initialize AnalyticsService.

        Args:
            session: SQLAlchemy async session

        """
        self.session = session

    async def get_query_volume_by_day(
        self, days_back: int = 7
    ) -> List[Dict[str, Any]]:
        """Get query volume by day for trend analysis.

        Args:
            days_back: Number of days to analyze

        Returns:
            List of {date, query_count} dicts

        """
        try:
            cutoff = datetime.utcnow() - timedelta(days=days_back)

            # This is a simplified version; in production use database date functions
            stmt = select(ChatQuery).where(ChatQuery.timestamp >= cutoff)
            result = await self.session.execute(stmt)
            queries = result.scalars().all()

            # Group by day
            by_day = {}
            for q in queries:
                day = q.timestamp.date()
                by_day[day] = by_day.get(day, 0) + 1

            return [
                {"date": str(day), "query_count": count}
                for day, count in sorted(by_day.items())
            ]

        except SQLAlchemyError as e:
            logger.error(f"❌ Failed to get query volume: {e}")
            return []

    async def get_top_questions(
        self, limit: int = 10, days_back: int = 7
    ) -> List[Dict[str, Any]]:
        """Get most frequently asked questions.

        Args:
            limit: Max questions to return
            days_back: Analysis period

        Returns:
            List of {question, count, avg_confidence} dicts

        """
        try:
            cutoff = datetime.utcnow() - timedelta(days=days_back)

            stmt = select(ChatQuery).where(ChatQuery.timestamp >= cutoff)
            result = await self.session.execute(stmt)
            queries = result.scalars().all()

            # Group by question
            by_question = {}
            for q in queries:
                if q.question not in by_question:
                    by_question[q.question] = {
                        "count": 0,
                        "confidences": [],
                    }
                by_question[q.question]["count"] += 1
                by_question[q.question]["confidences"].append(q.confidence_score)

            # Sort by frequency
            top = sorted(
                by_question.items(),
                key=lambda x: x[1]["count"],
                reverse=True,
            )[:limit]

            return [
                {
                    "question": question,
                    "count": data["count"],
                    "avg_confidence": sum(data["confidences"])
                    / len(data["confidences"]),
                }
                for question, data in top
            ]

        except SQLAlchemyError as e:
            logger.error(f"❌ Failed to get top questions: {e}")
            return []

    async def get_low_confidence_queries(
        self, threshold: float = 0.5, limit: int = 10
    ) -> List[Dict[str, Any]]:
        """Get queries with low confidence scores (potential improvements).

        Args:
            threshold: Confidence threshold
            limit: Max results

        Returns:
            List of low-confidence queries

        """
        try:
            stmt = (
                select(ChatQuery)
                .where(ChatQuery.confidence_score < threshold)
                .order_by(ChatQuery.confidence_score)
                .limit(limit)
            )
            result = await self.session.execute(stmt)
            queries = result.scalars().all()

            return [
                {
                    "id": q.id,
                    "question": q.question,
                    "confidence_score": q.confidence_score,
                    "timestamp": q.timestamp.isoformat() if q.timestamp else None,
                }
                for q in queries
            ]

        except SQLAlchemyError as e:
            logger.error(f"❌ Failed to get low-confidence queries: {e}")
            return []

    async def get_performance_metrics(
        self, days_back: int = 7
    ) -> Dict[str, Any]:
        """Get comprehensive performance metrics.

        Args:
            days_back: Analysis period

        Returns:
            Metrics dict

        """
        try:
            cutoff = datetime.utcnow() - timedelta(days=days_back)

            stmt = select(ChatQuery).where(ChatQuery.timestamp >= cutoff)
            result = await self.session.execute(stmt)
            queries = result.scalars().all()

            if not queries:
                return self._empty_metrics(days_back)

            # Calculate metrics
            query_count = len(queries)
            confidences = [q.confidence_score for q in queries if q.confidence_score]
            durations = [q.query_duration_ms for q in queries if q.query_duration_ms]
            retrieval_times = [
                q.retrieval_duration_ms for q in queries if q.retrieval_duration_ms
            ]
            generation_times = [
                q.generation_duration_ms
                for q in queries
                if q.generation_duration_ms
            ]

            # Percentiles
            def percentile(data, p):
                if not data:
                    return 0
                sorted_data = sorted(data)
                idx = int(len(sorted_data) * p / 100)
                return sorted_data[min(idx, len(sorted_data) - 1)]

            return {
                "query_count": query_count,
                "period_days": days_back,
                "avg_confidence": (
                    sum(confidences) / len(confidences) if confidences else 0
                ),
                "min_confidence": min(confidences) if confidences else 0,
                "max_confidence": max(confidences) if confidences else 1,
                "avg_response_time_ms": (
                    sum(durations) / len(durations) if durations else 0
                ),
                "p95_response_time_ms": percentile(durations, 95) if durations else 0,
                "avg_retrieval_time_ms": (
                    sum(retrieval_times) / len(retrieval_times)
                    if retrieval_times
                    else 0
                ),
                "avg_generation_time_ms": (
                    sum(generation_times) / len(generation_times)
                    if generation_times
                    else 0
                ),
                "unique_sessions": len(set(q.session_id for q in queries)),
            }

        except SQLAlchemyError as e:
            logger.error(f"❌ Failed to get performance metrics: {e}")
            return self._empty_metrics(days_back)

    def _empty_metrics(self, days_back: int) -> Dict[str, Any]:
        """Return empty metrics dict."""
        return {
            "query_count": 0,
            "period_days": days_back,
            "avg_confidence": 0,
            "min_confidence": 0,
            "max_confidence": 0,
            "avg_response_time_ms": 0,
            "p95_response_time_ms": 0,
            "avg_retrieval_time_ms": 0,
            "avg_generation_time_ms": 0,
            "unique_sessions": 0,
        }

    async def get_content_coverage(
        self,
    ) -> Dict[str, Any]:
        """Analyze which course content is being queried.

        Returns:
            Coverage stats by chapter/lesson

        """
        try:
            stmt = select(ChatQuery)
            result = await self.session.execute(stmt)
            queries = result.scalars().all()

            coverage = {}
            for q in queries:
                if q.source_chapters:
                    for source in q.source_chapters:
                        key = f"Ch{source.get('chapter')}.L{source.get('lesson')}"
                        coverage[key] = coverage.get(key, 0) + 1

            return {
                "coverage": coverage,
                "total_queries": len(queries),
                "chapters_queried": len(set(k.split(".")[0] for k in coverage.keys())),
            }

        except Exception as e:
            logger.error(f"❌ Failed to get content coverage: {e}")
            return {}
