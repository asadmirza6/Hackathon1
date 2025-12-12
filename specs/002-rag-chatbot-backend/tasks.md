# Tasks: RAG Chatbot Backend

**Branch**: `002-rag-chatbot-backend`
**Feature**: RAG Chatbot Backend (002)
**Based On**: [spec.md](spec.md) (3 user stories, 12 FRs) + [plan.md](plan.md) (6-stage RAG pipeline)

**Organization**: Tasks organized by user story (P1 → P2 → P3) to enable independent implementation, testing, and deployment of each story.

**Total Tasks**: 58 implementation tasks across 5 phases

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic FastAPI structure

**Duration Estimate**: Day 1

- [x] T001 Create `backend/` directory structure: app/, tests/, scripts/, docs/ with __init__.py files
- [x] T002 Create `backend/requirements.txt` with core dependencies: fastapi==0.109.0, pydantic==2.5.0, qdrant-client==2.7.0, google-generativeai==0.3.1, sqlalchemy==2.0.23, asyncpg==0.29.0, pytest==7.4.3, pytest-asyncio==0.21.1, python-dotenv==1.0.0, httpx==0.25.2
- [x] T003 Create `backend/.env.example` with template variables: GEMINI_API_KEY, QDRANT_API_KEY, QDRANT_URL, DATABASE_URL, PYTHONPATH
- [x] T004 [P] Create `backend/main.py` with FastAPI app instantiation, CORS middleware, and root health endpoint stub
- [x] T005 [P] Create `backend/config.py` with Settings pydantic model loading env vars: api_key_gemini, qdrant_config, database_url, log_level
- [x] T006 [P] Create `backend/app/core/__init__.py` empty init file
- [x] T007 [P] Create `backend/app/core/config.py` with AppConfig class and environment loader
- [x] T008 [P] Create `backend/app/core/logging.py` with structured logging setup (json format for production)
- [x] T009 [P] Create `backend/app/core/constants.py` with app constants: RAG_CONSTRAINT_PROMPT, QDRANT_VECTOR_SIZE=768, MAX_CONTEXT_LENGTH=4000
- [x] T010 [P] Create `backend/app/__init__.py` empty init file
- [x] T011 [P] Create `backend/app/models/__init__.py` empty init file
- [x] T012 [P] Create `backend/app/services/__init__.py` empty init file
- [x] T013 [P] Create `backend/app/api/__init__.py` empty init file
- [x] T014 [P] Create `backend/app/utils/__init__.py` empty init file
- [x] T015 [P] Create `backend/tests/__init__.py` empty init file
- [x] T016 Create `backend/tests/conftest.py` with pytest fixtures: mock_qdrant_client, mock_gemini_client, mock_postgres_pool, async_client

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before user story implementation

**⚠️ CRITICAL**: No user story work can begin until this phase is COMPLETE

**Duration Estimate**: Day 2

### Database & ORM Foundation

- [x] T017 Create `backend/app/models/database.py` with SQLAlchemy async engine, session factory, and Base declarative class
- [x] T018 Create `backend/app/models/chat_query.py` with SQLAlchemy ChatQuery model: id, question, selected_context, session_id, timestamp, response_text, source_chapters (JSON), confidence_score
- [x] T019 [P] Create `backend/app/utils/validators.py` with validation functions: validate_query_length(min=5, max=2000), validate_session_id(pattern), validate_timestamp()
- [x] T020 [P] Create `backend/app/utils/exceptions.py` with custom exceptions: QdrantUnavailableError, GeminiAPIError, DatabaseError, ValidationError (with HTTPException mapping)

### Service Layer Foundation

- [x] T021 Create `backend/app/services/postgres_service.py` with PostgresService class: async init(), async save_query(), async get_query_logs(), async close() methods
- [x] T022 Create `backend/app/services/qdrant_service.py` with QdrantService class: async init(), async get_client(), async search_similar_chunks(), async close() methods
- [x] T023 Create `backend/app/services/gemini_service.py` with GeminiService class: async init(), async generate_embedding(), async generate_response(), async validate_scope()
- [x] T024 Create `backend/app/services/rag_service.py` orchestrator class (EMPTY - dependency injection stubs only, will be filled in Phase 3+)
- [x] T025 Create `backend/app/utils/rag_prompts.py` with system prompt templates: RAG_SYSTEM_PROMPT (with scope constraint), VALIDATION_PROMPT (for checking hallucinations)

