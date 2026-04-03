from sentence_transformers import SentenceTransformer
from typing import List

model = SentenceTransformer("all-MiniLM-L6-v2")  # downloads once, ~90MB, free forever

def get_embeddings(texts: List[str]) -> List[List[float]]:
    embeddings = model.encode(texts, convert_to_numpy=True)
    return embeddings.tolist()