from __future__ import annotations

from collections.abc import Generator

from pgvector.psycopg import register_vector
from sqlalchemy import create_engine, event
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import settings


engine = create_engine(
    settings.database_url,
    pool_pre_ping=True,
    pool_size=settings.db_pool_size,
    max_overflow=settings.db_max_overflow,
)


@event.listens_for(engine, "connect")
def on_connect(dbapi_connection, _connection_record) -> None:  # type: ignore[no-untyped-def]
    try:
        register_vector(dbapi_connection)
    except Exception:
        # DB might not have pgvector yet (before migrations). Safe to ignore here.
        pass


SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False, expire_on_commit=False)


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
