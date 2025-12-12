"""SQLAlchemy ORM model for chat queries and responses."""
from datetime import datetime
from typing import Optional

from sqlalchemy import Column, Integer, Text, String, DateTime, Float, JSON
from sqlalchemy.dialects.postgresql import UUID

from app.models.database import Base


class ChatQuery(Base):
    """ORM model for storing chat interactions in Postgres."""

    __tablename__ = "chat_queries"

    # Primary Key
    id = Column(Integer, primary_key=True, autoincrement=True)

    # Query Input
    question = Column(Text, nullable=False, index=True)
    selected_context = Column(Text, nullable=True)

    # Session & Timing
    session_id = Column(String(50), nullable=False, index=True)
    timestamp = Column(DateTime(timezone=True), default=datetime.utcnow, index=True)

    # Response Data
    response_text = Column(Text, nullable=False)
    source_chapters = Column(JSON, nullable=True)  # Array of source references

    # Scoring
    confidence_score = Column(Float, nullable=False)

    # Performance Metrics
    query_duration_ms = Column(Float, nullable=True)  # Total pipeline duration
    retrieval_duration_ms = Column(Float, nullable=True)  # Qdrant search time
    generation_duration_ms = Column(Float, nullable=True)  # Gemini generation time

    def __repr__(self) -> str:
        """String representation of ChatQuery."""
        return (
            f"<ChatQuery(id={self.id}, session_id={self.session_id}, "
            f"confidence={self.confidence_score:.2f})>"
        )

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "question": self.question,
            "selected_context": self.selected_context,
            "session_id": self.session_id,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
            "response_text": self.response_text,
            "source_chapters": self.source_chapters,
            "confidence_score": self.confidence_score,
            "query_duration_ms": self.query_duration_ms,
            "retrieval_duration_ms": self.retrieval_duration_ms,
            "generation_duration_ms": self.generation_duration_ms,
        }
