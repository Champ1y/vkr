from __future__ import annotations

import os

import pytest
from pgvector.psycopg import register_vector
from sqlalchemy import create_engine, event, text
from sqlalchemy.engine import Engine
from sqlalchemy.engine.url import make_url
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import settings
from app.db.base import Base


def _validate_test_database_url(test_database_url: str) -> None:
    app_database_url = settings.database_url
    if test_database_url == app_database_url:
        pytest.fail("TEST_DATABASE_URL совпадает с DATABASE_URL. Это небезопасно для integration-тестов.")

    parsed = make_url(test_database_url)
    db_name = (parsed.database or "").lower()

    # Защита от случайного удаления/пересоздания рабочей БД.
    if db_name == "rag_postgres" or ("rag_postgres" in db_name and "rag_postgres_test" not in db_name):
        pytest.fail(
            "TEST_DATABASE_URL указывает на небезопасную БД. "
            "Используйте только отдельную test-базу, например rag_postgres_test."
        )


def _truncate_all_tables(engine: Engine) -> None:
    table_names = [table.name for table in Base.metadata.sorted_tables]
    if not table_names:
        return
    joined = ", ".join(f'"{name}"' for name in table_names)
    with engine.begin() as conn:
        conn.execute(text(f"TRUNCATE TABLE {joined} RESTART IDENTITY CASCADE"))


@pytest.fixture(scope="session")
def integration_database_url() -> str:
    url = os.getenv("TEST_DATABASE_URL", "").strip()
    if not url:
        pytest.skip("TEST_DATABASE_URL не задан. Integration-тесты пропущены.")
    _validate_test_database_url(url)
    return url


@pytest.fixture(scope="session")
def integration_engine(integration_database_url: str) -> Engine:
    engine = create_engine(integration_database_url, pool_pre_ping=True)

    # Сначала создаём extension, затем регистрируем vector-type адаптер.
    with engine.begin() as conn:
        conn.execute(text("SELECT 1"))
        conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))

    @event.listens_for(engine, "connect")
    def on_connect(dbapi_connection, _connection_record) -> None:  # type: ignore[no-untyped-def]
        register_vector(dbapi_connection)

    # Пересоздаём пул, чтобы новые соединения уже прошли register_vector.
    engine.dispose()

    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)
    engine.dispose()


@pytest.fixture()
def db_session(integration_engine: Engine) -> Session:
    _truncate_all_tables(integration_engine)
    factory = sessionmaker(bind=integration_engine, autocommit=False, autoflush=False, expire_on_commit=False)
    session = factory()
    try:
        yield session
    finally:
        session.close()
