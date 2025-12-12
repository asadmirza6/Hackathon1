# Implementation Plan: RAG Chatbot Backend

**Branch**: `002-rag-chatbot-backend` | **Date**: 2025-12-09 | **Spec**: [specs/002-rag-chatbot-backend/spec.md](spec.md)

## Summary

Build a retrieval-augmented generation (RAG) chatbot backend for the Physical AI course using FastAPI, Gemini API, and Qdrant embeddings. The chatbot answers user queries by retrieving relevant content from 8 course lessons, generating contextual responses, and logging all interactions for analytics. Chatbot will be embedded as a widget on all Docusaurus book pages and strictly limited to course content (no external knowledge injection).

## Technical Context

**Language/Version**: Python 3.11+
**Primary Dependencies**: FastAPI 0.109+, Pydantic 2.x, qdrant-client 2.7+, google-generativeai 0.3+, sqlalchemy 2.0+, asyncpg 0.29+
**Storage**: Qdrant Cloud (vector embeddings) + Neon Postgres (query logs)
**Testing**: pytest 7.x + pytest-asyncio, httpx for async HTTP testing
**Target Platform**: Linux server (Docker-deployable), serverless compatible
**Project Type**: Backend API service (Python FastAPI microservice)
**Performance Goals**: <3 second response time p95, 100 concurrent users
**Constraints**: Response must only use content from 8 lessons, <500MB memory per instance
**Scale/Scope**: Single backend service, ~2000 LOC core logic

## Constitution Check

**Status**: ✅ GATE PASSED

✅ **RAG-First Architecture**: Query → Retrieval → Augmentation → Generation with traceability
✅ **Content-Source-of-Truth**: Book markdown files are authoritative source
✅ **Embedded-First UX**: Chatbot lives inside Docusaurus pages
✅ **Tech Stack Adherence**: Python + FastAPI + Gemini + Qdrant + Postgres
✅ **API Contracts**: REST endpoints with JSON schemas
✅ **Security**: Secrets via environment variables only

## Project Structure

### Documentation

```
specs/002-rag-chatbot-backend/
├── spec.md              # Feature specification (COMPLETE)
├── plan.md              # This file (COMPLETE)
├── research.md          # Phase 0: Technical decisions (TBD)
├── data-model.md        # Phase 1: Entity definitions (TBD)
├── contracts/           # Phase 1: API specifications (TBD)
└── quickstart.md        # Phase 1: Developer guide (TBD)
```

### Source Code Structure

```
backend/
├── main.py
├── config.py
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
│
├── app/
│   ├── core/            # Config, logging, constants
│   ├── models/          # Pydantic models
│   ├── services/        # Business logic layer
│   │   ├── qdrant_service.py
│   │   ├── gemini_service.py
│   │   ├── rag_service.py (orchestrator)
│   │   └── postgres_service.py
│   ├── api/
│   │   ├── v1/
│   │   │   ├── query.py (POST /v1/query)
│   │   │   ├── health.py (GET /v1/health)
│   │   │   └── logs.py (GET /v1/logs)
│   │   └── middleware.py
│   └── utils/           # Validators, exceptions, helpers
│
├── tests/
│   ├── conftest.py
│   ├── test_rag_service.py
│   ├── test_query_endpoint.py
│   ├── test_gemini_service.py
│   └── test_postgres_service.py
│
└── scripts/
    ├── seed_embeddings.py
    ├── migrate_postgres.py
    └── test_integration.py
```

## RAG Pipeline Architecture

```
User Query
    ↓
[1] Input Validation (length, session_id, context)
    ↓
[2] Vector Retrieval from Qdrant
    - Convert query to embedding
    - Search top-5 similar chunks
    - Return: text + lesson/section metadata + similarity score
    ↓
[3] RAG Augmentation
    - Build prompt with explicit constraints
    - Include: retrieved chunks + system instruction
    - Instruction: "Answer ONLY from provided content"
    ↓
[4] Generation via Gemini API
    - Call genai.generate_content()
    - Extract response text
    - Validate: response uses only retrieved content
    ↓
[5] Source Attribution
    - Extract lesson/section references
    - Build citations: "From Chapter X, Lesson Y: [Section]"
    ↓
[6] Async Logging to Postgres
    - Store: query, response, session_id, timestamp
    - Non-blocking (doesn't delay response)
    ↓
Return Response with Sources + Confidence Score
```

