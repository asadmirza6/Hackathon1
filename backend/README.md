# RAG Chatbot Backend

FastAPI-based Retrieval-Augmented Generation (RAG) chatbot backend for the "Physical AI & Humanoid Robotics Course" book.

## Quick Start

**1. Setup (5 minutes)**
```bash
# macOS/Linux
bash quickstart.sh

# Windows
quickstart.bat
```

**2. Configure Environment**
```bash
cp .env.example .env
# Edit .env with your API keys (Gemini, Qdrant, Postgres)
```

**3. Run Server**
```bash
uvicorn main:app --reload
```

**4. Test**
```bash
# Health check
curl http://localhost:8000/v1/health

# Interactive docs
# Open: http://localhost:8000/docs
```

---

## Architecture

### Tech Stack
- **Framework**: FastAPI 0.109.0
- **Server**: Uvicorn (ASGI)
- **Database**: PostgreSQL + SQLAlchemy async ORM
- **Vector DB**: Qdrant (embeddings storage)
- **LLM**: Google Gemini API
- **Testing**: Pytest, pytest-asyncio

### Core Services
```
RAGService (Orchestrator)
├── QdrantService (Vector retrieval)
├── GeminiService (LLM + embeddings)
└── PostgresService (Query logging)
```

### API Endpoints
| Method | Path | Purpose |
|--------|------|---------|
| GET | `/v1/health` | Service health check |
| POST | `/v1/query` | Submit chatbot query (RAG pipeline) |
| GET | `/v1/logs` | Get paginated query history |
| GET | `/v1/logs/aggregate` | Basic analytics |
| GET | `/v1/logs/metrics` | Performance metrics (p95 latency, etc.) |
| GET | `/v1/logs/top-questions` | Most frequently asked questions |
| GET | `/v1/logs/coverage` | Content coverage by chapter/lesson |

---

## Documentation

- **[LOCAL_SETUP.md](./LOCAL_SETUP.md)** - Complete local development setup guide
- **[TESTING_GUIDE.md](./TESTING_GUIDE.md)** - Testing all endpoints with curl/Python
- **[.env.example](./.env.example)** - Environment variables template

### Documentation Files in `/docs`
- API specification
- Data models
- Service layer documentation

---

## Requirements

### System
- Python 3.9+
- Virtual environment (`venv`)
- 2GB RAM, 100MB storage

