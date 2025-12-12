# Physical AI & Humanoid Robotics Course Constitution

## Core Principles

### Content-Source-of-Truth
The book content (Docusaurus markdown files) is the authoritative source for all chatbot knowledge. The chatbot MUST answer only from book content or user-selected text. No external knowledge injection or inference beyond the provided context is permitted.

### RAG-First Architecture
Every user query flows through Retrieval-Augmented Generation: retrieve relevant content from Qdrant vector store, augment OpenAI Agent context with those embeddings, generate responses. This ensures traceability and prevents hallucination.

### Embedded-First User Experience
The chatbot lives inside the book (Docusaurus integration), not as a separate tool. Users interact with course content and AI assistance in one unified interface with no context-switching.

### Tech Stack Adherence
Production deployment MUST use: Docusaurus (frontend), FastAPI (backend), OpenAI Agents/ChatKit SDK (LLM), Neon Postgres (session logs), Qdrant Cloud (vector embeddings), GitHub Pages (hosting). No alternatives without architecture review.

### Fixed Content Structure
The course is 4 chapters × 2 lessons each (8 lessons fixed). Lesson count is immutable. All content, embeddable demos, and chatbot training data MUST fit this structure.

## Technical Requirements

- **Frontend**: Docusaurus 3.x with React custom plugin for chatbot embedding
- **Backend**: FastAPI with async request handling, request logging to Neon Postgres
- **LLM**: OpenAI Agents SDK or ChatKit SDK for agentic RAG behavior
- **Vector DB**: Qdrant Cloud for embedding storage and semantic search
- **Deployment**: GitHub Pages static hosting (Docusaurus build) + serverless or containerized FastAPI backend
- **Security**: API key management via environment variables; no secrets in code or git
- **API Contracts**: REST endpoints documented with OpenAPI/Swagger; request/response schemas versioned

## Development Workflow

1. **Spec-Driven**: Every feature starts with a spec defining requirements, API contracts, and acceptance criteria
2. **TDD Enforcement**: Tests written first; implementation follows Red-Green-Refactor discipline
3. **Code Review**: All changes require review confirming alignment with this constitution and spec compliance
4. **Traceability**: Every change links to a spec, task, or ADR; commit messages reference feature context

## Governance

This constitution is the authoritative guide for all development decisions. Amendments require documented rationale and user approval. All PRs MUST verify compliance with core principles before merge.

**Version**: 1.0.0 | **Ratified**: 2025-12-09 | **Last Amended**: 2025-12-09
