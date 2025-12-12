# RAG Chatbot Backend - Local Setup Guide

Complete step-by-step instructions to run the RAG chatbot backend locally on your machine.

---

## 1. Environment Setup

### Prerequisites
- **Python 3.9+** (check: `python --version`)
- **Git** (check: `git --version`)
- **API Keys Required:**
  - Gemini API key (from [Google AI Studio](https://aistudio.google.com/app/apikeys))
  - Qdrant API key (or run Qdrant locally)
  - Postgres database URL (Neon or local)

### Step 1a: Clone/Navigate to Project
```bash
cd D:\sp\physical-ai\backend
```

### Step 1b: Create Python Virtual Environment
```bash
# Windows (PowerShell)
python -m venv venv
.\venv\Scripts\Activate.ps1

# Windows (CMD)
python -m venv venv
venv\Scripts\activate.bat

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### Step 1c: Verify Virtual Environment is Active
```bash
# Should show path to your venv
where python    # Windows
which python    # macOS/Linux
```

---

## 2. Required Dependencies

### Install Dependencies
```bash
pip install -r requirements.txt
```

**What this installs:**
- `fastapi==0.109.0` - Web framework
- `uvicorn==0.27.0` - ASGI server
- `sqlalchemy==2.0.23` - ORM for database
- `asyncpg==0.29.0` - Postgres async driver
- `qdrant-client==2.7.0` - Vector database client
- `google-generativeai==0.3.1` - Gemini API
- `pytest==7.4.3` - Testing framework
- All other utilities (see requirements.txt)

### Verify Installation
```bash
pip list | grep -E "fastapi|uvicorn|sqlalchemy|qdrant"
```

---

## 3. Configure Environment Variables

### Step 3a: Create `.env` File
```bash
# In backend/ directory, create .env file
touch .env    # macOS/Linux
# OR manually create .env file (Windows)
```

### Step 3b: Add Required Variables
**Copy this template and fill in YOUR values:**

```env
# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
API_DEBUG=true
LOG_LEVEL=info
ENVIRONMENT=development
PYTHONPATH=.

# Gemini API (REQUIRED)
GEMINI_API_KEY=your_gemini_api_key_here

# Qdrant Configuration (REQUIRED)
QDRANT_URL=http://localhost:6333
QDRANT_API_KEY=your_qdrant_api_key_or_password

# Postgres Database (REQUIRED)
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/chatbot
```

### Step 3c: Get Your API Keys

#### Gemini API Key
1. Go to [Google AI Studio](https://aistudio.google.com/app/apikeys)
2. Click "Create API Key"
3. Copy the key into `.env` as `GEMINI_API_KEY=...`

#### Qdrant Setup (Two Options)

**Option A: Local Qdrant (Recommended for Development)**
```bash
# Install Docker if you don't have it
# Then run Qdrant in a container:
docker run -p 6333:6333 qdrant/qdrant:v1.7.0

# In .env, use:
QDRANT_URL=http://localhost:6333
QDRANT_API_KEY=any_password_you_want
```

**Option B: Qdrant Cloud**
1. Create free account at [Qdrant Cloud](https://cloud.qdrant.io)
2. Create a cluster
3. Copy the URL and API key to `.env`

#### Postgres Database

**Option A: Local Postgres**
```bash
# Install PostgreSQL locally or via Docker:
docker run -e POSTGRES_PASSWORD=password -p 5432:5432 postgres:15

# In .env, use:
DATABASE_URL=postgresql+asyncpg://postgres:password@localhost:5432/chatbot
```

**Option B: Neon Postgres (Recommended)**
1. Create free account at [Neon](https://neon.tech)
2. Create a project and database
3. Copy connection string to `.env` as `DATABASE_URL=...`

---

## 4. Start the FastAPI Server

### Step 4a: Initialize the Database (First Time Only)
```bash
# Create tables in Postgres
python -c "from app.models.database import Base, engine; import asyncio; asyncio.run(Base.metadata.create_all(bind=engine))"
```

### Step 4b: Run the FastAPI Server
```bash
# Development mode (with auto-reload)
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# OR use Python directly:
python main.py
```

**Expected Output:**
```
INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     Application startup complete
✅ All services initialized
```

### Step 4c: Verify Server is Running
```bash
# In a new terminal, check health:
curl http://localhost:8000/

# Response should be:
{
  "service": "RAG Chatbot Backend",
  "version": "1.0.0",
  "status": "running",
  "docs": "/docs"
}
```

---

## 5. Test the Endpoints Locally

### 5a: Health Check Endpoint
```bash
# Check all services are healthy
curl http://localhost:8000/v1/health

# Expected 200 response with service status
```

### 5b: Query Endpoint (Main RAG Pipeline)
```bash
# Test the chatbot query
curl -X POST http://localhost:8000/v1/query \
  -H "Content-Type: application/json" \
  -d '{
    "question": "What is the difference between a humanoid and bipedal robot?",
    "session_id": "user_session_123",
    "selected_context": null
  }'

# Expected 200 response:
{
  "response_text": "Based on the course materials...",
  "source_references": [...],
  "confidence_score": 0.85,
  "timestamp": "2024-01-15T10:30:00Z"
}
```

### 5c: Logs Endpoint (Query History)
```bash
# Get last 10 queries
curl "http://localhost:8000/v1/logs?limit=10&offset=0"

# Expected response with paginated logs
```

### 5d: Analytics Endpoints
```bash
# Get performance metrics (last 7 days)
curl "http://localhost:8000/v1/logs/metrics?days_back=7"

# Get top questions (last 7 days)
curl "http://localhost:8000/v1/logs/top-questions?limit=10&days_back=7"

# Get content coverage (which chapters are being queried)
curl "http://localhost:8000/v1/logs/coverage"
```

### 5e: Interactive Testing with Swagger UI
```
Open in browser: http://localhost:8000/docs
```
- Explore all endpoints visually
- Test directly from the browser
- See request/response schemas

### 5f: Test with Python Requests
```python
import requests
import json

BASE_URL = "http://localhost:8000"

# Test query
response = requests.post(
    f"{BASE_URL}/v1/query",
    json={
        "question": "What is kinematics?",
        "session_id": "test_user_001",
        "selected_context": None
    }
)
print(response.json())

# Test health
health = requests.get(f"{BASE_URL}/v1/health")
print(health.json())

# Test logs
logs = requests.get(f"{BASE_URL}/v1/logs?limit=5")
print(logs.json())
```

---

## 6. Debugging Common Errors

### Error 1: "Missing required environment variables"
**Symptom:**
```
ValueError: Missing required environment variables: gemini_api_key, ...
```

**Fix:**
- Check `.env` file exists in `backend/` directory
- Verify all 4 variables are set: `GEMINI_API_KEY`, `QDRANT_URL`, `QDRANT_API_KEY`, `DATABASE_URL`
- Make sure there are no typos (case-sensitive)
- Restart the server after editing `.env`

### Error 2: "Cannot connect to Qdrant"
**Symptom:**
```
QdrantUnavailableError: Vector search temporarily unavailable
```

**Fix:**
```bash
# Check Qdrant is running:
curl http://localhost:6333/health

# If not running, start it:
docker run -p 6333:6333 qdrant/qdrant:v1.7.0

# OR update QDRANT_URL in .env if using cloud
```

### Error 3: "Cannot connect to database"
**Symptom:**
```
sqlalchemy.exc.OperationalError: could not connect to server
```

**Fix:**
```bash
# Check Postgres is running:
psql -U postgres -h localhost -c "SELECT 1"

# If not running, start it:
docker run -e POSTGRES_PASSWORD=password -p 5432:5432 postgres:15

# Verify DATABASE_URL in .env is correct
```

### Error 4: "Invalid Gemini API key"
**Symptom:**
```
GeminiAPIError: Unable to generate response
```

**Fix:**
- Go to [Google AI Studio](https://aistudio.google.com/app/apikeys)
- Generate a new API key
- Update `.env`: `GEMINI_API_KEY=new_key`
- Restart server

### Error 5: "ModuleNotFoundError: No module named 'app'"
**Symptom:**
```
ModuleNotFoundError: No module named 'app'
```

**Fix:**
```bash
# Ensure you're in the correct directory:
cd D:\sp\physical-ai\backend

# Verify PYTHONPATH is set:
echo $PYTHONPATH    # Should show current directory

# Try setting it manually:
export PYTHONPATH=.    # macOS/Linux
set PYTHONPATH=.       # Windows CMD
$env:PYTHONPATH="."    # Windows PowerShell
```

### Error 6: "Port 8000 already in use"
**Symptom:**
```
OSError: [WinError 10048] Only one usage of each socket address
```

**Fix:**
```bash
# Use a different port:
uvicorn main:app --reload --port 8001

# OR kill the process using port 8000:
lsof -i :8000 | grep LISTEN | awk '{print $2}' | xargs kill    # macOS/Linux
netstat -ano | findstr :8000                                    # Windows
```

### Error 7: Virtual environment not activated
**Symptom:**
```
pip: command not found or wrong Python version
```

**Fix:**
```bash
# Make sure virtual environment is active:
.\venv\Scripts\Activate.ps1    # Windows PowerShell
source venv/bin/activate        # macOS/Linux

# Should show (venv) in your terminal prompt
```

---

## 7. Quick Reference Commands

```bash
# Activate virtual environment
.\venv\Scripts\Activate.ps1          # Windows PowerShell
source venv/bin/activate              # macOS/Linux

# Install dependencies
pip install -r requirements.txt

# Run server with auto-reload
uvicorn main:app --reload

# Run tests
pytest tests/ -v

# Format code with Black
black app/

# Check code quality
pylint app/

# View logs in real-time
tail -f app.log    # macOS/Linux

# Test specific endpoint
curl -X GET http://localhost:8000/v1/health
```

---

## 8. Next Steps

### After Local Testing Works:

1. **Run Tests:**
   ```bash
   pytest tests/test_rag_service_us1.py -v
   pytest tests/test_query_endpoint_us1.py -v
   ```

2. **Check Logs:**
   - Swagger UI at `http://localhost:8000/docs`
   - Query logs at `/v1/logs`
   - Performance metrics at `/v1/logs/metrics`

3. **Deploy to Production:**
   - See `DEPLOYMENT.md` for Docker setup
   - Configure environment for production
   - Set up monitoring and logging

---

## Summary Checklist

- [ ] Python 3.9+ installed
- [ ] Virtual environment created and activated
- [ ] Dependencies installed (`pip install -r requirements.txt`)
- [ ] `.env` file created with all 4 required variables
- [ ] Gemini API key obtained
- [ ] Qdrant running (local Docker or cloud)
- [ ] Postgres running (local Docker or cloud)
- [ ] Server starts: `uvicorn main:app --reload`
- [ ] Health endpoint returns 200: `curl http://localhost:8000/v1/health`
- [ ] Query endpoint works: `curl -X POST http://localhost:8000/v1/query ...`
- [ ] Access Swagger UI: `http://localhost:8000/docs`

---

**Need Help?** Check the error messages above or review endpoint documentation at `/docs` when server is running.
