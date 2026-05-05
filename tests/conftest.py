from __future__ import annotations

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.api.deps import db_dep
from app.api.router import api_router
from app.core.config import settings


class DummyDB:
    pass


@pytest.fixture()
def app() -> FastAPI:
    test_app = FastAPI()
    test_app.include_router(api_router)

    def override_db():
        yield DummyDB()

    test_app.dependency_overrides[db_dep] = override_db
    return test_app


@pytest.fixture()
def client(app: FastAPI) -> TestClient:
    return TestClient(app)


@pytest.fixture(autouse=True)
def test_settings_guard():
    prev_env = settings.app_env
    prev_provider = settings.embedding_provider
    prev_model = settings.embedding_model
    prev_dim = settings.embedding_dimension
    try:
        settings.app_env = "test"
        settings.embedding_provider = "hashing"
        settings.embedding_model = "hashing-test"
        settings.embedding_dimension = 256
        yield
    finally:
        settings.app_env = prev_env
        settings.embedding_provider = prev_provider
        settings.embedding_model = prev_model
        settings.embedding_dimension = prev_dim
