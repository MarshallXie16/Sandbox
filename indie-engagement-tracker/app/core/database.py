"""Database connection and session management."""
from typing import Generator
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool

from app.core.config import settings
from app.core.logging import logger


# Create engine with appropriate settings
def create_db_engine() -> any:
    """Create SQLAlchemy engine based on database URL."""
    connect_args = {}

    # SQLite-specific configuration
    if settings.database_url.startswith("sqlite"):
        connect_args["check_same_thread"] = False
        # Use StaticPool for SQLite to avoid connection issues
        engine = create_engine(
            settings.database_url,
            connect_args=connect_args,
            poolclass=StaticPool,
            echo=settings.log_level == "DEBUG",
        )
    else:
        # PostgreSQL or other databases
        engine = create_engine(
            settings.database_url,
            pool_pre_ping=True,
            pool_size=5,
            max_overflow=10,
            echo=settings.log_level == "DEBUG",
        )

    logger.info(f"Database engine created for: {settings.database_url.split('@')[-1] if '@' in settings.database_url else 'sqlite'}")
    return engine


# Create engine
engine = create_db_engine()

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db() -> Generator[Session, None, None]:
    """
    Dependency for getting database sessions in FastAPI endpoints.

    Yields:
        Session: SQLAlchemy session

    Example:
        @app.get("/items")
        def read_items(db: Session = Depends(get_db)):
            return db.query(Item).all()
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db() -> None:
    """
    Initialize the database by creating all tables.

    This should be called once when the application starts.
    """
    from app.models import Base

    logger.info("Initializing database...")
    Base.metadata.create_all(bind=engine)
    logger.info("Database initialized successfully")


def get_session() -> Session:
    """
    Get a database session for CLI and background tasks.

    Returns:
        Session: SQLAlchemy session (caller must close it)

    Example:
        db = get_session()
        try:
            # Do database operations
            db.commit()
        finally:
            db.close()
    """
    return SessionLocal()
