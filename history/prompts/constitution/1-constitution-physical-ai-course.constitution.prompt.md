---
id: 1
title: Constitution - Physical AI Course
stage: constitution
date: 2025-12-09
surface: agent
model: claude-haiku-4-5-20251001
feature: none
branch: master
user: user
command: /sp.constitution
labels: ["constitution", "governance", "rag-chatbot", "docusaurus"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
  - .specify/memory/constitution.md
tests:
  - null
---

## Prompt

```text
Write the sp.constitution for this project:

Title: Physical AI & Humanoid Robotics Course

Project Requirements:
- Create an online book using Docusaurus and deploy it to GitHub Pages.
- Build and embed a RAG chatbot directly inside the book.
- The chatbot must answer only from the book's own content or text selected by the user.
- Use OpenAI Agents/ChatKit SDK, FastAPI backend, Neon Postgres for logs, and Qdrant Cloud for embeddings.
- Content structure: 4 chapters, each with 2 lessons (fixed).

Keep the constitution short, clear, and focused on high-level goals and deliverables.
```

## Response snapshot

Created constitution v1.0.0 with 5 core principles and 4 governance sections. Principles establish content-source-of-truth (book is authoritative), RAG-first architecture, embedded UX, tech stack adherence, and fixed content structure (4×2 lessons). Technical Requirements section specifies all tooling. Development Workflow mandates spec-driven, TDD, code review, and traceability. Constitution now guides all future specs, plans, and code reviews.

## Outcome

- ✅ Impact: Constitution provides clear guidance for the Physical AI course project; all future feature development will reference these principles
- 🧪 Tests: No tests applicable; governance artifact
- 📁 Files: .specify/memory/constitution.md (created/updated, v1.0.0)
- 🔁 Next prompts: Feature specifications for chatbot integration, Docusaurus setup, FastAPI backend, embedding pipeline
- 🧠 Reflection: Constitution captures the dual requirement: book as knowledge base + RAG chatbot as interface. Tech stack is concrete and constraints are clear (no hallucination, embedded UX, fixed lesson structure).

## Evaluation notes (flywheel)

- Failure modes observed: None
- Graders run and results (PASS/FAIL): Constitution validation PASS (no unresolved placeholders, version set, dates ISO format, all principles testable)
- Prompt variant (if applicable): null
- Next experiment: Proceed to feature specs for chatbot integration and book structure

