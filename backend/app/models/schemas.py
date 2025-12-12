"""Pydantic schemas for request/response validation."""
from typing import List, Optional, Dict
from datetime import datetime

from pydantic import BaseModel, Field, field_validator


class SourceReference(BaseModel):
    """Source reference for a response."""

    chapter: Optional[int] = Field(None, description="Chapter number (1-4)")
    lesson: Optional[int] = Field(None, description="Lesson number (1-2)")
    section: Optional[str] = Field(None, description="Section heading")
    context_grounded: bool = Field(
        False,
        description="True if sourced from user-selected context (US2)",
    )


class ChatQueryRequest(BaseModel):
    """Request schema for chat query endpoint."""

    question: str = Field(
        ..., min_length=5, max_length=2000, description="User question"
    )
    selected_context: Optional[str] = Field(
        None, max_length=4000, description="Optional selected text from lesson"
    )
    session_id: str = Field(..., description="User session ID")

    @field_validator("question")
    @classmethod
    def validate_question(cls, v: str) -> str:
        """Validate question is not just whitespace."""
        if not v.strip():
            raise ValueError("Question cannot be empty or whitespace")
        return v.strip()

    @field_validator("session_id")
    @classmethod
    def validate_session_id(cls, v: str) -> str:
        """Validate session ID format."""
        if not v or len(v) < 5:
            raise ValueError("Session ID must be at least 5 characters")
        return v


class ChatResponseSchema(BaseModel):
    """Response schema for chat query endpoint."""

    response_text: str = Field(..., description="Generated response text")
    source_references: List[SourceReference] = Field(
        default_factory=list, description="Source references"
    )
    confidence_score: float = Field(
        ..., ge=0.0, le=1.0, description="Response confidence (0-1)"
    )
    timestamp: str = Field(..., description="ISO-8601 timestamp")


class HealthCheckResponse(BaseModel):
    """Response schema for health check endpoint."""

    status: str = Field(..., description="Service status (healthy/degraded/unhealthy)")
    services: dict = Field(..., description="Status of each service")
    timestamp: str = Field(..., description="Health check timestamp")


class QueryLogEntry(BaseModel):
    """Schema for query log entry."""

    id: int
    question: str
    response_text: str
    session_id: str
    confidence_score: float
    timestamp: str
    source_chapters: Optional[List[dict]] = None
    query_duration_ms: Optional[float] = None


class PaginatedLogsResponse(BaseModel):
    """Response schema for paginated logs."""

    items: List[QueryLogEntry] = Field(..., description="Log entries")
    total: int = Field(..., description="Total count")
    limit: int = Field(..., description="Page size")
    offset: int = Field(..., description="Page offset")


class AnalyticsResponse(BaseModel):
    """Response schema for analytics endpoint."""

    query_count: int = Field(..., description="Total queries in period")
    avg_confidence: float = Field(..., description="Average confidence score")
    avg_response_time_ms: float = Field(..., description="Average response time")
    unique_sessions: int = Field(..., description="Unique user sessions")
    period_days: int = Field(..., description="Analysis period in days")


class ErrorResponse(BaseModel):
    """Error response schema."""

    error: str = Field(..., description="Error type")
    message: str = Field(..., description="Error message")
    status_code: int = Field(..., description="HTTP status code")
    correlation_id: Optional[str] = Field(None, description="Request correlation ID")


class PerformanceMetrics(BaseModel):
    """Performance metrics response."""

    query_count: int = Field(..., description="Total queries")
    period_days: int = Field(..., description="Analysis period")
    avg_confidence: float = Field(..., description="Average confidence score")
    min_confidence: float = Field(..., description="Minimum confidence")
    max_confidence: float = Field(..., description="Maximum confidence")
    avg_response_time_ms: float = Field(..., description="Average response time")
    p95_response_time_ms: float = Field(..., description="95th percentile latency")
    avg_retrieval_time_ms: float = Field(..., description="Average vector search time")
    avg_generation_time_ms: float = Field(..., description="Average LLM generation time")
    unique_sessions: int = Field(..., description="Unique user sessions")


class TopQuestion(BaseModel):
    """Top question entry."""

    question: str = Field(..., description="The question")
    count: int = Field(..., description="Number of times asked")
    avg_confidence: float = Field(..., description="Average confidence for this question")


class TopQuestionsResponse(BaseModel):
    """Top questions response."""

    items: List[TopQuestion] = Field(..., description="Top questions")
    period_days: int = Field(..., description="Analysis period")


class ContentCoverageResponse(BaseModel):
    """Content coverage analytics."""

    coverage: Dict[str, int] = Field(..., description="Query count by chapter/lesson")
    total_queries: int = Field(..., description="Total queries analyzed")
    chapters_queried: int = Field(..., description="Number of chapters queried")
