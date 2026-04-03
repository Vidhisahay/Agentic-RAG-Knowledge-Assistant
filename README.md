# Agentic RAG Knowledge Assistant

> An intelligent document querying system powered by FastAPI, FAISS, and OpenAI — with agent-style reasoning, Redis caching, and async endpoints.


## Overview

This project is a production-style **Retrieval-Augmented Generation (RAG)** backend that answers natural language queries over uploaded documents. Instead of a single retrieval-and-respond step, it uses an **agent-style workflow** to dynamically decide whether to summarize, extract, or answer — based on query intent.

Built to demonstrate real-world LLM system design skills: vector search, caching, async APIs, query logging, and performance optimization.


## Features

| Feature | Description |
|---|---|
| Document Ingestion | Upload PDFs/text, auto-chunk, embed, and store in FAISS |
| Intelligent Query | Retrieve relevant chunks → pass to LLM → return structured answer |
| Agent Workflow | Classify query intent → decide action (summarize / extract / Q&A) |
| Redis Caching | Cache repeated queries; measurable latency reduction |
| Query Logging | Log every query, response time, and token usage to PostgreSQL |
| Async FastAPI | Full async endpoints for concurrent request handling |



## Architecture

```
User Query
    │
    ▼
FastAPI Endpoint (async)
    │
    ▼
Redis Cache Check ──── Cache HIT ──────────────────────► Return Cached Response
    │
  Cache MISS
    │
    ▼
Agent Controller
    ├── Step 1: Classify Query Intent
    ├── Step 2: Retrieve Relevant Chunks (FAISS)
    ├── Step 3: Decide Action → summarize / extract / answer
    └── Step 4: Generate Response (OpenAI)
    │
    ▼
Store in Redis + Log to PostgreSQL
    │
    ▼
Return Response
```



## Tech Stack

| Layer | Technology |
|---|---|
| Backend Framework | FastAPI (async) |
| LLM | OpenAI API (GPT-4) |
| Vector Store | FAISS |
| Embeddings | OpenAI `text-embedding-3-small` |
| Cache | Redis |
| Database | PostgreSQL |
| Deployment | Render / Railway |
| Language | Python 3.11+ |


## Getting Started

### Prerequisites

- Python 3.11+
- Docker (for Redis + PostgreSQL)
- OpenAI API key

### 1. Clone the repository

```bash
git clone https://github.com/Vidhisahay/Agentic-RAG-Knowledge-Assistant.git
cd agentic-rag-assistant
```

### 2. Set up environment variables

```bash
cp .env.example .env
# Fill in: OPENAI_API_KEY, DATABASE_URL, REDIS_URL
```

### 3. Start infrastructure

```bash
docker-compose up -d   # Starts Redis + PostgreSQL
```

### 4. Install dependencies

```bash
pip install -r requirements.txt
```

### 5. Run the API

```bash
uvicorn app.main:app --reload
```

API docs available at: `http://localhost:8000/docs`



## API Endpoints

### `POST /ingest`
Upload a PDF or text file for processing.

```bash
curl -X POST "http://localhost:8000/ingest" \
  -F "file=@document.pdf"
```

**Response:**
```json
{
  "status": "success",
  "chunks_created": 42,
  "doc_id": "abc123"
}
```


### `POST /query`
Ask a natural language question over ingested documents.

```bash
curl -X POST "http://localhost:8000/query" \
  -H "Content-Type: application/json" \
  -d '{"question": "Summarize the key risks in this document"}'
```

**Response:**
```json
{
  "answer": "The document identifies three key risks: ...",
  "intent": "summarize",
  "cached": false,
  "response_time_ms": 312,
  "tokens_used": 487
}
```


## Agent Workflow — How It Works

The **Agent Controller** is the core differentiator. Instead of directly passing every query to the LLM, it first classifies intent:

| Intent | Trigger Example | Action |
|---|---|---|
| `summarize` | "Summarize the document" | Retrieve top chunks → ask LLM to summarize |
| `extract` | "Extract all dates / names" | Retrieve → structured extraction prompt |
| `answer` | "What does clause 3 say?" | Retrieve → direct Q&A prompt |

This means the system uses **different prompting strategies** based on what the user actually needs — not a one-size-fits-all approach.


## Caching Performance

Redis caches query results by a hash of the question text.

| Query Type | Without Cache | With Cache | Improvement |
|---|---|---|---|
| Repeated exact query | ~900ms | ~8ms | **~99% faster** |
| Semantically similar | ~900ms | —  | Full pipeline |

Cache TTL is configurable (default: 1 hour).


## Query Logs (PostgreSQL)

Every query is logged to the `query_logs` table:

```sql
CREATE TABLE query_logs (
    id          SERIAL PRIMARY KEY,
    question    TEXT,
    intent      VARCHAR(20),
    response    TEXT,
    cached      BOOLEAN,
    tokens_used INTEGER,
    response_ms INTEGER,
    created_at  TIMESTAMP DEFAULT NOW()
);
```

This enables analysis of usage patterns, slow queries, and model cost tracking.


## Example Queries

```
"What are the main conclusions of this report?"        → summarize
"Extract all monetary values from the document"        → extract
"Who is responsible for clause 4.2?"                  → answer
"List all risks mentioned in section 3"                → extract
"Give me a one-paragraph summary of this contract"     → summarize
```


## Future Improvements

- [ ] Multi-document cross-referencing
- [ ] Streaming responses via SSE
- [ ] User-level document namespacing
- [ ] Swap FAISS → Chroma for persistent storage
- [ ] LangSmith / OpenTelemetry tracing



## Author

Made with ❤️ by Vidhi - [GitHub](https://github.com/Vidhisahay) · [LinkedIn](https://www.linkedin.com/in/vidhisahay/)