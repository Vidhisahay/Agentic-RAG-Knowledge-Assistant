from fastapi import APIRouter, UploadFile, File, HTTPException
from PyPDF2 import PdfReader
from app.rag.chunker import chunk_text
from app.rag.embedder import get_embeddings
from app.rag.retriever import build_index
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
    # Step 1: Extract raw text
    text = extract_text(file)

    if not text.strip():
        raise HTTPException(status_code=400, detail="Could not extract text from file")

    # Step 2: Chunk it
    chunks = chunk_text(text)

    # Step 3: Embed chunks
    embeddings = get_embeddings(chunks)

    # Step 4: Store in FAISS
    build_index(embeddings, chunks)

    return {
        "status": "success",
        "filename": file.filename,
        "chunks_created": len(chunks)
    }