from fastapi.testclient import TestClient
from app.main import app
import io

client = TestClient(app)

def test_empty_question():
    response = client.post("/query/", json={"question": ""})
    assert response.status_code == 400

def test_full_pipeline():
    # Ingest first
    content = b"FAISS is Facebook AI Similarity Search. Redis is an in-memory cache. FastAPI is async."
    client.post(
        "/ingest/",
        files={"file": ("test.txt", io.BytesIO(content), "text/plain")}
    )

    # Then query
    response = client.post("/query/", json={"question": "What is FAISS?"})
    assert response.status_code == 200

    data = response.json()
    assert "answer" in data
    assert "intent" in data
    assert "cached" in data
    assert "response_time_ms" in data
    assert data["intent"] in ["summarize", "extract", "answer"]

def test_cache_hit():
    question = "What is Redis?"

    # First call — miss
    r1 = client.post("/query/", json={"question": question})
    assert r1.json()["cached"] == False

    # Second call — hit
    r2 = client.post("/query/", json={"question": question})
    assert r2.json()["cached"] == True
    assert r2.json()["response_time_ms"] < r1.json()["response_time_ms"]