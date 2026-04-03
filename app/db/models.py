from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text
from sqlalchemy.orm import declarative_base
import datetime

Base = declarative_base()

class QueryLog(Base):
    __tablename__ = "query_logs"

    id             = Column(Integer, primary_key=True, index=True)
    question       = Column(Text, nullable=False)
    intent         = Column(String(20))
    answer         = Column(Text)
    cached         = Column(Boolean, default=False)
    chunks_used    = Column(Integer)
    response_time_ms = Column(Integer)
    estimated_tokens = Column(Integer)
    created_at     = Column(DateTime, default=datetime.datetime.utcnow)