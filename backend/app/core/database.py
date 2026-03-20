from sqlmodel import SQLModel, create_engine, Session
from sqlalchemy import text
from app.core.config import settings

engine = create_engine(settings.DATABASE_URL, echo=settings.DEBUG)


def init_db():
    """Initialize database and create tables."""
    # Create pgvector extension
    with engine.connect() as conn:
        conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
        conn.commit()

    SQLModel.metadata.create_all(engine)


def get_session():
    """Get database session."""
    with Session(engine) as session:
        yield session