## API Endpoints

### POST /v1/query
Query the RAG chatbot with optional context.

**Request**:
```json
{
  "question": "What is ZMP in bipedal walking?",
  "selected_context": "Zero Moment Point is...",
  "session_id": "user-session-123"
}
```

**Response**:
```json
{
  "response_text": "Zero Moment Point (ZMP) is the point...",
  "source_references": [
    {
      "chapter": 3,
      "lesson": 2,
      "section": "Walking Pattern Generation"
    }
  ],
  "confidence_score": 0.92,
  "timestamp": "2025-12-09T13:45:23Z"
}
```

### GET /v1/health
Simple health check for monitoring.

### GET /v1/logs (admin)
Query all logged interactions with filters.

## Key Architectural Decisions

1. **Async-First**: FastAPI async/await, non-blocking logging
2. **Strict Scope Limiting**: System prompt forbids external knowledge
3. **Minimal Dependencies**: Only essential packages (FastAPI, Qdrant client, Gemini client)
4. **Single Responsibility**: Each service handles one concern
5. **Error Gracefully**: User-friendly error messages, don't break UI

## Data Schema

**chat_queries (Postgres)**:
- id: SERIAL PRIMARY KEY
- question: TEXT
- selected_context: TEXT (nullable)
- session_id: VARCHAR(50)
- timestamp: TIMESTAMPTZ
- response_text: TEXT
- source_chapters: TEXT (JSON array)
- confidence_score: FLOAT

**Lesson Embeddings (Qdrant)**:
- Vector: 768-dimensional (from Gemini embeddings)
- Metadata: {chapter: 1-4, lesson: 1-2, section: "heading"}
- Stored per lesson chunk (~500 chunks total)

## Integration Points

- **Docusaurus**: REST API calls from embedded chat widget
- **Qdrant Cloud**: Vector similarity search (authenticated)
- **Gemini API**: LLM response generation (authenticated)
- **Neon Postgres**: Query logging and analytics (authenticated)

## Performance Profile

- Qdrant search: ~50-100ms
- Gemini API: ~1-2 seconds
- Postgres insert: ~20-50ms (async)
- **Total p95**: <3 seconds

## Error Handling

1. Qdrant down → "Vector search temporarily unavailable"
2. Gemini error → "Unable to generate response"
3. Postgres error → Log async, don't block user
4. Invalid input → 400 with validation details
5. Rate limit → 429 with retry header

## Security

- All credentials: environment variables (.env git-ignored)
- Gemini: `GEMINI_API_KEY`
- Qdrant: `QDRANT_API_KEY`, `QDRANT_URL`
- Postgres: `DATABASE_URL`
- No hardcoded secrets in code

## Testing Strategy

- **Unit Tests**: Services, models, validators
- **Integration Tests**: End-to-end with mocked externals
- **E2E Tests**: Full pipeline with test data
- **Load Tests**: 100+ concurrent users
- **Hallucination Tests**: Verify book-content-only responses

## Phase 0: Research (Next Steps)

Research topics to document:
1. Gemini API embedding generation & generation API patterns
2. Qdrant query filtering with metadata
3. FastAPI async patterns for production
4. Neon Postgres connection pooling
5. Vector similarity scoring and threshold tuning
6. Docusaurus widget injection patterns

## Phase 1: Design & Contracts (After Research)

Will generate:
1. `data-model.md`: Complete entity schemas with relationships
2. `contracts/query-api.md`: OpenAPI spec for query endpoint
3. `contracts/logging-schema.md`: Postgres schema with indexes
4. `quickstart.md`: Developer environment setup guide

## Phase 2: Implementation (After Design)

Will generate `tasks.md` with 50+ tasks across:
- Backend service scaffolding
- API endpoint implementation
- Service layer integration
- Test coverage (unit + integration + E2E)
- Deployment & monitoring setup

---

**Status**: ✅ IMPLEMENTATION PLAN COMPLETE
**Gate Status**: ✅ Constitution check passed
**Next Command**: `/sp.tasks` to generate detailed implementation breakdown
