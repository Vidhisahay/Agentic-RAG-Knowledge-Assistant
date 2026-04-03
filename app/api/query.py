from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import time
from app.agent.controller import run_agent
from app.rag.embedder import get_embeddings
from app.rag.retriever import retrieve
from app.cache.redis_client import get_cached, set_cache
from app.db.logger import log_query, SessionLocal
from app.db.models import QueryLog

router = APIRouter()  # ← ALWAYS first

class QueryRequest(BaseModel):
    question: str

@router.post("/debug")
async def debug_query(request: QueryRequest):
    query_embedding = get_embeddings([request.question])[0]
    chunks = retrieve(query_embedding, top_k=5)
    return {"chunks": chunks}

@router.get("/logs")
async def get_logs(limit: int = 10):
    db = SessionLocal()
    try:
        logs = db.query(QueryLog)\
                 .order_by(QueryLog.created_at.desc())\
                 .limit(limit)\
                 .all()
        return [
            {
                "id": log.id,
                "question": log.question,
                "intent": log.intent,
                "cached": log.cached,
                "response_time_ms": log.response_time_ms,
                "estimated_tokens": log.estimated_tokens,
                "created_at": log.created_at.isoformat()
            }
            for log in logs
        ]
    finally:
        db.close()

@router.post("/")
async def query_documents(request: QueryRequest):
    if not request.question.strip():
        raise HTTPException(status_code=400, detail="Question cannot be empty")

    start = time.time()

    # Check cache
    cached = get_cached(request.question)
    if cached:
        response_time_ms = round((time.time() - start) * 1000)
        log_query(
            question=request.question,
            intent=cached["intent"],
            answer=cached["answer"],
            cached=True,
            chunks_used=cached["chunks_used"],
            response_time_ms=response_time_ms
        )
        return {
            "question": request.question,
            **cached,
            "cached": True,
            "response_time_ms": response_time_ms
        }

    # Cache miss — run agent
    result = run_agent(request.question)
    response_time_ms = round((time.time() - start) * 1000)

    set_cache(request.question, result)

    log_query(
        question=request.question,
        intent=result["intent"],
        answer=result["answer"],
        cached=False,
        chunks_used=result["chunks_used"],
        response_time_ms=response_time_ms
    )

    return {
        "question": request.question,
        "intent": result["intent"],
        "answer": result["answer"],
        "chunks_used": result["chunks_used"],
        "cached": False,
        "response_time_ms": response_time_ms
    }