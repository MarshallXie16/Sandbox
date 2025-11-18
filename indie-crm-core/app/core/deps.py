"""Dependency injection for FastAPI endpoints"""
from typing import Generator
from sqlalchemy.orm import Session
from app.db.session import SessionLocal


def get_db() -> Generator[Session, None, None]:
    """
    Database session dependency for FastAPI endpoints.

    Yields a SQLAlchemy session and ensures proper cleanup.

    Usage:
        @app.get("/items")
        def list_items(db: Session = Depends(get_db)):
            return db.query(Item).all()
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
