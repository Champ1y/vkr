from __future__ import annotations

from app.services.history import HistoryService


def test_history_includes_mode_version_and_extended(monkeypatch, client) -> None:
    def fake_get_history(self, *, limit: int = 50):
        return {
            "items": [
                {
                    "id": "e9a8ca06-df24-4af8-b4da-6f93a62ecdae",
                    "user_question": "Как настроить logical replication?",
                    "pg_version": "16",
                    "mode": "tutorial",
                    "extended_mode": True,
                    "answer_text": None,
                    "tutorial_json": {
                        "short_explanation": "x",
                        "prerequisites": [],
                        "steps": [],
                        "notes": [],
                    },
                    "status": "success",
                    "latency_ms": 123,
                    "created_at": "2026-04-22T10:00:00Z",
                    "sources": [],
                }
            ]
        }

    monkeypatch.setattr(HistoryService, "get_history", fake_get_history)

    response = client.get("/api/history")
    assert response.status_code == 200
    body = response.json()
    assert body["items"][0]["mode"] == "tutorial"
    assert body["items"][0]["pg_version"] == "16"
    assert body["items"][0]["extended_mode"] is True
