# RAG Chatbot Backend - Testing Guide

Quick reference for testing all endpoints locally with `curl` and Python.

---

## Prerequisites

Server must be running:
```bash
uvicorn main:app --reload
```

Base URL: `http://localhost:8000`

---

## 1. Health Check Endpoint

### Test if all services are healthy

```bash
curl http://localhost:8000/v1/health
```

**Expected Response (200):**
```json
{
  "status": "healthy",
  "services": {
    "qdrant": "healthy",
    "gemini": "healthy",
    "postgres": "healthy"
  },
  "timestamp": "2024-01-15T10:30:00Z"
}
```

**Troubleshooting:**
- If any service shows "unhealthy", check that Qdrant, Gemini API, and Postgres are running

---

## 2. Main Query Endpoint (User Story 1 - Basic RAG)

### Submit a question to the chatbot

```bash
curl -X POST http://localhost:8000/v1/query \
  -H "Content-Type: application/json" \
  -d '{
    "question": "What is kinematics in robotics?",
    "session_id": "user_session_001",
    "selected_context": null
  }'
```

**Expected Response (200):**
```json
{
  "response_text": "Kinematics is the branch of mechanics that deals with motion without considering forces. In robotics, kinematics describes how the robot's joints move to achieve a desired position and orientation...",
  "source_references": [
    {
      "chapter": 1,
      "lesson": 1,
      "section": "Introduction to Kinematics",
      "context_grounded": false
    }
  ],
  "confidence_score": 0.85,
  "timestamp": "2024-01-15T10:30:00Z"
}
```

**Test Different Questions:**
```bash
# Test 1: Basic question
curl -X POST http://localhost:8000/v1/query \
  -H "Content-Type: application/json" \
  -d '{
    "question": "Explain forward kinematics",
    "session_id": "user_001"
  }'

# Test 2: Out of scope question
curl -X POST http://localhost:8000/v1/query \
  -H "Content-Type: application/json" \
  -d '{
    "question": "How do I make sushi?",
    "session_id": "user_002"
  }'

# Test 3: Too short (should fail validation)
curl -X POST http://localhost:8000/v1/query \
  -H "Content-Type: application/json" \
  -d '{
    "question": "Hi",
    "session_id": "user_003"
  }'
```

**Response Codes:**
- `200` - Success
- `400` - Validation error (question too short, invalid session_id)
- `502` - Gemini API error
- `503` - Qdrant unavailable

---

## 3. Context-Aware Query (User Story 2)

### Submit a question with selected text context

```bash
curl -X POST http://localhost:8000/v1/query \
  -H "Content-Type: application/json" \
  -d '{
    "question": "Can you explain this specific passage about joint movement?",
    "session_id": "user_with_context_001",
    "selected_context": "In a revolute joint, the motion is rotational about a fixed axis, allowing only angular movement. This type of joint is commonly used in robot arms and legs."
  }'
```

**Expected Response (200):**
```json
{
  "response_text": "Based on the passage you selected about joint movement... [response focused on selected text]",
  "source_references": [
    {
      "chapter": 2,
      "lesson": 1,
      "section": "Joint Types",
      "context_grounded": true
    }
  ],
  "confidence_score": 0.92,
  "timestamp": "2024-01-15T10:30:00Z"
}
```

**Key Difference:** Notice `"context_grounded": true` in the source_references when selected_context is provided.

---

## 4. Query Logs Endpoint

### Get paginated query history

```bash
# Get first 10 queries
curl "http://localhost:8000/v1/logs?limit=10&offset=0"

# Get next 10 queries
curl "http://localhost:8000/v1/logs?limit=10&offset=10"

# Filter by session ID
curl "http://localhost:8000/v1/logs?session_id=user_001&limit=20"

# Get queries from last 7 days
curl "http://localhost:8000/v1/logs?days_back=7&limit=50"
```

**Expected Response (200):**
```json
{
  "items": [
    {
      "id": 1,
      "question": "What is kinematics?",
      "response_text": "...",
      "session_id": "user_001",
      "confidence_score": 0.85,
      "timestamp": "2024-01-15T10:00:00Z",
      "source_chapters": [...],
      "query_duration_ms": 2345
    }
  ],
  "total": 1,
  "limit": 10,
  "offset": 0
}
```

---

## 5. Analytics Endpoints

