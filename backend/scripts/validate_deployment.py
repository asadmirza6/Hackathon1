#!/usr/bin/env python3
"""Deployment validation script for the RAG Chatbot Backend.

This script validates that all required services and configurations
are properly set up before starting the production server.
"""
import asyncio
import sys
import os
from typing import Dict, List, Tuple
import requests
from google import genai
import asyncpg
from qdrant_client import QdrantClient
from qdrant_client.http import models
from qdrant_client.http.exceptions import UnexpectedResponse


async def validate_gemini_api(api_key: str) -> Tuple[bool, str]:
    """Validate that the Gemini API key works properly."""
    try:
        # Initialize the Gemini client
        genai.configure(api_key=api_key)

        # Test the API with a simple request
        model = genai.GenerativeModel('gemini-pro')
        response = await model.generate_content_async("Hello, are you working?")

        if response and response.text:
            return True, "Gemini API key is valid and working"
        else:
            return False, "Gemini API returned empty response"
    except Exception as e:
        return False, f"Gemini API validation failed: {str(e)}"


async def validate_qdrant_connection(url: str, api_key: str) -> Tuple[bool, str]:
    """Validate that Qdrant is reachable and credentials work."""
    try:
        # Create Qdrant client
        client = QdrantClient(
            url=url,
            api_key=api_key,
            timeout=10
        )

        # Test connection by trying to list collections
        collections = client.get_collections()

        return True, f"Qdrant connection successful, found {len(collections.collections)} collections"
    except UnexpectedResponse as e:
        if e.status_code == 401:
            return False, "Qdrant authentication failed - invalid API key"
        elif e.status_code == 403:
            return False, "Qdrant access forbidden - check API key permissions"
        else:
            return False, f"Qdrant connection failed with status {e.status_code}: {e.message}"
    except Exception as e:
        return False, f"Qdrant connection failed: {str(e)}"


async def validate_postgres_connection(database_url: str) -> Tuple[bool, str]:
    """Validate that Postgres is reachable and credentials work."""
    try:
        # Create connection pool
        pool = await asyncpg.create_pool(database_url, command_timeout=10)

        # Test connection with a simple query
        async with pool.acquire() as connection:
            result = await connection.fetchval("SELECT version();")

            if result:
                await pool.close()
                return True, f"Postgres connection successful: {result.split(',')[0] if ',' in result else result}"
            else:
                await pool.close()
                return False, "Postgres connection successful but version query failed"
    except asyncpg.exceptions.AuthenticationError:
        return False, "Postgres authentication failed - invalid credentials"
    except asyncpg.exceptions.CannotConnectNowError:
        return False, "Postgres is not ready to accept connections"
    except Exception as e:
        return False, f"Postgres connection failed: {str(e)}"


def validate_environment_variables() -> Tuple[bool, List[str]]:
    """Validate that all required environment variables are set."""
    required_vars = [
        "GEMINI_API_KEY",
        "QDRANT_API_KEY",
        "QDRANT_URL",
        "DATABASE_URL"
    ]

    missing_vars = []
    issues = []

    for var in required_vars:
        value = os.getenv(var)
        if not value or value.strip() == "":
            missing_vars.append(var)
        elif var == "GEMINI_API_KEY" and value == "your-gemini-api-key-here":
            issues.append(f"{var} is set to default placeholder value")
        elif var == "QDRANT_URL" and value == "https://your-cluster-url.qdrant.tech:6333":
            issues.append(f"{var} is set to default placeholder value")
        elif var == "QDRANT_API_KEY" and value == "your-qdrant-api-key-here":
            issues.append(f"{var} is set to default placeholder value")
        elif var == "DATABASE_URL" and value == "postgresql+asyncpg://username:password@host:port/database_name":
            issues.append(f"{var} is set to default placeholder value")

    all_valid = len(missing_vars) == 0 and len(issues) == 0

    if missing_vars:
        issues.insert(0, f"Missing required environment variables: {', '.join(missing_vars)}")

    return all_valid, issues


async def validate_services_health() -> Dict[str, Tuple[bool, str]]:
    """Validate the health of all external services."""
    print("🔍 Validating external services...")

    # Get environment variables
    gemini_api_key = os.getenv("GEMINI_API_KEY")
    qdrant_url = os.getenv("QDRANT_URL")
    qdrant_api_key = os.getenv("QDRANT_API_KEY")
    database_url = os.getenv("DATABASE_URL")

    results = {}

    # Validate environment variables first
    env_valid, env_issues = validate_environment_variables()
    if not env_valid:
        print("❌ Environment validation failed:")
        for issue in env_issues:
            print(f"   - {issue}")
        return {"environment": (False, "; ".join(env_issues))}

    print("✅ Environment variables validated")

    # Validate each service
    print("⏳ Validating Gemini API...")
    results["gemini"] = await validate_gemini_api(gemini_api_key)
    print(f"   Gemini: {'✅' if results['gemini'][0] else '❌'} {results['gemini'][1]}")

    print("⏳ Validating Qdrant connection...")
    results["qdrant"] = await validate_qdrant_connection(qdrant_url, qdrant_api_key)
    print(f"   Qdrant: {'✅' if results['qdrant'][0] else '❌'} {results['qdrant'][1]}")

    print("⏳ Validating Postgres connection...")
    results["postgres"] = await validate_postgres_connection(database_url)
    print(f"   Postgres: {'✅' if results['postgres'][0] else '❌'} {results['postgres'][1]}")

    return results


async def main():
    """Main function to run the deployment validation."""
    print("🚀 Starting deployment validation...")
    print("=" * 50)

    # Validate all services
    results = await validate_services_health()

    print("=" * 50)
    print("VALIDATION SUMMARY:")
    print("=" * 50)

    all_passed = True
    for service, (success, message) in results.items():
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{service.capitalize():<10} {status:<8} {message}")
        if not success:
            all_passed = False

    print("=" * 50)

    if all_passed:
        print("🎉 All validations passed! Deployment is ready.")
        print("✅ The RAG Chatbot Backend can be safely started.")
        return 0
    else:
        print("💥 Some validations failed!")
        print("❌ Please fix the above issues before starting the production server.")
        print("⚠️  Do not start the server until all validations pass.")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)