#!/usr/bin/env python3
"""Script to seed the database with sample analytics data for testing."""
import asyncio
import logging
import os
import random
from datetime import datetime, timedelta
from typing import List, Dict, Any

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from app.models.database import Base
from app.models.chat_query import ChatQuery
from app.services.postgres_service import PostgresService

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Sample questions and responses for seeding
SAMPLE_QUESTIONS = [
    "What is ZMP in bipedal walking?",
    "How does the inverted pendulum model work?",
    "What are the key principles of dynamic walking?",
    "Explain the difference between static and dynamic balance.",
    "How do robots maintain stability during locomotion?",
    "What is the role of feedback control in walking?",
    "How do humans maintain balance while walking?",
    "What are the challenges in bipedal robot locomotion?",
    "Explain the concept of limit cycles in walking.",
    "What sensors are used in balance control systems?",
    "How does the center of mass affect walking stability?",
    "What is the difference between passive and active walking?",
    "How do terrain variations affect walking patterns?",
    "What is the role of the ankle in walking?",
    "Explain the concept of capture point in balance.",
]

SAMPLE_RESPONSES = [
    "Zero Moment Point (ZMP) is a concept used in bipedal locomotion to describe the point on the ground where the net moment of the ground reaction force is zero.",
    "The inverted pendulum model is a simplified representation of human walking where the body is modeled as an inverted pendulum swinging over the stance foot.",
    "Dynamic walking relies on the natural dynamics of the system to achieve efficient and stable locomotion with minimal control effort.",
    "Static balance refers to maintaining equilibrium without motion, while dynamic balance involves maintaining stability during movement.",
    "Robots maintain stability through a combination of feedback control, predictive control, and careful design of the mechanical system.",
    "Feedback control in walking adjusts the robot's motion based on sensor readings to maintain balance and achieve desired trajectories.",
    "Humans maintain balance while walking through a complex interplay of sensory feedback, neural processing, and motor responses.",
    "Key challenges in bipedal robot locomotion include maintaining balance, adapting to terrain variations, and achieving energy efficiency.",
    "Limit cycles in walking represent stable periodic motions that the system naturally tends toward, providing robust walking patterns.",
    "Balance control systems commonly use accelerometers, gyroscopes, force sensors, and vision systems to maintain stability.",
    "The center of mass position and its movement relative to the support base are critical factors in determining walking stability.",
    "Passive walking relies on gravity and mechanical design for locomotion, while active walking uses powered actuators for control.",
    "Terrain variations require adaptive control strategies to maintain stability and adjust gait patterns accordingly.",
    "The ankle plays a crucial role in walking by providing propulsion and helping to maintain balance during the gait cycle.",
    "The capture point is a location where a point mass biped can come to rest by taking one step, providing insight into balance control.",
]

SOURCE_CHAPTERS = [
    [{"chapter": 1, "lesson": 1, "section": "Introduction to Bipedal Locomotion"}],
    [{"chapter": 2, "lesson": 1, "section": "Balance Control"}],
    [{"chapter": 3, "lesson": 1, "section": "Walking Pattern Generation"}],
    [{"chapter": 3, "lesson": 2, "section": "ZMP-Based Walking"}],
    [{"chapter": 4, "lesson": 1, "section": "Stability Analysis"}],
    [{"chapter": 4, "lesson": 2, "section": "Feedback Control"}],
    [{"chapter": 1, "lesson": 2, "section": "Human Walking Mechanics"}],
    [{"chapter": 2, "lesson": 2, "section": "Robot Balance Systems"}],
]


async def seed_database(database_url: str, num_samples: int = 50) -> None:
    """Seed the database with sample query data."""
    # Create async engine
    engine = create_async_engine(database_url)

    # Create tables if they don't exist
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # Create session
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with async_session() as session:
        postgres_service = PostgresService(session)

        logger.info(f"🌱 Seeding {num_samples} sample queries...")

        for i in range(num_samples):
            # Select random question and response
            question = random.choice(SAMPLE_QUESTIONS)
            response = random.choice(SAMPLE_RESPONSES)

            # Generate session ID
            session_id = f"session-{random.randint(1000, 9999)}"

            # Select random source chapters
            source_chapters = random.choice(SOURCE_CHAPTERS)

            # Generate confidence score (mostly high, some low)
            confidence_score = random.uniform(0.6, 0.98)

            # Generate optional selected context
            selected_context = random.choice([None, "Zero Moment Point is..."]) if random.random() > 0.7 else None

            # Generate timestamps (random dates in the last 30 days)
            days_ago = random.randint(0, 30)
            timestamp = datetime.utcnow() - timedelta(days=days_ago)

            # Generate performance metrics
            query_duration_ms = random.uniform(800, 3500)  # 0.8 to 3.5 seconds
            retrieval_duration_ms = random.uniform(50, 200)  # 50 to 200 ms
            generation_duration_ms = query_duration_ms - retrieval_duration_ms  # Remaining time

            # Save the query
            await postgres_service.save_query(
                question=question,
                response_text=response,
                session_id=session_id,
                source_chapters=source_chapters,
                confidence_score=confidence_score,
                selected_context=selected_context,
                query_duration_ms=query_duration_ms,
                retrieval_duration_ms=retrieval_duration_ms,
                generation_duration_ms=generation_duration_ms,
            )

            if (i + 1) % 10 == 0:
                logger.info(f"  ✅ Seeded {i + 1}/{num_samples} queries")

        logger.info(f"✅ Successfully seeded {num_samples} sample queries")


async def main() -> None:
    """Main function to run the seeding script."""
    # Get database URL from environment or use default
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        logger.error("❌ DATABASE_URL environment variable not set")
        return

    logger.info("🚀 Starting analytics data seeding...")

    try:
        await seed_database(database_url, num_samples=50)
        logger.info("✅ Analytics data seeding completed successfully!")
    except Exception as e:
        logger.error(f"❌ Analytics data seeding failed: {e}")
        raise


if __name__ == "__main__":
    asyncio.run(main())