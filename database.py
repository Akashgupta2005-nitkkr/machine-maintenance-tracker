"""Database setup: one engine, one session factory, one base class."""
import os

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

# Config comes from an environment variable (12-factor style), with a safe default.
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./maintenance.db")

engine = create_engine(
    DATABASE_URL,
    # SQLite only: allow use across FastAPI's worker threads.
    connect_args={"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {},
)
SessionLocal = sessionmaker(bind=engine, autoflush=False)


class Base(DeclarativeBase):
    pass


def get_db():
    """FastAPI dependency: give each request its own session, always close it."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
