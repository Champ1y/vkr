from __future__ import annotations

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.api.deps import db_dep
from app.api.router import api_router


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
