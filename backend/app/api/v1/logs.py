"""GET /v1/logs endpoint for query logging and analytics."""
import logging
import os
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Header
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.schemas import (
    PaginatedLogsResponse,
    QueryLogEntry,
    AnalyticsResponse,
    PerformanceMetrics,
    TopQuestion,
    TopQuestionsResponse,
    ContentCoverageResponse,
)
from app.services.postgres_service import PostgresService
from app.services.analytics_service import AnalyticsService
from app.models.database import get_session

logger = logging.getLogger(__name__)
router = APIRouter()

def require_admin_token(x_admin_token: str = Header(None)) -> bool:
    """Dependency to verify admin authorization token.

    Args:
        x_admin_token: Admin token from X-Admin-Token header

    Returns:
        True if token is valid

    Raises:
        HTTPException: If token is missing or invalid
    """
    expected_token = os.getenv("ADMIN_TOKEN")

    if not expected_token:
        # In development, allow access without token if env var is not set
        logger.warning("⚠️ ADMIN_TOKEN not set, bypassing admin auth (only for development)")
        return True

    if not x_admin_token or x_admin_token != expected_token:
        logger.warning("❌ Invalid admin token provided")
        raise HTTPException(
            status_code=401,
            detail="Unauthorized: Invalid admin token"
        )

    logger.info("✅ Admin token verified")
    return True


@router.get("/logs", response_model=PaginatedLogsResponse)
async def get_query_logs(
    session_id: Optional[str] = Query(None, description="Filter by session ID"),
    limit: int = Query(100, ge=1, le=1000, description="Results per page"),
    offset: int = Query(0, ge=0, description="Pagination offset"),
    days_back: Optional[int] = Query(None, ge=1, le=365, description="Days to query"),
    session: AsyncSession = Depends(get_session),
    admin_authorized: bool = Depends(require_admin_token),
) -> PaginatedLogsResponse:
    """Retrieve paginated query logs with optional filters.

    Requires admin authorization (X-Admin-Token header in production).

    Query Parameters:
        - session_id: Filter by user session ID
        - limit: Results per page (1-1000, default 100)
        - offset: Pagination offset
        - days_back: Only queries from last N days

    Returns:
        PaginatedLogsResponse with log entries

    """
    logger.info(
        f"📊 Logs requested: limit={limit}, offset={offset}, "
        f"session_id={session_id}, days_back={days_back}"
    )

    try:
        postgres_service = PostgresService(session)

        queries, total = await postgres_service.get_query_logs(
            session_id=session_id,
            limit=limit,
            offset=offset,
            days_back=days_back,
        )

        # Convert ORM objects to Pydantic schemas
        items = [
            QueryLogEntry(
                id=q.id,
                question=q.question,
                response_text=q.response_text,
                session_id=q.session_id,
                confidence_score=q.confidence_score,
                timestamp=q.timestamp.isoformat() if q.timestamp else None,
                source_chapters=q.source_chapters,
                query_duration_ms=q.query_duration_ms,
            )
            for q in queries
        ]

        response = PaginatedLogsResponse(
            items=items,
            total=total,
            limit=limit,
            offset=offset,
        )

        logger.info(f"✅ Returned {len(items)} logs (total: {total})")
        return response

    except Exception as e:
        logger.error(f"❌ Failed to retrieve logs: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="Failed to retrieve logs. Please try again.",
        )


@router.get("/logs/aggregate", response_model=AnalyticsResponse)
async def get_analytics(
    days_back: int = Query(7, ge=1, le=365, description="Analysis period"),
    session: AsyncSession = Depends(get_session),
    admin_authorized: bool = Depends(require_admin_token),
) -> AnalyticsResponse:
    """Get aggregated query analytics for the specified period.

    Query Parameters:
        - days_back: Analysis period in days (1-365, default 7)

    Returns:
        AnalyticsResponse with aggregated metrics

    """
    logger.info(f"📈 Analytics requested for last {days_back} days")

    try:
        postgres_service = PostgresService(session)
        analytics = await postgres_service.get_analytics(days_back=days_back)

        response = AnalyticsResponse(
            query_count=analytics.get("query_count", 0),
            avg_confidence=analytics.get("avg_confidence", 0.0),
            avg_response_time_ms=analytics.get("avg_response_time_ms", 0.0),
            unique_sessions=analytics.get("unique_sessions", 0),
            period_days=analytics.get("period_days", days_back),
        )

        logger.info(
            f"✅ Analytics: {response.query_count} queries, "
            f"avg confidence: {response.avg_confidence:.2f}"
        )
        return response

    except Exception as e:
        logger.error(f"❌ Failed to get analytics: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="Failed to retrieve analytics. Please try again.",
        )


