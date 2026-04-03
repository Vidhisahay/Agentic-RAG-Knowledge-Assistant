from fastapi.testclient import TestClient
from app.main import app
import io

client = TestClient(app)

def test_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["status"] == "running"

def test_ingest_txt():
    content = b"FastAPI is a modern Python web framework. FAISS is used for vector search."
    response = client.post(
        "/ingest/",
        files={"file": ("test.txt", io.BytesIO(content), "text/plain")}
    )
    assert response.status_code == 200
    assert response.json()["status"] == "success"
    assert response.json()["chunks_created"] >= 1

def test_ingest_invalid_format():
    content = b"some content"
    response = client.post(
        "/ingest/",
        files={"file": ("test.csv", io.BytesIO(content), "text/csv")}
    )
    assert response.status_code == 400