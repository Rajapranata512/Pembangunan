"""
models_ai.py — Model database tambahan untuk fitur AI.
ChatHistory: menyimpan riwayat percakapan chatbot.
NewsSentiment: cache analisis sentimen berita per wilayah.
"""
import datetime
from sqlalchemy import Column, Integer, String, Float, Text, DateTime, ForeignKey
from database import Base


class ChatHistory(Base):
    """Riwayat percakapan chatbot per session."""
    __tablename__ = "chat_history"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String(64), nullable=False, index=True)
    role = Column(String(10), nullable=False)   # "user" | "assistant"
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)


class NewsSentiment(Base):
    """Cache analisis sentimen berita per wilayah."""
    __tablename__ = "news_sentiments"

    id = Column(Integer, primary_key=True, index=True)
    region_id = Column(Integer, ForeignKey("regions.id"), nullable=False, index=True)
    headlines_json = Column(Text)           # JSON array of headline strings
    overall_sentiment = Column(String(20))  # "positif" | "netral" | "negatif"
    confidence_score = Column(Float)
    summary = Column(Text)
    highlights_json = Column(Text)          # JSON array of highlight objects
    analyzed_at = Column(DateTime, default=datetime.datetime.utcnow)