### API Foundation & Middleware

- [x] T026 [P] Create `backend/app/api/middleware.py` with CORS middleware, request ID generator, error handling middleware
- [x] T027 [P] Create `backend/app/api/v1/__init__.py` empty init file
- [x] T028 Create `backend/app/models/schemas.py` with Pydantic request/response schemas: ChatQueryRequest, ChatResponseSchema, SourceReference, HealthCheckResponse

### Error Handling & Logging

- [x] T029 Create `backend/app/utils/error_handlers.py` with FastAPI exception handlers for all custom exceptions (QdrantError → 503, ValidationError → 400, etc.)
- [x] T030 [P] Create `backend/app/utils/logging_utils.py` with request/response logging context managers, query timing decorators

**Checkpoint**: Foundation complete - all user stories can now proceed independently 🟢

---

## Phase 3: User Story 1 - Query Book Content via Chatbot (Priority: P1) 🎯 MVP

**Goal**: Users can ask questions about book content and receive RAG-based answers sourced only from the 8 lessons

**Independent Test**: Submit query "What is ZMP in bipedal walking?" to `/v1/query` endpoint → verify response includes answer from lesson with confidence score > 0.8

### Implementation for User Story 1

- [x] T031 [US1] Implement input validation in `backend/app/services/rag_service.py`: validate_input() method checking question length, session_id format
- [x] T032 [US1] Implement vector retrieval in `backend/app/services/qdrant_service.py`: async search_lessons() method using Qdrant metadata filters for chapter/lesson/section
- [x] T033 [US1] Implement RAG augmentation in `backend/app/services/rag_service.py`: build_augmented_prompt() method combining retrieved chunks with system constraint
- [x] T034 [US1] Implement Gemini generation in `backend/app/services/gemini_service.py`: async generate_response_for_query() calling genai.generate_content() with augmented prompt
- [x] T035 [US1] Implement source attribution in `backend/app/services/rag_service.py`: extract_source_references() parsing response for chapter/lesson/section metadata
- [x] T036 [US1] Implement confidence scoring in `backend/app/services/rag_service.py`: calculate_confidence_score() using vector similarity scores and token matching
- [x] T037 [US1] Implement hallucination validation in `backend/app/services/gemini_service.py`: async validate_no_hallucination() using secondary Gemini call to verify response stays within content bounds
- [x] T038 [US1] Implement async logging in `backend/app/services/postgres_service.py`: async log_query_background() task that runs non-blocking after response returned
- [x] T039 [US1] Create POST `/v1/query` endpoint in `backend/app/api/v1/query.py` accepting ChatQueryRequest: question, selected_context (optional), session_id
- [x] T040 [US1] Implement response generation logic in `/v1/query`: orchestrate validation → retrieval → augmentation → generation → attribution pipeline
- [x] T041 [US1] Implement error handling in `/v1/query` endpoint: handle QdrantUnavailableError → 503 with user message, GeminiAPIError → 502, DatabaseError → don't block response
- [x] T042 [US1] Implement timeout handling in `/v1/query`: set 30 second timeout on Gemini call, 5 second timeout on Qdrant call
- [x] T043 [US1] Create unit test file `backend/tests/test_rag_service_us1.py` with tests for: validate_input(), build_augmented_prompt(), extract_source_references(), calculate_confidence_score()
- [x] T044 [US1] Create integration test file `backend/tests/test_query_endpoint_us1.py` with tests for: POST /v1/query happy path, validation error handling, service error handling (mocked externals)
- [x] T045 [US1] Add logging to all US1 services: query_id tracking, stage timing (retrieval: 50-100ms, generation: 1-2s), error context
- [x] T046 [US1] Create GET `/v1/health` endpoint in `backend/app/api/v1/health.py` checking Qdrant, Gemini API, Postgres connectivity (basic connectivity check only)

**Checkpoint US1**: User Story 1 is fully functional and independently testable. Can submit queries and receive sourced responses. 🟢

---

## Phase 4: User Story 2 - Select Text and Ask Follow-up Questions (Priority: P2)

**Goal**: Users can highlight lesson text and ask context-aware follow-up questions using selected passage as RAG context

