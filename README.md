# Agentic RAG Knowledge Assistant
 
> An intelligent document querying system powered by FastAPI, FAISS, Groq (LLaMA 3.1), and sentence-transformers - with agent-style reasoning, Redis caching, PostgreSQL logging, and full test coverage.
 
[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-async-green.svg)](https://fastapi.tiangolo.com)
[![Tests](https://img.shields.io/badge/Tests-6%2F6%20passing-brightgreen.svg)]()
[![Deploy](https://img.shields.io/badge/Deployed-Render-purple.svg)](https://render.com)
 

 
## Overview
 
This project is a production-style **Retrieval-Augmented Generation (RAG)** backend that answers natural language queries over uploaded documents.
 
Instead of a single retrieval-and-respond step, it uses an **agent-style workflow** to dynamically classify query intent and apply a different prompting strategy - summarization, extraction, or direct Q&A - based on what the user actually needs.
 
Built to demonstrate real-world LLM system design: vector search, caching, async APIs, query logging, and performance optimization.
 
 
## Features
 
| Feature | Description |
|---|---|
| Document Ingestion | Upload PDFs or TXT files - auto-chunked, embedded, stored in FAISS |
| Semantic Retrieval | Query embedding matched against FAISS index for top-k chunks |
| Agent Workflow | Classifies intent → picks prompt strategy → generates response |
| Redis Caching | Repeated queries return instantly (~7ms vs ~800ms) |
| Query Logging | Every query logged to PostgreSQL with intent, latency, token estimate |
| Async FastAPI | Full async endpoints for concurrent request handling |
| Test Coverage | 6/6 pytest tests covering ingestion, querying, and cache behaviour |
 
 
## Architecture
 
```
User Query
    │
    ▼
FastAPI Endpoint (async)
    │
    ▼
Redis Cache Check ──── Cache HIT ──────────────────► Return in ~7ms
    │
  Cache MISS
    │
    ▼
Agent Controller
    ├── Step 1: Classify Intent (summarize / extract / answer)
    ├── Step 2: Embed Query (sentence-transformers)
    ├── Step 3: Retrieve Top-K Chunks (FAISS)
    ├── Step 4: Select Prompt Template
    └── Step 5: Generate Response (Groq LLaMA 3.1)
    │
    ▼
Store in Redis + Log to PostgreSQL
    │
    ▼
Return structured JSON response
```
 
 
## Tech Stack
 
| Layer | Technology |
|---|---|
| Backend Framework | FastAPI (async) |
| LLM | Groq API - LLaMA 3.1 8B Instant |
| Vector Store | FAISS (Facebook AI Similarity Search) |
| Embeddings | sentence-transformers `all-MiniLM-L6-v2` (local, free) |
| Cache | Redis |
| Database | PostgreSQL + SQLAlchemy |
| Testing | pytest + FastAPI TestClient |
| Deployment | Render (API + Redis + PostgreSQL) |
| Language | Python 3.11+ |
 

 
## Getting Started (Local)
 
### Prerequisites
- Python 3.11+
- Docker Desktop
- Groq API key - free at [console.groq.com](https://console.groq.com)
 
### 1. Clone the repo
 
```bash
git clone https://github.com/your-username/agentic-rag-assistant.git
cd agentic-rag-assistant
```
 
### 2. Set up environment variables
 
```bash
cp .env.example .env
# Fill in: GROQ_API_KEY, DATABASE_URL, REDIS_URL
```
 
### 3. Start infrastructure
 
```bash
docker-compose up -d
```
 
### 4. Install dependencies
 
```bash
pip install -r requirements.txt
```
 
### 5. Run the API
 
```bash
uvicorn app.main:app
```
 
Swagger UI: `http://localhost:8000/docs`
 
 
## API Endpoints
 
### `POST /ingest/`
Upload a PDF or TXT file.
 
```bash
curl -X POST "http://localhost:8000/ingest/" \
  -F "file=@document.pdf"
```
 
```json
{
  "status": "success",
  "filename": "document.pdf",
  "chunks_created": 34
}
```
 
 
### `POST /query/`
Ask a natural language question.
 
```bash
curl -X POST "http://localhost:8000/query/" \
  -H "Content-Type: application/json" \
  -d '{"question": "What is RAG?"}'
```
 
```json
{
  "question": "What is RAG?",
  "intent": "answer",
  "answer": "RAG stands for Retrieval Augmented Generation - it combines search with LLM generation.",
  "chunks_used": 5,
  "cached": false,
  "response_time_ms": 823
}
```
 
Second call - cache hit:
```json
{
  "question": "What is RAG?",
  "intent": "answer",
  "answer": "RAG stands for Retrieval Augmented Generation - it combines search with LLM generation.",
  "chunks_used": 5,
  "cached": true,
  "response_time_ms": 7
}
```
 
 
### `GET /query/logs`
View recent query logs.
 
```bash
curl http://localhost:8000/query/logs
```
 
```json
[
  {
    "id": 3,
    "question": "What is RAG?",
    "intent": "answer",
    "cached": true,
    "response_time_ms": 7,
    "estimated_tokens": 124,
    "created_at": "2026-04-04T10:23:11"
  }
]
```
 
 
## Agent Workflow - How It Works
 
The **Agent Controller** classifies intent before retrieving or generating anything:
 
| Intent | Example Query | Strategy |
|---|---|---|
| `summarize` | "Give me a summary of this document" | Top chunks → summarization prompt |
| `extract` | "Extract all technologies mentioned" | Top chunks → structured extraction prompt |
| `answer` | "What is FAISS?" | Top chunks → direct Q&A prompt |
 
Each intent maps to a **different prompt template** - so the LLM is always given the right instruction for the task, not a one-size-fits-all approach.
 
 
## Caching Performance
 
Redis caches results by MD5 hash of the question (lowercased, stripped).
 
| Call | Latency | Cached |
|---|---|---|
| First (cache miss) | ~800ms | false |
| Second (cache hit) | ~7ms | true |
| Improvement | **~99% faster** | - |
 
Cache TTL: 1 hour. Automatically invalidated on new document ingestion.
 
 
## Query Logs Schema (PostgreSQL)
 
```sql
CREATE TABLE query_logs (
    id               SERIAL PRIMARY KEY,
    question         TEXT,
    intent           VARCHAR(20),
    answer           TEXT,
    cached           BOOLEAN,
    chunks_used      INTEGER,
    response_time_ms INTEGER,
    estimated_tokens INTEGER,
    created_at       TIMESTAMP
);
```
 
 
## Running Tests
 
```bash
pytest tests/ -v
```
 
```
tests/test_ingest.py::test_root                  PASSED
tests/test_ingest.py::test_ingest_txt            PASSED
tests/test_ingest.py::test_ingest_invalid_format PASSED
tests/test_query.py::test_empty_question         PASSED
tests/test_query.py::test_full_pipeline          PASSED
tests/test_query.py::test_cache_hit              PASSED
 
6 passed in 57s
```

## Deployment
 
Deployed on **Render** - API + Redis + PostgreSQL.
 
- Live API: https://agentic-rag-assistant.onrender.com
- Swagger Docs: https://agentic-rag-assistant.onrender.com/docs
 
> Note: FAISS index is in-memory. Re-ingest documents after each cold start.

## Future Improvements

- [ ] Persistent FAISS via disk or migrate to Chroma
- [ ] Multi-document namespacing per user
- [ ] Streaming responses via Server-Sent Events
- [ ] Frontend UI for document upload and querying
- [ ] LangSmith / OpenTelemetry tracing



## Author

Made with ❤️ by Vidhi - [GitHub](https://github.com/Vidhisahay) · [LinkedIn](https://www.linkedin.com/in/vidhisahay/)