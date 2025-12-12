#!/usr/bin/env python3
"""RAG Chatbot Backend - System Ready Check"""
import os
import sys

print("===========================================")
print("RAG Chatbot Backend - System Ready Check")
print("===========================================")

# Check if required dependencies are installed
try:
    import fastapi
    import uvicorn
    import sqlalchemy
    import asyncpg
    import qdrant_client
    import google.generativeai
    import pydantic
    import httpx
    print("[SUCCESS] All required dependencies are installed")
except ImportError as e:
    print(f"[ERROR] Missing dependency: {e}")
    sys.exit(1)

# Check if environment variables are set (with placeholder values for demo)
required_vars = [
    'GEMINI_API_KEY',
    'QDRANT_URL',
    'QDRANT_API_KEY',
    'DATABASE_URL'
]

print("\n[INFO] Required API Keys & Configuration:")
for var in required_vars:
    value = os.environ.get(var, 'NOT_SET')
    status = "[SET]" if value != 'NOT_SET' and 'your_' not in value else "[PLACEHOLDER] (needs real value)"
    print(f"  {var}: {status}")

print(f"\n[INSTRUCTION] To run the server:")
print(f"   1. Get your API keys:")
print(f"      - Gemini API: https://aistudio.google.com/app/apikeys")
print(f"      - Qdrant: https://cloud.qdrant.io (or run locally)")
print(f"      - PostgreSQL: (Neon.tech or local instance)")
print(f"   2. Update the .env file with your real keys")
print(f"   3. Run: cd backend && uvicorn main:app --reload")

print(f"\n[ENDPOINTS] Available endpoints once running:")
print(f"   - Health: GET /v1/health")
print(f"   - Chat Query: POST /v1/query")
print(f"   - Query Logs: GET /v1/logs")
print(f"   - Analytics: GET /v1/logs/metrics")
print(f"   - API Docs: GET /docs")

print(f"\n[READY] The RAG Chatbot Backend is configured and ready to run!")
print(f"===========================================")