**Independent Test**: Pass selected_context="Zero Moment Point is..." to `/v1/query` endpoint → verify response references selected text in attribution chain

### Implementation for User Story 2

- [x] T047 [US2] Extend ChatQueryRequest schema in `backend/app/models/schemas.py`: add optional selected_context field with max length 5000
- [x] T048 [US2] Implement context-aware retrieval in `backend/app/services/qdrant_service.py`: async search_with_context() that weights retrieved chunks if they're similar to selected_context
- [x] T049 [US2] Extend RAG augmentation in `backend/app/services/rag_service.py`: modify build_augmented_prompt() to prepend selected_context with marker "User selected this passage: [context]"
- [x] T050 [US2] Implement context attribution in `backend/app/services/rag_service.py`: add flag in SourceReference indicating "from_selected_context": bool
- [x] T051 [US2] Update POST `/v1/query` endpoint to pass selected_context through pipeline to rag_service
- [x] T052 [US2] Update response schema `ChatResponseSchema` to include sources with context_grounded boolean flag (for frontend styling)
- [x] T053 [US2] Implement context validation in `backend/app/services/rag_service.py`: validate_selected_context_within_bounds() ensuring selected text is actually from a lesson
- [x] T054 [US2] Create unit test file `backend/tests/test_rag_service_us2.py` with tests for: search_with_context(), context-weighted retrieval, context attribution
- [x] T055 [US2] Create integration test file `backend/tests/test_query_endpoint_us2.py` with tests for: POST /v1/query with selected_context, context grounding verification (mocked externals)
- [x] T056 [US2] Add logging for context tracking: log selected_context hash, retrieval boosts applied, matched chunks with similarity scores

**Checkpoint US2**: User Story 2 is fully functional. Selected text context is passed through and properly attributed. Stories 1 AND 2 work independently. 🟢

---

## Phase 5: User Story 3 - Query Logging and Analytics (Priority: P3)

**Goal**: All queries are logged to Postgres for admin analytics and course improvement insights

**Independent Test**: Submit 5 queries → verify all 5 appear in Postgres with correct metadata (timestamp, session_id, response text, sources, confidence)

### Implementation for User Story 3

- [ ] T057 [US3] Implement async background logging task in `backend/app/services/postgres_service.py`: log_query_async() task using asyncio.create_task() that runs non-blocking after response returned
- [ ] T058 [US3] Implement retry logic in postgres_service.py: retry_on_connection_error() decorator with exponential backoff (max 3 retries, 100ms initial delay)
- [ ] T059 [US3] Update ChatQuery SQLAlchemy model: add query_duration_ms, retrieval_duration_ms, generation_duration_ms fields for performance tracking
- [ ] T060 [US3] Create GET `/v1/logs` admin endpoint in `backend/app/api/v1/logs.py` returning paginated query logs (limit=100, offset params) with filters by session_id, date_range, confidence_score
- [ ] T061 [US3] Implement logs endpoint authentication stub in `/v1/logs`: add X-Admin-Token header check (basic for now, prevent accidental exposure)
- [ ] T062 [US3] Implement aggregation endpoint POST `/v1/logs/aggregate` computing: avg_response_time, hallucination_rate, query_count_by_lesson, top_questions, low_confidence_queries
- [ ] T063 [US3] Create database migration script `backend/scripts/migrate_postgres.py` creating chat_queries table with proper indexes on session_id, timestamp, confidence_score
- [ ] T064 [US3] Create unit test file `backend/tests/test_postgres_service_us3.py` with tests for: save_query(), get_query_logs(), async logging non-blocking behavior
- [ ] T065 [US3] Create integration test file `backend/tests/test_logs_endpoint_us3.py` with tests for: GET /v1/logs pagination, filtering, POST /v1/logs/aggregate computations
- [ ] T066 [US3] Add structured logging for all queries: emit JSON logs with query_id, user_session, timestamp, duration, confidence for centralized log analysis
- [ ] T067 [US3] Create `backend/scripts/seed_analytics_data.py` script for testing: insert 50 sample queries with varying confidence scores, lessons, timestamps

**Checkpoint US3**: User Story 3 is fully functional. All queries logged to Postgres. All 3 user stories work independently. 🟢

