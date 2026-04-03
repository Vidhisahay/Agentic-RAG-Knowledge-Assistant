from fastapi import APIRouter, UploadFile, File, HTTPException
from pypdf import PdfReader
from app.rag.chunker import chunk_text
from app.rag.embedder import get_embeddings
from app.rag.retriever import build_index
from app.cache.redis_client import clear_cache
import io

router = APIRouter()

def extract_text(file: UploadFile) -> str:
    content = file.file.read()
    if file.filename.endswith(".pdf"):
        reader = PdfReader(io.BytesIO(content))
        return " ".join(page.extract_text() for page in reader.pages if page.extract_text())
    elif file.filename.endswith(".txt"):
        return content.decode("utf-8")
    else:
        raise HTTPException(status_code=400, detail="Only PDF and TXT files supported")

@router.post("/")
async def ingest_document(file: UploadFile = File(...)):
    text = extract_text(file)

    if not text.strip():
        raise HTTPException(status_code=400, detail="Could not extract text from file")

    chunks = chunk_text(text)
    embeddings = get_embeddings(chunks)
    build_index(embeddings, chunks)

    # Clear stale cache since document changed
    clear_cache()

    return {
        "status": "success",
        "filename": file.filename,
        "chunks_created": len(chunks)
    }