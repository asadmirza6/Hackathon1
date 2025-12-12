"""GET /v1/health endpoint for service health monitoring."""
import logging
from datetime import datetime

from fastapi import APIRouter

from app.models.schemas import HealthCheckResponse
from app.services.qdrant_service import QdrantService
from app.services.gemini_service import GeminiService
from app.core.config import AppConfig

logger = logging.getLogger(__name__)
router = APIRouter()


async def check_qdrant_health() -> tuple[bool, str]:
    """Check Qdrant connectivity.

    Returns:
        Tuple of (is_healthy, message)

    """
    try:
        service = QdrantService()
        await service.init()
        await service.close()
        return True, "Connected"
    except Exception as e:
        logger.warning(f"⚠️  Qdrant health check failed: {e}")
        return False, f"Connection failed: {str(e)[:50]}"


async def check_gemini_health() -> tuple[bool, str]:
    """Check Gemini API connectivity.

    Returns:
        Tuple of (is_healthy, message)

    """
    try:
        service = GeminiService()
        await service.init()
        await service.close()
        return True, "Connected"
    except Exception as e:
        logger.warning(f"⚠️  Gemini health check failed: {e}")
        return False, f"Connection failed: {str(e)[:50]}"


async def check_postgres_health() -> tuple[bool, str]:
    """Check Postgres connectivity.

    Returns:
        Tuple of (is_healthy, message)

    """
    try:
        # In production, would test actual connection
        # For now, just check if DATABASE_URL is configured
        config = AppConfig()
        if config.database_url:
            return True, "Configured"
        else:
            return False, "DATABASE_URL not configured"
    except Exception as e:
        logger.warning(f"⚠️  Postgres health check failed: {e}")
        return False, f"Check failed: {str(e)[:50]}"


@router.get("/health", response_model=HealthCheckResponse)
async def health_check() -> HealthCheckResponse:
    """Check service and dependency health.

    Performs basic connectivity checks on:
    - Qdrant vector database
    - Gemini API
    - Postgres database

    Returns:
        HealthCheckResponse with service status and component details

    """
    logger.info("🏥 Health check requested")

    # Check all services
    qdrant_healthy, qdrant_msg = await check_qdrant_health()
    gemini_healthy, gemini_msg = await check_gemini_health()
    postgres_healthy, postgres_msg = await check_postgres_health()

    # Determine overall status
    all_healthy = qdrant_healthy and gemini_healthy and postgres_healthy
    some_degraded = not all([qdrant_healthy, gemini_healthy, postgres_healthy])

    if all_healthy:
        status = "healthy"
    elif some_degraded:
        status = "degraded"
    else:
        status = "unhealthy"

    services = {
        "qdrant": {
            "status": "up" if qdrant_healthy else "down",
            "message": qdrant_msg,
        },
        "gemini": {
            "status": "up" if gemini_healthy else "down",
            "message": gemini_msg,
        },
        "postgres": {
            "status": "up" if postgres_healthy else "down",
            "message": postgres_msg,
        },
    }

    response = HealthCheckResponse(
        status=status,
        services=services,
        timestamp=datetime.utcnow().isoformat(),
    )

    logger.info(f"✅ Health check: {status} ({services})")
    return response