---

## Phase 6: Testing & Quality Assurance

**Purpose**: Comprehensive test coverage, performance validation, hallucination prevention

**Duration Estimate**: Day 4-5

### Unit Tests

- [ ] T068 [P] Create `backend/tests/test_validators.py`: test all validation functions with valid/invalid inputs, boundary cases
- [ ] T069 [P] Create `backend/tests/test_schemas.py`: test Pydantic schema validation for all request/response types, required fields, field constraints
- [ ] T070 [P] Create `backend/tests/test_rag_prompts.py`: verify system prompts contain scope constraints, validation prompts correctly formatted

### Integration Tests

- [ ] T071 Create `backend/tests/test_full_pipeline.py`: end-to-end test with mocked Gemini/Qdrant: query → retrieval → augmentation → generation → logging (happy path + 3 error cases)
- [ ] T072 Create `backend/tests/test_error_scenarios.py`: Qdrant unavailable, Gemini timeout, Postgres connection failure, invalid input validation failure, hallucination detection
- [ ] T073 Create `backend/tests/test_concurrent_requests.py`: simulate 10 concurrent requests, verify no connection pool exhaustion, proper error handling
- [ ] T074 Create `backend/tests/test_response_validation.py`: verify all responses conform to ChatResponseSchema, have confidence score, include sources, timestamps valid ISO-8601

### Performance & Load Tests

- [ ] T075 Create `backend/tests/test_performance.py`: measure latencies for retrieval (<100ms), generation (<2s), total (<3s p95)
- [ ] T076 Create `backend/scripts/load_test.py`: simulate 100 concurrent users, measure throughput (queries/sec), p50/p95/p99 latencies, error rate

### Hallucination Prevention Tests

- [ ] T077 Create `backend/tests/test_hallucination_prevention.py`: 10 out-of-scope questions (quantum computers, assignment deadlines, personal questions) → verify all rejected with "I don't have information..." message
- [ ] T078 Create `backend/tests/test_scope_limiting.py`: verify responses never mention facts outside the 8 lessons (manual spot-check with LLM scoring)

---

## Phase 7: Deployment & Monitoring

**Purpose**: Production readiness, deployment configuration, observability

**Duration Estimate**: Day 5-6

### Docker & Deployment

- [ ] T079 Create `backend/Dockerfile` with Python 3.11 slim base, multi-stage build, non-root user, health check CMD
- [ ] T080 Create `backend/docker-compose.yml` with services: app (FastAPI), postgres (Neon config), optional redis (for rate limiting future enhancement)
- [ ] T081 Create `backend/.dockerignore` excluding: __pycache__, *.pyc, .pytest_cache, .env, tests/, venv/

### Configuration & Secrets

- [ ] T082 Create `backend/.env.production.example` with secrets: GEMINI_API_KEY, QDRANT_API_KEY, QDRANT_URL, DATABASE_URL, LOG_LEVEL=info
- [ ] T083 Add environment variable validation to `backend/config.py`: verify all required vars present at startup, clear error messages for missing credentials
- [ ] T084 Create `backend/scripts/validate_deployment.py`: health check script verifying Gemini API key works, Qdrant reachable, Postgres connectable before starting server

### Observability

- [ ] T085 Add request tracing to `backend/app/api/middleware.py`: correlation_id in request headers, propagated to all service calls, included in logs
- [ ] T086 Add metrics collection in `backend/app/services/`: measure_latency decorator recording operation durations, add error counters, success rate metrics
- [ ] T087 Create `backend/app/core/metrics.py` with Prometheus-compatible metrics export (ready for future Grafana integration)
- [ ] T088 Add detailed logging to all error paths: include context (query_id, user_session, operation), error type, attempt counts, retry status

### Documentation

- [ ] T089 Create `backend/README.md` with: project overview, tech stack, installation steps, configuration, running tests, deployment instructions, API documentation link
- [ ] T090 Create `backend/DEVELOPMENT.md` with: local setup, running in Docker, debugging tips, adding new endpoints checklist, performance profiling
- [ ] T091 Create `specs/002-rag-chatbot-backend/quickstart.md` with: 5-minute local setup, 3 example API calls with curl, expected responses, troubleshooting
- [ ] T092 Create `specs/002-rag-chatbot-backend/data-model.md` with: ChatQuery schema documentation, SourceReference schema, QueryLog queries, Qdrant metadata structure

