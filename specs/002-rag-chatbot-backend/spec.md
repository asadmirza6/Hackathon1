# Feature Specification: RAG Chatbot Backend

**Feature Branch**: `002-rag-chatbot-backend`
**Created**: 2025-12-09
**Status**: Draft
**Input**: User description: "Generate for Backend Phase of Physical AI & Humanoid Robotics Course book. RAG chatbot using OpenAI Agents SDK style, Python + FastAPI backend, Gemini API key, Qdrant embeddings, Neon Postgres logs. Chatbot answers only from book content or user-selected text. Deploy on all book pages."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Query Book Content via Chatbot (Priority: P1)

A learner visits any lesson page on the Physical AI course website and encounters a question about the content. They open the embedded chatbot, type their question (e.g., "What is ZMP in bipedal walking?"), and the chatbot retrieves the answer directly from the book's lesson content, providing context and page references.

**Why this priority**: This is the core RAG functionality. Users need reliable, accurate answers sourced only from the course material without hallucinations or external knowledge injection.

**Independent Test**: Can be fully tested by querying the bot with questions answered in specific lessons and verifying responses match book content exactly. Delivers immediate value: learners get contextual help without leaving the page.

**Acceptance Scenarios**:

1. **Given** a learner is on Chapter 2, Lesson 1 (Control Systems), **When** they ask "What is a PID controller?", **Then** the chatbot returns the definition from the book with a reference to the source section
2. **Given** the chatbot receives a query, **When** the query is processed, **Then** only content from the 8 lessons is used to generate responses (no external knowledge)
3. **Given** a user asks a question outside the book scope (e.g., "Tell me about quantum computers"), **When** the query is processed, **Then** the chatbot responds "I don't have information about this in the course material" rather than generating external knowledge

---

### User Story 2 - Select Text and Ask Follow-up Questions (Priority: P2)

A learner is reading a complex section about motion planning algorithms. They highlight a passage in the lesson content and click "Ask about this" in the chatbot. The chatbot uses the selected text as context to answer follow-up questions, helping learners dive deeper into specific topics.

**Why this priority**: Enables context-aware interaction model. Users can reference specific parts of the content and ask clarifying questions without retyping context. Improves learning experience.

**Independent Test**: Can be tested by selecting text passages and verifying chatbot uses selected text in RAG context. Delivers value: personalized guidance on specific content.

**Acceptance Scenarios**:

1. **Given** a user selects text from a lesson, **When** they click "Ask about this" and ask a follow-up question, **Then** the chatbot responds using the selected text plus broader book context
2. **Given** selected text is passed to the chatbot API, **When** the response is generated, **Then** responses are grounded in the selected passage and related content

---

### User Story 3 - Query Logging and Analytics (Priority: P3)

The course administrator needs to understand what learners are asking and how the chatbot is performing. All user queries are logged to a Postgres database with timestamps, questions, responses, and metadata, enabling future improvements to the chatbot and identification of knowledge gaps.

**Why this priority**: Enables data-driven improvements and course analytics. Not critical for MVP but essential for continuous improvement.

**Independent Test**: Can be tested by submitting queries and verifying they appear in the database with correct metadata. Delivers value: actionable insights into learner needs.

**Acceptance Scenarios**:

1. **Given** a user submits a query through the chatbot, **When** the query is processed, **Then** it is logged to Postgres with timestamp, question text, response text, and user session ID
2. **Given** logs are stored in Postgres, **When** an admin queries the log table, **Then** they can analyze query patterns and chatbot performance

---

### Edge Cases

