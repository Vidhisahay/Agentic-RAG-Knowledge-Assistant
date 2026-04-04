from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.api import ingest, query
from app.rag.retriever import load_index
from app.db.logger import engine
from app.db.models import Base

Base.metadata.create_all(bind=engine)

@asynccontextmanager
async def lifespan(app: FastAPI):
    load_index()
    print("FAISS index loaded")
    print("Database ready")
    print("Agentic RAG Assistant is running")
    yield

app = FastAPI(
    title="Agentic RAG Assistant",
    description="Intelligent document querying with agent-style reasoning, FAISS, Redis, and PostgreSQL",
    version="1.0.0",
    lifespan=lifespan
)

app.include_router(ingest.router, prefix="/ingest", tags=["Ingestion"])
app.include_router(query.router, prefix="/query", tags=["Query"])

@app.get("/", tags=["Health"])
async def root():
    return {"status": "running", "version": "1.0.0"}

@app.get("/health", tags=["Health"])
async def health():
    from app.rag.retriever import index as faiss_index
    return {
        "api": "healthy",
        "index_loaded": faiss_index is not None,
        "docs": "/docs"
    }