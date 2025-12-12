"""Application constants for RAG Chatbot Backend."""

# RAG Configuration
RAG_CONSTRAINT_PROMPT = """You are a helpful assistant for the Physical AI & Humanoid Robotics course.
Answer ONLY using information provided in the course materials below.
If the user asks about something not covered in the course materials, respond with:
"I don't have information about this in the course material. Please ask about topics covered in the course."
Do not use any external knowledge or information outside the provided context."""

VALIDATION_PROMPT = """Given the user question and the retrieved course material, check if the response stays within
the bounds of the provided material. Respond with only "VALID" or "HALLUCINATION"."""

# Vector Database Configuration
QDRANT_VECTOR_SIZE = 768  # Gemini embeddings dimension
QDRANT_COLLECTION_NAME = "course_lessons"

# Context and Query Limits
MAX_QUERY_LENGTH = 2000
MIN_QUERY_LENGTH = 5
MAX_CONTEXT_LENGTH = 4000
MAX_RETRIEVED_CHUNKS = 5

# Performance Targets
TARGET_P95_LATENCY_MS = 3000
GEMINI_TIMEOUT_SECONDS = 30
QDRANT_TIMEOUT_SECONDS = 5
POSTGRES_TIMEOUT_SECONDS = 5

# Scoring
MIN_CONFIDENCE_SCORE = 0.3
MIN_SIMILARITY_THRESHOLD = 0.5

# Session Configuration
SESSION_ID_PATTERN = r"^[a-zA-Z0-9\-_]{10,50}$"

# Logging
LOG_FORMAT_PRODUCTION = "json"
LOG_FORMAT_DEVELOPMENT = "plain"
