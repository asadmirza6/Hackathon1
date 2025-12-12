"""
Application configuration module.

Loads and validates environment variables for the RAG Chatbot Backend.
Provides centralized configuration management through Pydantic Settings.
"""
import os
import sys
from typing import Optional
from pydantic_settings import BaseSettings
from pydantic import field_validator, ValidationError


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # API Configuration
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    debug: bool = False
    log_level: str = "info"
    environment: str = "development"

    # External Services
    gemini_api_key: str
    qdrant_url: str
    qdrant_api_key: str
    database_url: str
    admin_token: Optional[str] = None

    @field_validator('gemini_api_key')
    @classmethod
    def validate_gemini_api_key(cls, v):
        """Validate Gemini API key is present and not empty."""
        if not v or v == "your-gemini-api-key-here":
            print("❌ Error: GEMINI_API_KEY environment variable is required and cannot be the default placeholder value", file=sys.stderr)
            sys.exit(1)
        if not v.strip():
            print("❌ Error: GEMINI_API_KEY environment variable cannot be empty", file=sys.stderr)
            sys.exit(1)
        return v

    @field_validator('qdrant_url')
    @classmethod
    def validate_qdrant_url(cls, v):
        """Validate Qdrant URL is present and not empty."""
        if not v or v == "https://your-cluster-url.qdrant.tech:6333":
            print("❌ Error: QDRANT_URL environment variable is required and cannot be the default placeholder value", file=sys.stderr)
            sys.exit(1)
        if not v.strip():
            print("❌ Error: QDRANT_URL environment variable cannot be empty", file=sys.stderr)
            sys.exit(1)
        if not v.startswith(('http://', 'https://')):
            print("❌ Error: QDRANT_URL must start with http:// or https://", file=sys.stderr)
            sys.exit(1)
        return v

    @field_validator('qdrant_api_key')
    @classmethod
    def validate_qdrant_api_key(cls, v):
        """Validate Qdrant API key is present and not empty."""
        if not v or v == "your-qdrant-api-key-here":
            print("❌ Error: QDRANT_API_KEY environment variable is required and cannot be the default placeholder value", file=sys.stderr)
            sys.exit(1)
        if not v.strip():
            print("❌ Error: QDRANT_API_KEY environment variable cannot be empty", file=sys.stderr)
            sys.exit(1)
        return v

    @field_validator('database_url')
    @classmethod
    def validate_database_url(cls, v):
        """Validate Database URL is present and not empty."""
        if not v or v == "postgresql+asyncpg://username:password@host:port/database_name":
            print("❌ Error: DATABASE_URL environment variable is required and cannot be the default placeholder value", file=sys.stderr)
            sys.exit(1)
        if not v.strip():
            print("❌ Error: DATABASE_URL environment variable cannot be empty", file=sys.stderr)
            sys.exit(1)
        if not v.startswith('postgresql'):
            print("❌ Error: DATABASE_URL must start with 'postgresql' for Postgres connection", file=sys.stderr)
            sys.exit(1)
        return v

    @field_validator('admin_token')
    @classmethod
    def validate_admin_token(cls, v):
        """Validate Admin token if provided."""
        if v is not None:
            if v == "your-secure-admin-token-here":
                print("❌ Warning: ADMIN_TOKEN is using the default placeholder value. This should be changed in production.", file=sys.stderr)
            if len(v.strip()) < 8:
                print("❌ Error: ADMIN_TOKEN should be at least 8 characters long for security", file=sys.stderr)
                sys.exit(1)
        return v

    class Config:
        """Pydantic config."""

        env_file = ".env"
        case_sensitive = False


def validate_environment():
    """Validate all required environment variables are present and correct at startup."""
    try:
        # This will trigger validation of all fields
        settings_instance = Settings()
        print("✅ All environment variables validated successfully")
        return settings_instance
    except ValidationError as e:
        print(f"❌ Configuration validation error: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"❌ Environment variable validation error: {e}", file=sys.stderr)
        sys.exit(1)


# Validate environment variables at import time
settings = validate_environment()
