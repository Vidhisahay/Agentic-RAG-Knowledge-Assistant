from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.rag.embedder import get_embeddings
from app.rag.retriever import retrieve
from app.rag.generator import generate_answer

router = APIRouter()  # ← router must be defined FIRST

class QueryRequest(BaseModel):
    question: str

@router.post("/debug")          # ← THEN decorators
async def debug_query(request: QueryRequest):
    query_embedding = get_embeddings([request.question])[0]
    chunks = retrieve(query_embedding, top_k=5)
    return {"chunks": chunks}

@router.post("/")
async def query_documents(request: QueryRequest):
    if not request.question.strip():
        raise HTTPException(status_code=400, detail="Question cannot be empty")

    query_embedding = get_embeddings([request.question])[0]
    relevant_chunks = retrieve(query_embedding, top_k=5)

    if not relevant_chunks:
        raise HTTPException(status_code=404, detail="No documents ingested yet")

    answer = generate_answer(request.question, relevant_chunks)

    return {
        "question": request.question,
        "answer": answer,
        "chunks_used": len(relevant_chunks)
    }