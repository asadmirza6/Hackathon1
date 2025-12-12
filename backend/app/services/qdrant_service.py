"""Qdrant vector database service for semantic search."""
import logging
from typing import List, Dict, Any, Optional

from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
from qdrant_client.http.exceptions import UnexpectedResponse

from config import settings
from app.core.constants import QDRANT_VECTOR_SIZE, QDRANT_COLLECTION_NAME
from app.utils.exceptions import QdrantUnavailableError

logger = logging.getLogger(__name__)


class QdrantService:
    """Service for Qdrant vector database operations."""

    def __init__(self):
        """Initialize QdrantService."""
        self.client: Optional[QdrantClient] = None
        self.collection_name = QDRANT_COLLECTION_NAME

    async def init(self) -> None:
        """Initialize Qdrant client and verify connection.

        Raises:
            QdrantUnavailableError: If Qdrant is unreachable

        """
        try:
            self.client = QdrantClient(
                url=settings.qdrant_url,
                api_key=settings.qdrant_api_key,
                timeout=5.0,
            )
            # Verify connection
            self.client.get_collections()
            logger.info("✅ Connected to Qdrant")
        except Exception as e:
            logger.error(f"❌ Failed to connect to Qdrant: {e}")
            raise QdrantUnavailableError(
                "Could not connect to vector database"
            )

    async def search_similar_chunks(
        self,
        embedding: List[float],
        limit: int = 5,
        score_threshold: float = 0.5,
    ) -> List[Dict[str, Any]]:
        """Search for similar chunks by embedding.

        Args:
            embedding: Query embedding vector (768-dim)
            limit: Max results to return
            score_threshold: Minimum similarity score

        Returns:
            List of similar chunks with metadata

        Raises:
            QdrantUnavailableError: If search fails

        """
        if not self.client:
            raise QdrantUnavailableError("Qdrant client not initialized")

        try:
            results = self.client.search(
                collection_name=self.collection_name,
                query_vector=embedding,
                query_filter=None,  # Can add metadata filters here
                limit=limit,
                score_threshold=score_threshold,
            )

            chunks = []
            for result in results:
                chunk = {
                    "id": result.id,
                    "similarity_score": result.score,
                    "text": result.payload.get("text", ""),
                    "chapter": result.payload.get("chapter"),
                    "lesson": result.payload.get("lesson"),
                    "section": result.payload.get("section"),
                }
                chunks.append(chunk)

            logger.info(f"🔍 Found {len(chunks)} similar chunks")
            return chunks

        except UnexpectedResponse as e:
            logger.error(f"❌ Qdrant search failed: {e}")
            raise QdrantUnavailableError(f"Search failed: {str(e)}")
        except Exception as e:
            logger.error(f"❌ Qdrant error: {e}")
            raise QdrantUnavailableError(f"Vector search error: {str(e)}")

    async def search_lessons(
        self,
        embedding: List[float],
        chapter: Optional[int] = None,
        lesson: Optional[int] = None,
        limit: int = 5,
    ) -> List[Dict[str, Any]]:
        """Search with optional chapter/lesson filters.

        Args:
            embedding: Query embedding
            chapter: Optional chapter filter
            lesson: Optional lesson filter
            limit: Max results

        Returns:
            Filtered search results

        """
        # Could add filter logic here based on chapter/lesson
        # For now, use generic search
        return await self.search_similar_chunks(
            embedding=embedding, limit=limit
        )

    async def get_client(self) -> QdrantClient:
        """Get Qdrant client instance.

        Returns:
            QdrantClient

        Raises:
            QdrantUnavailableError: If not initialized

        """
        if not self.client:
            await self.init()
        return self.client

    async def close(self) -> None:
        """Close Qdrant connection."""
        if self.client:
            self.client.close()
            logger.info("🛑 Closed Qdrant connection")
