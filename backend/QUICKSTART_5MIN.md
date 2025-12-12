# 5-Minute Quick Start Guide

Get the RAG chatbot backend running in 5 minutes.

---

## Prerequisites
- Python 3.9+ installed
- Gemini API key (get free at [aistudio.google.com/app/apikeys](https://aistudio.google.com/app/apikeys))
- 5 minutes of time

---

## Step 1: Setup (2 minutes)

**Windows (PowerShell):**
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

**macOS/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

---

## Step 2: Configure (1 minute)

Copy the template:
```bash
cp .env.example .env
```

Edit `.env` and add your Gemini API key:
```env
GEMINI_API_KEY=your_key_from_aistudio_here
QDRANT_URL=http://localhost:6333
QDRANT_API_KEY=any_password
DATABASE_URL=postgresql+asyncpg://postgres:password@localhost:5432/chatbot
```

---

## Step 3: Start Backend (1 minute)

```bash
uvicorn main:app --reload
```

Expected output:
```
INFO:     Uvicorn running on http://0.0.0.0:8000
✅ All services initialized
```

---

## Step 4: Test Endpoints (1 minute)

**Option A: Browser (Easiest)**
Open: http://localhost:8000/docs
- Explore all endpoints
- Click "Try it out" on each endpoint

**Option B: Terminal**
```bash
# Health check
curl http://localhost:8000/v1/health

# Test query
curl -X POST http://localhost:8000/v1/query \
  -H "Content-Type: application/json" \
  -d '{"question":"What is kinematics?","session_id":"test_001"}'

# View logs
curl "http://localhost:8000/v1/logs?limit=5"
```

---

## That's It! ✅

Your RAG chatbot backend is running locally.

---

## Next Steps

- **See detailed setup**: [LOCAL_SETUP.md](./LOCAL_SETUP.md)
- **Learn endpoint testing**: [TESTING_GUIDE.md](./TESTING_GUIDE.md)
- **Full documentation**: [README.md](./README.md)

---

## Troubleshooting

| Problem | Solution |
|---------|----------|
| `ModuleNotFoundError` | Make sure venv is activated: `source venv/bin/activate` |
| `Port 8000 in use` | Use different port: `uvicorn main:app --reload --port 8001` |
| API key error | Check `.env` has correct `GEMINI_API_KEY` value |
| Cannot connect to Qdrant | Run: `docker run -p 6333:6333 qdrant/qdrant:v1.7.0` |
| Cannot connect to database | Run: `docker run -e POSTGRES_PASSWORD=password -p 5432:5432 postgres:15` |

For more help, see [LOCAL_SETUP.md](./LOCAL_SETUP.md#6-debugging-common-errors).

---

## API Endpoints Reference

| Endpoint | Purpose |
|----------|---------|
| `POST /v1/query` | Ask the chatbot a question |
| `GET /v1/health` | Check if all services are working |
| `GET /v1/logs` | View query history |
| `GET /v1/logs/metrics` | View performance metrics |
| `GET /v1/logs/top-questions` | See most asked questions |

Visit http://localhost:8000/docs for interactive testing.

---

**Questions?** Check [LOCAL_SETUP.md](./LOCAL_SETUP.md) for comprehensive guide.
