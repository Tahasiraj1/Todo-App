# [Task]: T011, T016 [From]: plan.md §Project Structure, data-model.md
"""
Database connection and session management for Neon PostgreSQL.
Uses SQLModel with connection pooling for efficient database access.
"""

import os
from contextlib import contextmanager
from typing import Generator, Optional

from dotenv import load_dotenv
from sqlmodel import Session, SQLModel, create_engine

# Load environment variables from .env file
load_dotenv()

# Get database URL from environment
DATABASE_URL = os.getenv("DATABASE_URL", "")

# Engine will be initialized lazily when first needed
_engine: Optional[object] = None


def get_engine():
    """Get or create the database engine."""
    global _engine
    if _engine is None:
        if not DATABASE_URL:
            raise ValueError(
                "DATABASE_URL environment variable is required. "
                "Create a .env file with your Neon PostgreSQL connection string."
            )
        _engine = create_engine(
            DATABASE_URL,
            echo=os.getenv("DEBUG", "false").lower() == "true",
            pool_pre_ping=True,
            pool_size=5,
            max_overflow=10,
        )
    return _engine


def create_db_and_tables() -> None:
    """Create all tables defined in SQLModel metadata."""
    engine = get_engine()
    SQLModel.metadata.create_all(engine)


def get_session() -> Generator[Session, None, None]:
    """
    Dependency for FastAPI routes to get a database session.
    Automatically handles commit/rollback and closes the session.
    """
    engine = get_engine()
    with Session(engine) as session:
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise


@contextmanager
def get_db_session() -> Generator[Session, None, None]:
    """
    Context manager for getting a database session outside of FastAPI routes.
    """
    engine = get_engine()
    session = Session(engine)
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
