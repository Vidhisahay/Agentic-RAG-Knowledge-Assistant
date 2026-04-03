import faiss
import numpy as np
from typing import List

# In-memory store (replace with disk persistence later)
index = None
stored_chunks: List[str] = []

def build_index(embeddings: List[List[float]], chunks: List[str]):
    global index, stored_chunks

    dim = len(embeddings[0])
    index = faiss.IndexFlatL2(dim)
    vectors = np.array(embeddings).astype("float32")
    index.add(vectors)
    stored_chunks = chunks

def retrieve(query_embedding: List[float], top_k: int = 5) -> List[str]:
    if index is None:
        return []

    query_vector = np.array([query_embedding]).astype("float32")
    _, indices = index.search(query_vector, top_k)

    return [stored_chunks[i] for i in indices[0] if i < len(stored_chunks)]