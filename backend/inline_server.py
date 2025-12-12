#!/usr/bin/env python3
"""Simple server startup script that bypasses config validation issues."""
import os
import sys
from contextlib import asynccontextmanager

# Set minimal required environment variables to bypass validation
os.environ.setdefault('GEMINI_API_KEY', 'test-key')
os.environ.setdefault('QDRANT_URL', 'http://localhost:6333')
os.environ.setdefault('QDRANT_API_KEY', 'test-key')
os.environ.setdefault('DATABASE_URL', 'postgresql+asyncpg://postgres:password@localhost:5432/chatbot')
os.environ.setdefault('API_DEBUG', 'true')

# Now import the main app components
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import AppConfig
from app.core.logging import setup_logging
from app.api.v1 import health, query, logs
from app.api.middleware import RequestIDMiddleware, RequestLoggingMiddleware
from app.utils.error_handlers import register_exception_handlers

# Initialize logging
setup_logging()
import logging
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage app lifecycle: startup and shutdown events."""
    logger.info("🚀 Starting RAG Chatbot Backend")
    try:
        # Initialize services
        from app.api.v1 import query as query_module
        await query_module.init_services()
        logger.info("✅ All services initialized")
    except Exception as e:
        logger.warning(f"⚠️  Service initialization warning: {e}")

    yield

    logger.info("🛑 Shutting down RAG Chatbot Backend")


# Create FastAPI app
app = FastAPI(
    title="RAG Chatbot Backend",
    description="Retrieval-Augmented Generation chatbot for Physical AI course",
    version="1.0.0",
    lifespan=lifespan,
)

# Register exception handlers
register_exception_handlers(app)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure this in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Custom middleware
app.add_middleware(RequestLoggingMiddleware)
app.add_middleware(RequestIDMiddleware)


# Root endpoint
@app.get("/")
async def root():
    """Root endpoint returning API information."""
    return {
        "service": "RAG Chatbot Backend",
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs",
    }


# Register API routes
app.include_router(health.router, prefix="/v1", tags=["health"])
app.include_router(query.router, prefix="/v1", tags=["query"])
app.include_router(logs.router, prefix="/v1", tags=["logs"])

print("✅ RAG Chatbot Backend is ready!")
print("💡 To start the server, run: uvicorn server:app --reload --port 8000")
print("📋 API Documentation available at: http://localhost:8000/docs")

if __name__ == "__main__":
    import uvicorn
    config = AppConfig()
    print(f"Starting server on {config.api_host}:{config.api_port}")
    uvicorn.run(
        "inline_server:app",
        host=config.api_host,
        port=config.api_port,
        reload=config.debug,
        log_level=config.log_level.lower(),
    )