@router.get("/logs/metrics", response_model=PerformanceMetrics)
async def get_performance_metrics(
    days_back: int = Query(7, ge=1, le=365, description="Analysis period"),
    session: AsyncSession = Depends(get_session),
    admin_authorized: bool = Depends(require_admin_token),
) -> PerformanceMetrics:
    """Get comprehensive performance metrics for the specified period.

    Query Parameters:
        - days_back: Analysis period in days (1-365, default 7)

    Returns:
        PerformanceMetrics with latency, confidence, and throughput data

    """
    logger.info(f"📊 Performance metrics requested for last {days_back} days")

    try:
        analytics_service = AnalyticsService(session)
        metrics = await analytics_service.get_performance_metrics(days_back=days_back)

        response = PerformanceMetrics(
            query_count=metrics.get("query_count", 0),
            period_days=metrics.get("period_days", days_back),
            avg_confidence=metrics.get("avg_confidence", 0.0),
            min_confidence=metrics.get("min_confidence", 0.0),
            max_confidence=metrics.get("max_confidence", 1.0),
            avg_response_time_ms=metrics.get("avg_response_time_ms", 0.0),
            p95_response_time_ms=metrics.get("p95_response_time_ms", 0.0),
            avg_retrieval_time_ms=metrics.get("avg_retrieval_time_ms", 0.0),
            avg_generation_time_ms=metrics.get("avg_generation_time_ms", 0.0),
            unique_sessions=metrics.get("unique_sessions", 0),
        )

        logger.info(
            f"✅ Metrics: {response.query_count} queries, "
            f"p95 latency: {response.p95_response_time_ms:.0f}ms, "
            f"avg confidence: {response.avg_confidence:.2f}"
        )
        return response

    except Exception as e:
        logger.error(f"❌ Failed to get performance metrics: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="Failed to retrieve performance metrics. Please try again.",
        )


@router.get("/logs/top-questions", response_model=TopQuestionsResponse)
async def get_top_questions(
    limit: int = Query(10, ge=1, le=100, description="Max questions to return"),
    days_back: int = Query(7, ge=1, le=365, description="Analysis period"),
    session: AsyncSession = Depends(get_session),
    admin_authorized: bool = Depends(require_admin_token),
) -> TopQuestionsResponse:
    """Get the most frequently asked questions for the specified period.

    Query Parameters:
        - limit: Maximum questions to return (1-100, default 10)
        - days_back: Analysis period in days (1-365, default 7)

    Returns:
        TopQuestionsResponse with most asked questions and confidence scores

    """
    logger.info(f"❓ Top questions requested: limit={limit}, days_back={days_back}")

    try:
        analytics_service = AnalyticsService(session)
        top_questions = await analytics_service.get_top_questions(
            limit=limit, days_back=days_back
        )

        response = TopQuestionsResponse(
            items=[
                TopQuestion(
                    question=q["question"],
                    count=q["count"],
                    avg_confidence=q["avg_confidence"],
                )
                for q in top_questions
            ],
            period_days=days_back,
        )

        logger.info(f"✅ Retrieved {len(response.items)} top questions")
        return response

    except Exception as e:
        logger.error(f"❌ Failed to get top questions: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="Failed to retrieve top questions. Please try again.",
        )


@router.get("/logs/coverage", response_model=ContentCoverageResponse)
async def get_content_coverage(
    session: AsyncSession = Depends(get_session),
    admin_authorized: bool = Depends(require_admin_token),
) -> ContentCoverageResponse:
    """Analyze which course content is being queried (content coverage analytics).

    Returns:
        ContentCoverageResponse with coverage stats by chapter/lesson

    """
    logger.info("📚 Content coverage analytics requested")

    try:
        analytics_service = AnalyticsService(session)
        coverage = await analytics_service.get_content_coverage()

        response = ContentCoverageResponse(
            coverage=coverage.get("coverage", {}),
            total_queries=coverage.get("total_queries", 0),
            chapters_queried=coverage.get("chapters_queried", 0),
        )

        logger.info(
            f"✅ Coverage: {response.chapters_queried} chapters queried, "
            f"{response.total_queries} total queries analyzed"
        )
        return response

    except Exception as e:
        logger.error(f"❌ Failed to get content coverage: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="Failed to retrieve content coverage. Please try again.",
        )