---

## Phase 8: Frontend Integration

**Purpose**: Embed chatbot widget on Docusaurus book pages

**Duration Estimate**: Day 6-7 (frontend team)

- [ ] T093 Create `book/src/components/ChatbotWidget/ChatbotWidget.tsx` component: chat input form, message history display, loading states, error messages
- [ ] T094 [P] Create `book/src/components/ChatbotWidget/api.ts` client library: POST /api/v1/query wrapper with error handling, request timeout (5s)
- [ ] T095 [P] Create `book/src/components/ChatbotWidget/styles.module.css` with responsive design: mobile (<480px), tablet, desktop, dark mode support
- [ ] T096 Create `book/src/pages/ChatbotPage.tsx` standalone demo page: full-width chatbot, test conversation examples
- [ ] T097 Create `book/docusaurus.config.js` integration: inject ChatbotWidget on all lesson pages via theme wrapper
- [ ] T098 Create `book/src/theme/ChatbotInjection.tsx` wrapper component: conditionally shows chatbot on `/docs/**` routes only, excludes homepage
- [ ] T099 [P] Create `book/src/utils/selectedText.ts` helper: extract selected text on highlight, show "Ask chatbot about this" button, pass context to widget
- [ ] T100 Create integration test `book/tests/chatbot.integration.test.ts`: open lesson page, type question, verify API call, verify response displays, verify selected text flow

---

## Phase 9: Polish & Cross-Cutting Concerns

**Purpose**: Refinements, documentation, final validation

**Duration Estimate**: Day 7-8

### Code Quality & Documentation

- [ ] T101 [P] Add docstrings to all public methods in `backend/app/services/` and `backend/app/api/` following Google style guide
- [ ] T102 [P] Add type hints to all functions in `backend/app/`: verify with `mypy backend/app/ --strict` zero errors
- [ ] T103 [P] Add README docstrings to each module explaining purpose, key classes, usage examples
- [ ] T104 Run code formatter: `black backend/` formatting all files
- [ ] T105 Run linter: `pylint backend/app/` addressing all issues, document any waivers
- [ ] T106 Create `backend/CONTRIBUTING.md` with: code style guide, commit message format, PR checklist, testing requirements

### Final Validation

- [ ] T107 Run all tests: `pytest backend/tests/ -v` → all pass with >90% coverage
- [ ] T108 Run production build: `docker build -t rag-chatbot:latest .` → builds successfully
- [ ] T109 Run full pipeline test: start Docker container, run 20 sample queries, verify all succeed, latencies <3s, no errors in logs
- [ ] T110 Verify acceptance criteria: run checklist from spec.md → 12/12 FRs implemented, 3/3 user stories working, 7/7 success criteria met
- [ ] T111 Run hallucination test suite: 20 out-of-scope queries → 95%+ rejection rate with proper messaging
- [ ] T112 Load test validation: 100 concurrent users for 5 minutes → <3s p95 latency, 0 errors, sustained throughput
- [ ] T113 Security check: scan for secrets in code, verify no API keys committed, all in env vars, validate .gitignore covers .env
- [ ] T114 Documentation validation: verify README, DEVELOPMENT.md, quickstart.md are complete and accurate, follow links work

### Optional Enhancements (Post-MVP)

- [ ] T115 Add rate limiting: implement request throttling per session_id (100 queries/hour), return 429 with retry-after header
- [ ] T116 Add caching: implement Redis caching for frequently asked questions (by semantic similarity), 1-hour TTL
- [ ] T117 Add admin dashboard: basic query analytics UI (Query count over time, top questions, confidence distribution, out-of-scope rejections)
- [ ] T118 Add A/B testing: support multiple Gemini model versions, track which performs better on hallucination prevention
- [ ] T119 Add user feedback loop: collect ratings on responses (helpful/not helpful), use for model improvement tracking

---

## Dependencies & Execution Order

### Phase Dependencies

