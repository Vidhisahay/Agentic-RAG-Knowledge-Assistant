from fastapi import FastAPI
from app.api import ingest, query

from dotenv import load_dotenv
load_dotenv()

app = FastAPI(title="Agentic RAG Assistant")

app.include_router(ingest.router, prefix="/ingest", tags=["Ingestion"])
app.include_router(query.router, prefix="/query", tags=["Query"])

@app.get("/")
async def root():
    return {"status": "Agentic RAG Assistant is running"}