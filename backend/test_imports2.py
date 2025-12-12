#!/usr/bin/env python3
"""Simple test to verify the application components work without env vars."""
import os

# Clear environment variables that might interfere
for var in ['GEMINI_API_KEY', 'QDRANT_URL', 'QDRANT_API_KEY', 'DATABASE_URL', 'API_DEBUG']:
    if var in os.environ:
        del os.environ[var]

# Set minimal environment variables to avoid validation errors
os.environ['GEMINI_API_KEY'] = 'test-key'
os.environ['QDRANT_URL'] = 'http://localhost:6333'
os.environ['QDRANT_API_KEY'] = 'test-key'
os.environ['DATABASE_URL'] = 'sqlite+aiosqlite:///./test.db'
os.environ['API_DEBUG'] = 'true'  # This will be converted to bool by the config

try:
    # Import core modules to verify they work
    from app.core.config import AppConfig
    print("[SUCCESS] AppConfig imported successfully")

    # Try to create config instance
    config = AppConfig()
    print(f"[SUCCESS] AppConfig instance created successfully: debug={config.debug}")

    # Test other core modules
    from app.core import logging
    print("[SUCCESS] Logging module imported successfully")

    from app.core import constants
    print("[SUCCESS] Constants module imported successfully")

    print("[SUCCESS] All basic imports work correctly")

except Exception as e:
    print(f"[ERROR] Error: {e}")
    import traceback
    traceback.print_exc()