"""Logging configuration for the application.

Sets up structured logging with JSON format for production environments.
"""
import json
import logging
import sys
from datetime import datetime
from typing import Any, Dict

import os


def setup_logging() -> None:
    """Configure structured logging for the application."""
    log_level = os.getenv("LOG_LEVEL", "info").upper()

    # Create root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)

    # Remove existing handlers
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)

    # Console handler with JSON formatter for production
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(log_level)

    environment = os.getenv("ENVIRONMENT", "development")
    if environment == "production":
        formatter = JsonFormatter()
    else:
        formatter = logging.Formatter(
            fmt="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )

    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)


class JsonFormatter(logging.Formatter):
    """JSON log formatter for structured logging."""

    def format(self, record: logging.LogRecord) -> str:
        """Format log record as JSON."""
        log_data: Dict[str, Any] = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }

        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)

        if hasattr(record, "extra"):
            log_data.update(record.extra)

        return json.dumps(log_data)
