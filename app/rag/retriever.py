import faiss
import numpy as np
import pickle
import os
from typing import List

INDEX_PATH = "faiss_index.bin"
CHUNKS_PATH = "chunks.pkl"

index = None
stored_chunks: List[str] = []

def build_index(embeddings: List[List[float]], chunks: List[str]):
    global index, stored_chunks

    dim = len(embeddings[0])
    index = faiss.IndexFlatL2(dim)
    vectors = np.array(embeddings).astype("float32")
    index.add(vectors)
    stored_chunks = chunks

    faiss.write_index(index, INDEX_PATH)
    with open(CHUNKS_PATH, "wb") as f:
        pickle.dump(chunks, f)

def load_index():
    global index, stored_chunks
    if os.path.exists(INDEX_PATH) and os.path.exists(CHUNKS_PATH):
        index = faiss.read_index(INDEX_PATH)
        with open(CHUNKS_PATH, "rb") as f:
            stored_chunks = pickle.load(f)

def retrieve(query_embedding: List[float], top_k: int = 5) -> List[str]:
    if index is None:
        load_index()

    if index is None:
        return []

    query_vector = np.array([query_embedding]).astype("float32")
    _, indices = index.search(query_vector, top_k)
    return [stored_chunks[i] for i in indices[0] if i < len(stored_chunks)]