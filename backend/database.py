"""
database.py — SQLAlchemy engine, session factory, dan Base class.
Menggunakan SQLite untuk MVP lokal. Ganti SQLALCHEMY_DATABASE_URL ke
PostgreSQL connection string untuk production.
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

SQLALCHEMY_DATABASE_URL = "sqlite:///./wilayah_jawa.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},  # khusus SQLite
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    """Dependency injection untuk FastAPI — menghasilkan DB session per request."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