```
Phase 1: Setup (T001-T016)
   ↓ (Setup must complete first)
Phase 2: Foundational (T017-T030) ⚠️ BLOCKS all stories
   ↓ (Foundational must complete before ANY story)
   ├→ Phase 3: User Story 1 (T031-T046) [Can run in parallel with US2, US3]
   ├→ Phase 4: User Story 2 (T047-T056) [Can run in parallel with US1, US3]
   └→ Phase 5: User Story 3 (T057-T067) [Can run in parallel with US1, US2]
   ↓ (All stories should be complete before testing/deployment)
Phase 6: Testing (T068-T078)
Phase 7: Deployment (T079-T092)
Phase 8: Frontend (T093-T100)
Phase 9: Polish (T101-T119)
```

### User Story Dependencies

- **User Story 1 (P1)**: MVP focus - core RAG pipeline. Can start after Phase 2.
- **User Story 2 (P2)**: Builds on US1 context - enhances retrieval. Can run parallel with US1 after Phase 2.
- **User Story 3 (P3)**: Independent logging system. Can run parallel with US1/US2 after Phase 2.

### Within Each User Story

- Models → Services → Endpoints → Tests
- All core logic implemented before performance optimization
- Tests written to verify specification acceptance criteria

### Parallel Opportunities

**Phase 1 Setup**:
- T004-T015: All marked [P] can run in parallel (different modules, no dependencies)

**Phase 2 Foundational**:
- T019-T020: Both validation/exception utilities can run parallel
- T026-T027: API middleware and init can run parallel
- Core services (T021-T023) can run parallel except rag_service needs dependencies from others

**Phase 3-5 User Stories**:
- Once Phase 2 complete, all 3 user stories can run in parallel by different team members
- Within US1: tests can run parallel with service implementation (write tests first)

**Phase 6 Testing**:
- Unit tests (T068-T070): All parallel
- Integration tests (T071-T074): Can run parallel, each tests different scenario

**Phase 8 Frontend**:
- Can run parallel with backend phases (separate codebase)
- T094-T095: Both client utilities can run parallel

---

## Parallel Example: Team of 3

**Day 1-2 (Setup + Foundational)**: Team works together
- Developer A: T001-T010 Setup scaffold + config
- Developer B: T017-T020 Database + validation
- Developer C: T021-T025 Services foundation

**Day 3-4 (User Stories Parallel)**: Team splits
- Developer A: Phase 3 US1 (T031-T046) - Core RAG pipeline
- Developer B: Phase 4 US2 (T047-T056) - Context awareness
- Developer C: Phase 5 US3 (T057-T067) - Query logging

**Day 5-6 (Testing + Deployment)**: Team reunites
- All: Phase 6 testing (T068-T078)
- All: Phase 7 deployment (T079-T092)
- Frontend: Phase 8 widget (T093-T100)

**Day 7+ (Polish + Optional)**: Final refinements
- All: Phase 9 (T101-T119)

---

## MVP Scope (Recommended Start)

**Minimal Viable Product** focuses on User Story 1 + basic logging:

1. Complete Phase 1: Setup ✅
2. Complete Phase 2: Foundational ✅
3. Complete Phase 3: User Story 1 ✅
4. Add basic US3: GET `/v1/logs` endpoint only (T060)
5. Phase 6: Core tests only (T071-T074)
6. Phase 7: Docker deployment
7. Phase 8: Frontend integration
8. **Result**: Core RAG chatbot working, basic query logging, ready for production

Then add User Story 2 (context awareness) and US3 (analytics) incrementally.

---

## Notes

- **[P] marker**: Tasks with different files, no dependencies - can run in parallel
- **[Story] label**: Maps task to specific user story (US1, US2, US3) for traceability
- **Each phase**: Independent checkpoint where features can be tested/validated
- **Error handling**: Graceful degradation - never break user experience for backend errors
- **Performance**: Target <3s p95 across all latency-sensitive operations
- **Security**: All credentials via environment variables, no secrets in code
- **Testing**: Write tests first (TDD), verify they fail before implementing
- **Commits**: After each task or logical group (clean git history)
- **Validation**: Stop at any checkpoint to independently validate and deploy user story

---

**Status**: ✅ TASKS GENERATED
**Total Tasks**: 119 across 9 phases
**MVP Checkpoint**: After Phase 3 (US1) + basic US3 logging
**Full Feature**: All 3 user stories + testing + deployment + frontend
**Estimated Timeline**: 7-10 days for 1 developer, 3-5 days for team of 3
