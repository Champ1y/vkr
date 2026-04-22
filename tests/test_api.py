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


def test_ask_validation_rejects_extended_mode_for_answer(client) -> None:
    response = client.post(
        "/api/ask",
        json={
            "question": "как включить репликацию",
            "pg_version": "16",
            "mode": "answer",
            "extended_mode": True,
        },
    )

    assert response.status_code == 422


def test_ask_validation_rejects_unsupported_version(client) -> None:
    response = client.post(
        "/api/ask",
        json={
            "question": "как включить репликацию",
            "pg_version": "19",
            "mode": "answer",
            "extended_mode": False,
        },
    )
    assert response.status_code == 422
    assert "supported versions" in response.text


def test_ask_validation_rejects_unsupported_mode(client) -> None:
    response = client.post(
        "/api/ask",
        json={
            "question": "как включить репликацию",
            "pg_version": "16",
            "mode": "extended",
            "extended_mode": False,
        },
    )
    assert response.status_code == 422


def test_ask_answer_success_payload(monkeypatch, client) -> None:
    def fake_handle(self, req):
        return {
            "mode": "answer",
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
            "mode": "answer",
            "extended_mode": False,
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["mode"] == "answer"
    assert "extended_mode" not in body
    assert "tutorial" not in body
    assert body["sources"][0]["corpus_type"] == "official"


def test_ask_tutorial_extended_success_payload(monkeypatch, client) -> None:
    def fake_handle(self, req):
        return {
            "mode": "tutorial",
            "pg_version": req.pg_version,
            "extended_mode": req.extended_mode,
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
            "mode": "tutorial",
            "extended_mode": True,
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["mode"] == "tutorial"
    assert body["extended_mode"] is True
    assert "answer" not in body
    assert set(body["tutorial"]) == {"short_explanation", "prerequisites", "steps", "notes"}
    assert body["tutorial"]["steps"]
    assert body["sources"][0]["corpus_type"] == "official"
    assert body["sources"][1]["source_role"] == "supplementary"


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
