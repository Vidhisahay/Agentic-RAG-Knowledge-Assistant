from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import time
from app.agent.controller import run_agent
from app.rag.embedder import get_embeddings
from app.rag.retriever import retrieve
from app.cache.redis_client import get_cached, set_cache

router = APIRouter()

class QueryRequest(BaseModel):
    question: str

@router.post("/debug")
async def debug_query(request: QueryRequest):
    query_embedding = get_embeddings([request.question])[0]
    chunks = retrieve(query_embedding, top_k=5)
    return {"chunks": chunks}

@router.post("/")
async def query_documents(request: QueryRequest):
    if not request.question.strip():
        raise HTTPException(status_code=400, detail="Question cannot be empty")

    start = time.time()

    # Step 1: Check cache first
    cached = get_cached(request.question)
    if cached:
        cached["cached"] = True
        cached["response_time_ms"] = round((time.time() - start) * 1000)
        return {"question": request.question, **cached}

    # Step 2: Cache miss — run the full agent pipeline
    result = run_agent(request.question)

    response_time_ms = round((time.time() - start) * 1000)

    # Step 3: Store result in cache
    set_cache(request.question, result)

    return {
        "question": request.question,
        "intent": result["intent"],
        "answer": result["answer"],
        "chunks_used": result["chunks_used"],
        "cached": False,
        "response_time_ms": response_time_ms
    }