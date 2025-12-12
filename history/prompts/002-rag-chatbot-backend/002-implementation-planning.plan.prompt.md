---
id: 002
title: Implementation Planning
stage: plan
date: 2025-12-09
surface: agent
model: claude-haiku-4-5-20251001
feature: 002-rag-chatbot-backend
branch: 002-rag-chatbot-backend
user: architect
command: /sp.plan
labels: [rag, chatbot, backend, architecture, planning]
links:
  spec: specs/002-rag-chatbot-backend/spec.md
  plan: specs/002-rag-chatbot-backend/plan.md
  adr: null
  pr: null
---

# Prompt History Record: Implementation Planning

## Session Summary

Executed `/sp.plan` command to produce comprehensive implementation architecture for the RAG chatbot backend. This planning session established the technical design, project structure, and integration strategy for the backend service that will power the embedded chatbot across all Physical AI course pages.

## Planning Deliverables

### 1. Technical Context Definition

- **Language**: Python 3.11+
- **Framework**: FastAPI 0.109+
- **Vector DB**: Qdrant Cloud
- **LLM**: Gemini API
- **Database**: Neon Postgres
- **Performance Target**: <3 seconds p95 response time
- **Concurrency**: 100 concurrent users

### 2. Project Structure Design

**Backend Code Organization**:
```
backend/
├── app/
│   ├── core/         (config, logging)
│   ├── models/       (Pydantic schemas)
│   ├── services/     (qdrant, gemini, rag, postgres)
│   ├── api/          (v1 endpoints)
│   └── utils/        (validators, exceptions)
├── tests/            (unit, integration, E2E)
├── scripts/          (seeding, migrations)
└── docker/           (containerization)
```

**Specification Documentation**:
```
specs/002-rag-chatbot-backend/
├── spec.md           (requirements - COMPLETE)
├── plan.md           (architecture - COMPLETE)
├── research.md       (Phase 0 - TBD)
├── data-model.md     (Phase 1 - TBD)
├── contracts/        (API specs - Phase 1 TBD)
└── quickstart.md     (developer guide - Phase 1 TBD)
```

### 3. RAG Pipeline Architecture

Designed 6-stage processing pipeline:
1. **Input Validation**: Query length, session ID, context
2. **Vector Retrieval**: Top-5 similar chunks from Qdrant + metadata
3. **RAG Augmentation**: Build system prompt with scope constraints
4. **Generation**: Gemini API call with augmented prompt
5. **Source Attribution**: Extract lesson/section references
6. **Async Logging**: Non-blocking write to Postgres

### 4. API Contract Design

**Endpoints**:
- POST /v1/query: Submit question + optional context
- GET /v1/health: Monitoring health check
- GET /v1/logs: Admin query access to interaction logs

**Response Format**:
```json
{
  "response_text": "answer...",
  "source_references": [{chapter, lesson, section}],
  "confidence_score": 0.92,
  "timestamp": "ISO-8601"
}
```

### 5. Data Models

**Postgres Schema**:
- chat_queries table: question, context, session_id, response, timestamp, sources, confidence

**Qdrant Vectors**:
- 768-dimensional embeddings from Gemini
- Metadata: chapter (1-4), lesson (1-2), section (heading)
- ~500 chunks from 8 lessons

### 6. Key Architectural Decisions

1. **Async-First Design**: Non-blocking I/O throughout, async Postgres writes
2. **Strict Scope Limiting**: System prompt explicitly forbids external knowledge
3. **Minimal Dependencies**: Only FastAPI, Qdrant client, Gemini client
4. **Single Responsibility**: Each service handles one concern only
5. **Graceful Degradation**: User-friendly errors, don't break UI on failures

### 7. Constitution Alignment

