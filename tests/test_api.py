from __future__ import annotations

from datetime import datetime, timezone
from types import SimpleNamespace
from uuid import uuid4

from app.services.orchestration import AskOrchestrationService


def test_api_health_endpoint(client) -> None:
    response = client.get("/api/health")
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    assert "timestamp" in body


def test_embeddings_health_endpoint(client) -> None:
    response = client.get("/api/health/embeddings")
    assert response.status_code == 200
    body = response.json()
    assert body["provider"] == "hashing"
    assert body["app_env"] == "test"
    assert body["configured_dimension"] == 256
    assert body["batch_size"] == 8
    assert body["max_seq_length"] == 8192


def test_ask_validation_rejects_unsupported_version(client) -> None:
    response = client.post(
        "/api/ask",
        json={
            "question": "как включить репликацию",
            "pg_version": "19",
            "answer_mode": "short",
        },
    )
    assert response.status_code == 422
    assert "supported versions" in response.text


def test_ask_validation_rejects_unsupported_answer_mode(client) -> None:
    response = client.post(
        "/api/ask",
        json={
            "question": "как включить репликацию",
            "pg_version": "16",
            "answer_mode": "extended",
        },
    )
    assert response.status_code == 422


def test_ask_short_success_payload(monkeypatch, client) -> None:
    def fake_handle(self, req):
        return {
            "answer_mode": "short",
            "pg_version": req.pg_version,
            "answer": "Краткий ответ",
            "sources": [
                {
                    "title": "PostgreSQL 16 docs",
                    "url": "https://www.postgresql.org/docs/16/logical-replication.html",
                    "corpus_type": "official",
                    "source_role": "base",
                    "section_path": "Chapter / Logical Replication",
                    "rank_position": 1,
                    "similarity_score": 0.91234,
                }
            ],
        }

    monkeypatch.setattr(AskOrchestrationService, "handle_ask", fake_handle)

    response = client.post(
        "/api/ask",
        json={
            "question": "как включить логическую репликацию",
            "pg_version": "16",
            "answer_mode": "short",
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["answer_mode"] == "short"
    assert "tutorial" not in body
    assert body["sources"][0]["corpus_type"] == "official"


def test_ask_detailed_success_payload(monkeypatch, client) -> None:
    def fake_handle(self, req):
        return {
            "answer_mode": "detailed",
            "pg_version": req.pg_version,
            "answer": "Развёрнутый ответ",
            "sources": [
                {
                    "title": "PostgreSQL 16 docs",
                    "url": "https://www.postgresql.org/docs/16/sql-vacuum.html",
                    "corpus_type": "official",
                    "source_role": "base",
                    "section_path": "SQL Command Reference / VACUUM",
                    "rank_position": 1,
                    "similarity_score": 0.90123,
                }
            ],
        }

    monkeypatch.setattr(AskOrchestrationService, "handle_ask", fake_handle)

    response = client.post(
        "/api/ask",
        json={
            "question": "подробно объясни VACUUM",
            "pg_version": "16",
            "answer_mode": "detailed",
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["answer_mode"] == "detailed"
    assert body["sources"][0]["corpus_type"] == "official"


def test_ask_tutorial_success_payload(monkeypatch, client) -> None:
    def fake_handle(self, req):
        return {
            "answer_mode": "tutorial",
            "pg_version": req.pg_version,
            "tutorial": {
                "short_explanation": "Короткое объяснение",
                "prerequisites": ["Установлен PostgreSQL"],
                "steps": ["Выполните шаг 1", "Выполните шаг 2"],
                "notes": ["Учтите ограничения версии"],
            },
            "sources": [
                {
                    "title": "PostgreSQL 16 docs",
                    "url": "https://www.postgresql.org/docs/16/logical-replication.html",
                    "corpus_type": "official",
                    "source_role": "base",
                    "section_path": "Chapter / Logical Replication",
                    "rank_position": 1,
                    "similarity_score": 0.94211,
                },
                {
                    "title": "Tutorial note",
                    "url": "supplementary://16/guide.md",
                    "corpus_type": "supplementary",
                    "source_role": "supplementary",
                    "section_path": "Guide / Logical Replication",
                    "rank_position": 2,
                    "similarity_score": 0.72111,
                },
            ],
        }

    monkeypatch.setattr(AskOrchestrationService, "handle_ask", fake_handle)

    response = client.post(
        "/api/ask",
        json={
            "question": "объясни как настроить логическую репликацию",
            "pg_version": "16",
            "answer_mode": "tutorial",
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["answer_mode"] == "tutorial"
    assert "answer" not in body
    assert set(body["tutorial"]) == {"short_explanation", "prerequisites", "steps", "notes"}
    assert body["tutorial"]["steps"]
    assert body["sources"][0]["corpus_type"] == "official"
    assert body["sources"][1]["source_role"] == "supplementary"


def test_ask_ignores_unknown_extra_fields(monkeypatch, client) -> None:
    captured = {}

    def fake_handle(self, req):
        captured["answer_mode"] = req.answer_mode
        captured["has_client_hint"] = hasattr(req, "client_hint")
        captured["has_debug_flags"] = hasattr(req, "debug_flags")
        return {
            "answer_mode": req.answer_mode,
            "pg_version": req.pg_version,
            "answer": "ok",
            "sources": [],
        }

    monkeypatch.setattr(AskOrchestrationService, "handle_ask", fake_handle)

    response = client.post(
        "/api/ask",
        json={
            "question": "что такое vacuum",
            "pg_version": "16",
            "answer_mode": "short",
            "client_hint": "sidebar",
            "debug_flags": {"trace": True},
        },
    )

    assert response.status_code == 200
    assert captured["answer_mode"] == "short"
    assert captured["has_client_hint"] is False
    assert captured["has_debug_flags"] is False


def test_ask_returns_503_when_runtime_init_error(monkeypatch, client) -> None:
    def fake_init(self, db):  # type: ignore[no-untyped-def]
        raise RuntimeError("sentence-transformers not installed")

    monkeypatch.setattr(AskOrchestrationService, "__init__", fake_init)

    response = client.post(
        "/api/ask",
        json={
            "question": "что такое pg_hba.conf",
            "pg_version": "16",
            "answer_mode": "short",
        },
    )
    assert response.status_code == 503
    assert "sentence-transformers" in response.text


def test_versions_endpoint(monkeypatch, client) -> None:
    from app.repositories.versions import VersionRepository

    def fake_list_supported(self):
        return [
            SimpleNamespace(
                id=uuid4(),
                major_version="16",
                docs_base_url="https://www.postgresql.org/docs/16/",
                is_supported=True,
                loaded_at=datetime.now(timezone.utc),
            )
        ]

    monkeypatch.setattr(VersionRepository, "list_supported", fake_list_supported)

    response = client.get("/api/versions")
    assert response.status_code == 200
    body = response.json()
    assert body["versions"][0]["major_version"] == "16"
