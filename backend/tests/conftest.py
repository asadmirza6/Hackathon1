"""Pytest configuration and fixtures for testing."""
import asyncio
from typing import AsyncGenerator

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from unittest.mock import AsyncMock, MagicMock

from main import app


@pytest.fixture(scope="session")
def event_loop():
    """Create an event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
async def async_client() -> AsyncGenerator[AsyncClient, None]:
    """Create an async test client for FastAPI."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client


@pytest.fixture
def mock_qdrant_client() -> AsyncMock:
    """Create a mock Qdrant client."""
    client = AsyncMock()
    client.search = AsyncMock(return_value=[])
    client.upsert = AsyncMock()
    client.delete = AsyncMock()
    return client


@pytest.fixture
def mock_gemini_client() -> AsyncMock:
    """Create a mock Gemini API client."""
    client = AsyncMock()
    client.generate_content = AsyncMock(
        return_value=MagicMock(text="Mock generated response")
    )
    client.embed_content = AsyncMock(
        return_value=MagicMock(embedding=[0.1] * 768)  # 768-dimensional vector
    )
    return client


@pytest.fixture
def mock_postgres_pool() -> AsyncMock:
    """Create a mock Postgres connection pool."""
    pool = AsyncMock()
    connection = AsyncMock()
    pool.acquire = AsyncMock(return_value=connection)
    connection.execute = AsyncMock()
    connection.fetch = AsyncMock(return_value=[])
    return pool


@pytest.fixture
async def test_db() -> AsyncGenerator[AsyncSession, None]:
    """Create an in-memory test database session."""
    # Use SQLite in-memory for testing
    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        echo=False,
        future=True,
    )

    # Create tables
    async with engine.begin() as conn:
        # Tables would be created here
        pass

    # Create session factory
    async_session = async_sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )

    async with async_session() as session:
        yield session

    await engine.dispose()


@pytest.fixture
def sample_query_request() -> dict:
    """Sample ChatQueryRequest for testing."""
    return {
        "question": "What is ZMP in bipedal walking?",
        "selected_context": None,
        "session_id": "test-session-12345",
    }


@pytest.fixture
def sample_query_response() -> dict:
    """Sample ChatResponseSchema for testing."""
    return {
        "response_text": "Zero Moment Point (ZMP) is a concept in bipedal walking...",
        "source_references": [
            {
                "chapter": 3,
                "lesson": 2,
                "section": "Walking Pattern Generation",
            }
        ],
        "confidence_score": 0.92,
        "timestamp": "2025-12-09T13:45:23Z",
    }