### 5a. Aggregated Analytics (Simple)

```bash
# Get basic analytics for last 7 days
curl "http://localhost:8000/v1/logs/aggregate?days_back=7"

# Get analytics for last 30 days
curl "http://localhost:8000/v1/logs/aggregate?days_back=30"
```

**Expected Response (200):**
```json
{
  "query_count": 42,
  "avg_confidence": 0.78,
  "avg_response_time_ms": 2450,
  "unique_sessions": 15,
  "period_days": 7
}
```

### 5b. Performance Metrics (Detailed)

```bash
# Get detailed performance metrics
curl "http://localhost:8000/v1/logs/metrics?days_back=7"

# With different time ranges
curl "http://localhost:8000/v1/logs/metrics?days_back=30"
```

**Expected Response (200):**
```json
{
  "query_count": 42,
  "period_days": 7,
  "avg_confidence": 0.78,
  "min_confidence": 0.42,
  "max_confidence": 0.99,
  "avg_response_time_ms": 2450,
  "p95_response_time_ms": 3500,
  "avg_retrieval_time_ms": 800,
  "avg_generation_time_ms": 1200,
  "unique_sessions": 15
}
```

### 5c. Top Questions

```bash
# Get top 10 questions
curl "http://localhost:8000/v1/logs/top-questions?limit=10&days_back=7"

# Get top 5 questions for last 30 days
curl "http://localhost:8000/v1/logs/top-questions?limit=5&days_back=30"
```

**Expected Response (200):**
```json
{
  "items": [
    {
      "question": "What is forward kinematics?",
      "count": 12,
      "avg_confidence": 0.85
    },
    {
      "question": "Explain inverse kinematics",
      "count": 8,
      "avg_confidence": 0.72
    }
  ],
  "period_days": 7
}
```

### 5d. Content Coverage

```bash
# Get content coverage analytics
curl "http://localhost:8000/v1/logs/coverage"
```

**Expected Response (200):**
```json
{
  "coverage": {
    "Ch1.L1": 15,
    "Ch1.L2": 8,
    "Ch2.L1": 22,
    "Ch3.L1": 5
  },
  "total_queries": 50,
  "chapters_queried": 3
}
```

---

## Testing with Python

### Complete Python Test Script

```python
import requests
import json
from datetime import datetime

BASE_URL = "http://localhost:8000"

def test_health():
    """Test health endpoint"""
    print("Testing health endpoint...")
    response = requests.get(f"{BASE_URL}/v1/health")
    print(f"Status: {response.status_code}")
    print(json.dumps(response.json(), indent=2))
    print()

def test_query():
    """Test main query endpoint"""
    print("Testing query endpoint...")
    payload = {
        "question": "What is kinematics in robotics?",
        "session_id": "test_user_001",
        "selected_context": None
    }
    response = requests.post(f"{BASE_URL}/v1/query", json=payload)
    print(f"Status: {response.status_code}")
    result = response.json()
    print(f"Confidence: {result['confidence_score']}")
    print(f"Response: {result['response_text'][:100]}...")
    print()

def test_query_with_context():
    """Test context-aware query"""
    print("Testing context-aware query...")
    payload = {
        "question": "Can you explain this?",
        "session_id": "test_user_002",
        "selected_context": "Kinematics is the study of motion without considering forces."
    }
    response = requests.post(f"{BASE_URL}/v1/query", json=payload)
    print(f"Status: {response.status_code}")
    result = response.json()
    print(f"Context grounded: {result['source_references'][0]['context_grounded'] if result['source_references'] else 'N/A'}")
    print()

def test_logs():
    """Test logs endpoint"""
    print("Testing logs endpoint...")
    response = requests.get(f"{BASE_URL}/v1/logs?limit=5")
    print(f"Status: {response.status_code}")
    data = response.json()
    print(f"Total logs: {data['total']}")
    print(f"Items returned: {len(data['items'])}")
    print()

def test_analytics():
    """Test analytics endpoints"""
    print("Testing analytics endpoints...")

    # Metrics
    response = requests.get(f"{BASE_URL}/v1/logs/metrics?days_back=7")
    print(f"Metrics Status: {response.status_code}")
    metrics = response.json()
    print(f"  Query count: {metrics['query_count']}")
    print(f"  P95 latency: {metrics['p95_response_time_ms']:.0f}ms")

    # Top questions
    response = requests.get(f"{BASE_URL}/v1/logs/top-questions?limit=5")
    print(f"Top Questions Status: {response.status_code}")
    top_q = response.json()
    print(f"  Top {len(top_q['items'])} questions found")

    # Coverage
    response = requests.get(f"{BASE_URL}/v1/logs/coverage")
    print(f"Coverage Status: {response.status_code}")
    coverage = response.json()
    print(f"  Chapters queried: {coverage['chapters_queried']}")
    print()

def test_validation_errors():
    """Test error handling"""
    print("Testing validation errors...")

    # Question too short
    payload = {"question": "Hi", "session_id": "test"}
    response = requests.post(f"{BASE_URL}/v1/query", json=payload)
    print(f"Short question: {response.status_code} (should be 400)")

    # Invalid session ID
    payload = {"question": "Valid question here", "session_id": "x"}
    response = requests.post(f"{BASE_URL}/v1/query", json=payload)
    print(f"Invalid session_id: {response.status_code} (should be 400)")
    print()

if __name__ == "__main__":
    print("=" * 50)
    print("RAG Chatbot Backend - Comprehensive Test Suite")
    print("=" * 50)
    print()

    try:
        test_health()
        test_query()
        test_query_with_context()
        test_logs()
        test_analytics()
        test_validation_errors()

        print("✅ All tests completed!")
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to server at http://localhost:8000")
        print("Make sure the server is running: uvicorn main:app --reload")
    except Exception as e:
        print(f"❌ Error: {e}")
```

