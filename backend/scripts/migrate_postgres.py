#!/usr/bin/env python3
"""Database migration script for creating chat_queries table with proper indexes."""
import asyncio
import logging
import os
from typing import Optional

from sqlalchemy import create_engine, text
from sqlalchemy.ext.asyncio import create_async_engine

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def create_chat_queries_table(database_url: str) -> None:
    """Create the chat_queries table with proper indexes."""
    # Create async engine
    engine = create_async_engine(database_url)

    async with engine.connect() as conn:
        # Create the chat_queries table
        create_table_sql = """
        CREATE TABLE IF NOT EXISTS chat_queries (
            id SERIAL PRIMARY KEY,
            question TEXT NOT NULL,
            selected_context TEXT,
            session_id VARCHAR(50) NOT NULL,
            timestamp TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
            response_text TEXT NOT NULL,
            source_chapters JSON,
            confidence_score FLOAT NOT NULL,
            query_duration_ms FLOAT,
            retrieval_duration_ms FLOAT,
            generation_duration_ms FLOAT
        );
        """
        await conn.execute(text(create_table_sql))
        await conn.commit()
        logger.info("✅ Created chat_queries table")

    # Close the connection
    await engine.dispose()


async def create_indexes(database_url: str) -> None:
    """Create indexes on the chat_queries table for better performance."""
    engine = create_async_engine(database_url)

    async with engine.connect() as conn:
        # Create index on session_id
        session_idx_sql = """
        CREATE INDEX IF NOT EXISTS idx_chat_queries_session_id
        ON chat_queries(session_id);
        """
        await conn.execute(text(session_idx_sql))
        await conn.commit()
        logger.info("✅ Created index on session_id")

        # Create index on timestamp
        timestamp_idx_sql = """
        CREATE INDEX IF NOT EXISTS idx_chat_queries_timestamp
        ON chat_queries(timestamp);
        """
        await conn.execute(text(timestamp_idx_sql))
        await conn.commit()
        logger.info("✅ Created index on timestamp")

        # Create index on confidence_score
        confidence_idx_sql = """
        CREATE INDEX IF NOT EXISTS idx_chat_queries_confidence_score
        ON chat_queries(confidence_score);
        """
        await conn.execute(text(confidence_idx_sql))
        await conn.commit()
        logger.info("✅ Created index on confidence_score")

    # Close the connection
    await engine.dispose()


async def main() -> None:
    """Main migration function."""
    # Get database URL from environment or use default
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        logger.error("❌ DATABASE_URL environment variable not set")
        return

    logger.info("🚀 Starting database migration...")

    try:
        # Create the table
        await create_chat_queries_table(database_url)

        # Create indexes
        await create_indexes(database_url)

        logger.info("✅ Database migration completed successfully!")

    except Exception as e:
        logger.error(f"❌ Database migration failed: {e}")
        raise


if __name__ == "__main__":
    asyncio.run(main())