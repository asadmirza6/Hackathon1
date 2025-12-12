# RAG Chatbot Backend - Documentation Index

Complete guide to all documentation for the RAG chatbot backend.

---

## 📚 Where to Start?

### I have 5 minutes
→ **[QUICKSTART_5MIN.md](./QUICKSTART_5MIN.md)**
- Fastest way to get running
- Minimal setup
- Just the essentials

### I have 15 minutes
→ **[README.md](./README.md)**
- Architecture overview
- Project structure
- Quick reference
- Key features explained

### I want detailed setup
→ **[LOCAL_SETUP.md](./LOCAL_SETUP.md)**
- Complete step-by-step instructions
- API key setup for all services
- Debugging common errors
- Comprehensive troubleshooting

### I want to test endpoints
→ **[TESTING_GUIDE.md](./TESTING_GUIDE.md)**
- curl examples for every endpoint
- Python test script
- Response format reference
- Load testing examples
- Common test scenarios

### I need environment config
→ **[.env.example](./.env.example)**
- All configuration options
- Commented explanations
- Options for local/cloud services

---

## 🚀 Quick Navigation

### Setup Phase
1. **[QUICKSTART_5MIN.md](./QUICKSTART_5MIN.md)** - Get running in 5 minutes
2. **[LOCAL_SETUP.md](./LOCAL_SETUP.md)** - Detailed setup guide
3. **[.env.example](./.env.example)** - Configuration template

### Running & Testing
4. **[README.md](./README.md)** - Project overview & commands
5. **[TESTING_GUIDE.md](./TESTING_GUIDE.md)** - How to test all endpoints
6. **http://localhost:8000/docs** - Interactive Swagger UI (when running)

---

## 📖 Document Summary

| Document | Purpose | Read Time | Audience |
|----------|---------|-----------|----------|
| [QUICKSTART_5MIN.md](./QUICKSTART_5MIN.md) | Get running ASAP | 5 min | Everyone |
| [LOCAL_SETUP.md](./LOCAL_SETUP.md) | Complete setup guide | 20 min | Developers |
| [TESTING_GUIDE.md](./TESTING_GUIDE.md) | Test all endpoints | 15 min | QA / Testers |
| [README.md](./README.md) | Project overview | 10 min | All |
| [.env.example](./.env.example) | Config template | 5 min | Setup phase |

---

## 🎯 Common Tasks

### "I want to run the backend locally"
1. Read: [QUICKSTART_5MIN.md](./QUICKSTART_5MIN.md)
2. If stuck: Read: [LOCAL_SETUP.md](./LOCAL_SETUP.md)

### "I want to test if it works"
1. Read: [TESTING_GUIDE.md](./TESTING_GUIDE.md)
2. Run curl commands or Python script

