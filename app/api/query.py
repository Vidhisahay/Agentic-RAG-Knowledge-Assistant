from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.agent.controller import run_agent
from app.rag.embedder import get_embeddings
from app.rag.retriever import retrieve

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

    result = run_agent(request.question)

    return {
        "question": request.question,
        "intent": result["intent"],
        "answer": result["answer"],
        "chunks_used": result["chunks_used"]
    }