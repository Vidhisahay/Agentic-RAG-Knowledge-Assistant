from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.db.models import Base, QueryLog
from app.config import DATABASE_URL

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)

# Create table if it doesn't exist
Base.metadata.create_all(bind=engine)

def estimate_tokens(text: str) -> int:
    # Rough estimate: 1 token ≈ 4 characters
    return len(text) // 4

def log_query(
    question: str,
    intent: str,
    answer: str,
    cached: bool,
    chunks_used: int,
    response_time_ms: int
):
    db = SessionLocal()
    try:
        entry = QueryLog(
            question=question,
            intent=intent,
            answer=answer,
            cached=cached,
            chunks_used=chunks_used,
            response_time_ms=response_time_ms,
            estimated_tokens=estimate_tokens(question + answer)
        )
        db.add(entry)
        db.commit()
    except Exception as e:
        db.rollback()
        print(f"Logging error: {e}")
    finally:
        db.close()