- What happens when a query matches content from multiple lessons? (Should return most relevant + indicate multiple sources)
- How does the system handle very long or ambiguous queries? (Should handle gracefully, ask for clarification or return top-N results)
- What happens if the Qdrant vector database is temporarily unavailable? (Should fail gracefully and display helpful error message to user)
- How does the chatbot handle user-selected text that spans multiple paragraphs or sections? (Should handle multi-line selections and maintain context)
- What happens if a learner asks about course logistics (e.g., "When is the assignment due?")? (Outside book scope - should decline politely)

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST accept natural language queries from users via REST API endpoint
- **FR-002**: System MUST retrieve relevant content from the 8 course lessons using Qdrant vector embeddings
- **FR-003**: System MUST generate responses using Gemini API based on retrieved content only (no external knowledge)
- **FR-004**: System MUST support optional user-selected text as additional context for queries
- **FR-005**: System MUST include source references (lesson chapter/section) in responses
- **FR-006**: System MUST explicitly decline to answer questions outside the book scope ("I don't have information about this in the course material")
- **FR-007**: System MUST log all queries to Neon Postgres database with timestamp, question, response, and session ID
- **FR-008**: System MUST handle vector database unavailability gracefully with user-friendly error message
- **FR-009**: System MUST provide API endpoints for query submission and response retrieval
- **FR-010**: System MUST support integration with Docusaurus book pages via embedded chat widget
- **FR-011**: System MUST process queries asynchronously using OpenAI Agents SDK async patterns
- **FR-012**: System MUST validate that responses use only content from book lessons (no hallucinated information)

### Key Entities

- **ChatQuery**: Represents a user question with timestamp, question text, optional selected text context, session ID
- **ChatResponse**: Contains generated response text, source references (lesson/section), confidence score, response timestamp
- **VectorEmbedding**: Maps lesson content chunks to vector embeddings in Qdrant for semantic search
- **QueryLog**: Stores all chat interactions in Postgres: query text, response text, metadata, user session, timestamp

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Chatbot responds to 95% of queries with answers sourced only from book content (no hallucinations)
- **SC-002**: Response generation completes within 3 seconds on average (for standard queries)
- **SC-003**: Vector search returns relevant content for 90% of course-related queries
- **SC-004**: System handles 100 concurrent users without errors or timeouts
- **SC-005**: All queries are successfully logged to Postgres database within 5 seconds
- **SC-006**: Chatbot correctly declines to answer 95% of out-of-scope questions with appropriate message
- **SC-007**: 85% of learner queries receive responses rated as "helpful" in user feedback

## Assumptions

- Book content (8 lesson markdown files) is already created and available in `book/docs/chapter-N/lesson-M.md`
- Docusaurus book is deployed and accessible at `/physical-ai/` base URL
- Provided credentials (Gemini API key, Qdrant cluster ID, Neon connection string) are valid and active
- Lesson content is in English and structured with standard markdown headers
- Users have JavaScript enabled in their browsers for embedded chat widget

## Scope

**In Scope**:
- FastAPI backend service with RAG chatbot endpoints
- Integration with Qdrant for vector embeddings
- Gemini API for response generation
- Neon Postgres logging
- Embedded chat widget for Docusaurus pages
- Query logging and analytics
- Error handling and graceful degradation

**Out of Scope**:
- User authentication or multi-user sessions (basic session tracking only)
- Advanced NLP preprocessing (use vectors directly from embeddings)
- Custom fine-tuning of models
- Admin dashboard for query analytics (logs stored but no UI)
- Chatbot response fine-tuning beyond scope-limiting

## Constraints

- Must use only Gemini API (not OpenAI, Claude, or other LLMs)
- Must use Qdrant for vector embeddings (not Pinecone or other vector DB)
- Must use Neon Postgres for query logs (not SQLite, MongoDB, etc.)
- Responses must be limited to 8 course lessons only
- Backend must be Python + FastAPI (not Node.js, Go, Java)
- Chatbot widget must embed cleanly in Docusaurus without breaking existing page layout

## Dependencies & Integration Points

**External Services**:
- Gemini API (Google Cloud) for LLM generation
- Qdrant Cloud for vector embeddings
- Neon Postgres for query logging

**Internal Systems**:
- Docusaurus book site (pages served from `book/build/`)
- Lesson markdown files (source of truth for content)

## Acceptance Gates

- All 12 functional requirements implemented and testable
- All 3 user stories independently testable and passing
- 7 success criteria measured and achieved
- No hallucinations in sample queries (manual testing)
- Load testing: 100 concurrent users without failure
- 0 broken integrations with external services