### "I'm getting an error"
1. Check: [LOCAL_SETUP.md#6-debugging-common-errors](./LOCAL_SETUP.md#6-debugging-common-errors)
2. If not listed: Check server logs with `LOG_LEVEL=debug`

### "I want to understand the architecture"
1. Read: [README.md#architecture](./README.md#architecture)
2. Browse: `app/` directory structure

---

## ✅ Getting Started Checklist

### Before Running Server
- [ ] Python 3.9+ installed
- [ ] Virtual environment created: `python -m venv venv`
- [ ] Virtual environment activated
- [ ] Dependencies installed: `pip install -r requirements.txt`
- [ ] `.env` file created with API keys
- [ ] Gemini API key obtained
- [ ] Qdrant configured (local or cloud)
- [ ] Postgres configured (local or cloud)

### Server Running
- [ ] Server starts: `uvicorn main:app --reload`
- [ ] Health check passes: `curl http://localhost:8000/v1/health`
- [ ] Can access Swagger UI: `http://localhost:8000/docs`

---

## 🔧 Getting Your API Keys

### 1. Gemini API Key (2 minutes)
- Visit: https://aistudio.google.com/app/apikeys
- Click "Create API Key"
- Copy to `.env`: `GEMINI_API_KEY=...`

### 2. Qdrant Setup (Choose One)
**Local (Recommended for Dev):**
```bash
docker run -p 6333:6333 qdrant/qdrant:v1.7.0
```
In `.env`:
```
QDRANT_URL=http://localhost:6333
QDRANT_API_KEY=any_password
```

**Cloud:**
- Sign up: https://cloud.qdrant.io
- Create cluster
- Copy URL and API key to `.env`

### 3. Postgres Setup (Choose One)
**Local (Recommended for Dev):**
```bash
docker run -e POSTGRES_PASSWORD=password -p 5432:5432 postgres:15
```
In `.env`:
```
DATABASE_URL=postgresql+asyncpg://postgres:password@localhost:5432/chatbot
```

**Cloud:**
- Sign up: https://neon.tech
- Create project
- Copy connection string to `.env`

---

## 🚦 Status Check Commands

```bash
# Check all services are healthy
curl http://localhost:8000/v1/health

# Check if server is running
curl http://localhost:8000/

# Test main query endpoint
curl -X POST http://localhost:8000/v1/query \
  -H "Content-Type: application/json" \
  -d '{"question":"Test?","session_id":"test"}'
```

---

## 📋 API Endpoints Quick Reference

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/v1/health` | GET | Check service status |
| `/v1/query` | POST | Ask chatbot a question |
| `/v1/logs` | GET | View query history |
| `/v1/logs/aggregate` | GET | Basic analytics (7 days) |
| `/v1/logs/metrics` | GET | Performance metrics |
| `/v1/logs/top-questions` | GET | Most asked questions |
| `/v1/logs/coverage` | GET | Content coverage by chapter |

See [TESTING_GUIDE.md](./TESTING_GUIDE.md) for full curl examples.

---

## 🗂️ Project Structure Quick Reference

```
backend/
├── README.md                    ← Overview & commands
├── LOCAL_SETUP.md              ← Detailed setup guide
├── TESTING_GUIDE.md            ← How to test
├── QUICKSTART_5MIN.md          ← 5-minute quick start
├── .env.example                ← Configuration template
├── requirements.txt            ← Dependencies
├── main.py                     ← FastAPI entry point
│
├── app/
│   ├── api/v1/
│   │   ├── query.py            ← Main chatbot endpoint
│   │   ├── health.py           ← Health checks
│   │   └── logs.py             ← Logs & analytics
│   ├── services/               ← Business logic
│   │   ├── rag_service.py      ← RAG pipeline (6 stages)
│   │   ├── qdrant_service.py   ← Vector search
│   │   ├── gemini_service.py   ← LLM + embeddings
│   │   ├── postgres_service.py ← Database operations
│   │   └── analytics_service.py← Analytics computations
│   ├── models/
│   │   ├── database.py         ← SQLAlchemy setup
│   │   ├── chat_query.py       ← ORM model
│   │   └── schemas.py          ← Pydantic schemas
│   ├── utils/
│   │   ├── validators.py       ← Input validation
│   │   ├── exceptions.py       ← Custom exceptions
│   │   └── error_handlers.py   ← Error handling
│   └── core/
│       ├── config.py           ← Environment config
│       ├── logging.py          ← Logging setup
│       └── constants.py        ← RAG prompts & thresholds
│
├── tests/                      ← Test files
│   ├── test_rag_service_us1.py
│   └── test_query_endpoint_us1.py
│
├── quickstart.sh               ← Setup script (macOS/Linux)
└── quickstart.bat              ← Setup script (Windows)
```

---

## 💡 Learning Path

### For Complete Beginners
1. Read this file (you are here!)
2. **[QUICKSTART_5MIN.md](./QUICKSTART_5MIN.md)** - Get it running
3. **[TESTING_GUIDE.md](./TESTING_GUIDE.md)** - Test the endpoints
4. **[LOCAL_SETUP.md](./LOCAL_SETUP.md)** - Understand what went wrong (if needed)

### For Developers
1. **[README.md](./README.md)** - Architecture overview
2. **[LOCAL_SETUP.md](./LOCAL_SETUP.md)** - Complete setup
3. Browse `app/` directory to understand code structure
4. **[TESTING_GUIDE.md](./TESTING_GUIDE.md)** - Run tests

### For DevOps/Deployment
1. **[README.md#deployment](./README.md#deployment)** - Deployment overview
2. Check `docs/` folder for deployment guides
3. **[LOCAL_SETUP.md](./LOCAL_SETUP.md)** - Understand all components

---

## ⏱️ Typical Setup Time

- **Reading docs**: 15 minutes
- **Downloading & installing**: 5 minutes
- **Setting up API keys**: 5 minutes
- **Running server**: 1 minute
- **Testing endpoints**: 2 minutes

**Total: ~30 minutes** (including reading)

---

## 🔍 Troubleshooting Quick Links

- **Python not found?** → See [LOCAL_SETUP.md#1-environment-setup](./LOCAL_SETUP.md#1-environment-setup)
- **Port already in use?** → See [LOCAL_SETUP.md#error-6-port-8000-already-in-use](./LOCAL_SETUP.md#error-6-port-8000-already-in-use)
- **API key error?** → See [LOCAL_SETUP.md#error-4-invalid-gemini-api-key](./LOCAL_SETUP.md#error-4-invalid-gemini-api-key)
- **Cannot connect to Qdrant?** → See [LOCAL_SETUP.md#error-2-cannot-connect-to-qdrant](./LOCAL_SETUP.md#error-2-cannot-connect-to-qdrant)
- **Database connection failed?** → See [LOCAL_SETUP.md#error-3-cannot-connect-to-database](./LOCAL_SETUP.md#error-3-cannot-connect-to-database)

---

## 📞 Need Help?

1. **Quick fix?** → Check [LOCAL_SETUP.md#6-debugging-common-errors](./LOCAL_SETUP.md#6-debugging-common-errors)
2. **Want to test?** → See [TESTING_GUIDE.md](./TESTING_GUIDE.md)
3. **Want examples?** → Check [TESTING_GUIDE.md#5-test-the-endpoints-locally](./TESTING_GUIDE.md#5-test-the-endpoints-locally)
4. **In a hurry?** → [QUICKSTART_5MIN.md](./QUICKSTART_5MIN.md)

---

## 📊 File Overview

| File | Size | Audience |
|------|------|----------|
| QUICKSTART_5MIN.md | 2K | Everyone (5 min read) |
| README.md | 8K | All developers |
| LOCAL_SETUP.md | 11K | Detailed setup |
| TESTING_GUIDE.md | 13K | Testing & QA |
| .env.example | 2K | Configuration |

---

**Status**: ✅ Ready to run locally
**Version**: 1.0.0 (Feature Complete MVP)
**Last Updated**: December 2024

---

## 🚀 Next Steps

1. **New to this?** → Start with [QUICKSTART_5MIN.md](./QUICKSTART_5MIN.md)
2. **Already setup?** → Run: `uvicorn main:app --reload`
3. **Ready to test?** → Open: http://localhost:8000/docs
4. **Need help?** → Check [LOCAL_SETUP.md](./LOCAL_SETUP.md)
