#!/usr/bin/env python3
"""Simple test to verify the application components work."""
import os

# Set minimal environment variables to avoid validation errors
os.environ['GEMINI_API_KEY'] = 'test-key'
os.environ['QDRANT_URL'] = 'http://localhost:6333'
os.environ['QDRANT_API_KEY'] = 'test-key'
os.environ['DATABASE_URL'] = 'sqlite+aiosqlite:///./test.db'

try:
    # Import core modules to verify they work
    from app.core.config import AppConfig
    print("[SUCCESS] AppConfig imported successfully")

    # Try to create config instance
    config = AppConfig()
    print("[SUCCESS] AppConfig instance created successfully")

    print("[SUCCESS] All basic imports work correctly")

except Exception as e:
    print(f"[ERROR] Error: {e}")
    import traceback
    traceback.print_exc()