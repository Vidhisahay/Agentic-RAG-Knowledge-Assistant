import redis
import hashlib
import json
from app.config import REDIS_URL

client = redis.from_url(REDIS_URL, decode_responses=True)

CACHE_TTL = 3600  # 1 hour

def make_key(question: str) -> str:
    # Hash the question so keys are fixed length and safe
    return "rag:" + hashlib.md5(question.strip().lower().encode()).hexdigest()

def get_cached(question: str) -> dict | None:
    key = make_key(question)
    cached = client.get(key)
    if cached:
        return json.loads(cached)
    return None

def set_cache(question: str, result: dict):
    key = make_key(question)
    client.setex(key, CACHE_TTL, json.dumps(result))

def clear_cache():
    # Useful when new documents are ingested
    keys = client.keys("rag:*")
    if keys:
        client.delete(*keys)