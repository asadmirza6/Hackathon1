"""App configuration module for core settings and environment management."""
import os
from typing import Optional

from pydantic_settings import BaseSettings


class AppConfig(BaseSettings):
    """Application configuration with environment variable loading."""

    # API
    api_host: str = os.getenv("API_HOST", "0.0.0.0")
    api_port: int = int(os.getenv("API_PORT", "8000"))
    debug: bool = os.getenv("API_DEBUG", "false").lower() == "true"
    log_level: str = os.getenv("LOG_LEVEL", "info")
    environment: str = os.getenv("ENVIRONMENT", "development")

    # External Services - Gemini
    gemini_api_key: str = os.getenv("GEMINI_API_KEY", "")

    # External Services - Qdrant
    qdrant_url: str = os.getenv("QDRANT_URL", "")
    qdrant_api_key: str = os.getenv("QDRANT_API_KEY", "")

    # External Services - Postgres
    database_url: str = os.getenv("DATABASE_URL", "")

    # Application Settings
    pythonpath: str = os.getenv("PYTHONPATH", ".")

    class Config:
        """Pydantic config."""

        env_file = ".env"
        case_sensitive = False

    def __init__(self):
        """Initialize config and validate required fields."""
        super().__init__()
        self._validate_required_fields()

    def _validate_required_fields(self) -> None:
        """Validate that all required environment variables are set."""
        required = ["gemini_api_key", "qdrant_url", "qdrant_api_key", "database_url"]
        missing = [field for field in required if not getattr(self, field)]
        if missing:
            raise ValueError(
                f"Missing required environment variables: {', '.join(missing)}"
            )
