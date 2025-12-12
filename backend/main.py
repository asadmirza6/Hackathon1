"""
FastAPI application entry point for RAG Chatbot Backend.

Initializes the FastAPI app with CORS middleware, middleware stack,
and registers all API routes for the RAG chatbot service.
"""
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import AppConfig
from app.core.logging import setup_logging
from app.api.v1 import health, query, logs
from app.api.middleware import RequestIDMiddleware, RequestLoggingMiddleware
from app.utils.error_handlers import register_exception_handlers

# Initialize logging
setup_logging()
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


if __name__ == "__main__":
    import uvicorn

    config = AppConfig()
    uvicorn.run(
        "main:app",
        host=config.api_host,
        port=config.api_port,
        reload=config.debug,
        log_level=config.log_level.lower(),
    )