✅ **RAG-First**: Query → Retrieval → Augmentation → Generation
✅ **Content-Source-of-Truth**: Only 8 course lessons used
✅ **Embedded-First UX**: Widget embedded in Docusaurus pages
✅ **Tech Stack**: Python + FastAPI + Gemini + Qdrant + Postgres
✅ **API Contracts**: REST with JSON schemas
✅ **Security**: All secrets via environment variables

## Integration Points

- **Docusaurus Book** (frontend): REST API calls from embedded chat widget
- **Qdrant Cloud**: Vector embeddings and semantic search
- **Gemini API**: LLM response generation
- **Neon Postgres**: Query logging and analytics

## Performance Characteristics

- Qdrant vector search: ~50-100ms
- Gemini API call: ~1-2 seconds
- Postgres insert: ~20-50ms (async, non-blocking)
- **Total p95**: <3 seconds (spec requirement)
- Concurrency: 100 users simultaneously

## Error Handling Strategy

1. Qdrant unavailable: User-friendly "Vector search temporarily unavailable"
2. Gemini API error: "Unable to generate response, please try again"
3. Postgres error: Log async, don't block user response
4. Invalid input: 400 with validation error details
5. Rate limit: 429 with retry-after header

## Security & Secrets

- Gemini API key: `GEMINI_API_KEY` env var
- Qdrant credentials: `QDRANT_API_KEY`, `QDRANT_URL` env vars
- Postgres connection: `DATABASE_URL` env var
- .env file: git-ignored locally
- No hardcoded secrets in code

## Testing Strategy

- **Unit Tests**: Individual services and models
- **Integration Tests**: Full pipeline with mocked externals
- **E2E Tests**: Complete flow with test data
- **Load Tests**: 100+ concurrent users
- **Hallucination Tests**: Verify book-content-only responses

## Phase 0: Research Topics (Next)

6 key research areas to document:
1. Gemini API embedding generation patterns
2. Qdrant filtering and metadata queries
3. FastAPI async production patterns
4. Neon Postgres connection pooling
5. Vector similarity scoring and thresholds
6. Docusaurus widget injection mechanisms

## Phase 1: Design & Contracts (After Research)

Will generate:
1. `data-model.md`: Complete entity schemas
2. `contracts/`: OpenAPI specs and Postgres schema
3. `quickstart.md`: Developer setup guide

## Phase 2: Implementation (After Design)

Will generate `tasks.md` with 50+ implementation tasks:
- Backend service scaffolding
- API endpoint implementation
- Service layer integration
- Comprehensive test coverage
- Deployment & monitoring

## Artifacts Generated

```
specs/002-rag-chatbot-backend/
└── plan.md (248 lines)
    ├── Technical context definition
    ├── Project structure design
    ├── RAG pipeline architecture (6 stages)
    ├── API endpoint specifications
    ├── Data model design
    ├── Architectural decisions (5 key)
    ├── Integration points
    ├── Performance profile
    ├── Error handling strategy
    ├── Security approach
    ├── Testing strategy
    └── Phase progression
```

## Quality Metrics

✅ **Complete**: All sections filled with concrete details
✅ **Actionable**: 50+ implementation tasks anticipated
✅ **Traceable**: Each component linked to spec requirements
✅ **Architecture-Sound**: Proven patterns (async, RAG, microservices)
✅ **Constitution-Compliant**: All 6 constitution principles addressed

## Next Steps

1. Run `/sp.tasks` to generate 50+ detailed implementation tasks
2. Or run another `/sp.plan` iteration if clarifications needed
3. Implementation ready: Python 3.11+, FastAPI, Pydantic, pytest

## Branch & File Paths

- **Branch**: `002-rag-chatbot-backend`
- **Plan File**: `specs/002-rag-chatbot-backend/plan.md`
- **Status**: ✅ Ready for task generation

---

**Planning Status**: ✅ COMPLETE AND READY FOR IMPLEMENTATION
**Architecture**: ✅ SOUND AND CONSTITUTION-COMPLIANT
**Next Phase**: Generate detailed implementation tasks via `/sp.tasks`
