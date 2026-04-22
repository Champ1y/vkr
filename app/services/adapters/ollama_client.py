"""Low-level Ollama HTTP client.

Shared by both generation and embedding adapters.
Communicates via the Ollama REST API using httpx.
"""
from __future__ import annotations

import httpx

from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)


class OllamaClient:
    """Thin wrapper around Ollama REST API."""

    def __init__(
        self,
        *,
        base_url: str | None = None,
        timeout: int | None = None,
    ) -> None:
        self.base_url = (base_url or settings.ollama_base_url).rstrip("/")
        self.timeout = timeout or settings.ollama_timeout

    # ---- Chat completions (/api/chat) ----

    def chat(
        self,
        *,
        model: str,
        messages: list[dict[str, str]],
        temperature: float = 0.2,
    ) -> str:
        """Non-streaming chat completion. Returns assistant message content."""
        payload = {
            "model": model,
            "messages": messages,
            "stream": False,
            "options": {"temperature": temperature},
        }
        response = self._post("/api/chat", payload)
        return response["message"]["content"].strip()

    # ---- Embeddings (/api/embed) ----

    def embed(self, *, model: str, texts: list[str]) -> list[list[float]]:
        """Get embeddings for a list of texts."""
        payload = {
            "model": model,
            "input": texts,
        }
        response = self._post("/api/embed", payload)
        return response["embeddings"]

    # ---- Health check ----

    def is_available(self) -> bool:
        """Check if Ollama server is running."""
        try:
            with httpx.Client(timeout=5) as client:
                r = client.get(f"{self.base_url}/api/tags")
                return r.status_code == 200
        except Exception:
            return False

    def list_models(self) -> list[str]:
        """List locally available models."""
        try:
            with httpx.Client(timeout=10) as client:
                r = client.get(f"{self.base_url}/api/tags")
                r.raise_for_status()
                return [m["name"] for m in r.json().get("models", [])]
        except Exception:
            return []

    # ---- Internal ----

    def _post(self, path: str, payload: dict) -> dict:
        url = f"{self.base_url}{path}"
        try:
            with httpx.Client(timeout=self.timeout) as client:
                response = client.post(url, json=payload)
                response.raise_for_status()
                return response.json()
        except httpx.ConnectError:
            raise RuntimeError(
                f"Не удалось подключиться к Ollama ({self.base_url}). "
                "Убедитесь, что Ollama запущен: ollama serve. "
                "Если backend работает в Docker, используйте OLLAMA_BASE_URL=http://host.docker.internal:11434"
            )
        except httpx.TimeoutException:
            raise RuntimeError(
                f"Timeout при запросе к Ollama ({self.base_url}). "
                f"Модель может быть не загружена. Выполните: ollama pull {payload.get('model', '?')}"
            )
        except httpx.HTTPStatusError as exc:
            status = exc.response.status_code
            body = exc.response.text[:500]
            if status == 404:
                model = payload.get("model", "?")
                raise RuntimeError(
                    f"Модель '{model}' не найдена в Ollama. Выполните: ollama pull {model}"
                )
            raise RuntimeError(f"Ошибка Ollama (HTTP {status}): {body}")