---

## 7. Common Test Scenarios

### Scenario 1: Basic RAG Query Flow
1. Health check passes
2. Submit question
3. Get response with sources and confidence
4. Check logs to see query was recorded

```bash
# Step 1
curl http://localhost:8000/v1/health

# Step 2
curl -X POST http://localhost:8000/v1/query \
  -H "Content-Type: application/json" \
  -d '{"question":"What is dynamics?","session_id":"test_001"}'

# Step 3
curl "http://localhost:8000/v1/logs?limit=1"
```

### Scenario 2: Context-Aware Follow-up
1. Query with selected_context
2. Verify context_grounded=true in response
3. Check logs show selected_context was stored

```bash
curl -X POST http://localhost:8000/v1/query \
  -H "Content-Type: application/json" \
  -d '{
    "question": "Explain this more",
    "session_id": "test_002",
    "selected_context": "Newton proposed three laws of motion."
  }'
```

### Scenario 3: Analytics Over Time
1. Submit multiple queries from different sessions
2. Check analytics aggregation
3. Verify top_questions identifies frequently asked questions

```bash
# Submit 5 similar questions
for i in {1..5}; do
  curl -X POST http://localhost:8000/v1/query \
    -H "Content-Type: application/json" \
    -d "{\"question\":\"What is kinematics?\",\"session_id\":\"user_$i\"}"
done

# Check top questions
curl "http://localhost:8000/v1/logs/top-questions"
```

---

## 8. Load Testing (Basic)

### Test with multiple concurrent requests

```bash
# Using Apache Bench (install: apt-get install apache2-utils)
ab -n 100 -c 10 http://localhost:8000/v1/health

# Using GNU parallel
seq 1 100 | parallel -j 10 "curl -s http://localhost:8000/v1/health > /dev/null && echo 'Request {}: OK'"
```

---

## 9. Response Status Codes

| Code | Meaning | Example |
|------|---------|---------|
| 200 | Success | Query processed, logs retrieved |
| 400 | Validation Error | Question too short, invalid session_id |
| 502 | Gateway Error | Gemini API unreachable |
| 503 | Service Unavailable | Qdrant connection failed, Postgres down |
| 500 | Server Error | Unexpected error in processing |

---

## Tips

- **Swagger UI**: Visit `http://localhost:8000/docs` for interactive testing
- **Request ID**: Every response includes `X-Correlation-ID` header for tracing
- **Debug Logs**: Set `LOG_LEVEL=debug` in `.env` to see detailed operation logs
- **Session ID**: Can be any string, used to group queries by user
- **Confidence Score**: 0.0-1.0, higher = more confident answer
- **P95 Latency**: Target <3000ms; check in `/v1/logs/metrics`

---

**Next Steps**: After testing passes locally, see `DEPLOYMENT.md` for production setup.