### External Services (Required)
1. **Gemini API**: Get key from [Google AI Studio](https://aistudio.google.com/app/apikeys)
2. **Qdrant**: Local Docker or [Qdrant Cloud](https://cloud.qdrant.io)
3. **PostgreSQL**: Local or [Neon Cloud](https://neon.tech)

---

## Installation

```bash
# 1. Clone/navigate to backend
cd backend

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate        # macOS/Linux
# or
.\venv\Scripts\activate.ps1     # Windows PowerShell

# 3. Install dependencies
pip install -r requirements.txt

# 4. Setup .env file
cp .env.example .env
# Edit .env with your keys
```

---

## Running Locally

### Start Server
```bash
# Development (auto-reload)
uvicorn main:app --reload

# Production
uvicorn main:app --host 0.0.0.0 --port 8000
```

### Database Setup (First Time)
```bash
python -c "from app.models.database import Base, engine; import asyncio; asyncio.run(Base.metadata.create_all(bind=engine))"
```

### Run Tests
```bash
pytest tests/ -v

# With coverage
pytest tests/ --cov=app --cov-report=html
```

---

## Project Structure

```
backend/
├── app/
│   ├── api/
│   │   ├── v1/
│   │   │   ├── query.py       # Main RAG endpoint
│   │   │   ├── health.py      # Health checks
│   │   │   └── logs.py        # Query logs & analytics
│   │   └── middleware.py       # Request tracking
│   ├── services/
│   │   ├── rag_service.py     # RAG orchestrator (6-stage pipeline)
│   │   ├── qdrant_service.py  # Vector search
│   │   ├── gemini_service.py  # LLM + embeddings
│   │   ├── postgres_service.py # Database queries
│   │   └── analytics_service.py # Analytics computations
│   ├── models/
│   │   ├── database.py         # SQLAlchemy setup
│   │   ├── chat_query.py       # ChatQuery ORM model
│   │   └── schemas.py          # Pydantic request/response models
│   ├── utils/
│   │   ├── validators.py       # Input validation
│   │   ├── exceptions.py       # Custom exceptions
│   │   └── error_handlers.py   # FastAPI error handlers
│   └── core/
│       ├── config.py           # Environment configuration
│       ├── logging.py          # Logging setup
│       └── constants.py        # RAG prompts & thresholds
├── tests/
│   ├── test_rag_service_us1.py
│   └── test_query_endpoint_us1.py
├── main.py                      # FastAPI entry point
├── config.py                    # Legacy config (see app/core/config.py)
├── requirements.txt             # Python dependencies
├── .env.example                 # Environment template
├── LOCAL_SETUP.md              # Setup instructions
└── TESTING_GUIDE.md            # Testing reference
```

---

## Key Features

### User Story 1: Basic RAG Query
- Vector similarity search in Qdrant
- LLM generation with RAG context
- Confidence scoring
- Query logging to Postgres

### User Story 2: Context-Aware Questions
- Optional `selected_context` parameter
- Prioritizes user-highlighted text in prompt
- Tracks context-grounded source attribution

### User Story 3: Query Analytics
- Query volume trends (by day)
- Performance metrics (p95 latency, avg confidence)
- Top questions analysis
- Content coverage by chapter/lesson

---

## Configuration

### Environment Variables

**Required:**
- `GEMINI_API_KEY` - Google Gemini API key
- `QDRANT_URL` - Qdrant cluster URL
- `QDRANT_API_KEY` - Qdrant API key
- `DATABASE_URL` - PostgreSQL connection string

**Optional:**
- `API_PORT` - Server port (default: 8000)
- `API_DEBUG` - Enable debug mode (default: false)
- `LOG_LEVEL` - Logging level (default: info)

See `.env.example` for full list.

---

## Troubleshooting

| Issue | Fix |
|-------|-----|
| "Missing required environment variables" | Copy `.env.example` to `.env` and fill in API keys |
| "Cannot connect to Qdrant" | Check Qdrant is running on specified URL |
| "Cannot connect to database" | Verify PostgreSQL is running and DATABASE_URL is correct |
| "ModuleNotFoundError: app" | Ensure PYTHONPATH=. or run from backend/ directory |
| "Port 8000 already in use" | Use different port: `--port 8001` |

See **[LOCAL_SETUP.md](./LOCAL_SETUP.md)** for detailed debugging guide.

---

## Performance Targets

| Metric | Target |
|--------|--------|
| Query P95 Latency | <3000ms |
| Average Confidence | >0.75 |
| Qdrant Retrieval | <1000ms |
| LLM Generation | <2000ms |
| Database Queries | <100ms |

---

## API Examples

### Query the Chatbot
```bash
curl -X POST http://localhost:8000/v1/query \
  -H "Content-Type: application/json" \
  -d '{
    "question": "What is forward kinematics?",
    "session_id": "user_123",
    "selected_context": null
  }'
```

### Get Performance Metrics
```bash
curl "http://localhost:8000/v1/logs/metrics?days_back=7"
```

### Interactive Testing
Open browser: `http://localhost:8000/docs`

See **[TESTING_GUIDE.md](./TESTING_GUIDE.md)** for comprehensive examples.

---

## Development

### Code Quality
```bash
# Format code
black app/

# Type checking
mypy app/

# Linting
pylint app/

# All checks
black app/ && mypy app/ && pylint app/
```

### Running Specific Tests
```bash
pytest tests/test_rag_service_us1.py::TestRAGServiceValidation -v
pytest tests/test_query_endpoint_us1.py -k "test_query_success" -v
```

---

## Deployment

For production deployment, see documentation on:
- Docker containerization
- Environment-specific configuration
- Monitoring and logging
- Scaling considerations

---

## License

Part of Physical AI & Humanoid Robotics Course project.

---

## Quick Links

- [Setup Guide](./LOCAL_SETUP.md) - Complete local setup instructions
- [Testing Guide](./TESTING_GUIDE.md) - How to test all endpoints
- [API Docs](http://localhost:8000/docs) - Interactive Swagger UI (when running)
- [Environment Template](./.env.example) - Configuration template

---

## Support

1. Check [LOCAL_SETUP.md](./LOCAL_SETUP.md) troubleshooting section
2. Review [TESTING_GUIDE.md](./TESTING_GUIDE.md) for endpoint testing
3. Check `/v1/logs` endpoint for recent queries and errors
4. Enable debug logging: `LOG_LEVEL=debug` in `.env`
