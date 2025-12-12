"""Gemini API service for embeddings and text generation."""
import logging
from typing import List, Optional

import google.generativeai as genai
from google.generativeai.types.generation_types import GenerateContentResponse

from config import settings
from app.core.constants import QDRANT_VECTOR_SIZE
from app.utils.exceptions import GeminiAPIError

logger = logging.getLogger(__name__)


class GeminiService:
    """Service for Gemini API operations."""

    def __init__(self):
        """Initialize GeminiService."""
        self.model_name = "gemini-pro"
        self.embedding_model = "models/embedding-001"
        genai.configure(api_key=settings.gemini_api_key)

    async def init(self) -> None:
        """Initialize and verify Gemini API connection.

        Raises:
            GeminiAPIError: If API is unreachable

        """
        try:
            # Test connection with a simple call
            response = genai.list_models()
            if response:
                logger.info("✅ Connected to Gemini API")
            else:
                raise GeminiAPIError("No models available")
        except Exception as e:
            logger.error(f"❌ Failed to connect to Gemini API: {e}")
            raise GeminiAPIError(f"Gemini connection failed: {str(e)}")

    async def generate_embedding(self, text: str) -> List[float]:
        """Generate embedding for text using Gemini.

        Args:
            text: Text to embed

        Returns:
            768-dimensional embedding vector

        Raises:
            GeminiAPIError: If embedding fails

        """
        try:
            result = genai.embed_content(
                model=self.embedding_model,
                content=text,
                task_type="retrieval_document",
            )
            embedding = result["embedding"]

            if len(embedding) != QDRANT_VECTOR_SIZE:
                logger.warning(
                    f"⚠️  Embedding size {len(embedding)} != {QDRANT_VECTOR_SIZE}"
                )

            logger.debug(f"📊 Generated embedding of size {len(embedding)}")
            return embedding

        except Exception as e:
            logger.error(f"❌ Embedding generation failed: {e}")
            raise GeminiAPIError(f"Failed to generate embedding: {str(e)}")

    async def generate_response_for_query(
        self,
        question: str,
        augmented_prompt: str,
        temperature: float = 0.7,
        max_tokens: int = 500,
    ) -> str:
        """Generate response using Gemini API.

        Args:
            question: Original user question
            augmented_prompt: RAG-augmented prompt with context
            temperature: Sampling temperature (0-1)
            max_tokens: Max response tokens

        Returns:
            Generated response text

        Raises:
            GeminiAPIError: If generation fails

        """
        try:
            response: GenerateContentResponse = genai.generate_content(
                augmented_prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=temperature,
                    max_output_tokens=max_tokens,
                ),
            )

            if response.text:
                logger.info(f"✅ Generated response ({len(response.text)} chars)")
                return response.text
            else:
                logger.warning("⚠️  Empty response from Gemini")
                return "Unable to generate a response. Please rephrase your question."

        except Exception as e:
            logger.error(f"❌ Generation failed: {e}")
            raise GeminiAPIError(f"Failed to generate response: {str(e)}")

    async def validate_no_hallucination(
        self,
        question: str,
        response: str,
        context: str,
    ) -> bool:
        """Validate that response doesn't hallucinate outside context.

        Args:
            question: Original question
            response: Generated response
            context: Retrieved content context

        Returns:
            True if response stays within context bounds

        """
        try:
            validation_prompt = f"""Given this context from course materials:
{context}

And this user question:
{question}

Is the following response grounded in the provided context and doesn't add external knowledge?
Response: {response}

Answer only with: VALID or HALLUCINATION"""

            result: GenerateContentResponse = genai.generate_content(
                validation_prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=0.0,
                    max_output_tokens=10,
                ),
            )

            is_valid = result.text and "VALID" in result.text.upper()
            logger.info(
                f"🛡️  Hallucination check: {'✅ VALID' if is_valid else '❌ HALLUCINATION'}"
            )
            return is_valid

        except Exception as e:
            logger.error(f"❌ Hallucination validation failed: {e}")
            # Default to valid if validation fails (don't block user)
            return True

    async def validate_scope(self, response: str) -> bool:
        """Check if response respects scope boundaries.

        Args:
            response: Generated response text

        Returns:
            True if response is in scope

        """
        # Check for hallucination indicators
        out_of_scope_phrases = [
            "I don't have information",
            "outside the course",
            "not covered",
        ]

        in_scope = not any(phrase.lower() in response.lower() for phrase in out_of_scope_phrases)
        return in_scope

    async def close(self) -> None:
        """Close Gemini connection (if needed)."""
        logger.info("🛑 Closed Gemini connection")
